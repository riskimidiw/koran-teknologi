"""Uber Engineering blog scraper implementation."""

import zoneinfo
from datetime import datetime

from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper, BlogPost


class UberScraper(BaseScraper):
    """Scraper for the Uber Engineering blog."""

    def __init__(self) -> None:
        """Initialize the Uber blog scraper."""
        super().__init__(
            base_url="https://eng.uber.com",
            source_name="Uber Engineering",
        )

    async def fetch_latest_posts(self) -> list[BlogPost]:
        """Fetch latest blog posts from Uber Engineering."""
        posts: list[BlogPost] = []

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            }
            response = self.session.get(self.base_url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Find all article cards
            articles = soup.find_all("a", attrs={"data-baseweb": "card"})
            self.logger.debug(f"Found {len(articles)} articles")

            for article in articles:
                try:
                    # Extract title from h2 tag
                    title_elem = article.find("h2")
                    if not title_elem:
                        continue

                    # Get URL from article card link and clean it
                    url = article["href"]
                    if "?" in url:
                        url = url.split("?")[0]  # Remove tracking parameters
                    if not url.startswith("http"):
                        url = "https://www.uber.com" + url

                    # Extract date from p tag with format "Month Day / Region"
                    date_elem = article.find(
                        "p", class_=lambda x: x and "f5" in x.split()
                    )
                    if not date_elem:
                        continue

                    title = title_elem.text.strip()
                    date_text = date_elem.text.split("/")[0].strip()
                    try:
                        # Try parsing with year if present, otherwise add current year
                        try:
                            date = datetime.strptime(date_text, "%B %d, %Y")
                        except ValueError:
                            current_year = datetime.now(zoneinfo.ZoneInfo("UTC")).year
                            date = datetime.strptime(
                                f"{date_text} {current_year}", "%B %d %Y"
                            )
                        # Make datetime timezone-aware
                        date = date.replace(tzinfo=zoneinfo.ZoneInfo("UTC"))
                    except ValueError:
                        self.logger.warning(f"Could not parse date: {date_text}")
                        continue

                    posts.append(
                        BlogPost(
                            title=title,
                            url=url,
                            date=date,
                            source=self.source_name,
                        )
                    )
                except (AttributeError, KeyError, ValueError) as e:
                    self.logger.warning(f"Error parsing article: {str(e)}")
                    continue

            self.logger.info(f"Successfully fetched {len(posts)} posts")

        except Exception as e:
            self.logger.error(f"Error fetching posts: {str(e)}")
            raise

        return posts
