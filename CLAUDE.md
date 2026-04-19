# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Koran Teknologi** is a tech blog aggregator that scrapes content from multiple engineering blogs (Netflix, Uber, Airbnb, AWS, Lyft, ByteByteGo) and delivers updates to a Telegram channel. The application runs in two modes: CLI (for scheduled jobs) and HTTP server (for webhook-based triggers).

## Architecture

The codebase follows a clean separation of concerns:

### Core Layers

**Scrapers (`scrapers/`)**: Each blog source has its own scraper class extending `BaseScraper`. Key responsibilities:
- Fetch HTML from the blog source
- Parse blog posts using BeautifulSoup
- Extract title, URL, and publication date
- Return `BlogPost` dataclass instances
- Implement retry logic and HTTP session management in the base class

All scrapers must implement `async def fetch_latest_posts() -> list[BlogPost]`.

**Channels (`channels/`)**: Adapters for delivery methods (currently just Telegram). The `TelegramChannel` class:
- Groups posts by date for readability
- Formats messages with markdown with emoji icons per source
- Supports dry-run mode for testing
- Handles async message sending
- SOURCE_EMOJIS mapping in `telegram.py` controls visual distinction; add entries when adding new scrapers

**Services (`services/`)**: Business orchestration layer (`KoranService`):
- Aggregates all scrapers
- Filters posts within a time window
- Coordinates with the Telegram channel
- Manages the full workflow

**Commands (`cmd/`)**: Entry points for different execution modes:
- `cli.py`: CLI mode - fetches posts and sends them
- `http.py`: HTTP server mode - FastAPI app with endpoints for manual triggering

### Data Flow

1. CLI/HTTP server triggers `KoranService.fetch_new_posts(since: datetime)`
2. Service iterates through all scraper instances and calls `fetch_latest_posts()`
3. Posts from all scrapers are aggregated and filtered by date
4. `KoranService.send_posts()` groups posts and sends them via Telegram
5. Dry-run mode short-circuits the Telegram send and prints instead

## Development Commands

All commands use `make` with Poetry for dependency management:

```bash
# Initial setup (one-time)
make setup        # Creates .env from template, installs dependencies

# Development
make install      # Install/update all dependencies
make lint         # Run quality checks (black, isort, flake8)
make format       # Auto-format code with black and isort
make clean        # Remove build artifacts and cache

# Running the application
make run          # Fetch from last 24 hours (DAYS=3 for 3 days)
make run DRY_RUN=1 DAYS=1  # Validate formatting quickly without sending to Telegram
make run-http     # Start HTTP server on localhost:8000
```

## Adding New Blog Scrapers

1. Create a new file in `scrapers/` (e.g., `scrapers/example_blog.py`)
2. Extend `BaseScraper` and implement `fetch_latest_posts()`
3. Register the scraper in `services/koran_service.py` by instantiating it in the service constructor
4. The scraper will automatically be included in post fetching

**Scraper Approaches** (in order of preference):
- **RSS feeds** (`/feed` endpoints) - Most reliable, use `xml.etree.ElementTree` with `parsedate_to_datetime` for dates
- **HTML parsing** - Use BeautifulSoup to find article containers; probe with curl first to find CSS selectors
- **Selenium** - Last resort for JS-heavy sites; use headless Chrome with `--headless=new`, `--no-sandbox`, `--disable-dev-shm-usage`

**Before implementing:** Probe the blog with curl to decide approach, don't assume HTML parsing will work

Key implementation details:
- Parse dates consistently and handle timezones (RFC 2822 from RSS via `parsedate_to_datetime`)
- Log errors and recoverable issues via `self.logger`
- Raise exceptions on fetch failures so KoranService can handle them (don't silently return empty lists)
- HTTP session with retries is provided by the base class

## Environment Configuration

Required environment variables (set in `.env`):
- `TELEGRAM_BOT_TOKEN`: Telegram bot API token
- `TELEGRAM_CHANNEL_ID`: Target Telegram channel ID

The `.env` file is created from `.env.template` during `make setup`. Never commit `.env` with real credentials.

## Testing

Test framework setup in `pyproject.toml`:
- Uses pytest with asyncio support
- Tests should be in `tests/` directory following `test_*.py` pattern
- Async tests work natively with `pytest-asyncio`

Run tests: `poetry run pytest` (currently no test suite checked in)

**Quick scraper validation** (for testing individual scrapers before full test suite):
```bash
python3 -c "
import asyncio
from scrapers.[module] import [Scraper]

async def test():
    scraper = [Scraper]()
    posts = await scraper.fetch_latest_posts()
    print(f'Posts: {len(posts)}')
    if posts:
        for post in posts[:3]:
            print(f'  - {post.title[:60]} ({post.date.strftime(\"%Y-%m-%d\")})')

asyncio.run(test())
"
```

## Key Dependencies

- **python-telegram-bot**: Async Telegram bot library
- **beautifulsoup4**: HTML parsing for scraping
- **aiohttp**: Async HTTP (currently requests is used in base scraper, may be migrated)
- **fastapi/uvicorn**: HTTP server for webhook mode
- **python-dotenv**: Environment variable loading
- **poetry**: Dependency and environment management

## Notes for Contributors

**⚠️ CODE QUALITY: ALWAYS RUN `make lint` AFTER MAKING CODE CHANGES**

After adding or modifying code, immediately run:
```bash
make lint      # Check for linting errors (Black, isort, flake8)
make format    # Auto-format code if lint fails
```

This ensures code consistency and catches issues early. The linter checks:
- **Black**: Code formatting and line length
- **isort**: Import statement organization
- **flake8**: PEP 8 compliance, complexity, and common errors

Commit only after linting passes.

---

- All scrapers must be async (use `async def fetch_latest_posts()`)
- Environment validation happens before Telegram operations to fail fast
- Dry-run mode exists for local testing - always respect the `dry_run` flag in channels
- Posts are grouped by date in Telegram messages to reduce spam
- Markdown formatting is used in Telegram messages - test rendered output

**When a scraper returns 0 posts:**
1. Run scraper test (see Quick scraper validation above) to confirm the issue
2. Use curl to probe the blog: `curl -s https://[blog]/ -H "User-Agent: Mozilla/5.0" | head -500`
3. Identify root cause: Did HTML structure change? Is RSS feed still available? Does page require JavaScript?
4. Fix the scraper (update selectors, switch to RSS, or implement Selenium)
5. Re-test and verify integration with other scrapers
6. Common fixes: CSS selector changes (HTML parsing), RSS feed moved/unavailable, page needs Selenium for JS rendering
