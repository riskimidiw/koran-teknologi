---
name: scraper-ops
description: Create new blog scrapers or debug/fix broken ones. Use this whenever the user mentions adding a new blog source, a scraper is returning 0 posts, tests are failing for a scraper, or scrapers need integration fixes. The skill handles intelligent detection (curl first, then decide between RSS, HTML parsing, or Selenium), implements the appropriate scraper, and validates it with automated testing.
compatibility: Requires python3, curl, git repository with scrapers/ directory
---

# Scraper Operations Skill

Create, debug, and fix blog scrapers for the Koran Teknologi project. This skill provides a complete workflow for both new scraper creation and troubleshooting broken scrapers.

## Workflow Overview

```
User Request
    ↓
Determine Mode (Create vs Debug)
    ↓
[CREATE MODE]                    [DEBUG MODE]
Probe Blog with curl             Run existing scraper
↓                                ↓
Decide scraper type              Analyze errors/logs
↓                                ↓
Write scraper code               Identify root cause
↓                                ↓
Test implementation              Fix the issue
↓                                ↓
Verify integration               Test fix
```

## Mode 1: Creating a New Scraper

### Step 1: Probe the Blog

Before writing any code, understand the blog structure using curl:

```bash
curl -s -I "https://example.com/blog" -H "User-Agent: Mozilla/5.0" | head -20
curl -s "https://example.com/blog" -H "User-Agent: Mozilla/5.0" 2>&1 | head -500
curl -s "https://example.com/feed" -H "User-Agent: Mozilla/5.0" 2>&1 | head -50
curl -s "https://example.com/rss.xml" -H "User-Agent: Mozilla/5.0" 2>&1 | head -50
```

**What to look for:**
- Does `curl` return HTML directly, or does it say "Not Acceptable" or "JavaScript required"?
- Is there an RSS/feed endpoint? Look for `<rss>`, `<?xml`, or `feed` in the response.
- Does the HTML contain article data, or only skeleton/scripts?

### Step 2: Decide Scraper Type

Based on the curl results, choose the best approach:

**Option A: RSS Feed** (Preferred - fastest, most reliable)
- ✅ Use if: curl returns valid XML with `<item>` tags and `<title>`, `<link>`, `<pubDate>`
- ✅ Example: Netflix, Airbnb, Lyft all use RSS feeds at `/feed` endpoints
- ✅ Implementation: Parse XML with `xml.etree.ElementTree`, extract title/URL/date from standard RSS fields

**Option B: HTML Parsing** (Moderate - needs CSS selectors)
- ✅ Use if: curl returns HTML with clear article structure (divs with class names, h2 titles, date elements)
- ✅ Example: Lyft was originally HTML-parsed but switched to RSS
- ✅ Implementation: Use BeautifulSoup to find article containers, extract title/URL/date via CSS selectors
- ❌ Avoid if: page structure is inconsistent or uses obfuscated class names

**Option C: Selenium (JavaScript Rendering)** (Slowest - last resort)
- ✅ Use if: curl returns mostly `<script>` tags and no article content; page requires JS to render
- ✅ Example: Uber, ByteByteGo use Selenium with headless Chrome
- ✅ Implementation: Use Selenium with headless Chrome, wait for elements to load, then parse rendered HTML
- ✅ Accept trade-off: ~5-10 seconds per scraper run vs instant RSS parsing
- ❌ Use only if RSS/HTML approaches won't work

### Step 3: Implement the Scraper

Follow the **BaseScraper** pattern. All scrapers inherit from `BaseScraper` and implement `async def fetch_latest_posts() -> List[BlogPost]`:

**Template Structure:**

