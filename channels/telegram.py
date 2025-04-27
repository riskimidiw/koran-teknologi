"""Telegram channel for sending blog post updates."""

import os
from typing import List, Optional

from telegram.ext import Application

from telegram import Bot
from sources.base import BlogPost
from utils.logger import setup_logger

logger = setup_logger(__name__)


class TelegramChannel:
    """A channel for sending blog posts via Telegram."""

    def __init__(self, bot: Optional[Bot] = None) -> None:
        """Initialize the Telegram channel.

        Args:
            bot: Optional Bot instance for testing

        Raises:
            ValueError: If required environment variables are missing
        """
        logger.info("Initializing Telegram bot")

        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        self.channel_id = os.environ.get("TELEGRAM_CHANNEL_ID")

        if not token or not self.channel_id:
            raise ValueError(
                "TELEGRAM_BOT_TOKEN and TELEGRAM_CHANNEL_ID environment variables are required"
            )

        self.bot = bot or Bot(token=token)

    async def send_post(self, post: BlogPost) -> None:
        """Send a single blog post to Telegram.

        Args:
            post: The blog post to send

        Raises:
            Exception: If there's an error sending the message
        """
        message = (
            f"📝 [{post.title}]({post.url})\n\n"
            f"📚 Source: {post.source}\n"
            f"📅 Date: {post.date.strftime('%Y-%m-%d')}"
        )

        try:
            await self.bot.send_message(
                chat_id=self.channel_id, text=message, parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            raise

    async def send_posts(self, posts: List[BlogPost]) -> None:
        """Send multiple blog posts to Telegram.

        Args:
            posts: List of blog posts to send
        """
        # Sort posts by date (newest first) before sending
        sorted_posts = sorted(posts, key=lambda x: x.date, reverse=True)

        for post in sorted_posts:
            await self.send_post(post)
