# Koran Teknologi

A Python-based tech blog aggregator that scrapes content from various engineering blogs and delivers updates via Telegram.

## Features

- Scrapes tech blogs from:
  - Netflix Tech Blog
  - Uber Engineering
  - Airbnb Engineering
  - ByteByteGo
- Sends updates via Telegram channel
- Customizable time range for fetching posts
- Supports dry-run mode for testing
- Async/await for efficient network operations

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

## Development

Available make commands:

```bash
lint                 Run code quality checks
clean                 Remove temporary files and build artifacts
format                Format code with black and isort
help                  Show this help message
install               Install project dependencies
run                   Run the blog checker (use DAYS=n for custom days, DRY_RUN=1 for dry run)
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

To add a new blog source:

1. Create a new file in `scraper/` directory
2. Implement the `BaseScraper` class
3. Add the scraper to the list in `main.py`

## License

MIT