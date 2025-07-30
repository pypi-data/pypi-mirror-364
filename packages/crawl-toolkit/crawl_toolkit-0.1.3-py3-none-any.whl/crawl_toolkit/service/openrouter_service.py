from typing import Dict, Any, List, Optional
import aiohttp
from pydantic import BaseModel, Field

class OpenRouterService:
    """Service for handling OpenRouter API interactions."""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://openrouter.ai/api/v1"
    ):
        self.api_key = api_key
        self.base_url = base_url
        
    async def _make_request(
        self,
        endpoint: str,
        method: str = "POST",
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make request to OpenRouter API.
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            data: Request data
            headers: Custom headers
            
        Returns:
            API response
        """
        url = f"{self.base_url}/{endpoint}"
        
        default_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/patryk-samulewicz/crawl-toolkit"
        }
        if headers:
            default_headers.update(headers)
            
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method,
                url,
                json=data,
                headers=default_headers
            ) as response:
                return await response.json()
                
    async def generate_text(
        self,
        prompt: str,
        model: str = "anthropic/claude-3-opus",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 1.0,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate text using OpenRouter API.
        
        Args:
            prompt: Input prompt
            model: Model to use
            max_tokens: Maximum tokens to generate
            temperature: Response temperature
            top_p: Top p sampling
            stream: Whether to stream response
            
        Returns:
            Generated text
        """
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stream": stream
        }
        
        return await self._make_request("chat/completions", data=data)
        
    async def analyze_content(
        self,
        content: str,
        analysis_type: str = "general",
        model: str = "anthropic/claude-3-opus"
    ) -> Dict[str, Any]:
        """
        Analyze content using OpenRouter API.
        
        Args:
            content: Content to analyze
            analysis_type: Type of analysis
            model: Model to use
            
        Returns:
            Analysis results
        """
        prompts = {
            "general": "Analyze the following content and provide key insights:",
            "seo": "Analyze the following content for SEO optimization opportunities:",
            "sentiment": "Analyze the sentiment of the following content:",
            "keywords": "Extract and analyze key keywords from the following content:"
        }
        
        prompt = f"{prompts.get(analysis_type, prompts['general'])}\n\n{content}"
        
        return await self.generate_text(
            prompt=prompt,
            model=model,
            max_tokens=2000
        )
        
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get list of available models.
        
        Returns:
            List of available models
        """
        response = await self._make_request("models", method="GET")
        return response.get("data", [])
        
    async def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """
        Get information about specific model.
        
        Args:
            model_id: Model ID
            
        Returns:
            Model information
        """
        response = await self._make_request(f"models/{model_id}", method="GET")
        return response.get("data", {}) 