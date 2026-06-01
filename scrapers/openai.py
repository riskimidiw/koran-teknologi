"""OpenAI blog scraper implementation."""

import re
from datetime import datetime, timezone
from typing import List

import cloudscraper
from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper, BlogPost


class OpenAIScraper(BaseScraper):
    """Scraper for the OpenAI blog."""

    def __init__(self) -> None:
        """Initialize the OpenAI blog scraper."""
        super().__init__(
            base_url="https://openai.com/news/",
            source_name="OpenAI",
        )
        self.scraper = cloudscraper.create_scraper()

    async def fetch_latest_posts(self) -> List[BlogPost]:
        """Fetch latest blog posts from OpenAI.

        Uses cloudscraper to bypass Cloudflare protection and fetch the page,
        then parses the HTML to extract articles with titles, URLs, and dates.
        """
        posts: List[BlogPost] = []

        try:
            self.logger.info("Fetching OpenAI news with cloudscraper...")

            # Use cloudscraper to bypass Cloudflare
            response = self.scraper.get(self.base_url, timeout=20)
            response.raise_for_status()

            self.logger.debug(
                f"Got response: {response.status_code}, {len(response.text)} bytes"
            )

            # Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")

            # Find all links on the page
            links = soup.find_all("a", href=True)
            self.logger.debug(f"Found {len(links)} links")

            for link in links:
                try:
                    href = link.get("href", "").strip()
                    title = link.get_text(strip=True).strip()

                    # Skip empty links
                    if not href or not title or len(title) < 5:
                        continue

                    # Get the parent div to search for nearby date
                    parent_div = link.find_parent("div")
                    if not parent_div:
                        continue

                    parent_text = parent_div.get_text(strip=True)

                    # Look for date pattern in parent text
                    date_match = re.search(
                        r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
                        r"[a-z]*\s+\d{1,2},?\s+\d{4}",
                        parent_text,
                    )

                    if not date_match:
                        self.logger.debug(f"No date found for: {title[:40]}")
                        continue

                    date_str = date_match.group(0)

                    try:
                        # Parse the date (e.g., "May 29, 2026")
                        pub_date = datetime.strptime(date_str, "%b %d, %Y").replace(
                            tzinfo=timezone.utc
                        )
                    except ValueError as e:
                        self.logger.debug(f"Could not parse date '{date_str}': {e}")
                        continue

                    # Make absolute URL if relative
                    if not href.startswith("http"):
                        url = f"https://openai.com{href}"
                    else:
                        url = href

                    posts.append(
                        BlogPost(
                            title=title,
                            url=url,
                            date=pub_date,
                            source=self.source_name,
                        )
                    )
                    self.logger.debug(f"Found post: {title[:60]}")

                except (AttributeError, KeyError, ValueError) as e:
                    self.logger.debug(f"Error parsing article: {str(e)}")
                    continue

            # Remove duplicates based on URL
            unique_posts = {}
            for post in posts:
                if post.url not in unique_posts:
                    unique_posts[post.url] = post

            posts = list(unique_posts.values())

            self.logger.info(f"Successfully fetched {len(posts)} posts from OpenAI")

        except Exception as e:
            self.logger.error(f"Error fetching OpenAI posts: {str(e)}")
            raise

        return posts
