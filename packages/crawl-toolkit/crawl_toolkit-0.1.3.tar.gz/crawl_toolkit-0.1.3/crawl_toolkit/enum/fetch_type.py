from enum import Enum

class FetchType(Enum):
    """Typ pobieranej treści"""
    HTML = "html"
    MARKDOWN = "markdown"
    PLAIN = "plain" 