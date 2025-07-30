from typing import List, Optional
import re
from .abstract_cleaner import AbstractContentCleaner
from crawl_toolkit.enum.language import Language

class MarkdownCleaner(AbstractContentCleaner):
    """Markdown content cleaner implementation."""
    
    def __init__(self, markdown: str):
        """
        Inicjalizacja cleaner'a Markdown
        
        Args:
            markdown: Treść Markdown do wyczyszczenia
        """
        self.markdown = markdown
        self.link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
        self.image_pattern = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
        
    def clean(self) -> str:
        """
        Czyści treść Markdown
        
        Returns:
            Wyczyszczona treść
        """
        # Usuń obrazy
        text = re.sub(r'!\[.*?\]\(.*?\)', '', self.markdown)
        
        # Usuń linki, zachowując tekst
        text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
        
        # Usuń puste linie
        text = re.sub(r'\n\s*\n', '\n', text)
        
        # Usuń znaczniki kodu
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        text = re.sub(r'`.*?`', '', text)
        
        # Usuń znaczniki pogrubienia i kursywy
        text = re.sub(r'[*_]{1,2}(.*?)[*_]{1,2}', r'\1', text)
        
        # Usuń znaczniki cytatów
        text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
        
        # Usuń znaczniki list
        text = re.sub(r'^[-*+]\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\d+\.\s*', '', text, flags=re.MULTILINE)
        
        return text.strip()

    def extract_links(self, content: str) -> List[str]:
        """
        Extract links from Markdown.
        
        Args:
            content: Markdown content
            
        Returns:
            List of links
        """
        links = []
        for match in self.link_pattern.finditer(content):
            url = match.group(2)
            if not url.startswith(("#", "javascript:", "mailto:", "tel:")):
                links.append(url)
        return links
        
    def extract_images(self, content: str) -> List[str]:
        """
        Extract images from Markdown.
        
        Args:
            content: Markdown content
            
        Returns:
            List of image URLs
        """
        images = []
        for match in self.image_pattern.finditer(content):
            url = match.group(2)
            if not url.startswith(("data:", "javascript:")):
                images.append(url)
        return images
        
    def normalize(self, content: str) -> str:
        """
        Normalize Markdown content.
        
        Args:
            content: Markdown content to normalize
            
        Returns:
            Normalized Markdown
        """
        # Clean first
        cleaned = self.clean()
        
        # Normalize headers
        for i in range(6, 0, -1):
            pattern = f"^{'#' * i}\\s+"
            replacement = f"{'#' * i} "
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.MULTILINE)
            
        # Normalize lists
        cleaned = re.sub(r"^[-*+]\s+", "- ", cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r"^\d+\.\s+", "1. ", cleaned, flags=re.MULTILINE)
        
        # Normalize code blocks
        cleaned = re.sub(r"```\s*\n", "```\n", cleaned)
        cleaned = re.sub(r"\n\s*```", "\n```", cleaned)
        
        # Normalize inline code
        cleaned = re.sub(r"`\s+", "`", cleaned)
        cleaned = re.sub(r"\s+`", "`", cleaned)
        
        return cleaned.strip()

    def extract_headings(self) -> list[str]:
        """
        Wyodrębnia nagłówki z treści Markdown
        
        Returns:
            Lista nagłówków
        """
        headings = []
        
        # Znajdź wszystkie nagłówki (# do ######)
        for line in self.markdown.split('\n'):
            match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if match:
                headings.append(match.group(2).strip())
                
        return headings 