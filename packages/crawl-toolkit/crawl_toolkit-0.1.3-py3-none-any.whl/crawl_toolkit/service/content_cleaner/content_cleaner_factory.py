from typing import Protocol
from crawl_toolkit.enum.fetch_type import FetchType
from .html_cleaner import HtmlCleaner
from .markdown_cleaner import MarkdownCleaner
from .crawl4ai_cleaner import Crawl4AICleaner

class ContentCleaner(Protocol):
    """Protokół dla cleanerów treści"""
    def clean(self) -> str:
        """Czyści treść"""
        ...

    def extract_headings(self) -> list[str]:
        """Wyodrębnia nagłówki"""
        ...

class ContentCleanerFactory:
    """Fabryka do tworzenia odpowiednich cleanerów treści"""
    
    @staticmethod
    def create(fetch_type: FetchType, content: str) -> ContentCleaner:
        """
        Tworzy odpowiedni cleaner na podstawie typu treści
        
        Args:
            fetch_type: Typ treści
            content: Treść do wyczyszczenia
            
        Returns:
            Odpowiedni cleaner
            
        Raises:
            ValueError: Jeśli podano nieprawidłowy typ treści
        """
        if fetch_type == FetchType.HTML:
            return HtmlCleaner(content)
        elif fetch_type == FetchType.MARKDOWN:
            return MarkdownCleaner(content)
        elif fetch_type.name.lower() == 'crawl4ai':
            return Crawl4AICleaner(content)
        else:
            raise ValueError(f'Nieprawidłowy typ treści: {fetch_type}') 