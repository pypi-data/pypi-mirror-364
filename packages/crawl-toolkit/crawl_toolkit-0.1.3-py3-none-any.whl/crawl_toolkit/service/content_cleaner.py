from typing import List, Optional
import re
from bs4 import BeautifulSoup
import html2text

class ContentCleaner:
    """Service for cleaning and normalizing content."""
    
    def __init__(self):
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = True
        
    def clean_html(self, html: str) -> str:
        """
        Clean HTML content.
        
        Args:
            html: HTML content to clean
            
        Returns:
            Cleaned HTML
        """
        soup = BeautifulSoup(html, "lxml")
        
        # Remove script and style elements
        for element in soup(["script", "style", "meta", "link"]):
            element.decompose()
            
        # Remove comments
        for comment in soup.find_all(text=lambda text: isinstance(text, str) and text.strip().startswith("<!--")):
            comment.extract()
            
        return str(soup)
        
    def html_to_text(self, html: str) -> str:
        """
        Convert HTML to clean text.
        
        Args:
            html: HTML content to convert
            
        Returns:
            Clean text
        """
        cleaned_html = self.clean_html(html)
        text = self.html_converter.handle(cleaned_html)
        return self.normalize_text(text)
        
    def normalize_text(self, text: str) -> str:
        """
        Normalize text content.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)
        
        # Remove special characters
        text = re.sub(r"[^\w\s.,!?-]", "", text)
        
        # Normalize whitespace
        text = text.strip()
        
        return text
        
    def extract_links(self, html: str) -> List[str]:
        """
        Extract all links from HTML.
        
        Args:
            html: HTML content
            
        Returns:
            List of links
        """
        soup = BeautifulSoup(html, "lxml")
        return [a.get("href") for a in soup.find_all("a", href=True)]
        
    def extract_images(self, html: str) -> List[str]:
        """
        Extract all image URLs from HTML.
        
        Args:
            html: HTML content
            
        Returns:
            List of image URLs
        """
        soup = BeautifulSoup(html, "lxml")
        return [img.get("src") for img in soup.find_all("img", src=True)]
        
    def remove_duplicates(self, text: str) -> str:
        """
        Remove duplicate lines from text.
        
        Args:
            text: Text content
            
        Returns:
            Text without duplicates
        """
        lines = text.split("\n")
        unique_lines = []
        seen = set()
        
        for line in lines:
            line = line.strip()
            if line and line not in seen:
                seen.add(line)
                unique_lines.append(line)
                
        return "\n".join(unique_lines) 