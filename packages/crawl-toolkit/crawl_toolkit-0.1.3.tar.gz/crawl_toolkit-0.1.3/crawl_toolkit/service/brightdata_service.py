from typing import Optional, List
import aiohttp
from urllib.parse import quote_plus
from enum import Enum
from crawl_toolkit.enum.fetch_type import FetchType
from crawl_toolkit.enum.language import Language

class BrightDataService:
    """Service class for interacting with BrightData API for web crawling and SERP data retrieval.
    
    This service provides functionality to fetch web content and search results using
    BrightData's API, supporting both HTML and Markdown formats.
    """
    
    API_URL = 'https://api.brightdata.com/request'
    
    def __init__(
        self,
        bright_data_serp_key: str,
        bright_data_serp_zone: str,
        bright_data_crawl_key: str,
        bright_data_crawl_zone: str
    ):
        """Initialize BrightDataService with required API keys and zones.
        
        Args:
            bright_data_serp_key: API key for BrightData SERP service
            bright_data_serp_zone: Zone for BrightData SERP service
            bright_data_crawl_key: API key for BrightData Crawler service
            bright_data_crawl_zone: Zone for BrightData Crawler service
        """
        self.bright_data_serp_key = bright_data_serp_key
        self.bright_data_serp_zone = bright_data_serp_zone
        self.bright_data_crawl_key = bright_data_crawl_key
        self.bright_data_crawl_zone = bright_data_crawl_zone
        
    async def fetch_url(self, url: str, fetch_type: FetchType = FetchType.HTML) -> Optional[str]:
        """Fetch content from a specified URL using BrightData's crawler service.
        
        Args:
            url: The URL to fetch content from
            fetch_type: The desired output format ('markdown' or 'html')
            
        Returns:
            The fetched content or None if the request fails
            
        Raises:
            RuntimeError: When an error occurs during the request
        """
        headers = {
            'Authorization': f'Bearer {self.bright_data_crawl_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'zone': self.bright_data_crawl_zone,
            'url': url,
            'format': 'raw'
        }
        
        if fetch_type == FetchType.MARKDOWN:
            payload['data_format'] = 'markdown'
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.API_URL,
                    json=payload,
                    headers=headers,
                    timeout=320
                ) as response:
                    if response.status == 200:
                        return await response.text()
                    return None
        except Exception as e:
            raise RuntimeError(f'Error fetching Brightdata: {str(e)}')
            
    async def get_top_urls(
        self,
        keyword: str,
        max_results: int = 20,
        country_code: str = 'pl',
        url: Optional[str] = None,
        collected_urls: List[str] = None
    ) -> List[str]:
        """Retrieves top URLs from Google search results for a given keyword.
        
        Args:
            keyword: The search keyword
            max_results: Maximum number of results to return (default: 20)
            country_code: Country code for localized results (default: 'pl')
            url: Custom search URL (optional)
            collected_urls: Previously collected URLs for pagination
            
        Returns:
            List of unique URLs from search results
            
        Raises:
            RuntimeError: When an error occurs during the request or processing
        """
        if collected_urls is None:
            collected_urls = []

        country_lang = Language.from_country_code(country_code)
        if country_lang is not None:
            country_code = country_lang.map_forbidden_lang_to_default().get_country_code()

        headers = {
            'Authorization': f'Bearer {self.bright_data_serp_key}',
            'Content-Type': 'application/json'
        }

        if url is None:
            url = f'https://www.google.com/search?q={quote_plus(keyword)}&gl={country_code}'
        url = self._ensure_brd_json(url)
            
        payload = {
            'zone': self.bright_data_serp_zone,
            'url': url,
            'format': 'raw',
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.API_URL,
                    json=payload,
                    headers=headers,
                    timeout=180
                ) as response:
                    if response.status != 200:
                        raise RuntimeError(f'Request failed with status code {response.status}')

                    if 'application/json' not in response.headers.get('Content-Type', ''):
                        text = await response.text()
                        raise RuntimeError(f'BrightData returned non-JSON response: {text}')
                    response_data = await response.json()
                    next_page_url = self._get_next_page_url(response_data)
                    
                    if not response_data.get('organic'):
                        if not next_page_url and collected_urls:
                            return collected_urls[:max_results]
                            
                        if next_page_url:
                            return await self.get_top_urls(
                                keyword,
                                max_results,
                                country_code,
                                next_page_url,
                                collected_urls
                            )
                            
                        raise RuntimeError('Unable to get top URLs')
                        
                    urls = collected_urls.copy()
                    for item in response_data.get('organic', []):
                        if 'link' in item:
                            urls.append(item['link'])
                            
                    urls = list(dict.fromkeys(urls))
                    
                    if len(urls) < max_results and next_page_url:
                        return await self.get_top_urls(
                            keyword,
                            max_results,
                            country_code,
                            next_page_url,
                            urls
                        )
                        
                    return urls[:max_results]
                    
        except Exception as e:
            raise RuntimeError(f'Error during get top URLs: {str(e)}')
            
    def _get_next_page_url(self, response_data: dict) -> Optional[str]:
        """Extract the next page URL from the search results response.
        
        Args:
            response_data: The decoded response data from BrightData
            
        Returns:
            The URL for the next page of results, or None if not available
        """
        if response_data.get('pagination', {}).get('next_page_link'):
            return response_data['pagination']['next_page_link']
        return None

    def _ensure_brd_json(self, url: str) -> str:
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        qs['brd_json'] = ['1']
        new_query = urlencode(qs, doseq=True)
        return urlunparse(parsed._replace(query=new_query))
