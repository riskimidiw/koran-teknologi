from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

@dataclass
class BlogPost:
    title: str
    url: str
    date: datetime
    source: str

class BaseScraper(ABC):
    def __init__(self, base_url: str, source_name: str):
        self.base_url = base_url
        self.source_name = source_name

    @abstractmethod
    async def fetch_latest_posts(self) -> list[BlogPost]:
        """Fetch latest blog posts from the source"""
        pass