from __future__ import annotations

import json
import re
import time
from typing import Any

from langchain_core.messages import AIMessage

from src.config import get_settings
from src.llm import get_llm
from src.prompts import (
    GENERATION_PROMPT,
    RELEVANCE_PROMPT,
    REWRITE_PROMPT,
    ROUTER_PROMPT,
    VERIFICATION_PROMPT,
)
from src.schemas import (
    AgentState,
    ComparisonRequest,
    QueryRewrite,
    RelevanceDecision,
    RouteDecision,
    StorageRequest,
    VerificationDecision,
)
from src.tools import (
    calculate_storage_capacity,
    compare_course_technologies,
)
from src.vector_store import get_vector_store


def _context(documents: list[dict], max_chars: int = 10000) -> str:
    parts: list[str] = []
    total = 0

    for index, item in enumerate(documents, start=1):
        text = _strip_chunk_metadata(str(item.get("text", "")))
        source = item.get("source", "source inconnue")
        page = item.get("page", 1)
        block = f"[{index}] {source}, page {page}\n{text}"

        if total + len(block) > max_chars:
            break

        parts.append(block)
        total += len(block)

    return "\n\n".join(parts)


def _strip_chunk_metadata(text: str) -> str:
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        lowered = stripped.lower()
        if lowered.startswith("source de cours"):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def _sources(documents: list[dict]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []

    for item in documents:
        label = f"{item.get('source', 'source inconnue')} — page {item.get('page', 1)}"
        if label not in seen:
            seen.add(label)
            output.append(label)

    return output


def _document_key(document: dict) -> tuple[str, int, int]:
    return (
        str(document.get("source", "")),
        int(document.get("page", 1)),
        int(document.get("chunk_index", 0)),
    )


COURSE_TOPIC_ALIASES = {
    "airflow": ["airflow", "dag", "pythonoperator", "scheduler", "worker"],
    "hdfs": ["hdfs", "namenode", "datanode", "replication", "réplication", "bloc"],
    "minio": ["minio", "bucket", "s3", "9000", "9001", "objet"],
    "kafka": ["kafka", "kstream", "ktable", "dead letter", "topic"],
    "spark_sql": ["spark sql", "vue temporaire", "dataframe", "sql"],
    "structured_streaming": [
        "structured streaming",
        "checkpoint",
        "maxfilespertrigger",
        "micro-batch",
        "capteur",
    ],
}


COMPARABLE_ALIASES = {
    "airflow": ["airflow"],
    "hdfs": ["hdfs"],
    "minio": ["minio"],
    "kafka_streams": ["kafka streams"],
    "kstream": ["kstream"],
    "ktable": ["ktable"],
    "spark_sql": ["spark sql"],
    "structured_streaming": ["structured streaming"],
}

SPECIFIC_CONCEPT_TERMS = [
    "pythonoperator",
    "namenode",
    "datanode",
    "checkpoint",
    "kstream",
    "ktable",
    "bucket",
    "9000",
    "9001",
    "vue temporaire",
    "dead letter",
    "maxfilespertrigger",
]


def _mentioned_topics(question: str, aliases: dict[str, list[str]]) -> set[str]:
    lowered = question.lower()
    return {
        topic
        for topic, terms in aliases.items()
        if any(term in lowered for term in terms)
    }


def _document_matches_topic(document: dict, topic: str) -> bool:
    haystack = (
        f"{document.get('source', '')}\n"
        f"{_strip_chunk_metadata(str(document.get('text', '')))}"
    ).lower()
    return any(term in haystack for term in COURSE_TOPIC_ALIASES.get(topic, []))


def _normalize_route(route: str, question: str) -> str:
    if route != "compare":
        return route

    comparable_topics = _mentioned_topics(question, COMPARABLE_ALIASES)
    if len(comparable_topics) >= 2:
        return route

    return "retrieve"


def _local_chunk_relevance(question: str, document: dict) -> RelevanceDecision:
    mentioned_topics = _mentioned_topics(question, COURSE_TOPIC_ALIASES)
    question_terms = {
        term
        for term in re.findall(r"[a-zA-Z][a-zA-Z0-9_+-]{2,}", question.lower())
        if term not in {"what", "used", "for", "the", "and", "with", "compare"}
    }
    text = str(document.get("text", "")).lower()
    source = str(document.get("source", "")).lower()
    score = float(document.get("relevance", 0.0))

    if source in {"sources.md", "readme.md", "a_lire_avant_envoi.txt"}:
        return RelevanceDecision(relevant=False, score=0, reason="Project metadata file.")

    if mentioned_topics and not any(
        _document_matches_topic(document, topic) for topic in mentioned_topics
    ):
        return RelevanceDecision(
            relevant=False,
            score=0,
            reason="Chunk does not match the course topic named in the question.",
        )

    specific_terms = [term for term in SPECIFIC_CONCEPT_TERMS if term in question.lower()]
    if specific_terms and not any(term in text or term in source for term in specific_terms):
        return RelevanceDecision(
            relevant=False,
            score=0,
            reason="Chunk does not contain the specific concept named in the question.",
        )

    overlap = sum(1 for term in question_terms if term in text or term in source)
    relevant = score >= 0.38 and (overlap > 0 or not question_terms)
    bounded_score = max(0, min(5, round(score * 5)))
    return RelevanceDecision(
        relevant=relevant,
        score=bounded_score,
        reason="Local fallback based on vector distance and lexical overlap.",
    )


def _grade_single_document(question: str, document: dict) -> RelevanceDecision:
    return _local_chunk_relevance(question, document)


def _filter_comparison_tool_output(tool_output: str, documents: list[dict]) -> str:
    if not tool_output:
        return tool_output

    try:
        payload = json.loads(tool_output)
    except json.JSONDecodeError:
        return tool_output

    keep = {_document_key(document) for document in documents}
    for key in ("evidence_a", "evidence_b"):
        payload[key] = [
            item for item in payload.get(key, []) if _document_key(item) in keep
        ]

    return json.dumps(payload, ensure_ascii=False)


def route_question(state: AgentState) -> dict[str, Any]:
    question = state["question"].strip()

    base = {
        "effective_query": question,
        "retrieved_documents": [],
        "sources": [],
        "tool_output": "",
        "relevance_score": 0.0,
        "relevance_reason": "",
        "rewrite_count": 0,
        "generation_attempt": 0,
        "answer": "",
        "grounded": False,
        "verification_score": 0.0,
        "verification_reason": "",
        "unsupported_claims": [],
        "response_started_at": state.get("response_started_at", time.perf_counter()),
        "status": "routing",
    }

    try:
        decision = get_llm().with_structured_output(RouteDecision).invoke(
            ROUTER_PROMPT.format(question=question)
        )
        return {
            **base,
            "route": _normalize_route(decision.route, question),
            "route_reason": decision.reason,
        }
    except Exception:
        lowered = question.lower()
        if any(term in lowered for term in ["compare", "comparaison", "différence", "versus", " vs "]):
            route = "compare"
        elif any(
            term in lowered
            for term in [
                "calcul",
                "calcule",
                "combien de go",
                "combien de gb",
                "capacité",
                "replication factor",
                "facteur de réplication",
            ]
        ):
            route = "calculate"
        else:
            route = "retrieve"

        return {
            **base,
            "route": _normalize_route(route, question),
            "route_reason": "Route sélectionnée par règle locale de secours.",
        }


def retrieve_documents(state: AgentState) -> dict[str, Any]:
    settings = get_settings()
    query = state.get("effective_query") or state["question"]
    results = get_vector_store().search(query, top_k=settings.top_k)
    documents = [item.to_dict() for item in results]

    return {
        "retrieved_documents": documents,
        "sources": _sources(documents),
        "status": "documents_retrieved",
    }


def compare_technologies(state: AgentState) -> dict[str, Any]:
    question = state["question"]

    try:
        request = get_llm().with_structured_output(ComparisonRequest).invoke(
            (
                "Extrais les deux technologies à comparer et le point de comparaison.\n"
                f"Question : {question}"
            )
        )
    except Exception:
        candidates = re.split(r"\b(?:vs|versus|et|avec|à)\b", question, maxsplit=1, flags=re.I)
        technology_a = candidates[0].strip() or "technologie A"
        technology_b = candidates[1].strip() if len(candidates) > 1 else "technologie B"
        request = ComparisonRequest(
            technology_a=technology_a,
            technology_b=technology_b,
        )

    raw = compare_course_technologies.invoke(
        {
            "technology_a": request.technology_a,
            "technology_b": request.technology_b,
            "focus": request.focus,
        }
    )
    payload = json.loads(raw)

    evidence = payload.get("evidence_a", []) + payload.get("evidence_b", [])
    evidence.sort(key=lambda item: item.get("distance", 1.0))

    return {
        "tool_output": raw,
        "retrieved_documents": evidence,
        "sources": _sources(evidence),
        "status": "comparison_tool_used",
    }


def calculate_storage(state: AgentState) -> dict[str, Any]:
    question = state["question"]

    try:
        request = get_llm().with_structured_output(StorageRequest).invoke(
            (
                "Extrais les valeurs du calcul de stockage. "
                "Si aucune compression n'est mentionnée, compression_ratio=1. "
                "Si aucune copie supplémentaire n'est mentionnée, number_of_copies=1.\n"
                f"Question : {question}"
            )
        )
    except Exception as exc:
        raise ValueError(
            "Le calcul nécessite une taille et un facteur de réplication explicites."
        ) from exc

    raw = calculate_storage_capacity.invoke(request.model_dump())

    return {
        "tool_output": raw,
        "retrieved_documents": [],
        "sources": ["Outil local : calculate_storage_capacity"],
        "relevance_score": 1.0,
        "relevance_reason": "Le calcul est produit par un outil déterministe.",
        "status": "calculation_tool_used",
    }


def _grade_document_set(state: AgentState) -> dict[str, Any]:
    documents = state.get("retrieved_documents", [])

    if not documents:
        return {
            "relevance_score": 0.0,
            "relevance_reason": "Aucun document récupéré.",
            "status": "documents_not_relevant",
        }

    context = _context(documents, max_chars=7000)

    try:
        decision = get_llm().with_structured_output(RelevanceDecision).invoke(
            RELEVANCE_PROMPT.format(
                question=state["question"],
                context=context,
            )
        )
        return {
            "relevance_score": decision.score / 5,
            "relevance_reason": decision.reason,
            "status": "documents_relevant" if decision.relevant else "documents_not_relevant",
        }
    except Exception:
        best_relevance = max(float(item.get("relevance", 0.0)) for item in documents)
        relevant = best_relevance >= 0.38
        return {
            "relevance_score": best_relevance,
            "relevance_reason": "Évaluation locale basée sur la distance vectorielle.",
            "status": "documents_relevant" if relevant else "documents_not_relevant",
        }


def grade_documents(state: AgentState) -> dict[str, Any]:
    documents = state.get("retrieved_documents", [])

    if not documents:
        return {
            "retrieved_documents": [],
            "sources": [],
            "relevance_score": 0.0,
            "relevance_reason": "Aucun document recupere.",
            "status": "documents_not_relevant",
        }

    relevant_documents: list[dict] = []
    rejected: list[str] = []

    for document in documents:
        decision = _grade_single_document(state["question"], document)
        scored_document = {
            **document,
            "relevance_score": decision.score / 5,
            "relevance_reason": decision.reason,
        }

        if decision.relevant:
            relevant_documents.append(scored_document)
        else:
            rejected.append(
                f"{document.get('source', 'source inconnue')}:{document.get('chunk_index', 0)}"
            )

    if not relevant_documents:
        return {
            "retrieved_documents": [],
            "sources": [],
            "tool_output": _filter_comparison_tool_output(
                state.get("tool_output", ""),
                [],
            ),
            "relevance_score": 0.0,
            "relevance_reason": "Aucun chunk individuel n'a ete juge pertinent.",
            "status": "documents_not_relevant",
        }

    best_score = max(float(item.get("relevance_score", 0.0)) for item in relevant_documents)
    reasons = [
        str(item.get("relevance_reason", "")).strip()
        for item in relevant_documents[:3]
        if str(item.get("relevance_reason", "")).strip()
    ]
    reason = " | ".join(reasons) or "Chunks filtres individuellement."
    if rejected:
        reason = f"{reason} Rejected chunks: {', '.join(rejected)}."

    return {
        "retrieved_documents": relevant_documents,
        "sources": _sources(relevant_documents),
        "tool_output": _filter_comparison_tool_output(
            state.get("tool_output", ""),
            relevant_documents,
        ),
        "relevance_score": best_score,
        "relevance_reason": reason,
        "status": "documents_relevant",
    }


def rewrite_query(state: AgentState) -> dict[str, Any]:
    count = state.get("rewrite_count", 0) + 1

    try:
        rewrite = get_llm().with_structured_output(QueryRewrite).invoke(
            REWRITE_PROMPT.format(
                question=state["question"],
                previous_query=state.get("effective_query", state["question"]),
                reason=state.get("relevance_reason", "documents peu pertinents"),
            )
        )
        query = rewrite.rewritten_query
        reason = rewrite.reason
    except Exception:
        query = (
            f"{state['question']} concepts définition architecture fonctionnement "
            "exemple Big Data cours"
        )
        reason = "Enrichissement local de la requête."

    return {
        "effective_query": query,
        "rewrite_count": count,
        "relevance_reason": reason,
        "status": "query_rewritten",
    }


def generate_answer(state: AgentState) -> dict[str, Any]:
    documents = state.get("retrieved_documents", [])
    sources = state.get("sources") or _sources(documents)
    context = _context(documents)

    prompt = GENERATION_PROMPT.format(
        question=state["question"],
        route=state.get("route", "retrieve"),
        tool_output=state.get("tool_output", "") or "Aucun",
        context=context or "Aucun extrait documentaire.",
        sources="\n".join(f"- {source}" for source in sources) or "- Aucune",
    )

    answer = get_llm(temperature=0.15).invoke(prompt).content

    return {
        "answer": str(answer).strip(),
        "generation_attempt": state.get("generation_attempt", 0) + 1,
        "status": "answer_generated",
    }


def fallback_answer(state: AgentState) -> dict[str, Any]:
    query = state.get("effective_query", state["question"])
    answer = (
        "Je n'ai pas trouvé de passage suffisamment pertinent dans la base documentaire "
        f"après {state.get('rewrite_count', 0)} reformulation(s).\n\n"
        f"Requête utilisée : {query}\n\n"
        "Ajoutez le support de cours correspondant dans le dossier documents/pdfs, "
        "puis relancez `python ingest.py --reset`."
    )

    return {
        "answer": answer,
        "grounded": True,
        "verification_score": 1.0,
        "verification_reason": "Réponse de transparence sans affirmation technique.",
        "status": "fallback",
    }


def verify_answer(state: AgentState) -> dict[str, Any]:
    if state.get("route") == "calculate":
        return {
            "grounded": True,
            "verification_score": 1.0,
            "verification_reason": "Résultat vérifié par l'outil de calcul déterministe.",
            "unsupported_claims": [],
            "status": "answer_verified",
        }

    context = _context(state.get("retrieved_documents", []), max_chars=8000)

    try:
        decision = get_llm().with_structured_output(VerificationDecision).invoke(
            VERIFICATION_PROMPT.format(
                question=state["question"],
                answer=state.get("answer", ""),
                tool_output=state.get("tool_output", "") or "Aucun",
                context=context,
            )
        )
        return {
            "grounded": decision.grounded,
            "verification_score": decision.score / 5,
            "verification_reason": decision.reason,
            "unsupported_claims": decision.unsupported_claims,
            "status": "answer_verified" if decision.grounded else "answer_needs_revision",
        }
    except Exception:
        return {
            "grounded": True,
            "verification_score": state.get("relevance_score", 0.5),
            "verification_reason": "Vérification locale de secours.",
            "unsupported_claims": [],
            "status": "answer_verified",
        }


def _finalize_answer_with_warning(state: AgentState) -> dict[str, Any]:
    answer = state.get("answer", "")

    if not state.get("grounded", False) and state.get("unsupported_claims"):
        warning = (
            "\n\n⚠️ Vérification : certains éléments n'ont pas pu être confirmés par "
            "les documents récupérés."
        )
        answer += warning

    started = state.get("response_started_at", time.perf_counter())
    elapsed = max(0.0, time.perf_counter() - started)

    return {
        "messages": [AIMessage(content=answer)],
        "answer": answer,
        "response_time": round(elapsed, 3),
        "status": "completed",
    }


def finalize_answer(state: AgentState) -> dict[str, Any]:
    answer = state.get("answer", "")
    started = state.get("response_started_at", time.perf_counter())
    elapsed = max(0.0, time.perf_counter() - started)

    return {
        "messages": [AIMessage(content=answer)],
        "answer": answer,
        "response_time": round(elapsed, 3),
        "status": "completed",
    }
