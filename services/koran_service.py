"""Service layer for Koran Teknologi."""

from datetime import datetime, timedelta, timezone
from typing import List, Optional

from channels.telegram import TelegramChannel
from scrapers.airbnb import AirbnbScraper
from scrapers.anthropic import AnthropicScraper
from scrapers.aws import AWSArchitectureScraper
from scrapers.base_scraper import BlogPost
from scrapers.bytebytego import ByteByteGoScraper
from scrapers.claude import ClaudeScraper
from scrapers.github import GitHubAIScraper
from scrapers.google_research import GoogleResearchScraper
from scrapers.lyft import LyftScraper
from scrapers.netflix import NetflixScraper
from scrapers.uber import UberScraper
from utils.logger import setup_logger

logger = setup_logger(__name__)


class KoranService:
    """Service class that orchestrates blog fetching and distribution."""

    def __init__(self, dry_run: bool = False):
        self.scrapers = [
            UberScraper(),
            NetflixScraper(),
            AirbnbScraper(),
            ByteByteGoScraper(),
            AWSArchitectureScraper(),
            LyftScraper(),
            AnthropicScraper(),
            GitHubAIScraper(),
            GoogleResearchScraper(),
            ClaudeScraper(),
        ]
        self.channel = TelegramChannel(dry_run=dry_run)
        self.dry_run = dry_run

    async def fetch_new_posts(self, since: Optional[datetime] = None) -> List[BlogPost]:
        """Fetch new posts from all configured scrapers.

        Args:
            since: Only return posts newer than this date. Defaults to 24h ago.

        Returns:
            List of new blog posts
        """
        if since is None:
            since = datetime.now(timezone.utc) - timedelta(days=1)
        elif since.tzinfo is None:
            since = since.replace(tzinfo=timezone.utc)

        logger.info(f"Starting blog check since {since}...")
        all_posts = []

        for scraper in self.scrapers:
            try:
                logger.info(f"Fetching posts from {scraper.source_name}")
                posts = await scraper.fetch_latest_posts()
                new_posts = [p for p in posts if p.date > since]

                if new_posts:
                    logger.info(
                        f"Found {len(new_posts)} new posts from {scraper.source_name}"
                    )
                    all_posts.extend(new_posts)
                else:
                    logger.info(f"No new posts from {scraper.source_name}")

            except Exception as e:
                logger.error(
                    f"Error fetching posts from {scraper.source_name}: {str(e)}"
                )

        return sorted(all_posts, key=lambda x: x.date, reverse=True)

    async def send_posts(self, posts: List[BlogPost]) -> None:
        """Send posts to the configured notification channel.

        In dry-run mode, messages are printed instead of sent.

        Args:
            posts: List of posts to send
        """
        if not posts:
            logger.info("No new posts to send")
            return

        try:
            logger.info(f"Processing {len(posts)} new posts")
            await self.channel.send_posts(posts)
        except Exception as e:
            logger.error(f"Error processing posts: {str(e)}")
