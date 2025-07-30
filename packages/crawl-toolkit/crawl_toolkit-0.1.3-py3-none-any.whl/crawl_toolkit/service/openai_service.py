import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI

class OpenAIService:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.variables = {
            'current_date': datetime.now().strftime('%Y-%m-%d')
        }
        prompts_dir = Path(__file__).parent.parent / 'prompts'
        self.GET_KEYWORDS_PROMPT = (prompts_dir / 'get_keywords_3.txt').read_text()
        self.EXTRACT_KEYWORD_CONNECTIONS_SYSTEM_PROMPT = (prompts_dir / 'extract_keyword_connections_system.txt').read_text()

    async def analyze_keyword(
        self,
        keyword: str,
        texts: List[Dict[str, str]],
        language: str = 'english',
        helpful_instructions: str = ''
    ) -> Dict[str, Any]:
        self.variables['keyword'] = keyword
        self.variables['language'] = language

        if helpful_instructions:
            self.variables['helpful_instructions'] = '### Helpful Instructions\n' + helpful_instructions + '\n'

        max_formatted_text_tokens = 50000
        formatted_texts = ''
        for idx, text in enumerate(texts):
            if not text.get('content'):
                continue
            formatted_texts += f"-----TEXT{idx+1}-----\n"
            formatted_texts += f"URL: {text['url']}\n"
            formatted_texts += "Content: " + json.dumps(
                text['content'],
                ensure_ascii=False
            ) + "\n"
            if self._calc_text_tokens(formatted_texts) >= max_formatted_text_tokens:
                break
        formatted_texts += "-----TEXT END-----\n"

        body = (
            f"\n- **Central Keyword**:\n{keyword}\n"
            f"- **Language**:\n{language}\n"
            f"- **Web Content Context**:\n{formatted_texts}"
        )
        body = self._clean_and_prepare_content(body)

        messages = [
            {"role": "system", "content": self.GET_KEYWORDS_PROMPT},
            {"role": "user", "content": body}
        ]

        response = await self._call_openai(
            messages,
            model='gpt-4.1-2025-04-14',
            temperature=0.7,
            max_tokens=16000
        )
        if response is None:
            return {}
        return self._response_json(response)

    async def extract_phrase_content(
        self,
        keyword: str,
        content: str,
        lang: str = 'english',
        helpful_instructions: str = ''
    ) -> Dict[str, Any]:
        self.variables['lang'] = lang
        self.variables['phrase'] = keyword

        if helpful_instructions:
            self.variables['helpful_instructions'] = '### Helpful Instructions\n' + helpful_instructions + '\n'

        prompt = self._replace_variables(self.EXTRACT_KEYWORD_CONNECTIONS_SYSTEM_PROMPT)
        content = self._clean_and_prepare_content(content)
        body = f"###Text to check \n{content}\n###TEXT END"

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": body}
        ]

        response = await self._call_openai(
            messages,
            model='gpt-4.1-2025-04-14',
            temperature=0.7,
            max_tokens=16000
        )
        if response is None:
            return {}
        return self._response_json(response)

    def _clean_and_prepare_content(self, content: str) -> str:
        # Normalize encoding
        content = content.encode('utf-8', errors='ignore').decode('utf-8')
        # Remove unsupported Unicode characters
        content = ''.join(char for char in content if ord(char) < 0xFFFF)
        # Filter control characters while preserving tabs and newlines
        return ''.join(char for char in content if char >= ' ' or char in '\t\n')

    def _replace_variables(self, prompt: str) -> str:
        def replace_var(match):
            var_name = match.group(1).strip()
            return self.variables.get(var_name, match.group(0))
        return re.sub(r'\[\[(.*?)\]\]', replace_var, prompt)

    def _calc_text_tokens(self, text: str) -> int:
        length = len(text.encode('utf-8'))
        if length == 0:
            return 0
        if length < 4:
            return 1
        return (length + 3) // 4

    async def _call_openai(
        self,
        messages: List[Dict[str, str]],
        model: str = 'gpt-4',
        temperature: float = 0.7,
        max_tokens: int = 10000
    ) -> Optional[str]:
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            if not response:
                raise RuntimeError('Empty response from OpenAI API')
            return response.choices[0].message.content
        except Exception as e:
            # Optionally, save messages for debugging as in PHP
            with open('test_messages_open_ai.txt', 'w', encoding='utf-8') as f:
                json.dump(messages, f, ensure_ascii=False, indent=2)
            raise RuntimeError(f'Error calling OpenAI API: {str(e)}')

    def _response_json(self, response: str) -> Dict[str, Any]:
        cleaned_response = response.strip()
        cleaned_response = re.sub(r'^```(json)?\s*|\s*```$', '', cleaned_response, flags=re.IGNORECASE)
        try:
            decoded_response = json.loads(cleaned_response)
            if isinstance(decoded_response, dict):
                return decoded_response
        except json.JSONDecodeError:
            pass
        return {}