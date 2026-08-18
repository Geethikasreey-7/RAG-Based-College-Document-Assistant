from __future__ import annotations

import logging
import time
from dataclasses import dataclass

import numpy as np

from app.config import RELEVANCE_THRESHOLD, TOP_K
from app.services.embedding_service import EmbeddingService
from app.services.vectorstore_service import VectorStoreService

logger = logging.getLogger(__name__)


@dataclass
class RetrievedChunk:
    chunk_id: str
    text: str
    relevance_score: float
    source_filename: str
    page_number: int


class RetrievalService:
    def __init__(self, top_k: int = TOP_K, relevance_threshold: float = RELEVANCE_THRESHOLD) -> None:
        if top_k <= 0:
            raise ValueError("top_k must be greater than 0")
        if not (0.0 <= relevance_threshold <= 1.0):
            raise ValueError("relevance_threshold must be between 0.0 and 1.0")

        self.top_k = top_k
        self.relevance_threshold = relevance_threshold
        self.embeddings = EmbeddingService()
        self.vector_store = VectorStoreService()

    def search(self, query: str) -> list[RetrievedChunk]:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        if not self.vector_store.metadata:
            raise ValueError("No documents have been uploaded to the vector database.")

        logger.info("Searching for query: %s", query)
        start_time = time.perf_counter()

        try:
            query_vector = self.embeddings.embed_query(query)
        except Exception as exc:
            logger.exception("Failed to embed query")
            raise ValueError("Failed to embed the query. Check that OPENAI_API_KEY is set correctly.") from exc

        embedding_elapsed = time.perf_counter() - start_time
        logger.info("Embedding time for query: %.3f seconds", embedding_elapsed)

        if self.vector_store.index is None:
            raise ValueError("Vector index is not initialized.")

        query_array = np.asarray([query_vector], dtype="float32")
        fetch_k = min(max(self.top_k * 3, self.top_k), len(self.vector_store.metadata))
        distances, indices = self.vector_store.index.search(query_array, fetch_k)

        if indices is None or len(indices) == 0:
            logger.info("No results found for query: %s", query)
            return []

        results: list[RetrievedChunk] = []
        seen_chunk_ids: set[str] = set()
        score_log: list[float] = []

        for idx in indices[0]:
            if idx < 0 or idx >= len(self.vector_store.metadata):
                continue

            metadata = self.vector_store.metadata[idx]
            chunk_id = metadata["chunk_id"]
            if chunk_id in seen_chunk_ids:
                continue
            seen_chunk_ids.add(chunk_id)

            distance = float(distances[0][list(indices[0]).tolist().index(idx)]) if idx in indices[0].tolist() else float("inf")
            relevance_score = self._distance_to_relevance(distance)
            score_log.append(relevance_score)

            if relevance_score < self.relevance_threshold:
                logger.debug(
                    "Filtering out low-relevance chunk %s with score %.4f < %.4f",
                    chunk_id,
                    relevance_score,
                    self.relevance_threshold,
                )
                continue

            results.append(
                RetrievedChunk(
                    chunk_id=chunk_id,
                    text=metadata["text"],
                    relevance_score=relevance_score,
                    source_filename=metadata["source_filename"],
                    page_number=metadata["page_number"],
                )
            )

        results.sort(key=lambda item: item.relevance_score, reverse=True)
        retrieval_elapsed = time.perf_counter() - start_time
        logger.info(
            "Query '%s' retrieved %s chunks in %.3f seconds; relevance scores: %s",
            query,
            len(results),
            retrieval_elapsed,
            [round(item.relevance_score, 4) for item in results],
        )

        return results[: self.top_k]

    def _distance_to_relevance(self, distance: float) -> float:
        if not np.isfinite(distance):
            return 0.0
        return float(max(0.0, min(1.0, 1.0 / (1.0 + distance / 10.0))))
