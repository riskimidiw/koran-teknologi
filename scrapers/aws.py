"""AWS Architecture blog scraper implementation."""

import xml.etree.ElementTree as ET
from typing import List

from .base_scraper import BaseScraper, BlogPost


class AWSArchitectureScraper(BaseScraper):
    """Scraper for the AWS Architecture blog."""

    def __init__(self) -> None:
        """Initialize the AWS Architecture blog scraper."""
        super().__init__(
            base_url="https://aws.amazon.com/blogs/architecture/",
            source_name="AWS Architecture",
        )

    async def fetch_latest_posts(self) -> List[BlogPost]:
        """Fetch latest blog posts from AWS Architecture using RSS feed.

        Uses RSS feed approach (most reliable - Skill.md recommendation).
        """
        posts = []

        try:
            # Use RSS feed endpoint
            rss_url = "https://aws.amazon.com/blogs/architecture/feed/"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            }

            response = self.session.get(rss_url, headers=headers, timeout=10)
            response.raise_for_status()

            # Parse RSS feed
            root = ET.fromstring(response.content)

            # Find all items in the RSS feed
            items = root.findall(".//item")
            self.logger.debug(f"Found {len(items)} items in AWS Architecture RSS feed")

            for item in items:
                try:
                    title_elem = item.find("title")
                    link_elem = item.find("link")
                    pub_date_elem = item.find("pubDate")

                    if title_elem is None or link_elem is None:
                        continue

                    title = title_elem.text.strip() if title_elem.text else ""
                    url = link_elem.text.strip() if link_elem.text else ""

                    if not title or not url:
                        continue

                    # Parse publication date
                    pub_date = None
                    if pub_date_elem is not None and pub_date_elem.text:
                        try:
                            # Parse RFC 2822 format
                            from email.utils import parsedate_to_datetime

                            pub_date = parsedate_to_datetime(pub_date_elem.text)
                        except Exception:
                            self.logger.debug(
                                f"Could not parse date: {pub_date_elem.text}"
                            )
                            continue

                    if pub_date is None:
                        continue

                    posts.append(
                        BlogPost(
                            title=title,
                            url=url,
                            date=pub_date,
                            source=self.source_name,
                        )
                    )
                except Exception as e:
                    self.logger.warning(f"Error parsing AWS RSS item: {str(e)}")
                    continue

            self.logger.info(
                f"Successfully fetched {len(posts)} posts from AWS Architecture"
            )

        except Exception as e:
            self.logger.error(f"Error fetching AWS Architecture posts: {str(e)}")
            raise

        return posts
