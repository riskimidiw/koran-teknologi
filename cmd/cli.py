"""CLI command handler for Koran Teknologi."""

import os
from datetime import datetime, timedelta

from services.koran_service import KoranService
from utils.logger import setup_logger

logger = setup_logger(__name__)


def validate_environment() -> bool:
    """Validate that all required environment variables are set."""
    required_env_vars = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHANNEL_ID"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )
        logger.error("Please set them in your .env file")
        return False
    return True


async def run_cli(days: int = 1, dry_run: bool = False) -> None:
    """Run the CLI command.

    Args:
        days: Number of days to look back for posts
        dry_run: If True, just print posts instead of sending to Telegram
    """
    try:
        if not dry_run and not validate_environment():
            return

        logger.info("Starting Koran Teknologi CLI...")
        service = KoranService()
        since = datetime.now() - timedelta(days=days)

        posts = await service.fetch_new_posts(since=since)

        if dry_run:
            await service.print_posts(posts)
        else:
            await service.send_posts(posts)

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise
