from __future__ import annotations

import argparse

from src.config import get_settings
from src.document_loader import build_chunks, discover_documents
from src.vector_store import get_vector_store


def main() -> None:
    parser = argparse.ArgumentParser(description="Index course documents in Chroma.")
    parser.add_argument("--reset", action="store_true", help="Recreate the collection.")
    parser.add_argument("--chunk-size", type=int, default=900)
    parser.add_argument("--overlap", type=int, default=150)
    args = parser.parse_args()

    settings = get_settings()
    documents = discover_documents(settings.documents_dir)

    if not documents:
        raise SystemExit(
            "Aucun document trouvé. Ajoutez des PDF, MD ou TXT dans documents/."
        )

    chunks = build_chunks(
        documents,
        chunk_size=args.chunk_size,
        overlap=args.overlap,
    )

    store = get_vector_store()
    if args.reset:
        store.reset()

    store.add_chunks(chunks)

    source_names = sorted({document.source for document in documents})
    print(f"Documents/pages chargés : {len(documents)}")
    print(f"Chunks indexés : {len(chunks)}")
    print(f"Collection totale : {store.count}")
    print("Sources :")
    for source in source_names:
        print(f"- {source}")


if __name__ == "__main__":
    main()
