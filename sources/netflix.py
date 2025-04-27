import requests
from bs4 import BeautifulSoup
from datetime import datetime
from .base import BaseScraper, BlogPost

class NetflixScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            base_url="https://netflixtechblog.com/",
            source_name="Netflix Tech Blog"
        )

    async def fetch_latest_posts(self) -> list[BlogPost]:
        response = requests.get(self.base_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        posts = []
        
        articles = soup.select('article')
        for article in articles:
            title_elem = article.select_one('h3')
            if not title_elem:
                continue
                
            title = title_elem.text.strip()
            url = article.select_one('a')['href']
            date_str = article.select_one('time')['datetime']
            date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            
            posts.append(BlogPost(
                title=title,
                url=url,
                date=date,
                source=self.source_name
            ))
        
        return posts