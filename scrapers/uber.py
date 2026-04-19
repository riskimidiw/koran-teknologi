"""Uber Engineering blog scraper implementation."""

from datetime import datetime, timezone
from typing import List

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from scrapers.base_scraper import BaseScraper, BlogPost


class UberScraper(BaseScraper):
    """Scraper for the Uber Engineering blog."""

    def __init__(self) -> None:
        """Initialize the Uber blog scraper."""
        super().__init__(
            base_url="https://eng.uber.com/",
            source_name="Uber Engineering",
        )

    async def fetch_latest_posts(self) -> List[BlogPost]:
        """Fetch latest blog posts from Uber Engineering using Selenium.

        Note: Uber's engineering blog is a JavaScript-heavy site, so we use
        Selenium with a headless Chrome browser to render the page dynamically.
        """
        posts: List[BlogPost] = []

        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, 15)

        try:
            driver.get(self.base_url)
            self.logger.info(f"Navigated to {self.base_url}")

            # Wait for article cards to be present
            wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "a[href*='blog/']")
                )
            )

            # Get the rendered page content
            content = driver.page_source
            soup = BeautifulSoup(content, "html.parser")

            # Find all article cards - look for divs that contain article links with dates
            for link in soup.find_all("a", href=True):
                try:
                    href = link.get("href", "")

                    # Filter for blog post URLs
                    if not href or "/blog/" not in href:
                        continue
                    if not href.startswith("http"):
                        href = f"https://www.uber.com{href}"

                    title = link.get_text(strip=True)
                    if not title or len(title) < 10:
                        continue

                    # Find the parent container and look for date
                    container = link.find_parent("div")
                    date_elem = None

                    # Search up the tree for a date element
                    while container and not date_elem:
                        date_elem = container.find(
                            lambda tag: tag.name == "div"
                            and (
                                any(
                                    month in tag.get_text()
                                    for month in [
                                        "January",
                                        "February",
                                        "March",
                                        "April",
                                        "May",
                                        "June",
                                        "July",
                                        "August",
                                        "September",
                                        "October",
                                        "November",
                                        "December",
                                    ]
                                )
                                or any(f"{i} " in tag.get_text() for i in range(1, 32))
                            )
                        )
                        container = container.find_parent("div")

                    if not date_elem:
                        self.logger.debug(f"No date found for: {title[:40]}")
                        continue

                    date_str = date_elem.get_text(strip=True)
                    try:
                        # Parse dates like "March 11, 2026" and make timezone-aware (UTC)
                        pub_date = datetime.strptime(date_str, "%B %d, %Y").replace(
                            tzinfo=timezone.utc
                        )
                    except ValueError:
                        self.logger.debug(f"Could not parse date: {date_str}")
                        continue

                    posts.append(
                        BlogPost(
                            title=title,
                            url=href,
                            date=pub_date,
                            source=self.source_name,
                        )
                    )
                    self.logger.debug(f"Found post: {title}")

                except (AttributeError, KeyError, ValueError) as e:
                    self.logger.debug(f"Error parsing article: {str(e)}")
                    continue

            # Remove duplicates based on URL
            unique_posts = {}
            for post in posts:
                if post.url not in unique_posts:
                    unique_posts[post.url] = post

            posts = list(unique_posts.values())

            self.logger.info(
                f"Successfully fetched {len(posts)} posts from Uber Engineering"
            )

        except Exception as e:
            self.logger.error(f"Error fetching Uber Engineering posts: {str(e)}")
            raise
        finally:
            driver.quit()

        return posts
