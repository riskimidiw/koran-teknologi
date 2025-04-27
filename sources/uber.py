import requests
from bs4 import BeautifulSoup
from datetime import datetime
from .base import BaseScraper, BlogPost

class UberScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            base_url="https://www.uber.com/en-ID/blog/engineering/",
            source_name="Uber Engineering"
        )

    async def fetch_latest_posts(self) -> list[BlogPost]:
        response = requests.get(self.base_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        posts = []
        
        # Uber's blog structure parsing
        articles = soup.select('article.post')
        for article in articles:
            title = article.select_one('h2').text.strip()
            url = article.select_one('a')['href']
            date_str = article.select_one('time')['datetime']
            date = datetime.strptime(date_str, '%Y-%m-%d')
            
            posts.append(BlogPost(
                title=title,
                url=url,
                date=date,
                source=self.source_name
            ))
        
        return posts