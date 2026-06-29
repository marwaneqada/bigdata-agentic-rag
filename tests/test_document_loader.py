from pathlib import Path

from src.document_loader import is_indexable_document, split_text


def test_split_text_creates_multiple_chunks() -> None:
    text = "\n\n".join(
        [
            "Airflow orchestre les pipelines Big Data. " * 20,
            "HDFS stocke les blocs sur les DataNodes. " * 20,
        ]
    )

    chunks = split_text(text, chunk_size=300, overlap=50)

    assert len(chunks) >= 3
    assert all(len(chunk) <= 300 for chunk in chunks)


def test_project_metadata_files_are_not_indexable() -> None:
    assert not is_indexable_document(Path("SOURCES.md"))
    assert not is_indexable_document(Path("README.md"))
    assert not is_indexable_document(Path("nested/README.txt"))
    assert not is_indexable_document(Path("A_LIRE_AVANT_ENVOI.txt"))
    assert is_indexable_document(Path("01_airflow.md"))
