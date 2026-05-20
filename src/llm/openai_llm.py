from typing import List, Optional, Dict, Any
from .base import BaseLLM, SubtitleItem, RewriteResult, LLMPromptBuilder
import os


class OpenAILLM(BaseLLM):
    def __init__(self, api_key: Optional[str] = None, model: str = 'gpt-3.5-turbo', 
                 base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        self.base_url = base_url
        self.prompt_builder = LLMPromptBuilder()
        self._client = None

    def _get_client(self):
        if self._client is None and self.api_key:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            except ImportError:
                return None
        return self._client

    def is_available(self) -> bool:
        return self._get_client() is not None and bool(self.api_key)

    def _call_llm(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.8) -> str:
        client = self._get_client()
        if client is None:
            return ""

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个专业的短视频解说文案改写专家。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content

    def rewrite(self, subtitles: List[SubtitleItem], style: str = 'commentary') -> List[RewriteResult]:
        if not subtitles:
            return []

        prompt = self.prompt_builder.build_rewrite_prompt(subtitles, style)
        rewritten_text = self._call_llm(prompt)
        
        if not rewritten_text:
            return [RewriteResult(
                original=sub.text,
                rewritten=sub.text,
                start=sub.start,
                end=sub.end
            ) for sub in subtitles]

        lines = [line.strip() for line in rewritten_text.split('\n') if line.strip()]
        results = []
        
        for i, line in enumerate(lines):
            if i < len(subtitles):
                results.append(RewriteResult(
                    original=subtitles[i].text,
                    rewritten=line,
                    start=subtitles[i].start,
                    end=subtitles[i].end
                ))
        
        return results

    def generate_commentary(self, topic: str, duration: float, style: str = 'exciting') -> str:
        prompt = self.prompt_builder.build_commentary_prompt(topic, duration, style)
        return self._call_llm(prompt, max_tokens=int(duration * 10))


class DeepSeekLLM(BaseLLM):
    def __init__(self, api_key: Optional[str] = None, model: str = 'deepseek-chat'):
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        self.model = model
        self.base_url = "https://api.deepseek.com"
        self.prompt_builder = LLMPromptBuilder()
        self._client = None

    def _get_client(self):
        if self._client is None and self.api_key:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            except ImportError:
                return None
        return self._client

    def is_available(self) -> bool:
        return self._get_client() is not None and bool(self.api_key)

    def _call_llm(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.8) -> str:
        client = self._get_client()
        if client is None:
            return ""

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个专业的短视频解说文案改写专家。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content

    def rewrite(self, subtitles: List[SubtitleItem], style: str = 'commentary') -> List[RewriteResult]:
        if not subtitles:
            return []

        prompt = self.prompt_builder.build_rewrite_prompt(subtitles, style)
        rewritten_text = self._call_llm(prompt)
        
        if not rewritten_text:
            return [RewriteResult(
                original=sub.text,
                rewritten=sub.text,
                start=sub.start,
                end=sub.end
            ) for sub in subtitles]

        lines = [line.strip() for line in rewritten_text.split('\n') if line.strip()]
        results = []
        
        for i, line in enumerate(lines):
            if i < len(subtitles):
                results.append(RewriteResult(
                    original=subtitles[i].text,
                    rewritten=line,
                    start=subtitles[i].start,
                    end=subtitles[i].end
                ))
        
        return results

    def generate_commentary(self, topic: str, duration: float, style: str = 'exciting') -> str:
        prompt = self.prompt_builder.build_commentary_prompt(topic, duration, style)
        return self._call_llm(prompt, max_tokens=int(duration * 10))


class OpenRouterLLM(BaseLLM):
    def __init__(self, api_key: Optional[str] = None, model: str = 'openai/gpt-3.5-turbo'):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"
        self.prompt_builder = LLMPromptBuilder()
        self._client = None

    def _get_client(self):
        if self._client is None and self.api_key:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            except ImportError:
                return None
        return self._client

    def is_available(self) -> bool:
        return self._get_client() is not None and bool(self.api_key)

    def _call_llm(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.8) -> str:
        client = self._get_client()
        if client is None:
            return ""

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个专业的短视频解说文案改写专家。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content

    def rewrite(self, subtitles: List[SubtitleItem], style: str = 'commentary') -> List[RewriteResult]:
        if not subtitles:
            return []

        prompt = self.prompt_builder.build_rewrite_prompt(subtitles, style)
        rewritten_text = self._call_llm(prompt)
        
        if not rewritten_text:
            return [RewriteResult(
                original=sub.text,
                rewritten=sub.text,
                start=sub.start,
                end=sub.end
            ) for sub in subtitles]

        lines = [line.strip() for line in rewritten_text.split('\n') if line.strip()]
        results = []
        
        for i, line in enumerate(lines):
            if i < len(subtitles):
                results.append(RewriteResult(
                    original=subtitles[i].text,
                    rewritten=line,
                    start=subtitles[i].start,
                    end=subtitles[i].end
                ))
        
        return results

    def generate_commentary(self, topic: str, duration: float, style: str = 'exciting') -> str:
        prompt = self.prompt_builder.build_commentary_prompt(topic, duration, style)
        return self._call_llm(prompt, max_tokens=int(duration * 10))