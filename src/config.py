from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    project_root: Path
    documents_dir: Path
    chroma_path: Path
    collection_name: str
    embedding_model: str
    groq_model: str
    top_k: int
    max_rewrites: int

    @property
    def groq_api_key(self) -> str:
        return os.getenv("GROQ_API_KEY", "").strip()

    @property
    def has_groq_key(self) -> bool:
        key = self.groq_api_key
        return bool(key and not key.startswith("gsk_your") and "PASTE" not in key)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    chroma_value = os.getenv("CHROMA_PATH", "storage/chroma")
    chroma_path = Path(chroma_value)
    if not chroma_path.is_absolute():
        chroma_path = PROJECT_ROOT / chroma_path

    return Settings(
        project_root=PROJECT_ROOT,
        documents_dir=PROJECT_ROOT / "documents",
        chroma_path=chroma_path,
        collection_name=os.getenv("CHROMA_COLLECTION", "bigdata_course"),
        embedding_model=os.getenv(
            "EMBEDDING_MODEL",
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        ),
        groq_model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        top_k=max(1, int(os.getenv("TOP_K", "5"))),
        max_rewrites=max(0, int(os.getenv("MAX_REWRITES", "2"))),
    )
