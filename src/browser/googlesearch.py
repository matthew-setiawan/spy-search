import asyncio
import concurrent.futures
import aiohttp
from html import unescape
import logging
from typing import List, Dict, Optional
import time
from functools import lru_cache
import re
from urllib.parse import urlparse, quote_plus
import os
import requests
from bs4 import BeautifulSoup
from selectolax.parser import HTMLParser
import json

logger = logging.getLogger(__name__)

class GoogleSearch:
    def __init__(self):
        # Google Custom Search Engine configuration
        self.api_key = os.getenv('GOOGLE_CSE_API_KEY')
        self.cse_id = os.getenv('GOOGLE_CSE_ID')
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        
        if not self.api_key or not self.cse_id:
            raise ValueError("GOOGLE_CSE_API_KEY and GOOGLE_CSE_ID must be set in environment variables")
        
        # Ultra-aggressive timeouts for 1.5s total requirement
        self._timeout = aiohttp.ClientTimeout(
            total=0.4,      # Max 400ms per request
            connect=0.1,    # 100ms to connect
            sock_read=0.3   # 300ms to read
        )
        
        # Optimized connector settings
        self._connector_config = {
            'limit': 50,
            'limit_per_host': 20,
            'ttl_dns_cache': 300,
            'use_dns_cache': True,
            'keepalive_timeout': 30,
            'enable_cleanup_closed': True,
        }
        
        # Simple caches
        self._failed_urls = set()
        self._content_cache = {}
        
        # Regex patterns
        self._text_cleanup = re.compile(r'\s+')
        self._html_tags = re.compile(r'<[^>]+>')
        
    def _search_google_cse(self, query: str, max_results: int = 20) -> List[Dict]:
        """
        Search using Google Custom Search Engine
        """
        try:
            # Google CSE max is 10 per request, so we need multiple requests for more results
            all_results = []
            start_index = 1
            
            while len(all_results) < max_results and start_index <= 91:  # Google CSE max is 100 results total
                # Calculate how many results to request in this batch
                batch_size = min(10, max_results - len(all_results))
                
                params = {
                    'key': self.api_key,
                    'cx': self.cse_id,
                    'q': query,
                    'num': batch_size,
                    'start': start_index,
                    'safe': 'off'
                }
                
                logger.info(f"Searching Google CSE for: {query} (batch starting at {start_index})")
                
                response = requests.get(self.base_url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    batch_results = self._parse_google_results(data, batch_size)
                    all_results.extend(batch_results)
                    
                    # If we got fewer results than requested, we've reached the end
                    if len(batch_results) < batch_size:
                        break
                        
                    start_index += 10
                else:
                    logger.error(f"Google CSE search failed with status code: {response.status_code}")
                    logger.error(f"Response: {response.text}")
                    break
            
            logger.info(f"Found {len(all_results)} results from Google CSE")
            return all_results[:max_results]
                
        except Exception as e:
            logger.error(f"Google CSE search error: {e}")
            return []
    
    def _parse_google_results(self, data: dict, max_results: int) -> List[Dict]:
        """
        Parse Google CSE API results
        """
        results = []
        
        try:
            items = data.get('items', [])
            
            for item in items[:max_results]:
                try:
                    title = item.get('title', '')
                    link = item.get('link', '')
                    snippet = item.get('snippet', '')
                    
                    if title and link:
                        results.append({
                            "title": title,
                            "link": link,
                            "snippet": snippet,
                            "full_content": ""
                        })
                        
                except Exception as e:
                    logger.debug(f"Error parsing Google result: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing Google CSE response: {e}")
            
        return results
        
    @lru_cache(maxsize=1000)
    def _is_valid_url(self, url: str) -> bool:
        """Fast URL validation."""
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc and parsed.scheme in ('http', 'https'))
        except:
            return False

    async def _extract_content_fast(self, session: aiohttp.ClientSession, url: str) -> str:
        """Ultra-fast content extraction - fail fast, succeed faster."""
        if not url or url in self._failed_urls or not self._is_valid_url(url):
            return ""
        
        if url in self._content_cache:
            return self._content_cache[url]
        
        try:
            # Add more generous request timeout for content extraction
            timeout = aiohttp.ClientTimeout(total=30, connect=10, sock_read=20)
            async with session.get(url, allow_redirects=True, max_redirects=2, timeout=timeout) as response:
                if response.status != 200:
                    self._failed_urls.add(url)
                    return ""
                
                # Read only first 20KB - enough for most articles
                content_bytes = await response.content.read(20480)
                content_str = content_bytes.decode('utf-8', errors='ignore')
                
                # Fast text extraction using BeautifulSoup, with simple fallbacks
                try:
                    soup = BeautifulSoup(content_str, 'html.parser')
                    texts = []

                    # 1) Meta description first if present
                    meta_desc = soup.find('meta', attrs={'name': 'description'})
                    if meta_desc and meta_desc.get('content'):
                        md = meta_desc.get('content', '').strip()
                        if md and len(md) > 40:
                            texts.append(md)

                    # 2) Article container common patterns
                    article = soup.find('article')
                    if article:
                        for p in article.find_all('p')[:15]:
                            t = p.get_text(strip=True)
                            if t and len(t) > 20:
                                texts.append(t)
                                if len(' '.join(texts)) > 600:
                                    break

                    # 3) Headings as context
                    if len(' '.join(texts)) < 200:
                        for h in soup.find_all(['h1','h2','h3'])[:5]:
                            t = h.get_text(strip=True)
                            if t and 10 < len(t) < 140:
                                texts.append(t)
                                if len(' '.join(texts)) > 300:
                                    break

                    # 4) General paragraphs fallback
                    if len(' '.join(texts)) < 200:
                        for p in soup.find_all('p')[:15]:
                            t = p.get_text(strip=True)
                            if t and len(t) > 20:
                                texts.append(t)
                                if len(' '.join(texts)) > 600:
                                    break
                except Exception:
                    # Fallback: simple regex when parser fails
                    matches = re.findall(r'<p[^>]*>(.*?)</p>', content_str, re.IGNORECASE | re.DOTALL)[:12]
                    texts = []
                    for match in matches:
                        text = self._html_tags.sub('', match).strip()
                        if text and len(text) > 20:
                            texts.append(text)
                            if len(' '.join(texts)) > 600:
                                break
                
                if not texts:
                    self._failed_urls.add(url)
                    return ""
                
                final_text = self._text_cleanup.sub(' ', unescape(' '.join(texts))).strip()[:10000]
                
                # Simple cache management
                if len(self._content_cache) > 100:
                    # Remove oldest 20 entries
                    old_keys = list(self._content_cache.keys())[:20]
                    for key in old_keys:
                        del self._content_cache[key]
                
                self._content_cache[url] = final_text
                return final_text
                
        except asyncio.TimeoutError:
            self._failed_urls.add(url)
            logger.debug(f"Content extraction timed out for {url}")
            return ""
        except Exception as e:
            self._failed_urls.add(url)
            logger.debug(f"Content extraction failed for {url}: {e}")
            return ""

    async def _process_results_fast(self, results: List[Dict], k: int) -> List[Dict]:
        """Process search results with content extraction - ultra fast or fail."""
        if not results:
            return []
        
        connector = aiohttp.TCPConnector(**self._connector_config)
        
        try:
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=self._timeout,
                headers={
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
                    "Accept": "text/html,*/*;q=0.8",
                },
            ) as session:
                
                # Limit concurrent requests to avoid overwhelming sites
                semaphore = asyncio.Semaphore(min(k, 5))
                
                async def process_single(result):
                    async with semaphore:
                        url = result.get("link", "")
                        content = await self._extract_content_fast(session, url)
                        result["full_content"] = content
                        return result
                
                # Process only the URLs we need
                tasks = [process_single(result) for result in results[:k]]
                
                # Race against time - 45s max for content extraction
                try:
                    completed_results = await asyncio.wait_for(
                        asyncio.gather(*tasks, return_exceptions=True),
                        timeout=45.0
                    )
                    
                    final_results = []
                    for i, result_or_exc in enumerate(completed_results):
                        if isinstance(result_or_exc, Exception):
                            # On any error, set empty content but keep the result
                            results[i]["full_content"] = ""
                            final_results.append(results[i])
                        else:
                            final_results.append(result_or_exc)
                    
                    return final_results
                    
                except asyncio.TimeoutError:
                    logger.debug("Content extraction timed out - returning results without content")
                    # If we timeout, return results with empty content
                    for result in results[:k]:
                        result["full_content"] = ""
                    return results[:k]
                    
        except Exception as e:
            logger.error(f"Session creation failed: {e}")
            # Return empty list on session creation failure
            return []
        finally:
            await connector.close()

    def search_result(self, query: str, k: int = 20, backend: str = "text", deep_search: bool = True) -> List[Dict]:
        """Super efficient search using Google CSE."""
        start_time = time.time()
        logger.info(f"Starting efficient search for: '{query}'")
        
        try:
            # Use Google CSE search
            results = self._search_google_cse(query, k)
            
            if not results:
                logger.info(f"No results found for: '{query}'")
                return []
                
            # Check if we're already close to time limit
            elapsed = time.time() - start_time
            if elapsed > 1.5:  # If basic search took too long, skip deep search
                logger.warning(f"Basic search took {elapsed:.3f}s - skipping deep search")
                for result in results:
                    result["full_content"] = ""
                return results[:k]
            
            if not deep_search:
                for result in results:
                    result["full_content"] = ""
                return results[:k]
            
            # Deep search with remaining time budget
            try:
                # Run async content extraction
                try:
                    # Check if there's already an event loop running
                    try:
                        loop = asyncio.get_running_loop()
                        # If we're in an async context (and likely on the event-loop thread),
                        # offload deep search to a worker thread with its own event loop to avoid deadlocks.
                        logger.info("Already in async context - offloading deep search to worker thread")
                        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                            future = pool.submit(lambda: asyncio.run(self._process_results_fast(results, k)))
                            final_results = future.result(timeout=60.0)
                    except RuntimeError:
                        # No event loop running, safe to create one
                        final_results = asyncio.run(self._process_results_fast(results, k))
                    
                    total_time = time.time() - start_time
                    logger.info(f"Search completed in {total_time:.3f}s")
                    
                    # Final time check - if we exceeded 1.5s, we failed
                    if total_time > 60.0:
                        logger.warning(f"Search exceeded 60s limit ({total_time:.3f}s) - returning empty")
                        return []
                    
                    return final_results if final_results else []
                    
                except concurrent.futures.TimeoutError:
                    logger.warning("Deep search worker timed out - returning results without content")
                    for result in results:
                        result["full_content"] = ""
                    return results[:k]
                except Exception as e:
                    logger.error(f"Async processing failed: {e}")
                    # Return results without content on async failure
                    for result in results:
                        result["full_content"] = ""
                    return results[:k]
                    
            except Exception as e:
                logger.error(f"Deep search failed: {e}")
                return []  # Return empty on any deep search failure
                
        except Exception as e:
            logger.error(f"Search failed for '{query}': {e}")
            return []  # Return empty on any search failure

    def today_new(self, category: str) -> List[Dict]:
        """Fast news retrieval using Google CSE."""
        category_queries = {
            "technology": "latest tech AI news",
            "finance": "latest finance market news", 
            "entertainment": "latest entertainment news",
            "sports": "latest sports news",
            "world": "latest world news",
            "health": "latest health news"
        }
        
        query = category_queries.get(category, "latest news")
        
        try:
            logger.info(f"Searching news for category: {category}")
            # Use Google CSE search for news
            return self._search_google_cse(query, 8)
        except Exception as e:
            logger.error(f"News search failed for '{category}': {e}")
            return []

    def clear_cache(self):
        """Clear caches."""
        self._content_cache.clear()
        self._failed_urls.clear()
        self._is_valid_url.cache_clear()
