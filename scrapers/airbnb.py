"""Airbnb Engineering blog scraper using Medium RSS feed."""

from typing import List
import xml.etree.ElementTree as ET

from scrapers.base_scraper import BaseScraper, BlogPost


class AirbnbScraper(BaseScraper):
    """Scraper for the Airbnb Engineering blog on Medium using RSS feed."""

    def __init__(self):
        """Initialize the Airbnb Engineering blog scraper."""
        super().__init__(
            base_url="https://medium.com/airbnb-engineering",
            source_name="Airbnb Engineering",
        )

    async def fetch_latest_posts(self) -> List[BlogPost]:
        """Fetch the latest blog posts from Airbnb Engineering using Medium RSS feed.
        
        Note: We use the RSS feed instead of HTML scraping because Medium has strong
        bot protection (Cloudflare CAPTCHA) that blocks regular HTTP clients.
        """
        posts = []

        try:
            # Use Medium RSS feed for Airbnb Engineering
            rss_url = "https://medium.com/feed/airbnb-engineering"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            }
            
            response = self.session.get(rss_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse RSS feed
            root = ET.fromstring(response.content)
            
            # Find all items in the RSS feed
            items = root.findall('.//item')
            self.logger.debug(f"Found {len(items)} items in Airbnb Engineering RSS feed")
            
            for item in items:
                try:
                    title_elem = item.find('title')
                    link_elem = item.find('link')
                    pub_date_elem = item.find('pubDate')
                    
                    if title_elem is None or link_elem is None:
                        continue
                    
                    title = title_elem.text.strip() if title_elem.text else ''
                    url = link_elem.text.strip() if link_elem.text else ''
                    
                    if not title or not url:
                        continue
                    
                    # Parse publication date
                    pub_date = None
                    if pub_date_elem is not None and pub_date_elem.text:
                        try:
                            # Parse RFC 2822 format
                            from email.utils import parsedate_to_datetime
                            pub_date = parsedate_to_datetime(pub_date_elem.text)
                        except Exception as e:
                            self.logger.debug(f"Could not parse date: {pub_date_elem.text}")
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
                    self.logger.warning(f"Error parsing Airbnb RSS item: {str(e)}")
                    continue
            
            self.logger.info(f"Successfully fetched {len(posts)} posts from Airbnb Engineering")

        except Exception as e:
            self.logger.error(f"Error fetching Airbnb Engineering posts: {str(e)}")
            raise

        return posts
