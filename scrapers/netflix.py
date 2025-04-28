"""Netflix Tech Blog scraper."""

from datetime import datetime, timezone
from typing import List

import aiohttp
from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper, BlogPost
from utils.logger.logger import setup_logger

logger = setup_logger("scraper.Netflix Tech Blog")


class NetflixScraper(BaseScraper):
    """Scraper for the Netflix Tech Blog."""

    def __init__(self):
        """Initialize the Netflix Tech Blog scraper."""
        super().__init__(
            base_url="https://netflixtechblog.com/",
            source_name="Netflix Tech Blog",
        )
        self._session = None

    def get_session(self):
        """Get or create an aiohttp session."""
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session

    async def fetch_latest_posts(self) -> List[BlogPost]:
        """Fetch the latest blog posts from Netflix Tech Blog."""
        posts = []

        try:
            async with self.get_session() as session:
                async with session.get(self.base_url) as response:
                    response.raise_for_status()
                    html = await response.text()

            soup = BeautifulSoup(html, "html.parser")
            articles = soup.find_all("div", class_="u-xs-size12of12")

            for article in articles:
                try:
                    # Find title from h3 element
                    title_elem = article.find("h3", class_="u-contentSansBold")
                    if not title_elem:
                        continue
                    title = title_elem.get_text().strip()

                    # Find link from first anchor tag
                    link_elem = article.find("a", href=True)
                    if link_elem:
                        link = link_elem.get("href")
                        if "?" in link:
                            link = link.split("?")[0]

                    # Find date from time element
                    date_elem = article.find("time")
                    if date_elem and date_elem.get("datetime"):
                        # Parse ISO format date and ensure it's timezone-aware
                        date_str = date_elem["datetime"]
                        if not date_str.endswith("Z"):
                            date_str += "Z"
                        date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                        date = date.replace(tzinfo=timezone.utc)

                    if title and link and date:
                        posts.append(
                            BlogPost(
                                title=title,
                                url=link,
                                date=date,
                                source=self.source_name,
                            )
                        )

                except Exception as e:
                    logger.warning(f"Error parsing article: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Error fetching Netflix Tech Blog: {str(e)}")
            raise

        logger.info(f"Successfully fetched {len(posts)} posts")
        return posts
