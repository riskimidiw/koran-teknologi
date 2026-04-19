"""Google Research blog scraper."""

import re
from datetime import datetime, timezone
from typing import List

from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper, BlogPost


class GoogleResearchScraper(BaseScraper):
    """Scraper for the Google Research blog."""

    def __init__(self) -> None:
        """Initialize the Google Research blog scraper."""
        super().__init__(
            base_url="https://research.google/blog/",
            source_name="Google Research",
        )

    async def fetch_latest_posts(self) -> List[BlogPost]:
        """Fetch latest blog posts from Google Research blog.

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

            # Find all article links - Google Research blog posts are links in specific sections
            all_links = soup.find_all("a", href=lambda x: x and "/blog/" in (x or ""))

            self.logger.debug(f"Found {len(all_links)} total links")

            month_names = {
                "january": 1,
                "february": 2,
                "march": 3,
                "april": 4,
                "may": 5,
                "june": 6,
                "july": 7,
                "august": 8,
                "september": 9,
                "october": 10,
                "november": 11,
                "december": 12,
            }

            for link in all_links:
                try:
                    url = link.get("href")

                    # Skip empty titles or label links (category links)
                    if not url or "/label/" in url:
                        continue

                    # Skip year filter links and other non-article links
                    # Check if URL ends with a 4-digit year (e.g., /blog/2026, /blog/2025, etc.)
                    # This is more future-proof than hardcoding specific years
                    if re.search(r"/\d{4}$", url):
                        # This is a year filter link, not an article
                        continue

                    # Make URL absolute if it's relative
                    if url.startswith("/"):
                        url = "https://research.google" + url
                    elif not url.startswith("http"):
                        url = "https://research.google/" + url

                    # Try to extract title from the headline span element
                    title_elem = link.find("span", class_="headline-5")
                    if title_elem:
                        clean_title = title_elem.get_text(strip=True)
                    else:
                        # Fallback to extracting from full text
                        title_text = link.get_text(strip=True)

                        # Extract date using regex pattern
                        date_pattern = r"^([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})"
                        match = re.match(date_pattern, title_text)

                        if match:
                            # Get the remaining text after the date
                            date_end_pos = match.end()
                            remaining_text = title_text[date_end_pos:].strip()

                            # Split by "·" to separate title from categories
                            if "·" in remaining_text:
                                # The first part before the dots
                                first_part = remaining_text.split("·")[0].strip()

                                # Look for question mark as end of title
                                if "?" in first_part:
                                    clean_title = first_part.split("?")[0].strip() + "?"
                                else:
                                    clean_title = first_part
                            else:
                                clean_title = remaining_text
                        else:
                            continue

                    # Skip if clean title is empty
                    if not clean_title:
                        continue

                    # Parse date from the date label element
                    pub_date = None
                    date_label = link.find("p", class_="glue-label")
                    if date_label:
                        date_text = date_label.get_text(strip=True)
                        # Format: "Month DD, YYYY"
                        date_pattern = r"^([A-Za-z]+)\s+(\d{1,2}),\s+(\d{4})"
                        match = re.match(date_pattern, date_text)
                        if match:
                            month_str = match.group(1).lower()
                            day = int(match.group(2))
                            year = int(match.group(3))

                            if month_str in month_names:
                                try:
                                    month = month_names[month_str]
                                    pub_date = datetime(
                                        year, month, day, tzinfo=timezone.utc
                                    )
                                except ValueError:
                                    pass

                    # If no date found, skip this link
                    if not pub_date:
                        continue

                    post = BlogPost(
                        title=clean_title,
                        url=url,
                        date=pub_date,
                        source=self.source_name,
                    )
                    posts.append(post)
                    self.logger.debug(
                        f"Successfully parsed post: {clean_title} ({pub_date.date()})"
                    )

                except Exception as e:
                    self.logger.debug(f"Error parsing link: {str(e)}")
                    continue

            self.logger.info(
                f"Successfully fetched {len(posts)} posts from Google Research"
            )

        except Exception as e:
            self.logger.error(f"Error fetching posts from Google Research: {str(e)}")
            raise

        return posts
