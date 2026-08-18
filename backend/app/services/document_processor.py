from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

from langchain.text_splitter import RecursiveCharacterTextSplitter
from pypdf import PdfReader

logger = logging.getLogger(__name__)


class DocumentProcessor:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")
        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be between 0 and chunk_size")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def load_pdf(self, file_path: str | Path) -> PdfReader:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {path}")
        if path.suffix.lower() != ".pdf":
            raise ValueError(f"Unsupported file type: {path.suffix}")

        try:
            return PdfReader(str(path))
        except Exception as exc:  # pragma: no cover - defensive guard
            logger.exception("Failed to open PDF: %s", path)
            raise ValueError(f"Invalid PDF file: {path.name}") from exc

    def clean_text(self, text: str) -> str:
        if not text:
            return ""

        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        normalized = normalized.replace("\t", " ")
        normalized = re.sub(r"(?m)^\s*[-*•]+\s*", "", normalized)
        normalized = re.sub(r"(?m)^Page\s+\d+\s*$", "", normalized, flags=re.IGNORECASE)
        normalized = re.sub(r"\n{3,}", "\n\n", normalized)
        normalized = normalized.replace("\u00a0", " ")
        normalized = re.sub(r"\s+", " ", normalized)
        normalized = re.sub(r"\s+([,.!?;:])", r"\1", normalized)
        normalized = re.sub(r"([,.!?;:])(?=[A-Za-z0-9])", r"\1 ", normalized)
        normalized = re.sub(r"\s+", " ", normalized)
        normalized = normalized.replace("\n ", " ").replace(" \n", " ")
        normalized = re.sub(r"\s+", " ", normalized)
        return normalized.strip()

    def chunk_text(
        self,
        text: str,
        source_filename: str,
        page_number: int,
    ) -> list[dict[str, Any]]:
        cleaned_text = self.clean_text(text)
        if not cleaned_text:
            return []

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""],
        )

        chunks: list[dict[str, Any]] = []
        for index, chunk in enumerate(splitter.split_text(cleaned_text)):
            cleaned_chunk = self.clean_text(chunk)
            if not cleaned_chunk:
                continue

            chunk_id = f"{source_filename}-p{page_number}-c{index:04d}"
            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "text": cleaned_chunk,
                    "source_filename": source_filename,
                    "page_number": page_number,
                    "chunk_index": index,
                    "metadata": {
                        "source_filename": source_filename,
                        "page_number": page_number,
                        "chunk_index": index,
                    },
                }
            )

        return chunks

    def process_pdf(self, file_path: str | Path) -> dict[str, Any]:
        path = Path(file_path)
        reader = self.load_pdf(path)
        total_pages = len(reader.pages)
        page_chunks: list[dict[str, Any]] = []

        for page_number, page in enumerate(reader.pages, start=1):
            try:
                raw_text = page.extract_text() or ""
            except Exception as exc:  # pragma: no cover - defensive guard
                logger.warning("Unable to extract text from page %s of %s: %s", page_number, path.name, exc)
                raw_text = ""

            if not raw_text.strip():
                logger.info("Skipping empty page %s in %s", page_number, path.name)
                continue

            cleaned_page_text = self.clean_text(raw_text)
            if not cleaned_page_text:
                logger.info("Skipping page %s in %s because it contains no readable content", page_number, path.name)
                continue

            page_chunks.extend(
                self.chunk_text(
                    text=cleaned_page_text,
                    source_filename=path.name,
                    page_number=page_number,
                )
            )

        if not page_chunks:
            raise ValueError(f"No readable text could be extracted from {path.name}")

        return {
            "filename": path.name,
            "page_count": total_pages,
            "chunk_count": len(page_chunks),
            "chunks": page_chunks,
            "status": "processed",
        }
