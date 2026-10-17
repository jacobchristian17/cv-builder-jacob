"""
LLM Module - Groq/OpenAI integration for intelligent text processing

HOW TO USE:
1. Set GROQ_API_KEY or OPENAI_API_KEY in .env file
2. Recommended: auto-selected client
   from modules.llm import get_llm_client
   client = get_llm_client()
   response = client.generate("Your prompt here")

3. Provider-specific:
   from modules.llm import GroqClient, OpenAIClient
   client = OpenAIClient()

MANUAL TEST:
   python modules/llm/manual_test.py
"""

from .factory import get_llm_client

__all__ = ['GroqClient', 'OpenAIClient', 'LLMProvider', 'get_llm_client']


def __getattr__(name):
    # Lazy-import provider-specific clients so a missing optional dependency
    # (e.g. the `groq` package when only using OpenAI) doesn't break imports.
    if name == 'GroqClient':
        from .groq_client import GroqClient
        return GroqClient
    if name == 'OpenAIClient':
        from .openai_client import OpenAIClient
        return OpenAIClient
    if name == 'LLMProvider':
        from .llm_provider import LLMProvider
        return LLMProvider
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
