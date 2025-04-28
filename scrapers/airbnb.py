from datetime import datetime

from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper, BlogPost


class AirbnbScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            base_url="https://medium.com/airbnb-engineering/",
            source_name="Airbnb Engineering",
        )

    async def fetch_latest_posts(self) -> list[BlogPost]:
        posts = []

        try:
            response = self.session.get(self.base_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            articles = soup.select("div.col.u-xs-size12of12")
            self.logger.debug(f"Found {len(articles)} articles")

            for article in articles:
                try:
                    title_elem = article.select_one("h3 div.u-letterSpacingTight")
                    if not title_elem:
                        continue

                    title = title_elem.text.strip()
                    link_elem = article.select_one("a[href*='/airbnb-engineering/']")
                    if not link_elem:
                        continue

                    url = link_elem["href"]
                    if isinstance(url, list):
                        url = url[0]
                    url = url.split("?")[0]  # Remove query parameters

                    date_elem = article.select_one("time")
                    if not date_elem:
                        continue

                    date_str = date_elem["datetime"]
                    if isinstance(date_str, list):
                        date_str = date_str[0]
                    # Convert ISO format with Z timezone to datetime
                    iso_date = date_str.replace("Z", "+00:00")
                    post = BlogPost(
                        title=title,
                        url=url,
                        date=datetime.fromisoformat(iso_date),
                        source=self.source_name,
                    )

                    posts.append(post)
                except (AttributeError, KeyError, ValueError) as e:
                    self.logger.warning(f"Error parsing article: {str(e)}")
                    continue

            self.logger.info(f"Successfully fetched {len(posts)} posts")

        except Exception as e:
            self.logger.error(f"Error fetching posts: {str(e)}")
            raise

        return posts
