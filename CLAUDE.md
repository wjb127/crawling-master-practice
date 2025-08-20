# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a comprehensive web crawling portfolio and practice project designed for 크몽 (Korean freelance platform) freelancers. It demonstrates various crawling techniques from basic to advanced, with a production-ready FastAPI + HTMX web service.

## Key Architecture Components

### Dual Server System
- **Main Crawling Service** (`web_crawler_service/simple_main.py`): Port 8000 - Production crawling service with HTMX real-time updates
- **Portfolio Demo** (`web_crawler_service/demo_portfolio.py`): Port 8001 - Interactive portfolio demonstrating 6 different crawling techniques

### Crawler Implementations
- `basic_crawler.py`: BeautifulSoup-based static HTML parsing
- `dynamic_crawler_simple.py`: Selenium for JavaScript-rendered content
- `advanced_api_crawler.py`: Direct API calls with async operations
- `login_crawler.py`: Session management and authentication handling

### Memory-Based Architecture
The system deliberately avoids database dependencies for simplicity:
- All job data stored in memory dictionaries (`jobs_store`)
- Results exported directly to Excel files
- Downloads stored in `downloads/` and `demo_results/` directories

## Common Development Commands

### Running Services

```bash
# Main crawling service
cd web_crawler_service
source venv/bin/activate  # macOS/Linux
./run.sh

# Or on Windows
venv\Scripts\activate
run.bat

# Portfolio demo (runs on port 8001)
python demo_portfolio.py

# Docker alternative
docker-compose up
```

### Testing

```bash
# Run all tests
cd web_crawler_service
source venv/bin/activate
pytest test_crawlers.py -v

# Run with coverage
pytest test_crawlers.py --cov=simple_main --cov-report=html

# Run specific test class
pytest test_crawlers.py::TestCrawlJob -v

# Run async tests
pytest test_crawlers.py -v -k "async"
```

### Development

```bash
# Install dependencies
pip install -r requirements.txt

# Install test dependencies
pip install pytest pytest-asyncio pytest-json-report

# Format check (if needed)
python -m black *.py --check
python -m isort *.py --check-only
```

## Key Implementation Patterns

### HTMX Real-time Updates
The main service uses HTMX for real-time UI updates without full page refreshes:
- Job status polling: `hx-get="/jobs/{job_id}/status" hx-trigger="every 2s"`
- Form submissions: `hx-post="/jobs/create" hx-target="#jobs-list"`

### Auto CSS Selector Detection
`auto_detect_selectors()` function automatically identifies common patterns:
- Searches for title elements: h1, h2, .title, .headline
- Content detection: article, .content, .body, main
- Metadata extraction: time, .date, .author, .price

### Excel Export with Styling
Uses openpyxl to create styled Excel files:
- Header styling with blue background
- Auto-adjusted column widths
- Korean text support (UTF-8)

### Async Crawling Pattern
```python
async with aiohttp.ClientSession() as session:
    tasks = [fetch_page(url) for url in urls]
    results = await asyncio.gather(*tasks)
```

## Critical Functions and Their Locations

- **Job Management**: `simple_main.py:35-50` - CrawlJob class definition
- **Auto Selector Detection**: `simple_main.py:auto_detect_selectors()` 
- **Data Extraction**: `simple_main.py:extract_data()`
- **Excel Export**: `simple_main.py:save_to_excel()`
- **Demo Runners**: `demo_portfolio.py:33-200` - DemoRunner class with 5 demo methods

## Korean Language Context

This project is specifically designed for Korean freelancers on 크몽 platform:
- Documentation includes Korean pricing strategies (5-50만원 range)
- Targets Korean websites (Naver, Coupang examples)
- UI text is bilingual (Korean/English)
- Excel outputs support Korean characters

## Testing Strategy

Tests are organized by functionality:
- `TestCrawlJob`: Job lifecycle management
- `TestAutoDetectSelectors`: Selector detection algorithms
- `TestDataExtraction`: HTML parsing and data extraction
- `TestExcelExport`: File generation and Korean text handling
- `TestAsyncCrawling`: Concurrent operations
- `TestErrorHandling`: Edge cases and error recovery

## Important Business Logic

### Pricing Tiers (from 크몽 guide)
- Basic (정적 사이트): 5-10만원
- Intermediate (동적/로그인): 10-30만원
- Advanced (API/대량): 30-50만원
- Premium (Anti-bot/실시간): 50만원+

### Crawling Feasibility Matrix
Detailed in `크롤링_가능_불가능_영역_가이드.md`:
- Feasible: Public HTML, APIs, login-based data
- Challenging: CAPTCHAs, rate limits, dynamic content
- Infeasible: Encrypted apps, hardware-dependent, illegal content