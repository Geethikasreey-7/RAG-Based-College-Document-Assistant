# Testing guide

This project uses a lightweight test setup so the backend and frontend can be checked without relying on external services.

## Running tests

### Backend

```bash
cd backend
python -m pytest -q
```

### Frontend

```bash
cd frontend
npm test
```

## What is being tested

### Backend

- health checks
- PDF upload success and rejected uploads
- text extraction from PDFs
- chunking logic and metadata generation
- embedding service behavior
- vector store creation and metadata persistence
- semantic search behavior
- RAG response generation
- invalid empty-question requests
- missing-document cases
- invalid API payloads

### Frontend

- Chat input send behavior
- Enter-to-send keyboard interaction
- Source reference rendering

## External services that are mocked

The tests do not call the real OpenAI API. Instead, they mock external interactions in the following ways:

- `OpenAIEmbeddings` calls are replaced with in-memory fake responses
- `ChatOpenAI.invoke` is stubbed for RAG response tests
- PDF upload tests use local byte streams rather than live cloud storage
- UI tests mock the chat API callback behavior and validate component interactions only

No API keys are checked into the repository or exposed in test files.
