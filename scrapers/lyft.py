"""Lyft Engineering blog scraper."""

from datetime import datetime, timezone

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper, BlogPost


class LyftScraper(BaseScraper):
    """Scraper for Lyft Engineering Blog."""

    def __init__(self) -> None:
        """Initialize Lyft Engineering blog scraper."""
        super().__init__(
            base_url="https://eng.lyft.com/", source_name="Lyft Engineering"
        )

    async def fetch_latest_posts(self) -> list[BlogPost]:
        """Fetch latest blog posts from Lyft Engineering blog.

        Returns:
            A list of BlogPost objects representing the latest posts
        """
        posts = []

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Referer": "https://eng.lyft.com/",
            }
            response = self.session.get(self.base_url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            articles = soup.find_all(
                "div", attrs={"data-post-id": True}
            )  # Medium's article container

            for article in articles:
                try:
                    # Find title from h3/h2 element
                    title_elem = article.find(
                        ["h2", "h3"], class_=lambda x: x and "graf--title" in x
                    )
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
                    else:
                        # Fallback to looking for date text
                        date_text = article.find(
                            "a", text=lambda x: x and len(x.split()) <= 2
                        )
                        if not date_text:
                            continue
                        try:
                            date_str = date_text.text.strip().split("·")[0].strip()
                            if "," in date_str:
                                date = datetime.strptime(date_str, "%b %d, %Y")
                            else:
                                current_year = datetime.now().year
                                date = datetime.strptime(
                                    f"{date_str}, {current_year}", "%b %d, %Y"
                                )
                            date = date.replace(hour=12, tzinfo=timezone.utc)
                        except ValueError:
                            continue

                    if title and link and date:
                        posts.append(
                            BlogPost(
                                title=title,
                                url=link,
                                date=date,
                                source=self.source_name,
                            )
                        )
                        self.logger.debug(f"Successfully added post: {title} ({date})")

                except Exception as e:
                    self.logger.warning(f"Error parsing article: {str(e)}")
                    continue

            self.logger.info(f"Successfully fetched {len(posts)} posts")
            return posts

        except Exception as e:
            self.logger.error(f"Error fetching Lyft Engineering blog posts: {str(e)}")
            return []
