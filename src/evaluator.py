from __future__ import annotations

from src.llm import get_llm
from src.schemas import EvaluationDecision


def evaluate_answer(
    *,
    question: str,
    expected_topics: list[str],
    answer: str,
    context: str,
) -> EvaluationDecision:
    prompt = f"""
Tu es un évaluateur strict d'un système RAG pédagogique.

Note de 1 à 5 :
- answer_quality : réponse correcte, complète et claire ;
- document_relevance : les documents récupérés sont utiles pour la question ;
- groundedness : la réponse est soutenue par le contexte.

Question :
{question}

Éléments attendus :
{", ".join(expected_topics)}

Réponse :
{answer}

Contexte récupéré :
{context}
"""
    return get_llm().with_structured_output(EvaluationDecision).invoke(prompt)
