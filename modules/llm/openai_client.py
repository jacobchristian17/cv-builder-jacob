import os
from typing import Optional, Dict, Any, List
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class OpenAIClient:
    """Drop-in replacement for GroqClient backed by the OpenAI API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.temperature = temperature if temperature is not None else float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        self.max_tokens = max_tokens if max_tokens is not None else int(os.getenv("OPENAI_MAX_TOKENS", "1000"))

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> str:
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature or self.temperature,
            max_tokens=max_tokens or self.max_tokens,
            stream=stream,
            store=False
        )

        if stream:
            return response

        return response.choices[0].message.content

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature or self.temperature,
            max_tokens=max_tokens or self.max_tokens,
            stream=stream,
            store=False
        )

        if stream:
            return response

        return response.choices[0].message.content

    def generate_with_retry(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_retries: int = 3,
        **kwargs
    ) -> Optional[str]:
        for attempt in range(max_retries):
            try:
                return self.generate(prompt, system_prompt, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                continue

        return None
