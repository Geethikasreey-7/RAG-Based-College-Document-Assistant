# Backend README

This folder contains the FastAPI backend for the RAG document chatbot.

## Structure

- `app/`: application package
- `data/documents/`: uploaded source documents
- `data/vectorstore/`: persistent vector database files

## Initial setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy the environment example:

```bash
copy .env.example .env
```

4. Fill in the required values, especially `OPENAI_API_KEY`.

## Run the API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Document ingestion flow

The document ingestion pipeline is handled by the backend service layer and exposed as a FastAPI upload endpoint.

1. A PDF is uploaded through `POST /api/documents/upload`.
2. The file is validated and saved to `backend/data/documents/`.
3. The PDF is opened with PyPDF and each page is read sequentially.
4. Empty pages are skipped, and invalid or unreadable PDFs raise an error response.
5. Text is normalized and cleaned to remove excessive whitespace and formatting noise.
6. The cleaned text is split into chunks using a configurable chunk size and overlap.
7. Each chunk is enriched with metadata: `source_filename`, `page_number`, and `chunk_id`.
8. The API responds with the processed filename, page count, chunk count, and status.

This scaffold now includes the ingestion foundation needed for the next RAG stages.
