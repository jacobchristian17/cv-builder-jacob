"""
LLM Module - Groq integration for intelligent text processing

HOW TO USE:
1. Set GROQ_API_KEY in .env file
2. Basic usage:
   from modules.llm import GroqClient
   client = GroqClient()
   response = client.generate("Your prompt here")

3. Provider pattern:
   from modules.llm import LLMProvider
   provider = GroqProvider()
   analysis = provider.analyze_resume(resume_text, job_text)

MANUAL TEST:
   python modules/llm/manual_test.py
"""

from .groq_client import GroqClient
from .llm_provider import LLMProvider

__all__ = ['GroqClient', 'LLMProvider']