```python
"""[Blog Name] blog scraper implementation."""

from typing import List
import xml.etree.ElementTree as ET  # For RSS
from bs4 import BeautifulSoup       # For HTML
from selenium import webdriver      # For JS rendering

from scrapers.base_scraper import BaseScraper, BlogPost


class [BlogName]Scraper(BaseScraper):
    """Scraper for the [Blog Name] blog."""

    def __init__(self) -> None:
        """Initialize the [Blog Name] blog scraper."""
        super().__init__(
            base_url="https://[blog-url]/",
            source_name="[Blog Name]",
        )

    async def fetch_latest_posts(self) -> List[BlogPost]:
        """Fetch latest blog posts from [Blog Name].
        
        Uses [RSS/HTML parsing/Selenium] approach.
        """
        posts = []

        try:
            # Step 1: Fetch content
            # Step 2: Parse/render
            # Step 3: Extract posts
            # Step 4: Return BlogPost objects
            
            self.logger.info(f"Successfully fetched {len(posts)} posts")
            
        except Exception as e:
            self.logger.error(f"Error fetching posts: {str(e)}")
            raise

        return posts
```

**Key Implementation Details:**

- **HTTP Session**: Inherited from `BaseScraper` — use `self.session.get()` for all requests (includes retry logic)
- **Logging**: Use `self.logger.info()`, `self.logger.debug()`, `self.logger.error()` (not print!)
- **Error Handling**: Log errors and raise exceptions so the service knows there was a problem
- **Return Type**: Always return `List[BlogPost]` — return empty list if no posts, not None
- **Timezone-Aware Datetimes**: ⚠️ CRITICAL — When parsing dates with `datetime.strptime()`, always make them timezone-aware by adding `.replace(tzinfo=timezone.utc)`. The service compares posts by date and fails with "can't compare offset-naive and offset-aware datetimes" if dates lack timezone info.

**Example - Timezone Handling:**

```python
from datetime import datetime, timezone

# ❌ WRONG - will cause comparison error
pub_date = datetime.strptime("March 11, 2026", "%B %d, %Y")

# ✅ CORRECT - timezone-aware (UTC)
pub_date = datetime.strptime("March 11, 2026", "%B %d, %Y").replace(tzinfo=timezone.utc)

# For RSS feeds with RFC 2822 dates, use parsedate_to_datetime (already timezone-aware)
from email.utils import parsedate_to_datetime
pub_date = parsedate_to_datetime(rss_date_string)  # No .replace() needed
```

### Step 4: Register in KoranService

Edit `services/koran_service.py` and add the scraper to the `__init__` method:

```python
# In KoranService.__init__():
self.scrapers = [
    # ... existing scrapers ...
    [BlogName]Scraper(),  # Add here
]
```

### Step 5: Test the New Scraper

```bash
python3 -c "
import asyncio
from scrapers.[module_name] import [BlogName]Scraper

async def test():
    scraper = [BlogName]Scraper()
    posts = await scraper.fetch_latest_posts()
    print(f'Posts fetched: {len(posts)}')
    if posts:
        for post in posts[:3]:
            print(f'  - {post.title[:60]}')
            print(f'    {post.date.strftime(\"%Y-%m-%d\")} | {post.url}')

asyncio.run(test())
"
```

**Success criteria:**
- ✅ No exceptions raised
- ✅ Posts returned > 0 (unless site genuinely has no recent posts)
- ✅ Each post has title, URL, date, source
- ✅ Dates are timezone-aware and parse correctly

---

## Mode 2: Debugging a Broken Scraper

### Step 1: Identify the Problem

**Run the scraper and capture the error:**

```bash
python3 -c "
import asyncio
from scrapers.[module_name] import [BlogName]Scraper

async def test():
    scraper = [BlogName]Scraper()
    try:
        posts = await scraper.fetch_latest_posts()
        print(f'Posts: {len(posts)}')
    except Exception as e:
        print(f'ERROR: {e}')
        import traceback
        traceback.print_exc()

asyncio.run(test())
" 2>&1
```

**Common issues & root causes:**

| Symptom | Likely Cause | Solution |
|---------|-------------|----------|
| Returns 0 posts | CSS selectors changed, page structure updated | Re-probe with curl, find new selectors |
| "406 Not Acceptable" | Server blocks user-agent or request headers | Add proper headers (User-Agent, Accept, Referer) |
| "403 Forbidden" | Bot detection, Cloudflare, rate limiting | Switch to RSS feed if available; add delays |
| "Timeout" | Page takes too long to load | Increase timeout; use Selenium if HTML parsing fails |
| Parsing error (KeyError, AttributeError) | Missing expected HTML elements | Log the actual HTML structure, update selectors |
| Date parsing fails | Date format changed or unexpected | Debug `pub_date_elem.text` and adjust strptime format |
| "can't compare offset-naive and offset-aware datetimes" | Dates are offset-naive from strptime() | Add `.replace(tzinfo=timezone.utc)` after strptime; use parsedate_to_datetime for RSS |

