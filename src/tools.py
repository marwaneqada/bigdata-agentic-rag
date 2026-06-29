from __future__ import annotations

import json

from langchain_core.tools import tool

from src.config import get_settings
from src.vector_store import get_vector_store


@tool
def retrieve_course_documents(query: str, top_k: int = 5) -> str:
    """Search the Big Data and Cloud course knowledge base for relevant passages."""
    results = get_vector_store().search(query, top_k=top_k)
    return json.dumps(
        [result.to_dict() for result in results],
        ensure_ascii=False,
    )


@tool
def compare_course_technologies(
    technology_a: str,
    technology_b: str,
    focus: str = "rôle, fonctionnement, avantages, limites et cas d'utilisation",
) -> str:
    """Retrieve evidence to compare two Big Data or Cloud technologies."""
    store = get_vector_store()
    settings = get_settings()

    query_a = f"{technology_a} {focus}"
    query_b = f"{technology_b} {focus}"

    results_a = store.search(query_a, top_k=max(2, settings.top_k // 2 + 1))
    results_b = store.search(query_b, top_k=max(2, settings.top_k // 2 + 1))

    return json.dumps(
        {
            "technology_a": technology_a,
            "technology_b": technology_b,
            "focus": focus,
            "evidence_a": [item.to_dict() for item in results_a],
            "evidence_b": [item.to_dict() for item in results_b],
        },
        ensure_ascii=False,
    )


@tool
def calculate_storage_capacity(
    data_size_gb: float,
    replication_factor: int = 1,
    number_of_copies: int = 1,
    compression_ratio: float = 1.0,
) -> str:
    """Calculate physical storage after compression, replication and extra copies."""
    if data_size_gb <= 0:
        raise ValueError("data_size_gb must be positive")
    if replication_factor < 1 or number_of_copies < 1:
        raise ValueError("replication_factor and number_of_copies must be at least 1")
    if compression_ratio <= 0:
        raise ValueError("compression_ratio must be positive")

    compressed_gb = data_size_gb * compression_ratio
    replicated_gb = compressed_gb * replication_factor
    total_gb = replicated_gb * number_of_copies

    return json.dumps(
        {
            "logical_data_gb": round(data_size_gb, 3),
            "compression_ratio": round(compression_ratio, 3),
            "after_compression_gb": round(compressed_gb, 3),
            "replication_factor": replication_factor,
            "after_replication_gb": round(replicated_gb, 3),
            "number_of_copies": number_of_copies,
            "required_physical_storage_gb": round(total_gb, 3),
            "formula": (
                "data_size_gb × compression_ratio × replication_factor "
                "× number_of_copies"
            ),
        },
        ensure_ascii=False,
    )


TOOLS = [
    retrieve_course_documents,
    compare_course_technologies,
    calculate_storage_capacity,
]
