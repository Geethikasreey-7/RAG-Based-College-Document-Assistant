from __future__ import annotations

import logging
import time
from dataclasses import dataclass

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from app.config import CHAT_HISTORY_LIMIT, MAX_CONTEXT_CHARS, OPENAI_API_KEY, OPENAI_MODEL, TEMPERATURE, TOP_K
from app.services.retrieval_service import RetrievalService

logger = logging.getLogger(__name__)


@dataclass
class Source:
    filename: str
    page: int


@dataclass
class RAGResponse:
    answer: str
    sources: list[Source]


class RAGService:
    SYSTEM_PROMPT = """You are a careful document-grounded assistant.

Rules:
- Answer only from the document context supplied below.
- Use the conversation history only to resolve follow-up references such as "that", "this", "the second point", or "what about it".
- Treat conversation history as a clarification aid, not as a source of new facts.
- If the context does not contain enough relevant information, state that clearly and do not guess.
- Do not invent facts, names, numbers, dates, or claims that are not present in the context.
- If the answer is uncertain or incomplete, say: "I cannot answer this from the available document context because it does not contain enough information."
- Keep the answer concise but informative.
- Cite each answer with the document filename and page number when available.
- Prefer exact wording from the provided context when possible.

Document Context:
{context}

Conversation History (most recent messages only; use this to resolve follow-up references):
{history}

Answer the user's question using only the provided document context and the recent conversation history for clarification. If the available context is insufficient, say so directly. Include source citations in the final answer."""

    def __init__(
        self,
        model_name: str | None = None,
        temperature: float | None = None,
        top_k: int | None = None,
        max_context_chars: int | None = None,
        max_history_messages: int | None = None,
    ) -> None:
        self.model_name = model_name or OPENAI_MODEL
        self.temperature = temperature if temperature is not None else TEMPERATURE
        self.top_k = top_k or TOP_K
        self.max_context_chars = max_context_chars or MAX_CONTEXT_CHARS
        self.max_history_messages = max_history_messages or CHAT_HISTORY_LIMIT

        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required for RAG.")

        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            openai_api_key=OPENAI_API_KEY,
        )
        self.retrieval = RetrievalService(top_k=self.top_k)

    def generate(self, question: str, conversation_history: list[dict] | None = None) -> RAGResponse:
        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        logger.info("Starting RAG generation for question: %s", question)
        recent_history = self._limit_history(conversation_history or [])

        try:
            start_time = time.perf_counter()
            retrieved_chunks = self.retrieval.search(question)
            retrieval_elapsed = time.perf_counter() - start_time
            logger.info("Retrieval completed in %.3f seconds for query: %s", retrieval_elapsed, question)
        except ValueError as exc:
            logger.exception("Retrieval failed for query: %s", question)
            raise ValueError(f"Retrieval error: {exc}") from exc

        if not retrieved_chunks:
            logger.warning("No relevant documents found for question: %s", question)
            answer = "I cannot answer this from the available document context because it does not contain enough information."
            return RAGResponse(answer=answer, sources=[])

        clean_chunks = self._prepare_context(retrieved_chunks)
        if not clean_chunks:
            logger.warning("Retrieved chunks were filtered out before generation for query: %s", question)
            answer = "I cannot answer this from the available document context because it does not contain enough information."
            return RAGResponse(answer=answer, sources=[])

        context = self._build_context(clean_chunks)
        history_text = self._build_history(recent_history)
        logger.info("Built LLM context from %s chunks and %s characters; included %s history messages", len(clean_chunks), len(context), len(recent_history))

        try:
            generation_start = time.perf_counter()
            answer = self._call_llm(question, context, history_text)
            generation_elapsed = time.perf_counter() - generation_start
            logger.info("LLM response generated in %.3f seconds for query: %s", generation_elapsed, question)
        except Exception as exc:
            logger.exception("LLM call failed for query: %s", question)
            raise ValueError(f"Failed to generate answer: {exc}") from exc

        sources = self._extract_sources(clean_chunks)
        final_answer = self._append_sources(answer, sources)
        logger.info("Generated answer with %s unique sources for query: %s", len(sources), question)

        return RAGResponse(answer=final_answer, sources=sources)

    def _limit_history(self, history: list[dict]) -> list[dict]:
        if not history:
            return []
        return history[-self.max_history_messages :]

    def _build_history(self, history: list[dict]) -> str:
        if not history:
            return "No recent conversation history."

        lines = []
        for message in history:
            role = message.get("role", "user")
            content = message.get("content", "").strip()
            if not content:
                continue
            lines.append(f"{role.title()}: {content}")

        return "\n".join(lines)

    def _prepare_context(self, chunks: list) -> list:
        unique_chunks: list = []
        seen_ids: set[str] = set()
        total_chars = 0

        for chunk in sorted(chunks, key=lambda item: item.relevance_score, reverse=True):
            if chunk.chunk_id in seen_ids:
                continue
            seen_ids.add(chunk.chunk_id)

            context_entry = self._format_chunk(chunk, len(unique_chunks) + 1)
            if total_chars + len(context_entry) > self.max_context_chars:
                logger.info(
                    "Stopping context build when limit reached for chunk %s: %s characters used",
                    chunk.chunk_id,
                    total_chars,
                )
                break

            unique_chunks.append(chunk)
            total_chars += len(context_entry)

        return unique_chunks

    def _format_chunk(self, chunk, index: int) -> str:
        return (
            f"[Document {index}] (Source: {chunk.source_filename}, Page {chunk.page_number})\n"
            f"{chunk.text}"
        )

    def _build_context(self, chunks: list) -> str:
        context_parts = [self._format_chunk(chunk, i + 1) for i, chunk in enumerate(chunks)]
        return "\n\n".join(context_parts)

    def _call_llm(self, question: str, context: str, history_text: str) -> str:
        system_prompt = self.SYSTEM_PROMPT.format(context=context, history=history_text)
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=question),
        ]

        logger.debug("Calling LLM with context length %s and history length %s", len(context), len(history_text))
        response = self.llm.invoke(messages)
        return response.content

    def _extract_sources(self, chunks: list) -> list[Source]:
        unique_sources: dict[tuple[str, int], Source] = {}
        for chunk in chunks:
            key = (chunk.source_filename, chunk.page_number)
            if key not in unique_sources:
                unique_sources[key] = Source(filename=chunk.source_filename, page=chunk.page_number)
        return sorted(unique_sources.values(), key=lambda s: (s.filename, s.page))

    def _append_sources(self, answer: str, sources: list[Source]) -> str:
        cleaned_answer = answer.strip()
        if not sources:
            return cleaned_answer

        source_lines = [f"- {source.filename} — Page {source.page}" for source in sources]
        return f"{cleaned_answer}\n\nSources:\n" + "\n".join(source_lines)
