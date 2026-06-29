from __future__ import annotations

from functools import lru_cache

from langchain_groq import ChatGroq

from src.config import get_settings


@lru_cache(maxsize=1)
def get_llm(temperature: float = 0.0) -> ChatGroq:
    settings = get_settings()
    if not settings.has_groq_key:
        raise RuntimeError(
            "GROQ_API_KEY est absente. Copiez .env.example vers .env puis ajoutez votre clé."
        )

    return ChatGroq(
        model=settings.groq_model,
        temperature=temperature,
        api_key=settings.groq_api_key,
        max_retries=2,
        timeout=45,
    )
