#!/usr/bin/env python3
"""
Test script for Spy Search API deployed on Render
Base URL: https://spy-search.onrender.com
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BASE_URL = "https://spy-search.onrender.com"
API_BASE = f"{BASE_URL}/api"

def test_health_check():
    """Test if the API is accessible"""
    print("🔍 Testing API Health...")
    try:
        # Try the root endpoint first
        response = requests.get(BASE_URL, timeout=30)
        print(f"✅ Root endpoint: {response.status_code}")
        
        # Try API docs
        docs_response = requests.get(f"{BASE_URL}/docs", timeout=30)
        print(f"✅ API Docs: {docs_response.status_code}")
        
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_quick_response():
    """Test the quick response endpoint"""
    print("\n🚀 Testing Quick Response...")
    
    url = f"{API_BASE}/quick/test search"
    
    # Sample messages for testing
    messages = [
        {"role": "user", "content": "Hello, can you help me with a search?"}
    ]
    
    data = {
        "messages": json.dumps(messages)
    }
    
    try:
        response = requests.post(url, data=data, timeout=60)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Quick response successful!")
            print(f"Response keys: {list(result.keys())}")
            if "report" in result:
                print(f"Report preview: {str(result['report'])[:200]}...")
        else:
            print(f"❌ Quick response failed: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Quick response error: {e}")

def test_report_generation():
    """Test the report generation endpoint"""
    print("\n📊 Testing Report Generation...")
    
    url = f"{API_BASE}/report/artificial intelligence trends"
    
    messages = [
        {"role": "user", "content": "Generate a report about AI trends"}
    ]
    
    data = {
        "messages": json.dumps(messages)
    }
    
    try:
        print("⏳ This may take a while (up to 2-3 minutes)...")
        response = requests.post(url, data=data, timeout=180)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Report generation successful!")
            print(f"Response keys: {list(result.keys())}")
            if "report" in result:
                print(f"Report length: {len(str(result['report']))} characters")
        else:
            print(f"❌ Report generation failed: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Report generation error: {e}")

def test_messages_endpoints():
    """Test message-related endpoints"""
    print("\n💬 Testing Messages Endpoints...")
    
    # Test get titles
    try:
        response = requests.get(f"{API_BASE}/get_titles", timeout=30)
        print(f"✅ Get titles: {response.status_code}")
        print(f"Response content: '{response.text[:200]}...'")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        if response.status_code == 200:
            if response.text.strip():
                titles = response.json()
                print(f"Titles: {titles}")
            else:
                print("⚠️  Empty response body")
    except requests.exceptions.RequestException as e:
        print(f"❌ Get titles error: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        print(f"Raw response: '{response.text[:200]}...'")

def test_files_endpoints():
    """Test file-related endpoints"""
    print("\n📁 Testing Files Endpoints...")
    
    # Test folder list
    try:
        response = requests.get(f"{API_BASE}/folder_list", timeout=30)
        print(f"✅ Folder list: {response.status_code}")
        print(f"Response content: '{response.text[:200]}...'")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        if response.status_code == 200:
            if response.text.strip():
                folders = response.json()
                print(f"Folders: {folders}")
            else:
                print("⚠️  Empty response body")
    except requests.exceptions.RequestException as e:
        print(f"❌ Folder list error: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        print(f"Raw response: '{response.text[:200]}...'")

def test_agents_endpoints():
    """Test agent-related endpoints"""
    print("\n🤖 Testing Agents Endpoints...")
    
    # Test get config
    try:
        response = requests.get(f"{API_BASE}/get_config", timeout=30)
        print(f"✅ Get config: {response.status_code}")
        print(f"Response content: '{response.text[:200]}...'")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        if response.status_code == 200:
            if response.text.strip():
                config = response.json()
                print(f"Config: {config}")
            else:
                print("⚠️  Empty response body")
    except requests.exceptions.RequestException as e:
        print(f"❌ Get config error: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        print(f"Raw response: '{response.text[:200]}...'")

def test_news_endpoint():
    """Test news endpoint"""
    print("\n📰 Testing News Endpoint...")
    
    categories = ["technology", "business", "science"]
    
    for category in categories:
        try:
            response = requests.get(f"{API_BASE}/news/{category}", timeout=30)
            print(f"✅ News {category}: {response.status_code}")
            if response.status_code == 200:
                news = response.json()
                print(f"News items: {len(news) if isinstance(news, list) else 'N/A'}")
        except requests.exceptions.RequestException as e:
            print(f"❌ News {category} error: {e}")

def test_streaming_endpoint():
    """Test streaming endpoint (basic test)"""
    print("\n🌊 Testing Streaming Endpoint...")
    
    url = f"{API_BASE}/stream_data"
    messages = [{"role": "user", "content": "Tell me about Python programming"}]
    
    data = {
        "messages": json.dumps(messages)
    }
    
    try:
        print("⏳ Testing streaming (may take time)...")
        response = requests.post(url, data=data, timeout=60, stream=True)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Streaming endpoint accessible!")
            # Read first few chunks
            chunk_count = 0
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    chunk_count += 1
                    if chunk_count <= 3:  # Show first 3 chunks
                        print(f"Chunk {chunk_count}: {chunk.decode('utf-8', errors='ignore')[:100]}...")
                    if chunk_count >= 5:  # Limit to 5 chunks for testing
                        break
        else:
            print(f"❌ Streaming failed: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Streaming error: {e}")

def main():
    """Run all tests"""
    print("🧪 Spy Search API Test Suite")
    print("=" * 50)
    print(f"Testing: {BASE_URL}")
    print(f"API Base: {API_BASE}")
    print("=" * 50)
    
    # Basic connectivity test
    if not test_health_check():
        print("❌ API is not accessible. Check your deployment.")
        return
    
    # Test individual endpoints
    test_messages_endpoints()
    test_files_endpoints()
    test_agents_endpoints()
    test_news_endpoint()
    
    # Test core functionality (these may take longer)
    test_quick_response()
    
    # Optional: Test report generation (takes longer)
    print("\n⚠️  Report generation test is optional (takes 2-3 minutes)")
    user_input = input("Run report generation test? (y/n): ").lower().strip()
    if user_input == 'y':
        test_report_generation()
    
    # Optional: Test streaming
    print("\n⚠️  Streaming test is optional (may take time)")
    user_input = input("Run streaming test? (y/n): ").lower().strip()
    if user_input == 'y':
        test_streaming_endpoint()
    
    print("\n✅ Test suite completed!")
    print("\n📋 Summary:")
    print("- Check the status codes above")
    print("- 200 = Success")
    print("- 404 = Endpoint not found")
    print("- 500 = Server error")
    print("- Timeout = May need to wait for cold start")

if __name__ == "__main__":
    main()
