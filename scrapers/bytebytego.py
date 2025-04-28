"""ByteByteGo blog scraper implementation."""

from datetime import datetime

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from scrapers.base_scraper import BaseScraper, BlogPost


class ByteByteGoScraper(BaseScraper):
    """Scraper for the ByteByteGo blog."""

    def __init__(self) -> None:
        """Initialize the ByteByteGo blog scraper."""
        super().__init__(
            base_url="https://blog.bytebytego.com/", source_name="ByteByteGo"
        )

    async def fetch_latest_posts(self) -> list[BlogPost]:
        """Fetch latest blog posts from ByteByteGo."""
        posts: list[BlogPost] = []

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, 10)

        try:
            driver.get(self.base_url)

            # Handle popup if it appears
            try:
                close_button = wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "button[data-testid='close-modal']")
                    )
                )
                close_button.click()
            except Exception as e:
                self.logger.warning(f"No popup found or couldn't close it: {str(e)}")

            # Wait for articles to load
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='article']"))
            )

            # Get the page content
            content = driver.page_source
            soup = BeautifulSoup(content, "html.parser")

            articles = soup.select("div[role='article']")
            self.logger.debug(f"Found {len(articles)} articles")

            for article in articles:
                try:
                    title_elem = article.select_one(
                        "a[data-testid='post-preview-title']"
                    )
                    if not title_elem:
                        continue

                    title = title_elem.text.strip()
                    url = title_elem["href"]
                    if isinstance(url, list):
                        url = url[0]

                    date_elem = article.select_one("time.date-rtYe1v")
                    if not date_elem or "datetime" not in date_elem.attrs:
                        raise ValueError("Article date not found")

                    datetime_str = date_elem["datetime"]
                    if isinstance(datetime_str, list):
                        datetime_str = datetime_str[0]
                    iso_date = datetime_str.replace("Z", "+00:00")

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
        finally:
            driver.quit()

        return posts
