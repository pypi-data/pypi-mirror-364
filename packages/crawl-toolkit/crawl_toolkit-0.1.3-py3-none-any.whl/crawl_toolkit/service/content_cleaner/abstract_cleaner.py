from abc import ABC, abstractmethod
from typing import List, Optional
from crawl_toolkit.enum.language import Language

class AbstractContentCleaner(ABC):
    """Abstract base class for content cleaners."""
    
    @abstractmethod
    def clean(self, content: str) -> str:
        """
        Clean the content.
        
        Args:
            content: Content to clean
            
        Returns:
            Cleaned content
        """
        pass
        
    @abstractmethod
    def extract_links(self, content: str) -> List[str]:
        """
        Extract links from content.
        
        Args:
            content: Content to process
            
        Returns:
            List of extracted links
        """
        pass
        
    @abstractmethod
    def extract_images(self, content: str) -> List[str]:
        """
        Extract images from content.
        
        Args:
            content: Content to process
            
        Returns:
            List of extracted image URLs
        """
        pass
        
    @abstractmethod
    def normalize(self, content: str) -> str:
        """
        Normalize content.
        
        Args:
            content: Content to normalize
            
        Returns:
            Normalized content
        """
        pass 