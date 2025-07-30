from typing import Optional, Dict, Any, List
from bs4 import BeautifulSoup
from dataclasses import dataclass

from .enum.language import Language
from .enum.fetch_type import FetchType
from .service.openai_service import OpenAIService
from .service.brightdata_service import BrightDataService
from .service.content_cleaner.html_cleaner import HtmlCleaner
from .service.content_cleaner.markdown_cleaner import MarkdownCleaner
from .service.content_cleaner.content_cleaner_factory import ContentCleanerFactory

@dataclass
class CrawlResult:
    """Struktura wyników crawlowania"""
    url: str
    content: str
    headers: Dict[str, str]
    status_code: int
    error: Optional[str] = None

class CrawlToolkit:
    """Główna klasa pakietu do crawlowania i analizy treści"""
    
    def __init__(
        self,
        brightdata_serp_key: str,
        brightdata_serp_zone: str,
        brightdata_crawl_key: str,
        brightdata_crawl_zone: str,
        openai_key: str,
        helpful_ai_instructions: str = ''
    ):
        """
        Inicjalizacja CrawlToolkit
        
        Args:
            brightdata_serp_key: Klucz API BrightData SERP
            brightdata_serp_zone: Strefa BrightData SERP
            brightdata_crawl_key: Klucz API BrightData Crawler
            brightdata_crawl_zone: Strefa BrightData Crawler
            openai_key: Klucz API OpenAI
            helpful_ai_instructions: Dodatkowe instrukcje dla AI
        """

        if not all([brightdata_serp_key, brightdata_serp_zone, 
                   brightdata_crawl_key, brightdata_crawl_zone, openai_key]):
            raise RuntimeError('Wszystkie klucze API i strefy muszą być podane.')

        self.brightdata_service = BrightDataService(
            bright_data_serp_key=brightdata_serp_key,
            bright_data_serp_zone=brightdata_serp_zone,
            bright_data_crawl_key=brightdata_crawl_key,
            bright_data_crawl_zone=brightdata_crawl_zone
        )
        self.openai_service = OpenAIService(openai_key)
        self.helpful_ai_instructions = helpful_ai_instructions

    async def get_top_urls(
        self,
        keyword: str,
        max_results: int = 20,
        language: Language = Language.ENGLISH
    ) -> List[str]:
        """
        Pobiera najlepsze URL-e z Google dla danego słowa kluczowego
        
        Args:
            keyword: Słowo kluczowe
            max_results: Maksymalna liczba wyników
            language: Język wyników
            
        Returns:
            Lista URL-i
        """
        try:
            return await self.brightdata_service.get_top_urls(
                keyword,
                max_results,
                language.get_country_code()
            )
        except Exception as e:
            raise RuntimeError(f'Błąd podczas pobierania najlepszych URL-i: {str(e)}')

    async def analyze_text(
        self,
        keyword: str,
        texts: List[Dict[str, str]],
        language: Language = Language.ENGLISH
    ) -> Dict[str, Any]:
        """
        Analizuje tekst używając OpenAI
        
        Args:
            keyword: Słowo kluczowe do analizy
            texts: Lista tekstów w formacie [{'url': str, 'content': str}]
            language: Język analizy
            
        Returns:
            Wyniki analizy
        """
        try:
            return await self.openai_service.analyze_keyword(
                keyword,
                texts,
                language.value,
                self.helpful_ai_instructions
            )
        except Exception as e:
            raise RuntimeError(f'Błąd podczas analizy tekstu: {str(e)}')

    async def clean_content(self, content: str, content_type: str = "html", url: str = None) -> str:
        """
        Czyści treść na podstawie typu (html, markdown, crawl4ai)
        Args:
            content: Treść do wyczyszczenia
            content_type: Typ treści ('html', 'markdown', 'crawl4ai')
            url: (opcjonalnie) URL źródłowy
        Returns:
            Wyczyszczona treść
        """
        if content_type == "crawl4ai":
            from crawl_toolkit.service.content_cleaner.crawl4ai_cleaner import Crawl4AICleaner
            cleaner = Crawl4AICleaner(content, url)
            return await cleaner.clean()
        elif content_type == "markdown":
            return MarkdownCleaner(content).clean()
        else:
            return HtmlCleaner(content).clean()

    async def fetch_and_clean_urls(
        self,
        urls: List[str],
        strategy: str = "classic"  # "classic", "crawl4ai", "markdown"
    ) -> List[Dict[str, Optional[str]]]:
        """
        Pobiera i czyści treść z podanych URL-i zgodnie ze strategią
        Args:
            urls: Lista URL-i do pobrania
            strategy: "classic" (HtmlCleaner), "crawl4ai" (Crawl4AICleaner), "markdown" (MarkdownCleaner)
        Returns:
            Lista wyników w formacie [{'url': str, 'content': Optional[str]}]
        """
        if not urls:
            raise RuntimeError('Lista URL-i nie może być pusta')

        result = []
        for url in urls:
            try:
                fetch_type = FetchType.HTML if strategy in ["classic", "crawl4ai"] else FetchType.MARKDOWN
                content = await self.brightdata_service.fetch_url(url, fetch_type)
                if not content:
                    raise RuntimeError(f'Błąd podczas pobierania URL: {url}')
            except Exception:
                result.append({'url': url, 'content': None})
                continue

            cleaned_content = await self.clean_content(
                content,
                content_type=strategy if strategy != "classic" else "html",
                url=url
            )
            result.append({'url': url, 'content': cleaned_content})

        return result

    async def process_connection_phrase_to_content(
        self,
        phrase: str,
        content: str,
        language: Language = Language.ENGLISH
    ) -> Dict[str, Any]:
        """
        Przetwarza frazę połączeniową na podstawie treści
        
        Args:
            phrase: Fraza połączeniowa
            content: Treść do analizy
            language: Język treści
            
        Returns:
            Wyniki przetwarzania
        """
        phrase = phrase.strip()
        phrase = phrase.replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')
        phrase = phrase.encode('utf-8').decode('utf-8')

        try:
            return await self.openai_service.extract_phrase_content(
                phrase,
                content,
                language.value,
                self.helpful_ai_instructions
            )
        except Exception as e:
            raise RuntimeError(f'Błąd podczas przetwarzania frazy połączeniowej: {str(e)}')

    async def get_headers_from_urls(
        self,
        urls: List[str],
        fetch_type: FetchType = FetchType.HTML
    ) -> List[Dict[str, Any]]:
        """
        Pobiera nagłówki z podanych URL-i
        
        Args:
            urls: Lista URL-i
            fetch_type: Typ pobieranej treści
            
        Returns:
            Lista nagłówków w formacie [{'url': str, 'headings': List[str]}]
        """
        if not urls:
            raise RuntimeError('Lista URL-i nie może być pusta')

        contents = await self.fetch_and_clean_urls(urls, fetch_type)

        if not contents:
            raise RuntimeError('Nie pobrano treści z podanych URL-i')

        result = []
        cleaner_factory = ContentCleanerFactory()
        
        for content in contents:
            if not content['content']:
                continue

            cleaner = cleaner_factory.create(fetch_type, content['content'])
            headings = cleaner.extract_headings()

            result.append({
                'url': content['url'],
                'headings': headings
            })

        return result

    async def make_keyword_analysis(
            self,
            keyword: str,
            max_urls: int = 20,
            language: Language = Language.ENGLISH
    ) -> Dict[str, Any]:
        """
        Performs comprehensive keyword analysis, matching the PHP logic.
        """
        keyword = keyword.strip()
        keyword = keyword.replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')
        keyword = keyword.encode('utf-8').decode('utf-8')

        try:
            result = []
            urls = await self.brightdata_service.get_top_urls(
                keyword,
                max_urls,
                language.get_country_code()
            )

            while urls and len(result) < max_urls:
                url = urls.pop(0)
                if url is None:
                    break

                try:
                    content = await self.fetch_url_content(url, FetchType.MARKDOWN)
                except Exception:
                    continue

                if not content:
                    continue

                cleaned_content = MarkdownCleaner(content).clean()
                extracted_content = await self.openai_service.extract_phrase_content(
                    keyword,
                    cleaned_content,
                    language.value,
                    self.helpful_ai_instructions
                )

                if extracted_content:
                    result.append({
                        'url': url,
                        'content': extracted_content
                    })

            return await self.openai_service.analyze_keyword(
                keyword,
                result,
                language.value,
                self.helpful_ai_instructions
            )

        except Exception as e:
            raise RuntimeError(f'Error during keyword analysis: {str(e)}')

    async def make_keyword_analysis_and_headers(
        self,
        keyword: str,
        max_urls: int = 20,
        language: Language = Language.ENGLISH
    ) -> Dict[str, Any]:
        """
        Wykonuje kompleksową analizę słowa kluczowego wraz z nagłówkami
        
        Args:
            keyword: Słowo kluczowe do analizy
            max_urls: Maksymalna liczba URL-i do przetworzenia
            language: Język analizy
            
        Returns:
            Wyniki analizy wraz z nagłówkami
        """
        keyword = keyword.strip()
        keyword = keyword.replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')
        keyword = keyword.encode('utf-8').decode('utf-8')

        try:
            result = []
            urls = await self.brightdata_service.get_top_urls(
                keyword,
                max_urls,
                language.get_country_code()
            )

            while urls and len(result) < max_urls:
                url = urls.pop(0)
                if not url:
                    break

                try:
                    content = await self.brightdata_service.fetch_url(url, FetchType.MARKDOWN)
                    if not content:
                        continue
                except Exception:
                    continue

                content = content.encode('utf-8').decode('utf-8')
                cleaner = MarkdownCleaner(content)
                headings = cleaner.extract_headings()
                cleaned_content = cleaner.clean()

                extracted_content = await self.openai_service.extract_phrase_content(
                    keyword,
                    cleaned_content,
                    language.value,
                    self.helpful_ai_instructions
                )

                result.append({
                    'url': url,
                    'content': extracted_content,
                    'headings': headings
                })

            return {
                'analysis': await self.openai_service.analyze_keyword(
                    keyword,
                    result,
                    language.value,
                    self.helpful_ai_instructions
                ),
                'results': result
            }

        except Exception as e:
            raise RuntimeError(f'Błąd podczas analizy słowa kluczowego: {str(e)}')

    async def get_headers_for_keyword(
        self,
        keyword: str,
        max_urls: int = 20,
        language: Language = Language.ENGLISH
    ) -> List[Dict[str, Any]]:
        """
        Pobiera nagłówki dla danego słowa kluczowego
        
        Args:
            keyword: Słowo kluczowe
            max_urls: Maksymalna liczba URL-i
            language: Język analizy
            
        Returns:
            Lista nagłówków
        """
        try:
            urls = await self.brightdata_service.get_top_urls(
                keyword,
                max_urls,
                language.get_country_code()
            )
            return await self.get_headers_from_urls(urls)
        except Exception as e:
            raise RuntimeError(f'Błąd podczas pobierania nagłówków dla słowa kluczowego: {str(e)}')

    async def fetch_url_content(
        self,
        url: str,
        fetch_type: FetchType = FetchType.HTML
    ) -> Optional[str]:
        """
        Pobiera treść z podanego URL
        
        Args:
            url: URL do pobrania
            fetch_type: Typ pobieranej treści
            
        Returns:
            Pobrana treść lub None w przypadku błędu
        """
        try:
            return await self.brightdata_service.fetch_url(url, fetch_type)
        except Exception as e:
            raise RuntimeError(f'Błąd podczas pobierania treści z URL: {str(e)}')

    async def make_keywords_from_content(
        self,
        keyword: str,
        url: str,
        content: str,
        language: Language = Language.ENGLISH
    ) -> Dict[str, Any]:
        """
        Tworzy słowa kluczowe z treści
        
        Args:
            keyword: Słowo kluczowe do analizy
            url: URL treści
            content: Treść do analizy
            language: Język analizy
            
        Returns:
            Wyniki analizy
        """
        try:
            extracted_content = await self.openai_service.extract_phrase_content(
                keyword,
                content,
                language.value,
                self.helpful_ai_instructions
            )

            if not extracted_content:
                raise RuntimeError(f'Nie wyodrębniono treści dla słowa kluczowego: {keyword}')

            return await self.openai_service.analyze_keyword(
                keyword,
                [{'url': url, 'content': extracted_content}],
                language.value,
                self.helpful_ai_instructions
            )

        except Exception as e:
            raise RuntimeError(f'Błąd podczas tworzenia słów kluczowych z treści: {str(e)}')

    async def make_keywords_from_contents(
        self,
        keyword: str,
        contents: List[Dict[str, str]],
        language: Language = Language.ENGLISH
    ) -> Dict[str, Any]:
        """
        Tworzy słowa kluczowe z wielu treści
        
        Args:
            keyword: Słowo kluczowe do analizy
            contents: Lista treści w formacie [{'url': str, 'content': str}]
            language: Język analizy
            
        Returns:
            Wyniki analizy
        """
        if not contents:
            raise RuntimeError('Lista treści nie może być pusta')

        try:
            extracted_contents = []
            for content in contents:
                if not content.get('content'):
                    continue

                extracted_content = await self.openai_service.extract_phrase_content(
                    keyword,
                    content['content'],
                    language.value,
                    self.helpful_ai_instructions
                )

                if extracted_content:
                    extracted_contents.append({
                        'url': content['url'],
                        'content': extracted_content
                    })

            if not extracted_contents:
                raise RuntimeError(f'Nie wyodrębniono prawidłowych treści dla słowa kluczowego: {keyword}')

            return await self.openai_service.analyze_keyword(
                keyword,
                extracted_contents,
                language.value,
                self.helpful_ai_instructions
            )

        except Exception as e:
            raise RuntimeError(f'Błąd podczas tworzenia słów kluczowych z treści: {str(e)}')

    @staticmethod
    def get_available_languages() -> List[str]:
        """
        Zwraca listę dostępnych języków
        
        Returns:
            Lista dostępnych języków
        """
        return Language.get_available_languages()

    async def analyze_content(
        self,
        content: str,
        analysis_type: str = "general",
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Analyze content using OpenAI API.
        
        Args:
            content: Content to analyze
            analysis_type: Type of analysis to perform
            max_tokens: Maximum tokens for OpenAI response
            
        Returns:
            Analysis results
        """
        prompt = self._get_analysis_prompt(analysis_type)
        
        response = await self.openai_service.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": content}
            ],
            max_tokens=max_tokens
        )
        
        return {
            "analysis": response.choices[0].message.content,
            "usage": response.usage.dict()
        }
        
    def _get_analysis_prompt(self, analysis_type: str) -> str:
        """Get the appropriate prompt for the analysis type."""
        prompts = {
            "general": "Analyze the following content and provide key insights:",
            "seo": "Analyze the following content for SEO optimization opportunities:",
            "sentiment": "Analyze the sentiment of the following content:",
            "keywords": "Extract and analyze key keywords from the following content:"
        }
        return prompts.get(analysis_type, prompts["general"])
        
    async def extract_links(self, content: str) -> List[str]:
        """Extract all links from HTML content."""
        soup = BeautifulSoup(content, "lxml")
        return [a.get("href") for a in soup.find_all("a", href=True)]
        
    async def extract_text(self, content: str) -> str:
        """Extract clean text from HTML content."""
        soup = BeautifulSoup(content, "lxml")
        return soup.get_text(separator=" ", strip=True) 