from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any

import chromadb
import numpy as np
from sentence_transformers import SentenceTransformer

from src.config import get_settings


@dataclass(frozen=True)
class RetrievedDocument:
    text: str
    source: str
    page: int
    distance: float
    chunk_index: int

    @property
    def relevance(self) -> float:
        return max(0.0, min(1.0, 1.0 - self.distance))

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "source": self.source,
            "page": self.page,
            "distance": self.distance,
            "relevance": self.relevance,
            "chunk_index": self.chunk_index,
        }


class VectorStore:
    def __init__(self) -> None:
        settings = get_settings()
        settings.chroma_path.mkdir(parents=True, exist_ok=True)

        self._settings = settings
        self._client = chromadb.PersistentClient(path=str(settings.chroma_path))
        self._collection = self._client.get_or_create_collection(
            name=settings.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        self._model = SentenceTransformer(settings.embedding_model)

    @property
    def count(self) -> int:
        return self._collection.count()

    def reset(self) -> None:
        try:
            self._client.delete_collection(self._settings.collection_name)
        except Exception:
            pass

        self._collection = self._client.get_or_create_collection(
            name=self._settings.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(self, chunks: list) -> None:
        if not chunks:
            return

        texts = [chunk.text for chunk in chunks]
        embeddings = self._model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

        batch_size = 64
        for start in range(0, len(chunks), batch_size):
            batch = chunks[start : start + batch_size]
            batch_embeddings = embeddings[start : start + batch_size]

            self._collection.upsert(
                ids=[chunk.id for chunk in batch],
                documents=[chunk.text for chunk in batch],
                embeddings=np.asarray(batch_embeddings).tolist(),
                metadatas=[
                    {
                        "source": chunk.source,
                        "page": int(chunk.page),
                        "chunk_index": int(chunk.chunk_index),
                        "document_type": chunk.document_type,
                    }
                    for chunk in batch
                ],
            )

    def search(self, query: str, top_k: int | None = None) -> list[RetrievedDocument]:
        if self.count == 0:
            return []

        limit = top_k or self._settings.top_k
        vector = self._model.encode(
            [query],
            normalize_embeddings=True,
            show_progress_bar=False,
        )[0]

        result = self._collection.query(
            query_embeddings=[np.asarray(vector).tolist()],
            n_results=min(limit, self.count),
            include=["documents", "metadatas", "distances"],
        )

        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        output: list[RetrievedDocument] = []
        for text, metadata, distance in zip(documents, metadatas, distances):
            metadata = metadata or {}
            output.append(
                RetrievedDocument(
                    text=text or "",
                    source=str(metadata.get("source", "source inconnue")),
                    page=int(metadata.get("page", 1)),
                    distance=float(distance),
                    chunk_index=int(metadata.get("chunk_index", 0)),
                )
            )
        return output


@lru_cache(maxsize=1)
def get_vector_store() -> VectorStore:
    return VectorStore()
