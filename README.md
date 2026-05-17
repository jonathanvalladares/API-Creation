# SSBCI News API

A REST API that continuously collects and serves news, announcements, and regulatory filings related to the U.S. Treasury **State Small Business Credit Initiative (SSBCI)**.

## Features

- Aggregates SSBCI news from multiple sources automatically every 6 hours
- Stores articles in a local SQLite database with deduplication
- Full-text search, date range filtering, source/category filtering, and pagination
- Trigger an on-demand collection via a single POST request

## Data Sources

| Source | Category | Type |
|--------|----------|------|
| Google News – SSBCI | media | RSS |
| Google News – Treasury SSBCI | media | RSS |
| Federal Register – SSBCI | federal | RSS |
| Treasury Press Releases | federal | RSS |
| SBA News | federal | RSS |
| GovInfo Federal Register | federal | RSS |
| Treasury SSBCI Official Page | federal | Web scrape |

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API (auto-collects on startup, refreshes every 6 hours)
uvicorn app.main:app --reload
```

Interactive docs: http://localhost:8000/docs

## API Endpoints

### `GET /`
Service info and endpoint index.

### `GET /health`
Health check — returns `{"status": "ok"}`.

### `GET /news`
List news articles with optional filters.

| Query param | Type | Description |
|-------------|------|-------------|
| `q` | string | Full-text search in title, summary, content |
| `source` | string | Filter by source name (partial match) |
| `category` | string | `federal`, `media`, or `state` |
| `from_date` | ISO 8601 datetime | Published on or after |
| `to_date` | ISO 8601 datetime | Published on or before |
| `page` | int (≥1) | Page number (default 1) |
| `page_size` | int (1–100) | Results per page (default 20) |

**Example**
```
GET /news?q=SSBCI+capital&category=federal&from_date=2024-01-01T00:00:00&page=1&page_size=10
```

**Response**
```json
{
  "total": 42,
  "page": 1,
  "page_size": 10,
  "articles": [
    {
      "id": 1,
      "title": "Treasury Allocates $10B under SSBCI",
      "url": "https://home.treasury.gov/...",
      "source": "Treasury Press Releases",
      "source_category": "federal",
      "summary": "...",
      "published_at": "2024-03-15T14:00:00",
      "collected_at": "2024-03-15T18:02:11",
      "tags": "ssbci,state small business credit initiative"
    }
  ]
}
```

### `GET /news/latest?limit=10`
Returns the N most recently collected articles (default 10, max 50).

### `GET /news/{id}`
Full article detail including `content` field.

### `GET /news/sources`
Lists all configured data sources with name, category, description, and URL.

### `GET /news/stats`
Summary counts by source and category, plus last collection timestamp.

### `POST /news/collect`
Triggers an immediate collection run. Returns counts of new articles saved and any per-source errors.

```json
{
  "message": "Collection complete",
  "new_articles": 12,
  "sources_queried": 7,
  "errors": []
}
```

## Project Structure

```
app/
├── main.py              FastAPI app + APScheduler background refresh
├── database.py          SQLAlchemy engine & session factory
├── models.py            NewsArticle ORM model
├── schemas.py           Pydantic request/response schemas
├── collectors/
│   ├── sources.py       Canonical list of RSS feeds and scrape targets
│   ├── rss.py           RSS/Atom feed parser (stdlib XML, no sgmllib dep)
│   ├── treasury.py      Treasury.gov HTML scraper
│   └── aggregator.py   Orchestrates collectors + deduplication
└── routers/
    └── news.py          All /news/* route handlers
tests/
└── test_api.py          20 pytest tests covering all endpoints
```

## Running Tests

```bash
pip install pytest httpx
python -m pytest tests/ -v
```
