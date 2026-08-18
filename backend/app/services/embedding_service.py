from __future__ import annotations

import logging

from langchain_openai import OpenAIEmbeddings

from app.config import OPENAI_API_KEY, OPENAI_MODEL

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self, model_name: str | None = None, api_key: str | None = None) -> None:
        self.model_name = model_name or OPENAI_MODEL
        self.api_key = api_key or OPENAI_API_KEY

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required for embeddings.")

        self.embeddings = OpenAIEmbeddings(model=self.model_name, openai_api_key=self.api_key)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        logger.info("Generating embeddings for %s document chunks.", len(texts))
        return self.embeddings.embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        if not text:
            raise ValueError("Query text cannot be empty.")

        logger.info("Generating embedding for a user query.")
        return self.embeddings.embed_query(text)
