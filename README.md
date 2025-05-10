# Koran Teknologi

A Python-based tech blog aggregator that scrapes content from various engineering blogs and delivers updates via Telegram.

## Features

- Scrapes tech blogs from:
  - Netflix Tech Blog
  - Uber Engineering
  - Airbnb Engineering
  - ByteByteGo
  - AWS Architecture
- Sends updates via Telegram channel
- Customizable time range for fetching posts
- Supports dry-run mode for testing

## Setup

### Quick Setup

```bash
make setup
```

This will:
1. Check if Poetry is installed
2. Install project dependencies
3. Create a `.env` file from template if it doesn't exist
4. Create necessary directories

## Usage

The application can run in two modes: CLI and HTTP server.

### CLI Mode

```bash
# Show all available commands
make help

# Run blog checker (last 24 hours)
make run

# Check posts from last 3 days
make run DAYS=3

# Test mode - just print posts without sending
make run DRY_RUN=1

# Check last 7 days in test mode
make run DAYS=7 DRY_RUN=1
```

### HTTP Server Mode

```bash
# Start HTTP server (default: http://0.0.0.0:8000)
make run-http

# Start server on custom host and port
make run-http HTTP_HOST=127.0.0.1 HTTP_PORT=3000
```

Available endpoints:
- POST `/send-posts` - Send new tech blog posts to Telegram
- GET `/health` - Health check endpoint

## Development

Available make commands:

```bash
help                  Show this help message
install               Install project dependencies
lint                  Run code quality checks
format                Format code with black and isort
setup                 Initial project setup
run                   Run the blog checker (use DAYS=n for custom days, DRY_RUN=1 for dry run)
run-http              Run the HTTP server (use HTTP_HOST and HTTP_PORT for custom host/port)
clean                 Remove temporary files and build artifacts
```

The project uses:
- Poetry for dependency management
- Black for code formatting
- Flake8 for linting
- isort for import sorting

### CI/CD

The project includes GitHub Actions workflows for:
- Running code quality checks on pull requests
- Configurable scheduled blog checks (at midnight UTC)

## Adding New Sources

### Manual Method

1. Create a new file in `scraper/` directory
2. Implement the `BaseScraper` class
3. Add the scraper to the list in `main.py`

### Using AI Commands

You can use GitHub Copilot to help implement a new web source scraper:

1. Open the project in VS Code with GitHub Copilot enabled
2. Create a new Python file in the `scraper/` directory
3. Provide the following information in your comment:
   ```python
   """
   Implement a scraper for [Blog Name] that extends BaseScraper
   
   Source URL: [Full URL of the blog, e.g. https://blog.example.com]
   
   Sample HTML structure for a blog post:
   <div class="post">
     <h2 class="title"><a href="/post-url">Post Title</a></h2>
     <div class="meta">
       <time datetime="2025-05-10T10:00:00Z">May 10, 2025</time>
     </div>
   </div>
   """
   ```
4. GitHub Copilot will suggest the implementation, including:
   - Required imports
   - Class structure extending BaseScraper
   - HTML parsing logic based on the provided structure
   - Date parsing and timezone handling
   - Error handling and logging

For example, here's a full comment for implementing an AWS Architecture blog scraper:
```python
"""
Implement a scraper for AWS Architecture blog that extends BaseScraper

Source URL: https://aws.amazon.com/blogs/architecture/

Sample HTML structure:
<div class="lb-row lb-snap">
  <div class="lb-col lb-mid-6 lb-tiny-24">
    <a href="[post-url]"><img src="[image-url]"></a>
  </div>
  <div class="lb-col lb-mid-18 lb-tiny-24">
    <h2 class="lb-bold blog-post-title">
      <a href="[post-url]">
        <span property="name headline">Post Title</span>
      </a>
    </h2>
    <footer class="blog-post-meta">
      <span>by <span property="author"><span property="name">Author Name</span></span></span>
      <span>on <time property="datePublished" datetime="2025-04-21T10:08:07-07:00">21 APR 2025</time></span>
    </footer>
  </div>
</div>
"""
```

The scraping implementation will be tailored to your specific blog source, considering:
- HTML element structure and class names
- Date formats and timezones
- Pagination if present
- Error handling for missing elements

## License

MIT