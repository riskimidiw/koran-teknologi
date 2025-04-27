import asyncio
import os
import schedule
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sources.uber import UberScraper
from sources.netflix import NetflixScraper
from sources.airbnb import AirbnbScraper
from sources.bytebytego import ByteByteGoScraper
from channels.telegram import TelegramChannel

class BlogAggregator:
    def __init__(self):
        self.scrapers = [
            UberScraper(),
            NetflixScraper(),
            AirbnbScraper(),
            ByteByteGoScraper()
        ]
        self.telegram = TelegramChannel()
        self.last_check = datetime.now() - timedelta(days=1)

    async def check_and_send_updates(self):
        all_posts = []
        for scraper in self.scrapers:
            try:
                posts = await scraper.fetch_latest_posts()
                new_posts = [p for p in posts if p.date > self.last_check]
                all_posts.extend(new_posts)
            except Exception as e:
                print(f"Error fetching posts from {scraper.source_name}: {e}")

        if all_posts:
            await self.telegram.send_posts(sorted(all_posts, key=lambda x: x.date, reverse=True))
        
        self.last_check = datetime.now()

async def run_check():
    aggregator = BlogAggregator()
    await aggregator.check_and_send_updates()

def main():
    load_dotenv()
    
    # Run immediately on startup
    asyncio.run(run_check())
    
    # Schedule to run daily at midnight
    schedule.every().day.at("00:00").do(lambda: asyncio.run(run_check()))
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()