"""AWS Architecture blog scraper."""

from datetime import datetime
import re
from bs4 import BeautifulSoup
import requests

from .base_scraper import BaseScraper, BlogPost


class AWSArchitectureScraper(BaseScraper):
    """Scraper for AWS Architecture Blog."""

    def __init__(self) -> None:
        """Initialize AWS Architecture blog scraper."""
        super().__init__(
            base_url="https://aws.amazon.com/blogs/architecture/",
            source_name="AWS Architecture"
        )

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string and handle various timezone formats.
        
        Args:
            date_str: ISO datetime string with timezone
            
        Returns:
            datetime object with timezone info
        """
        # Handle various timezone formats (-07:00, -08:00, etc)
        tz_pattern = r'(-\d{2}:\d{2})$'
        match = re.search(tz_pattern, date_str)
        if match:
            tz = match.group(1)
            # Convert timezone format from -HH:MM to -HHMM for datetime.fromisoformat
            clean_tz = tz.replace(':', '')
            date_str = date_str.replace(tz, clean_tz)
        
        return datetime.fromisoformat(date_str)

    async def fetch_latest_posts(self) -> list[BlogPost]:
        """Fetch latest blog posts from AWS Architecture blog.

        Returns:
            A list of BlogPost objects representing the latest posts
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            }
            response = self.session.get(self.base_url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            posts = []

            # Find all blog post rows
            blog_rows = soup.find_all("div", class_="lb-row lb-snap")
            self.logger.debug(f"Found {len(blog_rows)} blog post rows")

            for post_row in blog_rows:
                try:
                    # Try to find the article URL from both image and title columns
                    img_col = post_row.find("div", class_="lb-col lb-mid-6 lb-tiny-24")
                    content_col = post_row.find("div", class_="lb-col lb-mid-18 lb-tiny-24")
                    
                    if not content_col:
                        self.logger.debug("Skipping row - content column not found")
                        continue

                    # Get title and URL from the content column
                    title_elem = content_col.find("h2", class_="lb-bold blog-post-title")
                    if not title_elem:
                        self.logger.debug("Skipping row - title element not found")
                        continue

                    title_link = title_elem.find("a")
                    if not title_link:
                        self.logger.debug("Skipping row - title link not found")
                        continue
                    
                    title_span = title_link.find("span", property="name headline")
                    if not title_span:
                        self.logger.debug("Skipping row - title span not found")
                        continue

                    title = title_span.text.strip()
                    url = title_link["href"]
                    self.logger.debug(f"Found post: {title}")

                    # Get publication date
                    footer = content_col.find("footer", class_="blog-post-meta")
                    if not footer:
                        self.logger.debug(f"Skipping post '{title}' - footer not found")
                        continue

                    date_elem = footer.find("time", property="datePublished")
                    if not date_elem:
                        self.logger.debug(f"Skipping post '{title}' - date not found")
                        continue
                    
                    date_str = date_elem["datetime"]
                    self.logger.debug(f"Raw date string: {date_str}")
                    
                    try:
                        date = self._parse_date(date_str)
                        self.logger.debug(f"Parsed date: {date}")
                    except ValueError as e:
                        self.logger.warning(f"Error parsing date '{date_str}': {str(e)}")
                        continue

                    posts.append(
                        BlogPost(
                            title=title,
                            url=url,
                            date=date,
                            source=self.source_name,
                        )
                    )
                    self.logger.debug(f"Successfully added post: {title} ({date})")

                except Exception as e:
                    self.logger.warning(f"Error parsing blog post: {str(e)}")
                    continue

            self.logger.info(f"Successfully fetched {len(posts)} posts")
            return posts

        except Exception as e:
            self.logger.error(f"Error fetching AWS Architecture blog posts: {str(e)}")
            return []