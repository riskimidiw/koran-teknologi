"""Main script for the blog aggregator service."""

import argparse
import asyncio
import os
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from dotenv import load_dotenv

from channels.telegram import TelegramChannel
from scrapers.airbnb import AirbnbScraper
from scrapers.base_scraper import BaseScraper, BlogPost
from scrapers.bytebytego import ByteByteGoScraper
from scrapers.netflix import NetflixScraper
from scrapers.uber import UberScraper
from utils.logger.logger import setup_logger

logger = setup_logger(__name__)


async def fetch_new_posts(
    scrapers: List[BaseScraper], since: Optional[datetime] = None
) -> List[BlogPost]:
    """Fetch new posts from all configured scrapers.

    Args:
        scrapers: List of scraper instances to use
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

    for scraper in scrapers:
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
            logger.error(f"Error fetching posts from {scraper.source_name}: {str(e)}")

    return sorted(all_posts, key=lambda x: x.date, reverse=True)


async def send_posts(posts: List[BlogPost], channel: TelegramChannel) -> None:
    """Send posts to the configured notification channel.

    Args:
        posts: List of posts to send
        channel: Channel instance to send posts through
    """
    if not posts:
        logger.info("No new posts to send")
        return

    try:
        logger.info(f"Sending {len(posts)} new posts to Telegram")
        await channel.send_posts(posts)
        logger.info("Successfully sent posts to Telegram")
    except Exception as e:
        logger.error(f"Error sending posts to Telegram: {str(e)}")


def validate_environment() -> bool:
    """Validate that all required environment variables are set.

    Returns:
        bool: True if all required variables are set, False otherwise
    """
    required_env_vars = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHANNEL_ID"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )
        logger.error("Please set them in your .env file")
        return False
    return True


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Fetch and send tech blog updates to Telegram"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=int(os.getenv("DAYS", "1")),
        help="Number of days to look back for posts (default: from env or 1)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't send to Telegram, just print posts",
    )
    return parser.parse_args()


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


async def run_check(since: Optional[datetime] = None, dry_run: bool = False) -> None:
    """Run a single check iteration.

    Args:
        since: Only process posts newer than this date. Defaults to 24h ago.
        dry_run: If True, just print posts instead of sending to Telegram
    """
    scrapers = [
        UberScraper(),
        NetflixScraper(),
        AirbnbScraper(),
        ByteByteGoScraper(),
    ]

    posts = await fetch_new_posts(scrapers, since)

    if dry_run:
        await print_posts(posts)
    else:
        channel = TelegramChannel()
        await send_posts(posts, channel)


def main() -> None:
    """Main entry point for the blog aggregator service."""
    try:
        load_dotenv()
        args = parse_args()

        if not args.dry_run and not validate_environment():
            return

        logger.info("Starting Koran Teknologi...")
        since = datetime.now() - timedelta(days=args.days)
        asyncio.run(run_check(since=since, dry_run=args.dry_run))

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
