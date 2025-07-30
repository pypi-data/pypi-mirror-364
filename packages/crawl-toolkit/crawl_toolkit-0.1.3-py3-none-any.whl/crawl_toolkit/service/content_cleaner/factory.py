from typing import Dict, Type
from .abstract_cleaner import AbstractContentCleaner
from .html_cleaner import HtmlCleaner
from .markdown_cleaner import MarkdownCleaner
from crawl_toolkit.enum.fetch_type import FetchType

class ContentCleanerFactory:
    """Factory for creating content cleaners."""
    
    _cleaners: Dict[str, Type[AbstractContentCleaner]] = {
        "html": HtmlCleaner,
        "markdown": MarkdownCleaner
    }
    
    @classmethod
    def create(cls, content_type: str) -> AbstractContentCleaner:
        """
        Create a content cleaner for the specified type.
        
        Args:
            content_type: Type of content to clean (html, markdown)
            
        Returns:
            Content cleaner instance
            
        Raises:
            ValueError: If content type is not supported
        """
        cleaner_class = cls._cleaners.get(content_type.lower())
        if not cleaner_class:
            raise ValueError(f"Unsupported content type: {content_type}")
            
        return cleaner_class()
        
    @classmethod
    def register_cleaner(cls, content_type: str, cleaner_class: Type[AbstractContentCleaner]) -> None:
        """
        Register a new content cleaner.
        
        Args:
            content_type: Type of content
            cleaner_class: Cleaner class to register
        """
        cls._cleaners[content_type.lower()] = cleaner_class 