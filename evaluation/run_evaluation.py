from __future__ import annotations

import json
import time
import uuid
from pathlib import Path

import pandas as pd

from src.config import get_settings
from src.evaluator import evaluate_answer
from src.graph import get_graph, initial_state


def context_from_result(result: dict) -> str:
    parts = []
    for item in result.get("retrieved_documents", [])[:5]:
        parts.append(
            f"{item.get('source')} p.{item.get('page')}:\n{item.get('text', '')}"
        )
    return "\n\n".join(parts)


def main() -> None:
    root = get_settings().project_root
    questions = json.loads(
        (root / "evaluation" / "questions.json").read_text(encoding="utf-8")
    )
    graph = get_graph()
    rows: list[dict] = []

    output_dir = root / "results"
    output_dir.mkdir(parents=True, exist_ok=True)

    for item in questions:
        question = item["question"]
        print(f"[{item['id']}] {question}")

        started = time.perf_counter()
        result = graph.invoke(
            initial_state(question),
            config={
                "configurable": {
                    "thread_id": f"evaluation-{item['id']}-{uuid.uuid4()}",
                }
            },
        )
        elapsed = time.perf_counter() - started

        context = context_from_result(result)

        try:
            judgement = evaluate_answer(
                question=question,
                expected_topics=item["expected_topics"],
                answer=result.get("answer", ""),
                context=context,
            )
            quality = judgement.answer_quality
            relevance = judgement.document_relevance
            groundedness = judgement.groundedness
            comments = judgement.comments
        except Exception as exc:
            quality = None
            relevance = round(result.get("relevance_score", 0) * 5, 2)
            groundedness = round(result.get("verification_score", 0) * 5, 2)
            comments = f"Évaluation LLM indisponible : {exc}"

        rows.append(
            {
                "id": item["id"],
                "type": item["type"],
                "question": question,
                "route": result.get("route"),
                "answer": result.get("answer"),
                "response_time_seconds": round(elapsed, 3),
                "retrieved_sources": " | ".join(result.get("sources", [])),
                "retrieval_relevance_0_1": result.get("relevance_score"),
                "verification_0_1": result.get("verification_score"),
                "answer_quality_1_5": quality,
                "document_relevance_1_5": relevance,
                "groundedness_1_5": groundedness,
                "evaluation_comments": comments,
            }
        )

    dataframe = pd.DataFrame(rows)
    csv_path = output_dir / "evaluation_results.csv"
    dataframe.to_csv(csv_path, index=False, encoding="utf-8-sig")

    summary = {
        "questions": len(dataframe),
        "simple_questions": int((dataframe["type"] == "simple").sum()),
        "complex_questions": int((dataframe["type"] == "complex").sum()),
        "average_response_time_seconds": round(
            dataframe["response_time_seconds"].mean(), 3
        ),
        "average_answer_quality_1_5": (
            round(dataframe["answer_quality_1_5"].dropna().mean(), 3)
            if dataframe["answer_quality_1_5"].notna().any()
            else None
        ),
        "average_document_relevance_1_5": (
            round(dataframe["document_relevance_1_5"].dropna().mean(), 3)
            if dataframe["document_relevance_1_5"].notna().any()
            else None
        ),
        "average_groundedness_1_5": (
            round(dataframe["groundedness_1_5"].dropna().mean(), 3)
            if dataframe["groundedness_1_5"].notna().any()
            else None
        ),
    }

    (output_dir / "evaluation_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Résultats : {csv_path}")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
