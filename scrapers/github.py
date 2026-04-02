"""GitHub AI & ML Blog scraper."""

from datetime import datetime, timezone
from typing import List
import re

from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper, BlogPost


class GitHubAIScraper(BaseScraper):
    """Scraper for the GitHub AI & ML blog."""

    def __init__(self) -> None:
        """Initialize the GitHub AI & ML blog scraper."""
        super().__init__(
            base_url="https://github.blog/ai-and-ml/",
            source_name="GitHub AI",
        )

    async def fetch_latest_posts(self) -> List[BlogPost]:
        """Fetch latest blog posts from GitHub AI & ML blog.

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

            # Find all article containers - they contain title, description, author, and date
            articles = soup.find_all("article")
            self.logger.debug(f"Found {len(articles)} articles")

            for article in articles:
                try:
                    # Get the link from within the article
                    link_elem = article.find("a", href=True)
                    if not link_elem:
                        continue

                    title = link_elem.get_text(strip=True)
                    if not title:
                        self.logger.debug("Skipping article - no title found")
                        continue

                    url = link_elem.get("href")
                    if not url:
                        self.logger.debug(f"Skipping article '{title}' - no URL")
                        continue

                    # Make URL absolute if it's relative
                    if url.startswith("/"):
                        url = "https://github.blog" + url
                    elif not url.startswith("http"):
                        url = "https://github.blog/" + url

                    # Extract date from the article text
                    # Dates are in format "Month DD, YYYY" within the article
                    all_text = article.get_text()
                    pub_date = None
                    
                    # Try both full and abbreviated month names
                    date_pattern = r"(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),?\s+(\d{4})"
                    match = re.search(date_pattern, all_text)
                    
                    if match:
                        date_str = match.group(0)
                        # Normalize format: remove commas
                        date_str = date_str.replace(",", "")
                        
                        try:
                            # Try abbreviated month first
                            pub_date = datetime.strptime(date_str, "%b %d %Y")
                            if pub_date.tzinfo is None:
                                pub_date = pub_date.replace(tzinfo=timezone.utc)
                            self.logger.debug(f"Found date '{date_str}' for article '{title[:50]}'")
                        except ValueError:
                            # Try full month name
                            try:
                                pub_date = datetime.strptime(date_str, "%B %d %Y")
                                if pub_date.tzinfo is None:
                                    pub_date = pub_date.replace(tzinfo=timezone.utc)
                            except ValueError:
                                self.logger.debug(f"Could not parse date '{date_str}'")

                    # If no date found, skip this article
                    if not pub_date:
                        self.logger.debug(f"No date found for article '{title[:50]}', skipping")
                        continue

                    post = BlogPost(
                        title=title,
                        url=url,
                        date=pub_date,
                        source=self.source_name,
                    )
                    posts.append(post)
                    self.logger.debug(f"Successfully parsed post: {title[:50]}")

                except (AttributeError, ValueError) as e:
                    self.logger.warning(f"Error parsing article: {str(e)}")
                    continue

            self.logger.info(f"Successfully fetched {len(posts)} posts from GitHub AI Blog")

        except Exception as e:
            self.logger.error(f"Error fetching posts from GitHub AI Blog: {str(e)}")
            raise

        return posts
