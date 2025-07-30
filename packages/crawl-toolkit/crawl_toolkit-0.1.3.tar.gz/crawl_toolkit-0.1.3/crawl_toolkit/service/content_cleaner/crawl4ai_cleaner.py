import asyncio
from crawl4ai import AsyncWebCrawler
from .abstract_cleaner import AbstractContentCleaner

class Crawl4AICleaner(AbstractContentCleaner):
    """Cleaner wykorzystujący crawl4ai do konwersji HTML na markdown."""
    def __init__(self, html: str, url: str = None):
        self.html = html
        self.url = url

    async def clean(self) -> str:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(html=self.html, url=self.url)
            return result.markdown

    def extract_headings(self) -> list[str]:
        # crawl4ai zwraca markdown, więc nagłówki można wyciągnąć z markdowna
        import re
        headings = []
        for line in self.html.split('\n'):
            match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if match:
                headings.append(match.group(2).strip())
        return headings 