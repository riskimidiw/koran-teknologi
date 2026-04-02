"""Telegram channel for sending blog post updates."""

import os
from collections import defaultdict
from datetime import date
from typing import List, Optional

from telegram import Bot

from scrapers.base_scraper import BlogPost
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Emoji mapping for different blog sources
SOURCE_EMOJIS = {
    "Netflix Engineering": "🎬",
    "Uber Engineering": "🚗",
    "Airbnb Engineering": "🏠",
    "AWS Architecture": "☁️",
    "Lyft Engineering": "🚕",
    "ByteByteGo": "📚",
    "GitHub": "🐙",
    "Google Research": "🔬",
    "Anthropic": "🧠",
}


class TelegramChannel:
    """A channel for sending blog posts via Telegram."""

    def __init__(self, bot: Optional[Bot] = None, dry_run: bool = False) -> None:
        """Initialize the Telegram channel.

        Args:
            bot: Optional Bot instance for testing
            dry_run: If True, print messages instead of sending them

        Raises:
            ValueError: If required environment variables are missing
        """
        logger.info("Initializing Telegram bot")

        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        self.channel_id = os.environ.get("TELEGRAM_CHANNEL_ID")
        self.dry_run = dry_run

        if not token or not self.channel_id:
            raise ValueError(
                "TELEGRAM_BOT_TOKEN and TELEGRAM_CHANNEL_ID environment variables are required"
            )

        self.bot = bot or Bot(token=token)

    async def send_posts(self, posts: List[BlogPost]) -> None:
        """Send multiple blog posts to Telegram, grouped by day.

        Posts are grouped by their publication date and sent as a single message
        per day, reducing message spam and improving readability.

        Args:
            posts: List of blog posts to send
        """
        # Sort posts by date (newest first)
        sorted_posts = sorted(posts, key=lambda x: x.date, reverse=True)

        # Group posts by date
        posts_by_date = defaultdict(list)
        for post in sorted_posts:
            post_date = post.date.date()
            posts_by_date[post_date].append(post)

        # Send one message per day with all posts from that day
        for post_date in sorted(posts_by_date.keys(), reverse=True):
            posts_for_day = posts_by_date[post_date]
            await self._send_daily_posts(post_date, posts_for_day)

    async def _send_daily_posts(self, post_date: date, posts: List[BlogPost]) -> None:
        """Send all posts from a specific day as a single message.

        In dry-run mode, prints the message instead of sending it.

        Args:
            post_date: The date for these posts
            posts: List of blog posts from this date
        """
        # Build message with all posts from this day
        message_lines = [
            f"📰 *{post_date.strftime('%b %d, %Y')}*",
            ""
        ]

        # Group by source for better organization
        posts_by_source = defaultdict(list)
        for post in posts:
            posts_by_source[post.source].append(post)

        # Add posts organized by source
        for source in sorted(posts_by_source.keys()):
            source_posts = posts_by_source[source]
            emoji = SOURCE_EMOJIS.get(source, "📝")
            message_lines.append(f"{emoji} *{source}*")

            for i, post in enumerate(source_posts, 1):
                # Bold title with source counter
                message_lines.append(f"  *{i}.* {post.title}")
                # Shorter link text for better formatting
                message_lines.append(f"      [Read →]({post.url})")

            message_lines.append("")  # Blank line between sources

        message = "\n".join(message_lines).rstrip()

        if self.dry_run:
            # In dry-run mode, print the message
            print()
            print(message)
            logger.info(
                f"DRY-RUN: Would send {len(posts)} posts from {post_date} to Telegram"
            )
        else:
            # In normal mode, send via Telegram
            try:
                await self.bot.send_message(
                    chat_id=self.channel_id, text=message, parse_mode="Markdown"
                )
                logger.info(
                    f"Successfully sent {len(posts)} posts from {post_date} to Telegram"
                )
            except Exception as e:
                logger.error(
                    f"Failed to send posts from {post_date} to Telegram: {str(e)}"
                )
                raise
