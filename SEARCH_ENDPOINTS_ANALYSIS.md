# Spy Search - Search Endpoints Analysis

## Overview
Spy Search provides multiple search endpoints and implementations for different use cases. This analysis covers all available search functionality.

## API Endpoints

### 1. **Streaming Search Endpoints** (`/src/api/routes/streaming.py`)

#### `/stream_completion/{query}` (POST)
- **Purpose**: General streaming search with web search integration
- **Method**: POST
- **Parameters**: 
  - `query` (path): Search query
  - `messages` (form): JSON string of conversation messages
  - `files` (form, optional): File uploads
  - `api` (form, optional): API configuration
- **Features**:
  - Triggers web search when query contains "search:" prefix
  - Uses Google Custom Search Engine
  - Streams response in real-time
  - Supports file uploads
  - Handles conversation context

#### `/stream_completion_academic/{query}` (POST)
- **Purpose**: Academic-focused search using arXiv
- **Method**: POST
- **Parameters**: Same as above
- **Features**:
  - Searches specifically on arXiv.org
  - Optimized for academic papers and research
  - Uses Google CSE with "site:arxiv.org" filter

### 2. **General Search Endpoints** (`/src/api/routes/misc.py`)

#### `/quick/{query}` (POST)
- **Purpose**: Quick search and response generation
- **Method**: POST
- **Parameters**:
  - `query` (path): Search query
  - `messages` (form): JSON string of conversation messages
  - `files` (form, optional): File uploads
  - `api` (form, optional): API configuration
- **Features**:
  - Fast search and response
  - Uses Google CSE for web search
  - Returns structured JSON response
  - Includes file processing details

#### `/report/{query}` (POST)
- **Purpose**: Comprehensive report generation
- **Method**: POST
- **Parameters**: Same as quick search
- **Features**:
  - Full agent-based report generation
  - Uses multiple agents (reporter, etc.)
  - Takes longer but produces detailed reports
  - Supports complex multi-step analysis

#### `/news/{category}` (GET)
- **Purpose**: Category-based news search
- **Method**: GET
- **Parameters**:
  - `category` (path): News category (technology, finance, entertainment, sports, world, health)
- **Features**:
  - Uses Google CSE for news search
  - Returns structured news data
  - Optimized for current events

### 3. **Configuration Endpoints** (`/src/api/routes/agents.py`)

#### `/get_config` (GET)
- **Purpose**: Get current agent and model configuration
- **Returns**: Current agents, provider, and model settings

#### `/agents_selection` (POST)
- **Purpose**: Update agent configuration
- **Parameters**: Agents list, provider, model
- **Features**: Updates configuration for search behavior

## Search Implementations

### 1. **Google Custom Search Engine** (`/src/browser/googlesearch.py`)
- **Class**: `GoogleSearch`
- **Features**:
  - Uses Google CSE API
  - Ultra-fast timeouts (1.5s total)
  - Content extraction from URLs
  - Caching for performance
  - Deep search with content analysis
- **Methods**:
  - `search_result()`: Main search with content extraction
  - `today_new()`: News search by category
  - `_search_google_cse()`: Direct CSE API calls

### 2. **DuckDuckGo Search** (`/src/browser/duckduckgo.py`)
- **Class**: `DuckSearch`
- **Features**:
  - Uses DuckDuckGo API
  - Similar performance optimizations
  - Alternative to Google CSE
  - News and general search support

### 3. **Go Websearch Module** (`/websearch /main.go`)
- **Purpose**: Go-based web scraping service
- **Features**:
  - HTTP server on port 8080
  - Google CSE integration
  - Web scraping with content extraction
  - Concurrent processing
- **Endpoints**:
  - `/search?q={query}`: Search and scrape URLs

### 4. **Crawl4AI Integration** (`/src/browser/crawl_ai.py`)
- **Features**:
  - Advanced web crawling
  - Content extraction and processing
  - Database integration
  - AI-powered content analysis

## Search Flow Architecture

### 1. **Quick Search Flow**
```
User Query → /quick/{query} → GoogleSearch.search_result() → AI Model → Response
```

### 2. **Streaming Search Flow**
```
User Query → /stream_completion/{query} → 
  ├─ Check for "search:" prefix
  ├─ If search needed: GoogleSearch.search_result()
  ├─ Generate prompt with search results
  └─ Stream AI response
```

### 3. **Report Generation Flow**
```
User Query → /report/{query} → 
  ├─ Create Planner and Agents
  ├─ Multi-agent analysis
  ├─ Web search integration
  └─ Comprehensive report
```

### 4. **Academic Search Flow**
```
User Query → /stream_completion_academic/{query} → 
  ├─ Add "site:arxiv.org" filter
  ├─ GoogleSearch.search_result()
  ├─ Academic-focused prompt
  └─ Stream academic response
```

## Performance Optimizations

### 1. **Timeout Management**
- Ultra-aggressive timeouts (400ms per request)
- 1.5s total search time limit
- Graceful degradation on timeout

### 2. **Caching**
- Content cache for repeated URLs
- Failed URL tracking
- LRU cache for URL validation

### 3. **Concurrent Processing**
- Async/await for I/O operations
- Semaphore-based rate limiting
- Parallel content extraction

### 4. **Error Handling**
- Graceful fallbacks
- Retry mechanisms
- Comprehensive logging

## Environment Variables Required

### Google CSE
- `GOOGLE_CSE_API_KEY`: Google Custom Search API key
- `GOOGLE_CSE_ID`: Custom Search Engine ID

### AI Models
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key
- `DEEPSEEK_API`: DeepSeek API key
- `GEMINI_API`: Google Gemini API key
- `XAI_API_KEY`: xAI API key

## Usage Examples

### 1. **Quick Search**
```bash
curl -X POST "http://localhost:8000/quick/artificial intelligence trends" \
  -F "messages=[{\"role\":\"user\",\"content\":\"Search for AI trends\"}]"
```

### 2. **Streaming Search**
```bash
curl -X POST "http://localhost:8000/stream_completion/search:quantum computing" \
  -F "messages=[{\"role\":\"user\",\"content\":\"Search for quantum computing\"}]"
```

### 3. **News Search**
```bash
curl "http://localhost:8000/news/technology"
```

### 4. **Academic Search**
```bash
curl -X POST "http://localhost:8000/stream_completion_academic/machine learning" \
  -F "messages=[{\"role\":\"user\",\"content\":\"Academic search for ML\"}]"
```

## Frontend Integration

The frontend (`/frontend/src/config/api.ts`) defines these endpoints:
- `NEWS`: `/news`
- `REPORT`: `/report`
- `STREAM_COMPLETION`: `/stream_completion`
- `STREAM_COMPLETION_ACADEMIC`: `/stream_completion_academic`
- `STREAM_DATA`: `/stream_data`

## Testing

The test suite (`/test_search.py`) covers:
- Health checks
- Quick search functionality
- Report generation
- News search by category
- Streaming search
- Academic search

## Security Considerations

- API keys stored in environment variables
- No hardcoded credentials
- Proper error handling
- Rate limiting and timeouts
- Input validation and sanitization
