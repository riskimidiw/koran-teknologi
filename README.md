# Koran Teknologi

A Python-based tech blog aggregator that scrapes content from various engineering blogs and delivers updates via Telegram.

## Features

- Scrapes tech blogs from:
  - Netflix Tech Blog
  - Uber Engineering
  - Airbnb Engineering
  - ByteByteGo

- Sends updates via Telegram channel
- Daily scheduled checks for new content
- Asynchronous processing

## Setup

1. Install dependencies:
```bash
poetry install
```

2. Configure environment variables:
   - Copy `.env.template` to `.env`
   - Add your Telegram bot token and channel ID

3. Run the application:
```bash
poetry run python main.py
```

## Development

- Uses Poetry for dependency management
- Black for code formatting
- Flake8 for linting
- isort for import sorting

## Adding New Sources

To add a new blog source:

1. Create a new file in `sources/` directory
2. Implement the `BaseScraper` class
3. Add the scraper to the list in `main.py`

## License

MIT