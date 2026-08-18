from __future__ import annotations

import json
import logging
from pathlib import Path

import faiss
import numpy as np

from app.config import VECTORSTORE_PATH
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class VectorStoreService:
    def __init__(self, index_path: str | Path | None = None) -> None:
        self.index_path = Path(index_path) if index_path else Path(VECTORSTORE_PATH)
        self.index_path.mkdir(parents=True, exist_ok=True)
        self.metadata_path = self.index_path / "metadata.json"
        self.index_file = self.index_path / "faiss_index.index"
        self.embeddings = EmbeddingService()
        self.index: faiss.Index | None = None
        self.metadata: list[dict] = []
        self._load_or_create_index()

    def _load_or_create_index(self) -> None:
        if self.index_file.exists() and self.metadata_path.exists():
            logger.info("Loading existing FAISS index from %s", self.index_path)
            self.index = faiss.read_index(str(self.index_file))
            with self.metadata_path.open("r", encoding="utf-8") as handle:
                self.metadata = json.load(handle)
            return

        logger.info("Creating a new FAISS index at %s", self.index_path)
        self.index = faiss.IndexFlatL2(1536)
        self.metadata = []
        self.save_index()

    def create_index(self) -> None:
        self.index = faiss.IndexFlatL2(1536)
        self.metadata = []
        self.save_index()

    def is_document_processed(self, filename: str) -> bool:
        return any(item.get("source_filename") == filename for item in self.metadata)

    def add_documents(self, chunks: list[dict]) -> list[str]:
        if not chunks:
            return []

        existing_filenames = {item.get("source_filename") for item in self.metadata}
        new_chunks = [chunk for chunk in chunks if chunk.get("source_filename") not in existing_filenames]

        if not new_chunks:
            logger.info("Skipping embedding for already processed document chunks.")
            return []

        texts = [chunk["text"] for chunk in new_chunks]
        vectors = self.embeddings.embed_documents(texts)

        if self.index is None:
            raise ValueError("Vector index has not been initialized.")

        if not vectors:
            logger.warning("No vectors generated for incoming chunks.")
            return []

        vector_array = np.asarray(vectors, dtype="float32")
        self.index.add(vector_array)

        for chunk in new_chunks:
            self.metadata.append(
                {
                    "chunk_id": chunk["chunk_id"],
                    "source_filename": chunk["source_filename"],
                    "page_number": chunk["page_number"],
                    "text": chunk["text"],
                    "chunk_index": chunk.get("chunk_index", 0),
                }
            )

        self.save_index()
        logger.info("Added %s chunks to the vector index.", len(new_chunks))
        return [chunk["chunk_id"] for chunk in new_chunks]

    def save_index(self) -> None:
        if self.index is None:
            raise ValueError("Index is not initialized.")

        faiss.write_index(self.index, str(self.index_file))
        with self.metadata_path.open("w", encoding="utf-8") as handle:
            json.dump(self.metadata, handle, ensure_ascii=False, indent=2)
        logger.info("Saved FAISS index and metadata to %s", self.index_path)

    def load_index(self) -> None:
        self._load_or_create_index()

    def list_documents(self) -> list[dict]:
        unique_docs: dict[str, dict] = {}
        for item in self.metadata:
            filename = item.get("source_filename")
            if filename:
                unique_docs.setdefault(filename, {"filename": filename, "chunks": 0})
                unique_docs[filename]["chunks"] += 1

        return [
            {"filename": value["filename"], "chunk_count": value["chunks"]}
            for value in sorted(unique_docs.values(), key=lambda item: item["filename"])
        ]

    def delete_document(self, filename: str) -> bool:
        if not self.metadata:
            return False

        remaining = [item for item in self.metadata if item.get("source_filename") != filename]
        if len(remaining) == len(self.metadata):
            logger.info("No matching document found for removal: %s", filename)
            return False

        self.metadata = remaining

        if not self.metadata:
            self.index = faiss.IndexFlatL2(1536)
            self.save_index()
            logger.info("Removed the final document and reset the FAISS index.")
            return True

        texts = [item["text"] for item in self.metadata]
        vectors = self.embeddings.embed_documents(texts)
        new_index = faiss.IndexFlatL2(1536)
        if vectors:
            new_index.add(np.asarray(vectors, dtype="float32"))
        self.index = new_index
        self.save_index()
        logger.info("Removed document %s and rebuilt the FAISS index.", filename)
        return True
