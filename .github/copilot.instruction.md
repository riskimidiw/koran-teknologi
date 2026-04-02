---
name: koran-teknologi
description: "Guidance for Koran Teknologi: a tech blog aggregator that scrapes engineering blogs and delivers updates via Telegram. See CLAUDE.md for complete documentation."
applyTo: "**/*.py"
---

# Koran Teknologi — Copilot Instructions

For comprehensive project documentation, see [CLAUDE.md](../../CLAUDE.md).

## Quick Reference

**Koran Teknologi** is a tech blog aggregator that scrapes engineering blogs (Netflix, Uber, Airbnb, AWS, Lyft, ByteByteGo, Anthropic, GitHub, Google Research) and delivers updates to Telegram. It runs in CLI mode (scheduled) or HTTP server mode (webhook-based).

### Core Components

- **Scrapers** (`scrapers/`): Extend `BaseScraper`, implement `async def fetch_latest_posts() -> list[BlogPost]`
- **Channels** (`channels/`): `TelegramChannel` formats and sends posts; update `SOURCE_EMOJIS` when adding scrapers
- **Services** (`services/`): `KoranService` orchestrates scrapers and channels
- **Commands** (`cmd/`): `cli.py` for CLI mode, `http.py` for HTTP server

### Essential Commands

```bash
make setup           # One-time setup
make run             # Fetch posts (use DAYS=3 for 3 days)
make run DRY_RUN=1   # Test without sending to Telegram
make run-http        # Start HTTP server
make lint format     # Code quality checks
```

### Adding New Scrapers

1. Create `scrapers/blog_name.py` extending `BaseScraper`
2. Implement `async def fetch_latest_posts() -> list[BlogPost]`
3. Register in `services/koran_service.py`
4. Add emoji to `SOURCE_EMOJIS` in `channels/telegram.py`
5. Probe with curl first to decide: RSS feed, HTML parsing, or Selenium

See [CLAUDE.md](../../CLAUDE.md) for:
- Detailed architecture overview
- Complete development workflows
- Scraper implementation patterns
- Environment configuration
- Testing strategies
- Troubleshooting guide

### Quick Scraper Test

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

### Key Notes

- All scrapers must be `async`
- Raise exceptions on fetch failures (don't return empty lists silently)
- Respect `dry_run` flag in channels
- Use **scraper-ops** skill when creating/debugging scrapers
- Refer to CLAUDE.md for comprehensive guidance on all aspects of the project