### Step 2: Probe the Live Blog

Use curl to understand what changed:

```bash
curl -s "https://[blog-url]" -H "User-Agent: Mozilla/5.0" 2>&1 | head -500
curl -s -I "https://[blog-url]" -H "User-Agent: Mozilla/5.0" | head -20
```

Check:
- Does the page still have article data, or is it JS-only now?
- Are there new endpoint paths (e.g., `/api/posts` instead of RSS)?
- Has the CSS structure changed (class names, div hierarchy)?

### Step 3: Fix the Issue

**For HTML parsing scrapers:**
- Use browser DevTools (or `curl | grep`) to find the new article container selectors
- Update the BeautifulSoup `find_all()` and `select()` calls
- Re-test with fresh curl output

**For RSS feed scrapers:**
- Verify the feed endpoint still exists: `curl -s https://[blog-url]/feed | head -20`
- If feed is gone, fall back to HTML parsing (see above)
- If feed structure changed, update the XPath/element names

**For Selenium scrapers:**
- Add `print(driver.page_source)` or screenshot captures to debug what's actually rendering
- Wait for new element selectors: `EC.presence_of_element_located((By.CSS_SELECTOR, "..."))`
- Increase wait times if page loads slowly

### Step 4: Test the Fix

```bash
python3 -c "
import asyncio
from scrapers.[module_name] import [BlogName]Scraper

async def test():
    scraper = [BlogName]Scraper()
    posts = await scraper.fetch_latest_posts()
    print(f'✓ Posts: {len(posts)}')
    if posts:
        for post in posts[:3]:
            print(f'  - {post.title[:70]}')

asyncio.run(test())
"
```

---

## Integration Testing

Once a scraper is fixed or created, verify it integrates with the full service:

```bash
python3 -c "
import asyncio
from datetime import datetime, timedelta, timezone
from scrapers.uber import UberScraper
from scrapers.netflix import NetflixScraper
from scrapers.lyft import LyftScraper

async def test():
    scrapers = [
        UberScraper(),
        NetflixScraper(),
        LyftScraper(),
    ]
    
    total = 0
    for scraper in scrapers:
        try:
            posts = await scraper.fetch_latest_posts()
            status = '✓' if posts else '○'
            print(f'{status} {scraper.source_name:25} | {len(posts):3} posts')
            total += len(posts)
        except Exception as e:
            print(f'✗ {scraper.source_name:25} | Error: {str(e)[:40]}')
    
    print(f'Total: {total} posts')

asyncio.run(test())
"
```

**Success criteria:**
- ✅ All scrapers return > 0 posts (or gracefully handle unavailability)
- ✅ No unhandled exceptions in logs
- ✅ Service can be run with: `make run DRY_RUN=1` (test mode)

---

## Reference: BlogPost Dataclass

All scrapers must return this type:

```python
@dataclass
class BlogPost:
    title: str        # Article title
    url: str          # Full HTTP(S) URL to article
    date: datetime    # Publication date (timezone-aware recommended)
    source: str       # Blog source name (e.g., "Netflix Tech Blog")
```

---

## Checklist for New Scrapers

- [ ] Probed blog with curl to determine structure
- [ ] Chose RSS/HTML/Selenium based on findings
- [ ] Implemented scraper inheriting from BaseScraper
- [ ] Added to KoranService.__init__()
- [ ] Tested with test script (> 0 posts returned)
- [ ] Verified dates parse correctly
- [ ] Checked logs for errors/warnings
- [ ] Ran full integration test
- [ ] Committed changes to git

## Checklist for Debugging Scrapers

- [ ] Captured error message and stack trace
- [ ] Probed blog with curl to see what changed
- [ ] Identified root cause (selector change, new endpoint, etc.)
- [ ] Made fix (updated selectors, headers, endpoints)
- [ ] Tested fixed scraper (> 0 posts returned)
- [ ] Ran integration test to ensure no regressions
- [ ] Committed fix to git
