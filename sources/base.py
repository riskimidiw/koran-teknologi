"""Base classes and types for blog scrapers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from logging import Logger

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from utils.logger import setup_logger


@dataclass
class BlogPost:
    """Represents a blog post from any source."""

    title: str
    url: str
    date: datetime
    source: str


class BaseScraper(ABC):
    """Base class for all blog scrapers.

    Implements common functionality such as:
    - HTTP session management with retries
    - Logging configuration
    - Common interface for fetching posts
    """

    def __init__(self, base_url: str, source_name: str) -> None:
        """Initialize a new scraper instance.

        Args:
            base_url: The base URL of the blog to scrape
            source_name: Human-readable name of the blog source
        """
        self.base_url = base_url
        self.source_name = source_name
        self.logger: Logger = setup_logger(f"scraper.{source_name}")

        # Configure session with retries
        self.session = requests.Session()
        retries = Retry(
            total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504]
        )
        self.session.mount("http://", HTTPAdapter(max_retries=retries))
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    @abstractmethod
    async def fetch_latest_posts(self) -> list[BlogPost]:
        """Fetch latest blog posts from the source.

        Returns:
            A list of BlogPost objects representing the latest posts

        Raises:
            requests.RequestException: If there's an error fetching the posts
        """
        pass

    def __del__(self) -> None:
        """Clean up resources by closing the HTTP session."""
        self.session.close()
