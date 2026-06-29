from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import fitz


SUPPORTED_TEXT_EXTENSIONS = {".md", ".txt"}
EXCLUDED_DOCUMENT_NAMES = {
    "readme.md",
    "readme.txt",
    "sources.md",
    "a_lire_avant_envoi.txt",
}


@dataclass(frozen=True)
class SourceDocument:
    text: str
    source: str
    page: int
    document_type: str


@dataclass(frozen=True)
class TextChunk:
    id: str
    text: str
    source: str
    page: int
    chunk_index: int
    document_type: str


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def load_pdf(path: Path) -> list[SourceDocument]:
    output: list[SourceDocument] = []
    with fitz.open(path) as pdf:
        for page_index, page in enumerate(pdf):
            text = clean_text(page.get_text("text"))
            if text:
                output.append(
                    SourceDocument(
                        text=text,
                        source=path.name,
                        page=page_index + 1,
                        document_type="pdf",
                    )
                )
    return output


def load_text_file(path: Path) -> list[SourceDocument]:
    text = clean_text(path.read_text(encoding="utf-8", errors="ignore"))
    if not text:
        return []
    return [
        SourceDocument(
            text=text,
            source=path.name,
            page=1,
            document_type=path.suffix.lstrip("."),
        )
    ]


def is_indexable_document(path: Path) -> bool:
    name = path.name.lower()
    if name in EXCLUDED_DOCUMENT_NAMES:
        return False
    if name.startswith("readme."):
        return False
    return True


def discover_documents(documents_dir: Path) -> list[SourceDocument]:
    documents: list[SourceDocument] = []
    for path in sorted(documents_dir.rglob("*")):
        if not path.is_file():
            continue
        if not is_indexable_document(path):
            continue
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            documents.extend(load_pdf(path))
        elif suffix in SUPPORTED_TEXT_EXTENSIONS:
            documents.extend(load_text_file(path))
    return documents


def split_text(
    text: str,
    *,
    chunk_size: int = 900,
    overlap: int = 150,
) -> list[str]:
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")

    paragraphs = [item.strip() for item in re.split(r"\n\s*\n", text) if item.strip()]
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph

        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            chunks.append(current)

        if len(paragraph) <= chunk_size:
            current = paragraph
            continue

        start = 0
        while start < len(paragraph):
            end = min(len(paragraph), start + chunk_size)
            chunks.append(paragraph[start:end].strip())
            if end == len(paragraph):
                break
            start = max(start + 1, end - overlap)
        current = ""

    if current:
        chunks.append(current)

    return [chunk for chunk in chunks if len(chunk) >= 60]


def build_chunks(
    documents: Iterable[SourceDocument],
    *,
    chunk_size: int = 900,
    overlap: int = 150,
) -> list[TextChunk]:
    chunks: list[TextChunk] = []

    for document in documents:
        for index, text in enumerate(
            split_text(document.text, chunk_size=chunk_size, overlap=overlap)
        ):
            digest = hashlib.sha1(
                f"{document.source}:{document.page}:{index}:{text}".encode("utf-8")
            ).hexdigest()

            chunks.append(
                TextChunk(
                    id=digest,
                    text=text,
                    source=document.source,
                    page=document.page,
                    chunk_index=index,
                    document_type=document.document_type,
                )
            )

    return chunks
