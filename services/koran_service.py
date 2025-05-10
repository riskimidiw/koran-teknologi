"""Service layer for Koran Teknologi."""

from datetime import datetime, timedelta, timezone
from typing import List, Optional

from channels.telegram import TelegramChannel
from scrapers.airbnb import AirbnbScraper
from scrapers.aws import AWSArchitectureScraper
from scrapers.base_scraper import BlogPost
from scrapers.bytebytego import ByteByteGoScraper
from scrapers.netflix import NetflixScraper
from scrapers.uber import UberScraper
from utils.logger import setup_logger

logger = setup_logger(__name__)


class KoranService:
    """Service class that orchestrates blog fetching and distribution."""

    def __init__(self):
        self.scrapers = [
            UberScraper(),
            NetflixScraper(),
            AirbnbScraper(),
            ByteByteGoScraper(),
            AWSArchitectureScraper(),
        ]
        self.channel = TelegramChannel()

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

                if (new_posts):
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

        Args:
            posts: List of posts to send
        """
        if not posts:
            logger.info("No new posts to send")
            return

        try:
            logger.info(f"Sending {len(posts)} new posts to Telegram")
            await self.channel.send_posts(posts)
            logger.info("Successfully sent posts to Telegram")
        except Exception as e:
            logger.error(f"Error sending posts to Telegram: {str(e)}")

    @staticmethod
    async def print_posts(posts: List[BlogPost]) -> None:
        """Print posts to console in a readable format.

        Args:
            posts: List of posts to print
        """
        if not posts:
            print("No new posts found")
            return

        print(f"\nFound {len(posts)} new posts:\n")
        for post in posts:
            print(f"📝 {post.title}")
            print(f"📚 Source: {post.source}")
            print(f"📅 Date: {post.date.strftime('%Y-%m-%d')}")
            print(f"🔗 {post.url}\n")
