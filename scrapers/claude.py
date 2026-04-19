"""Claude blog scraper implementation."""

import json
from datetime import datetime, timezone
from typing import List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper, BlogPost


class ClaudeScraper(BaseScraper):
    """Scraper for the Claude blog."""

    def __init__(self) -> None:
        """Initialize the Claude blog scraper."""
        super().__init__(
            base_url="https://claude.com/blog/",
            source_name="Claude Blog",
        )

    async def fetch_latest_posts(self) -> List[BlogPost]:
        """Fetch latest blog posts from Claude blog.

        Uses HTML parsing with JSON-LD schema extraction approach.
        Strategy: Extract blog post links from the list page, then fetch
        each post's JSON-LD BlogPosting schema for metadata.
        """
        posts = []

        try:
            # Step 1: Fetch the blog list page
            blog_list_url = "https://claude.com/blog"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            }
            response = self.session.get(blog_list_url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            # Step 2: Extract blog post URLs from links
            post_links = []
            for a in soup.find_all("a", href=True):
                href = a.get("href")
                if href and "/blog/" in href and "/blog/category/" not in href:
                    # Normalize to full URL
                    full_url = urljoin("https://claude.com", href)
                    if full_url not in post_links:
                        post_links.append(full_url)

            self.logger.debug(f"Found {len(post_links)} blog post links")

            # Step 3: Fetch each post and extract metadata from JSON-LD schema
            for post_url in post_links:
                try:
                    post_response = self.session.get(
                        post_url, headers=headers, timeout=10
                    )
                    post_response.raise_for_status()
                    post_soup = BeautifulSoup(post_response.content, "html.parser")

                    # Find JSON-LD BlogPosting schema
                    blog_post_data = None
                    for script in post_soup.find_all(
                        "script", type="application/ld+json"
                    ):
                        try:
                            data = json.loads(script.string)
                            if data.get("@type") == "BlogPosting":
                                blog_post_data = data
                                break
                        except (json.JSONDecodeError, TypeError):
                            continue

                    if blog_post_data:
                        # Extract required fields
                        title = blog_post_data.get("headline", "Unknown Title")
                        date_str = blog_post_data.get("datePublished", "")

                        # Parse date (format: "Apr 14, 2026" or "April 14, 2026")
                        if date_str:
                            try:
                                # Try parsing "Apr 14, 2026" format
                                pub_date = datetime.strptime(
                                    date_str.strip(), "%b %d, %Y"
                                ).replace(tzinfo=timezone.utc)
                            except ValueError:
                                try:
                                    # Try parsing "April 14, 2026" format
                                    pub_date = datetime.strptime(
                                        date_str.strip(), "%B %d, %Y"
                                    ).replace(tzinfo=timezone.utc)
                                except ValueError:
                                    self.logger.warning(
                                        f"Could not parse date: {date_str} for {title}"
                                    )
                                    continue
                        else:
                            self.logger.warning(f"No date found for post: {title}")
                            continue

                        # Create BlogPost object
                        post = BlogPost(
                            title=title,
                            url=post_url,
                            date=pub_date,
                            source=self.source_name,
                        )
                        posts.append(post)
                        self.logger.debug(
                            f"Added post: {title} ({pub_date.strftime('%Y-%m-%d')})"
                        )

                except Exception as e:
                    self.logger.debug(f"Error fetching post {post_url}: {str(e)}")
                    continue

            self.logger.info(f"Successfully fetched {len(posts)} posts")

        except Exception as e:
            self.logger.error(f"Error fetching posts: {str(e)}")
            raise

        return posts
