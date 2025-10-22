package main

import (
	"context"
	"crypto/tls"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"math/rand"
	"net"
	"net/http"
	"net/url"
	"os"
	"strings"
	"sync"
	"time"

	"github.com/PuerkitoBio/goquery"
)

type Result struct {
	URL     string `json:"url"`
	Title   string `json:"title,omitempty"`
	Snippet string `json:"snippet,omitempty"`
	Elapsed string `json:"elapsed"`
	Error   string `json:"error,omitempty"`
}

var userAgents = []string{
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
	"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

func main() {
	http.HandleFunc("/search", searchHandler)
	log.Println("Server started on :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}

func searchHandler(w http.ResponseWriter, r *http.Request) {
	query := r.URL.Query().Get("q")
	if query == "" {
		http.Error(w, "missing query param 'q'", http.StatusBadRequest)
		return
	}
	log.Printf("[INFO] Received search request: q=%q", query)

	start := time.Now()

	urls, err := googleCSESearch(query, 5)
	if err != nil {
		http.Error(w, "search error: "+err.Error(), http.StatusInternalServerError)
		log.Printf("[ERROR] Google CSE search failed: %v", err)
		return
	}

	log.Printf("[INFO] Found %d URLs", len(urls))
	for i, u := range urls {
		log.Printf("  URL %d: %s", i+1, u)
	}

	const maxWorkers = 10
	sem := make(chan struct{}, maxWorkers)

	var wg sync.WaitGroup
	results := make([]Result, len(urls))

	ctx, cancel := context.WithTimeout(r.Context(), 15*time.Second)
	defer cancel()

	for i, link := range urls {
		wg.Add(1)
		go func(i int, link string) {
			defer wg.Done()

			select {
			case sem <- struct{}{}:
			case <-ctx.Done():
				results[i] = Result{URL: link, Error: "timeout before scraping started", Elapsed: "0"}
				return
			}
			defer func() { <-sem }()

			log.Printf("[INFO] Starting scrape for URL %d: %s", i+1, link)
			t0 := time.Now()
			title, snippet, err := scrapeURLWithRetry(ctx, link, 3)
			elapsed := time.Since(t0).String()

			if err != nil {
				log.Printf("[ERROR] Scrape failed for URL %d (%s): %v", i+1, link, err)
				results[i] = Result{URL: link, Error: err.Error(), Elapsed: elapsed}
			} else {
				log.Printf("[INFO] Completed scrape for URL %d in %s", i+1, elapsed)
				results[i] = Result{URL: link, Title: title, Snippet: snippet, Elapsed: elapsed}
			}
		}(i, link)
	}

	wg.Wait()
	totalTime := time.Since(start)
	log.Printf("[INFO] Total elapsed time for query %q: %s", query, totalTime)

	resp := map[string]interface{}{
		"query":      query,
		"total_time": totalTime.String(),
		"results":    results,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}

func createHTTPClient() *http.Client {
	tr := &http.Transport{
		MaxIdleConns:        100,
		MaxIdleConnsPerHost: 10,
		IdleConnTimeout:     90 * time.Second,
		DialContext: (&net.Dialer{
			Timeout:   10 * time.Second,
			KeepAlive: 30 * time.Second,
		}).DialContext,
		TLSHandshakeTimeout: 10 * time.Second,
		TLSClientConfig: &tls.Config{
			InsecureSkipVerify: false,
		},
		DisableCompression: false,
	}

	return &http.Client{
		Transport: tr,
		Timeout:   10 * time.Second,
		CheckRedirect: func(req *http.Request, via []*http.Request) error {
			if len(via) >= 10 {
				return fmt.Errorf("stopped after 10 redirects")
			}
			return nil
		},
	}
}

func googleCSESearch(query string, n int) ([]string, error) {
	client := createHTTPClient()
	
	// Google CSE API configuration - use environment variables
	apiKey := os.Getenv("GOOGLE_CSE_API_KEY")
	cseID := os.Getenv("GOOGLE_CSE_ID")
	
	if apiKey == "" || cseID == "" {
		return nil, fmt.Errorf("GOOGLE_CSE_API_KEY and GOOGLE_CSE_ID environment variables must be set")
	}
	
	searchURL := fmt.Sprintf("https://www.googleapis.com/customsearch/v1?key=%s&cx=%s&q=%s&num=%d", 
		apiKey, cseID, url.QueryEscape(query), n)

	req, err := http.NewRequest("GET", searchURL, nil)
	if err != nil {
		return nil, err
	}

	req.Header.Set("User-Agent", getRandomUserAgent())
	req.Header.Set("Accept", "application/json")
	req.Header.Set("Accept-Encoding", "gzip, deflate")
	req.Header.Set("Connection", "keep-alive")
	req.Header.Set("Upgrade-Insecure-Requests", "1")

	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return nil, fmt.Errorf("status code %d", resp.StatusCode)
	}

	// Parse Google CSE JSON response
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	var googleResponse struct {
		Items []struct {
			Link string `json:"link"`
		} `json:"items"`
	}

    err = json.Unmarshal(body, &googleResponse)
	if err != nil {
		return nil, err
	}

	var urls []string
	for i, item := range googleResponse.Items {
		if i >= n {
			break
		}
		urls = append(urls, item.Link)
	}

	if len(urls) == 0 {
		return nil, fmt.Errorf("no URLs found")
	}
	return urls, nil
}

func scrapeURLWithRetry(ctx context.Context, targetURL string, maxRetries int) (string, string, error) {
	var lastErr error

	for attempt := 0; attempt < maxRetries; attempt++ {
		if attempt > 0 {
			select {
			case <-ctx.Done():
				return "", "", ctx.Err()
			case <-time.After(time.Duration(attempt*500) * time.Millisecond):
			}
		}

		title, snippet, err := scrapeURL(ctx, targetURL)
		if err == nil {
			return title, snippet, nil
		}

		lastErr = err
		log.Printf("[WARN] Attempt %d failed for %s: %v", attempt+1, targetURL, err)
	}

	return "", "", fmt.Errorf("failed after %d attempts: %v", maxRetries, lastErr)
}

func scrapeURL(ctx context.Context, targetURL string) (string, string, error) {
	client := createHTTPClient()

	reqCtx, cancel := context.WithTimeout(ctx, 8*time.Second)
	defer cancel()

	req, err := http.NewRequestWithContext(reqCtx, "GET", targetURL, nil)
	if err != nil {
		return "", "", err
	}

	req.Header.Set("User-Agent", getRandomUserAgent())
	req.Header.Set("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8")
	req.Header.Set("Accept-Language", "en-US,en;q=0.9")
	req.Header.Set("Accept-Encoding", "gzip, deflate, br")
	req.Header.Set("Connection", "keep-alive")
	req.Header.Set("Upgrade-Insecure-Requests", "1")
	req.Header.Set("Sec-Fetch-Dest", "document")
	req.Header.Set("Sec-Fetch-Mode", "navigate")
	req.Header.Set("Sec-Fetch-Site", "none")
	req.Header.Set("Cache-Control", "max-age=0")

	if strings.Contains(targetURL, "github.com") {
		req.Header.Set("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
	}

	resp, err := client.Do(req)
	if err != nil {
		return "", "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode == 403 {
		return "", "", fmt.Errorf("access forbidden (403) - possible bot detection")
	}
	if resp.StatusCode == 429 {
		return "", "", fmt.Errorf("rate limited (429)")
	}
	if resp.StatusCode != 200 {
		return "", "", fmt.Errorf("status code %d", resp.StatusCode)
	}

	limitedReader := io.LimitReader(resp.Body, 200*1024)

	doc, err := goquery.NewDocumentFromReader(limitedReader)
	if err != nil {
		return "", "", err
	}

	title := extractTitle(doc)
	snippet := extractSnippet(doc)

	return title, snippet, nil
}

func extractTitle(doc *goquery.Document) string {
	title := strings.TrimSpace(doc.Find("title").First().Text())
	if title == "" {
		title = strings.TrimSpace(doc.Find("h1").First().Text())
	}
	if len(title) > 200 {
		title = title[:200] + "..."
	}
	return title
}

func extractSnippet(doc *goquery.Document) string {
	doc.Find("script, style, nav, header, footer, aside").Remove()

	var textParts []string

	doc.Find("meta[name='description']").Each(func(i int, s *goquery.Selection) {
		if content, exists := s.Attr("content"); exists && content != "" {
			textParts = append(textParts, strings.TrimSpace(content))
		}
	})

	if len(textParts) == 0 {
		doc.Find("p, div, span").Each(func(i int, s *goquery.Selection) {
			text := strings.TrimSpace(s.Text())
			if len(text) > 20 && len(textParts) < 5 {
				textParts = append(textParts, text)
			}
		})
	}

	fullText := strings.Join(textParts, " ")
	words := strings.Fields(fullText)

	if len(words) > 80 {
		words = words[:80]
	}

	snippet := strings.Join(words, " ")
	if len(snippet) > 500 {
		snippet = snippet[:500] + "..."
	}

	return snippet
}

func getRandomUserAgent() string {
	return userAgents[rand.Intn(len(userAgents))]
}

func init() {
	rand.Seed(time.Now().UnixNano())
}
