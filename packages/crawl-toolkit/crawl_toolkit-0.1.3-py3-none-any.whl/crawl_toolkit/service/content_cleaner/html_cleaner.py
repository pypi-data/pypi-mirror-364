from typing import List, Optional
import re
from bs4 import BeautifulSoup
from .abstract_cleaner import AbstractContentCleaner
from crawl_toolkit.enum.language import Language

class HtmlCleaner(AbstractContentCleaner):
    """HTML content cleaner implementation."""
    
    def __init__(self, html: str):
        """
        Inicjalizacja cleaner'a HTML
        
        Args:
            html: Treść HTML do wyczyszczenia
        """
        self.html = html
        self.soup = BeautifulSoup(html, 'html.parser')
        self.removable_tags = [
            "script", "style", "meta", "link", "noscript",
            "iframe", "object", "embed", "applet"
        ]
        self.removable_attrs = [
            "onclick", "onload", "onerror", "onmouseover",
            "onmouseout", "onkeypress", "onkeydown", "onkeyup"
        ]
        
    def clean(self) -> str:
        """
        Czyści treść HTML
        
        Returns:
            Wyczyszczona treść
        """
        # Usuń skrypty i style
        for script in self.soup(["script", "style"]):
            script.decompose()

        # Usuń komentarze
        for comment in self.soup.find_all(text=lambda text: isinstance(text, str) and text.strip().startswith('<!--')):
            comment.extract()

        # Usuń puste elementy
        for element in self.soup.find_all():
            if not element.get_text(strip=True):
                element.decompose()

        # Usuń atrybuty
        for tag in self.soup.find_all(True):
            tag.attrs = {}

        # Pobierz tekst
        text = self.soup.get_text(separator='\n', strip=True)

        # Usuń puste linie
        text = re.sub(r'\n\s*\n', '\n', text)

        return text.strip()

    def extract_headings(self) -> list[str]:
        """
        Wyodrębnia nagłówki z treści HTML
        
        Returns:
            Lista nagłówków
        """
        headings = []
        for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            for heading in self.soup.find_all(tag):
                text = heading.get_text(strip=True)
                if text:
                    headings.append(text)
        return headings
        
    def extract_links(self, content: str) -> List[str]:
        """
        Extract links from HTML.
        
        Args:
            content: HTML content
            
        Returns:
            List of links
        """
        soup = BeautifulSoup(content, "lxml")
        links = []
        
        for a in soup.find_all("a", href=True):
            href = a.get("href")
            if href and not href.startswith(("#", "javascript:", "mailto:", "tel:")):
                links.append(href)
                
        return links
        
    def extract_images(self, content: str) -> List[str]:
        """
        Extract images from HTML.
        
        Args:
            content: HTML content
            
        Returns:
            List of image URLs
        """
        soup = BeautifulSoup(content, "lxml")
        images = []
        
        for img in soup.find_all("img", src=True):
            src = img.get("src")
            if src and not src.startswith(("data:", "javascript:")):
                images.append(src)
                
        return images
        
    def normalize(self, content: str) -> str:
        """
        Normalize HTML content.
        
        Args:
            content: HTML content to normalize
            
        Returns:
            Normalized HTML
        """
        # Clean first
        cleaned = self.clean()
        
        # Normalize whitespace
        cleaned = re.sub(r"\s+", " ", cleaned)
        
        # Normalize quotes
        cleaned = cleaned.replace('"', '"').replace('"', '"')
        cleaned = cleaned.replace(''', "'").replace(''', "'")
        
        # Normalize line endings
        cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
        
        return cleaned.strip() 