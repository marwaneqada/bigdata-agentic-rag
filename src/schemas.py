from __future__ import annotations

from typing import Annotated, Literal, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


RouteName = Literal["retrieve", "compare", "calculate"]


class AgentState(TypedDict, total=False):
    messages: Annotated[list[AnyMessage], add_messages]
    question: str
    effective_query: str
    route: RouteName
    route_reason: str
    retrieved_documents: list[dict]
    sources: list[str]
    tool_output: str
    relevance_score: float
    relevance_reason: str
    rewrite_count: int
    generation_attempt: int
    answer: str
    grounded: bool
    verification_score: float
    verification_reason: str
    unsupported_claims: list[str]
    response_started_at: float
    response_time: float
    status: str


class RouteDecision(BaseModel):
    route: RouteName = Field(
        description=(
            "retrieve for factual course questions, compare for explicit technology comparisons, "
            "calculate for numerical storage/replication calculations"
        )
    )
    reason: str


class RelevanceDecision(BaseModel):
    relevant: bool
    score: int = Field(ge=0, le=5)
    reason: str


class VerificationDecision(BaseModel):
    grounded: bool
    score: int = Field(ge=0, le=5)
    reason: str
    unsupported_claims: list[str] = Field(default_factory=list)


class QueryRewrite(BaseModel):
    rewritten_query: str
    reason: str


class ComparisonRequest(BaseModel):
    technology_a: str
    technology_b: str
    focus: str = "rôle, fonctionnement, avantages, limites et cas d'utilisation"


class StorageRequest(BaseModel):
    data_size_gb: float = Field(gt=0)
    replication_factor: int = Field(default=1, ge=1)
    number_of_copies: int = Field(default=1, ge=1)
    compression_ratio: float = Field(
        default=1.0,
        gt=0,
        description="1.0 means no compression; 0.5 means data becomes half its original size",
    )


class EvaluationDecision(BaseModel):
    answer_quality: int = Field(ge=1, le=5)
    document_relevance: int = Field(ge=1, le=5)
    groundedness: int = Field(ge=1, le=5)
    comments: str
