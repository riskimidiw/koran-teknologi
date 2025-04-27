import os
from datetime import datetime
from telegram.ext import ApplicationBuilder
from telegram import Update
from sources.base import BlogPost

class TelegramChannel:
    def __init__(self):
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.channel_id = os.getenv('TELEGRAM_CHANNEL_ID')
        self.app = ApplicationBuilder().token(token).build()

    async def send_post(self, post: BlogPost):
        message = (
            f"🔥 New post from {post.source}!\n\n"
            f"📝 {post.title}\n\n"
            f"🔗 {post.url}\n\n"
            f"📅 {post.date.strftime('%Y-%m-%d')}"
        )
        await self.app.bot.send_message(
            chat_id=self.channel_id,
            text=message,
            disable_web_page_preview=False
        )

    async def send_posts(self, posts: list[BlogPost]):
        for post in sorted(posts, key=lambda x: x.date, reverse=True):
            await self.send_post(post)