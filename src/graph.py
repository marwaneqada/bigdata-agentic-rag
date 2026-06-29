from __future__ import annotations

import time
from functools import lru_cache
from typing import Literal

from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph

try:
    from langgraph.checkpoint.memory import InMemorySaver
except ImportError:  # Compatibility with older LangGraph releases.
    from langgraph.checkpoint.memory import MemorySaver as InMemorySaver

from src.config import get_settings
from src.nodes import (
    calculate_storage,
    compare_technologies,
    fallback_answer,
    finalize_answer,
    generate_answer,
    grade_documents,
    retrieve_documents,
    rewrite_query,
    route_question,
    verify_answer,
)
from src.schemas import AgentState


def route_after_classification(
    state: AgentState,
) -> Literal["retrieve_documents", "compare_technologies", "calculate_storage"]:
    route = state.get("route", "retrieve")
    return {
        "retrieve": "retrieve_documents",
        "compare": "compare_technologies",
        "calculate": "calculate_storage",
    }[route]


def route_after_relevance(
    state: AgentState,
) -> Literal["generate_answer", "rewrite_query", "fallback_answer"]:
    relevant = state.get("status") == "documents_relevant"
    if relevant:
        return "generate_answer"

    if state.get("rewrite_count", 0) < get_settings().max_rewrites:
        return "rewrite_query"

    return "fallback_answer"


def route_after_verification(
    state: AgentState,
) -> Literal["generate_answer", "finalize_answer"]:
    if state.get("grounded", False):
        return "finalize_answer"

    if state.get("generation_attempt", 0) < 2:
        return "generate_answer"

    return "finalize_answer"


def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node("route_question", route_question)
    builder.add_node("retrieve_documents", retrieve_documents)
    builder.add_node("compare_technologies", compare_technologies)
    builder.add_node("calculate_storage", calculate_storage)
    builder.add_node("grade_documents", grade_documents)
    builder.add_node("rewrite_query", rewrite_query)
    builder.add_node("generate_answer", generate_answer)
    builder.add_node("verify_answer", verify_answer)
    builder.add_node("fallback_answer", fallback_answer)
    builder.add_node("finalize_answer", finalize_answer)

    builder.add_edge(START, "route_question")

    builder.add_conditional_edges(
        "route_question",
        route_after_classification,
        {
            "retrieve_documents": "retrieve_documents",
            "compare_technologies": "compare_technologies",
            "calculate_storage": "calculate_storage",
        },
    )

    builder.add_edge("retrieve_documents", "grade_documents")
    builder.add_edge("compare_technologies", "grade_documents")
    builder.add_edge("calculate_storage", "generate_answer")

    builder.add_conditional_edges(
        "grade_documents",
        route_after_relevance,
        {
            "generate_answer": "generate_answer",
            "rewrite_query": "rewrite_query",
            "fallback_answer": "fallback_answer",
        },
    )

    builder.add_edge("rewrite_query", "retrieve_documents")
    builder.add_edge("generate_answer", "verify_answer")

    builder.add_conditional_edges(
        "verify_answer",
        route_after_verification,
        {
            "generate_answer": "generate_answer",
            "finalize_answer": "finalize_answer",
        },
    )

    builder.add_edge("fallback_answer", "finalize_answer")
    builder.add_edge("finalize_answer", END)

    return builder


@lru_cache(maxsize=1)
def get_graph():
    checkpointer = InMemorySaver()
    return build_graph().compile(checkpointer=checkpointer)


def initial_state(question: str) -> AgentState:
    return {
        "messages": [HumanMessage(content=question)],
        "question": question,
        "response_started_at": time.perf_counter(),
        "status": "started",
    }
