"""Anthropic Engineering blog scraper."""

from datetime import datetime, timezone
from typing import List
import re

from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper, BlogPost


class AnthropicScraper(BaseScraper):
    """Scraper for the Anthropic Engineering blog."""

    def __init__(self) -> None:
        """Initialize the Anthropic Engineering blog scraper."""
        super().__init__(
            base_url="https://www.anthropic.com/engineering",
            source_name="Anthropic Engineering",
        )

    async def fetch_latest_posts(self) -> List[BlogPost]:
        """Fetch latest blog posts from Anthropic Engineering blog.

        Returns:
            A list of BlogPost objects representing the latest posts
        """
        posts: List[BlogPost] = []

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
            response = self.session.get(self.base_url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Find all links to engineering posts
            links = soup.find_all("a", href=lambda x: x and "/engineering/" in x)
            self.logger.debug(f"Found {len(links)} engineering links")

            for link in links:
                try:
                    # Get title from link text
                    title_text = link.get_text(strip=True)
                    if not title_text:
                        continue

                    # Get URL
                    url = link.get("href")
                    if not url:
                        continue

                    # Make URL absolute if relative
                    if url.startswith("/"):
                        url = "https://www.anthropic.com" + url
                    elif not url.startswith("http"):
                        url = "https://www.anthropic.com/" + url

                    # Extract date from the link's text or parent's text
                    # Dates are embedded in the text like "Title Mar 25, 2026"
                    all_text = link.get_text()
                    parent = link.parent
                    while parent and not all_text:
                        all_text = parent.get_text()
                        parent = parent.parent

                    # Look for date pattern: "Mon DD, YYYY" or "Mon DD YYYY"
                    date_pattern = r"(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),?\s+(\d{4})"
                    match = re.search(date_pattern, all_text)
                    
                    if not match:
                        self.logger.debug(f"No date found for article '{title_text[:60]}'")
                        continue

                    # Parse the date
                    date_str = match.group(0)
                    # Normalize format: "Mar 25, 2026" or "Mar 25 2026"
                    date_str = date_str.replace(",", "")
                    
                    try:
                        pub_date = datetime.strptime(date_str, "%b %d %Y")
                        pub_date = pub_date.replace(tzinfo=timezone.utc)
                    except ValueError:
                        self.logger.debug(f"Could not parse date '{date_str}' for article '{title_text[:60]}'")
                        continue

                    post = BlogPost(
                        title=title_text,
                        url=url,
                        date=pub_date,
                        source=self.source_name,
                    )
                    posts.append(post)
                    self.logger.debug(f"Successfully parsed post: {title_text[:60]}")

                except (AttributeError, ValueError) as e:
                    self.logger.warning(f"Error parsing article: {str(e)}")
                    continue

            self.logger.info(f"Successfully fetched {len(posts)} posts from Anthropic Engineering")

        except Exception as e:
            self.logger.error(f"Error fetching posts from Anthropic Engineering: {str(e)}")
            raise

        return posts
