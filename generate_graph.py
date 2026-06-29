from __future__ import annotations

from pathlib import Path

from src.config import get_settings
from src.graph import get_graph


def main() -> None:
    output_dir = get_settings().project_root / "results"
    output_dir.mkdir(parents=True, exist_ok=True)

    graph = get_graph()
    mermaid = graph.get_graph().draw_mermaid()
    mermaid_path = output_dir / "langgraph_workflow.mmd"
    mermaid_path.write_text(mermaid, encoding="utf-8")

    try:
        image = graph.get_graph().draw_mermaid_png()
        (output_dir / "langgraph_workflow.png").write_bytes(image)
        print("PNG généré : results/langgraph_workflow.png")
    except Exception as exc:
        print(f"PNG non généré automatiquement : {exc}")
        print("Le fichier Mermaid est disponible dans results/langgraph_workflow.mmd")

    print(f"Mermaid généré : {mermaid_path}")


if __name__ == "__main__":
    main()
