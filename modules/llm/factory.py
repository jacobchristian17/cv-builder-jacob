import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

GROQ_MODEL_DEFAULT = "meta-llama/llama-4-scout-17b-16e-instruct"
OPENAI_MODEL_DEFAULT = "gpt-4o-mini"


def get_llm_client(
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    model: Optional[str] = None
):
    """
    Return an LLM client (GroqClient or OpenAIClient), auto-selected by which
    API key is available. Preference order: GROQ_API_KEY, then OPENAI_API_KEY.
    Set LLM_PROVIDER=openai (or groq) to force a specific provider.
    """
    provider = os.getenv("LLM_PROVIDER", "").strip().lower()

    if not provider:
        if os.getenv("GROQ_API_KEY"):
            provider = "groq"
        elif os.getenv("OPENAI_API_KEY"):
            provider = "openai"
        else:
            raise ValueError(
                "No LLM API key found. Set GROQ_API_KEY or OPENAI_API_KEY in your .env file."
            )

    if provider == "groq":
        from .groq_client import GroqClient
        return GroqClient(
            model=model or GROQ_MODEL_DEFAULT,
            temperature=temperature,
            max_tokens=max_tokens
        )
    elif provider == "openai":
        from .openai_client import OpenAIClient
        return OpenAIClient(
            model=model or OPENAI_MODEL_DEFAULT,
            temperature=temperature,
            max_tokens=max_tokens
        )
    else:
        raise ValueError(f"Unknown LLM_PROVIDER '{provider}'. Use 'groq' or 'openai'.")
