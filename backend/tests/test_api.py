from __future__ import annotations

import io

import numpy as np
import pytest
from fastapi import status

from app.services.document_processor import DocumentProcessor
from app.services.embedding_service import EmbeddingService
from app.services.rag_service import RAGService
from app.services.retrieval_service import RetrievedChunk, RetrievalService
from app.services.vectorstore_service import VectorStoreService


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "ok"


def test_upload_pdf_success(client, monkeypatch):
    class FakeEmbeddings:
        def embed_documents(self, texts):
            return [[0.1] * 1536 for _ in texts]

        def embed_query(self, text):
            return [0.1] * 1536

    monkeypatch.setattr("app.services.embedding_service.OpenAIEmbeddings", lambda *args, **kwargs: FakeEmbeddings())

    def fake_process_pdf(self, file_path):
        return {
            "filename": "sample.pdf",
            "page_count": 1,
            "chunk_count": 2,
            "status": "processed",
            "chunks": [
                {"chunk_id": "sample.pdf-p1-c0000", "text": "The model processes PDF content.", "source_filename": "sample.pdf", "page_number": 1, "chunk_index": 0},
                {"chunk_id": "sample.pdf-p1-c0001", "text": "It stores it in the vector database.", "source_filename": "sample.pdf", "page_number": 1, "chunk_index": 1},
            ],
        }

    monkeypatch.setattr(DocumentProcessor, "process_pdf", fake_process_pdf)
    monkeypatch.setattr(VectorStoreService, "add_documents", lambda self, chunks: [chunk["chunk_id"] for chunk in chunks])

    response = client.post(
        "/api/documents/upload",
        files={"file": ("sample.pdf", io.BytesIO(b"%PDF-1.4\n...fake pdf data..."), "application/pdf")},
    )

    assert response.status_code == status.HTTP_200_OK
    payload = response.json()
    assert payload["filename"] == "sample.pdf"
    assert payload["status"] == "processed"
    assert payload["chunk_count"] == 2


def test_invalid_file_upload(client):
    response = client.post(
        "/api/documents/upload",
        files={"file": ("not_a_pdf.txt", io.BytesIO(b"hello world"), "text/plain")},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Only PDF files are allowed" in response.json()["detail"]


def test_text_extraction_and_chunking():
    processor = DocumentProcessor(chunk_size=20, chunk_overlap=5)
    raw_text = "  Hello   world\n\nThis   is   a test.  "
    cleaned = processor.clean_text(raw_text)
    chunks = processor.chunk_text(raw_text, source_filename="demo.pdf", page_number=2)

    assert cleaned.startswith("Hello world")
    assert chunks
    assert all("chunk_id" in chunk for chunk in chunks)
    assert all(chunk["source_filename"] == "demo.pdf" for chunk in chunks)
    assert all(chunk["page_number"] == 2 for chunk in chunks)
    assert any("Hello" in chunk["text"] for chunk in chunks)


def test_embedding_service_uses_fake_embeddings(monkeypatch):
    service = EmbeddingService(api_key="test-key")

    class StubEmbeddings:
        def embed_documents(self, texts):
            return [[float(len(text)) for _ in range(3)] for text in texts]

        def embed_query(self, text):
            return [1.0, 2.0, 3.0]

    monkeypatch.setattr(service, "embeddings", StubEmbeddings())

    assert service.embed_documents(["one", "two"]) == [[float(len("one")) for _ in range(3)], [float(len("two")) for _ in range(3)]]
    assert service.embed_query("hello") == [1.0, 2.0, 3.0]


def test_vectorstore_creation_and_add_documents(monkeypatch, tmp_path):
    monkeypatch.setattr(EmbeddingService, "embed_documents", lambda self, texts: [[0.1, 0.2, 0.3] for _ in texts])

    store = VectorStoreService(index_path=tmp_path / "vectorstore")
    chunks = [
        {"chunk_id": "a-1", "text": "alpha beta", "source_filename": "a.pdf", "page_number": 1, "chunk_index": 0},
        {"chunk_id": "a-2", "text": "gamma delta", "source_filename": "a.pdf", "page_number": 2, "chunk_index": 1},
    ]

    result = store.add_documents(chunks)
    assert result == ["a-1", "a-2"]
    assert len(store.metadata) == 2
    assert (tmp_path / "vectorstore" / "faiss_index.index").exists()


def test_semantic_search_uses_relevance_filter(tmp_path):
    class FakeIndex:
        def search(self, query_array, k):
            return np.array([[0.0, 0.5]]), np.array([[0, 1]])

    fake_store = VectorStoreService(index_path=tmp_path / "search_store")
    fake_store.metadata = [
        {"chunk_id": "doc-1", "text": "Alpha concept", "source_filename": "doc1.pdf", "page_number": 1},
        {"chunk_id": "doc-2", "text": "Beta concept", "source_filename": "doc2.pdf", "page_number": 2},
    ]
    fake_store.index = FakeIndex()

    service = RetrievalService(top_k=2, relevance_threshold=0.0)
    service.vector_store = fake_store
    service.embeddings = type("Stub", (), {"embed_query": lambda self, text: [1.0, 2.0]})()

    results = service.search("alpha")
    assert len(results) >= 1
    assert results[0].source_filename in {"doc1.pdf", "doc2.pdf"}


def test_rag_response_returns_answer_and_sources(monkeypatch):
    rag = object.__new__(RAGService)
    rag.model_name = "gpt-4o-mini"
    rag.temperature = 0.0
    rag.top_k = 3
    rag.max_context_chars = 5000
    rag.max_history_messages = 5
    rag.retrieval = type("StubRetrieval", (), {"search": lambda self, question: [RetrievedChunk(chunk_id="c1", text="The model uses retrieval to ground answers.", relevance_score=0.9, source_filename="guide.pdf", page_number=4)]})()
    rag.llm = type("StubLLM", (), {"invoke": lambda self, messages: type("Resp", (), {"content": "This answer is grounded in the document context."})()})()

    response = rag.generate("What does the model do?")
    assert "grounded" in response.answer.lower()
    assert response.sources[0].filename == "guide.pdf"
    assert response.sources[0].page == 4


def test_empty_question_returns_validation_error(client):
    response = client.post("/api/chat", json={"question": "   "})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_no_documents_available_for_search(client):
    response = client.post("/api/search", json={"query": "test query"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_invalid_api_requests(client):
    response = client.post("/api/conversations", json={"bad": "value"})
    assert response.status_code in {status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY}

    bad_chat = client.post("/api/chat", json={})
    assert bad_chat.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
