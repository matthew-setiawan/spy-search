#!/usr/bin/env python3
"""
Focused test script for Spy Search API search features
Base URL: https://spy-search.onrender.com
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BASE_URL = "https://spy-search.onrender.com"
API_BASE = BASE_URL  # No /api prefix needed

def test_health_check():
    """Test if the API is accessible"""
    print("🔍 Testing API Health...")
    try:
        # Test root endpoint
        response = requests.get(BASE_URL, timeout=30)
        print(f"✅ Root endpoint: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"📄 Root response: {data}")
            except:
                print(f"📄 Root response (text): {response.text[:100]}...")
        
        # Test API docs
        docs_response = requests.get(f"{BASE_URL}/docs", timeout=30)
        print(f"✅ API Docs: {docs_response.status_code}")
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_quick_search():
    """Test the quick search endpoint"""
    print("\n🚀 Testing Quick Search...")
    
    query = "Please find latest news on Neo Bank Commerce"
    url = f"{API_BASE}/quick/{query}"
    
    # Sample messages for testing
    messages = [
        {"role": "user", "content": f"Search for information about: {query}"}
    ]
    
    data = {
        "messages": json.dumps(messages)
    }
    
    try:
        print(f"⏳ Sending request to: {url}")
        print(f"📝 Query: {query}")
        
        response = requests.post(url, data=data, timeout=120)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Quick search successful!")
            print(f"Response keys: {list(result.keys())}")
            
            if "report" in result:
                report = result["report"]
                print(f"📊 Report length: {len(str(report))} characters")
                print(f"📄 Report preview: {str(report)}...")
            else:
                print("⚠️  No report in response")
                
        else:
            print(f"❌ Quick search failed: {response.text[:200]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Quick search error: {e}")

def test_report_generation():
    """Test the report generation endpoint"""
    print("\n📊 Testing Report Generation...")
    
    query = "machine learning applications in healthcare"
    url = f"{API_BASE}/report/{query}"
    
    messages = [
        {"role": "user", "content": f"Generate a comprehensive report about: {query}"}
    ]
    
    data = {
        "messages": json.dumps(messages)
    }
    
    try:
        print(f"⏳ Sending request to: {url}")
        print(f"📝 Query: {query}")
        print("⏳ This may take 2-3 minutes for full report generation...")
        
        response = requests.post(url, data=data, timeout=300)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Report generation successful!")
            print(f"Response keys: {list(result.keys())}")
            
            if "report" in result:
                report = result["report"]
                print(f"📊 Report length: {len(str(report))} characters")
                print(f"📄 Report preview: {str(report)}...")
            else:
                print("⚠️  No report in response")
                
        else:
            print(f"❌ Report generation failed: {response.text[:200]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Report generation error: {e}")

def test_news_search():
    """Test news search by category"""
    print("\n📰 Testing News Search...")
    
    categories = ["technology", "business", "science"]
    
    for category in categories:
        try:
            url = f"{API_BASE}/news/{category}"
            print(f"⏳ Testing news category: {category}")
            
            response = requests.get(url, timeout=60)
            print(f"Status Code: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
            
            if response.status_code == 200:
                try:
                    news = response.json()
                    print(f"✅ News {category}: {len(news) if isinstance(news, list) else 'N/A'} items")
                    
                    if isinstance(news, list) and len(news) > 0:
                        print(f"📄 Sample headline: {news[0].get('title', 'No title')[:100]}...")
                    elif isinstance(news, dict) and 'news' in news:
                        print(f"📄 News items: {len(news['news'])}")
                        if news['news']:
                            print(f"📄 Sample headline: {news['news'][0].get('title', 'No title')[:100]}...")
                except json.JSONDecodeError:
                    print(f"⚠️  News {category}: Invalid JSON response")
                    print(f"Raw response: {response.text[:200]}...")
            else:
                print(f"❌ News {category} failed: {response.text[:200]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ News {category} error: {e}")

def test_streaming_search():
    """Test streaming search endpoint"""
    print("\n🌊 Testing Streaming Search...")
    
    query = "renewable energy innovations"
    url = f"{API_BASE}/stream_data"
    
    messages = [
        {"role": "user", "content": f"Search for information about: {query}"}
    ]
    
    data = {
        "messages": json.dumps(messages)
    }
    
    try:
        print(f"⏳ Testing streaming search: {query}")
        print("⏳ This may take time for streaming response...")
        
        response = requests.post(url, data=data, timeout=120, stream=True)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code == 200:
            print("✅ Streaming search accessible!")
            print("📡 Reading stream chunks...")
            
            chunk_count = 0
            total_content = ""
            
            for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
                if chunk:
                    chunk_count += 1
                    total_content += chunk
                    
                    if chunk_count <= 5:  # Show first 5 chunks
                        print(f"Chunk {chunk_count}: {chunk[:100]}...")
                    
                    if chunk_count >= 10:  # Limit to 10 chunks for testing
                        break
            
            print(f"📊 Total chunks received: {chunk_count}")
            print(f"📄 Total content length: {len(total_content)} characters")
            
        else:
            print(f"❌ Streaming search failed: {response.text[:200]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Streaming search error: {e}")

def test_academic_search():
    """Test academic search endpoint"""
    print("\n🎓 Testing Academic Search...")
    
    query = "quantum computing research"
    url = f"{API_BASE}/stream_completion_academic/{query}"
    
    messages = [
        {"role": "user", "content": f"Search for academic information about: {query}"}
    ]
    
    data = {
        "messages": json.dumps(messages)
    }
    
    try:
        print(f"⏳ Testing academic search: {query}")
        print("⏳ This may take time for academic response...")
        
        response = requests.post(url, data=data, timeout=120, stream=True)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code == 200:
            print("✅ Academic search accessible!")
            print("📡 Reading academic stream...")
            
            chunk_count = 0
            total_content = ""
            
            for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
                if chunk:
                    chunk_count += 1
                    total_content += chunk
                    
                    if chunk_count <= 3:  # Show first 3 chunks
                        print(f"Chunk {chunk_count}: {chunk[:100]}...")
                    
                    if chunk_count >= 5:  # Limit to 5 chunks for testing
                        break
            
            print(f"📊 Total chunks received: {chunk_count}")
            print(f"📄 Total content length: {len(total_content)} characters")
            
        else:
            print(f"❌ Academic search failed: {response.text[:200]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Academic search error: {e}")

def main():
    """Run focused search tests"""
    print("🔍 Spy Search API - Search Features Test")
    print("=" * 60)
    print(f"Testing: {BASE_URL}")
    print(f"API Base: {API_BASE}")
    print("=" * 60)
    
    # Basic connectivity test
    if not test_health_check():
        print("❌ API is not accessible. Check your deployment.")
        return
    
    # Test search features
    test_news_search()
    test_quick_search()
    
    # Optional: Test report generation (takes longer)
    print("\n⚠️  Report generation test is optional (takes 2-3 minutes)")
    user_input = input("Run report generation test? (y/n): ").lower().strip()
    if user_input == 'y':
        test_report_generation()
    
    # Optional: Test streaming
    print("\n⚠️  Streaming tests are optional (may take time)")
    user_input = input("Run streaming search test? (y/n): ").lower().strip()
    if user_input == 'y':
        test_streaming_search()
    
    user_input = input("Run academic search test? (y/n): ").lower().strip()
    if user_input == 'y':
        test_academic_search()
    
    print("\n✅ Search features test completed!")
    print("\n📋 Summary:")
    print("- Check the status codes above")
    print("- 200 = Success")
    print("- 404 = Endpoint not found")
    print("- 500 = Server error")
    print("- Timeout = May need to wait for cold start")

if __name__ == "__main__":
    main()
