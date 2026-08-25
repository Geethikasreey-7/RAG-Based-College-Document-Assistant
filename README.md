# RAG Document Chatbot

This repository contains a production-style document chatbot built with a Python backend and a React frontend. The system is designed around a Retrieval-Augmented Generation (RAG) architecture where user questions are answered using relevant document chunks retrieved from a vector database before generating a response with an LLM.

## Architecture

- Backend: FastAPI + Python + LangChain + OpenAI + FAISS/ChromaDB
- Frontend: React + Vite + Axios
- Storage: Local document uploads and vector store persistence

## Project structure

```text
rag-document-chatbot/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/
│   │   │   └── routes/
│   │   ├── services/
│   │   ├── models/
│   │   └── utils/
│   ├── data/
│   │   ├── documents/
│   │   ├── vectorstore/
│   │   └── chat_history.db
│   ├── requirements.txt
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── App.jsx
│   ├── package.json
│   └── README.md
│
├── .gitignore
└── README.md
```

## Notes

- The project features a fully implemented RAG pipeline including document processing, OpenAI embeddings, FAISS vector store indexing, similarity retrieval, and LLM-powered answer generation.
- API keys and secrets are not hardcoded; they are configured through environment variables.
- The backend and frontend are separated to support easier scaling and clearer responsibilities.

## Document ingestion flow

The backend implements a modular document ingestion pipeline for PDF files.

PDF
↓
Text extraction
↓
Chunking
↓
Embedding model
↓
Vector embeddings
↓
FAISS vector database

1. PDF upload: a file is accepted through `POST /api/documents/upload` using multipart form data.
2. Text extraction: PyPDF reads each page and extracts raw text while handling empty pages and invalid files.
3. Cleaning: whitespace and formatting noise are normalized into consistent text blocks.
4. Chunking: text is split into overlapping chunks using configurable chunk size and overlap settings.
5. Embedding model: each cleaned chunk is converted into a vector using the OpenAI embedding model.
6. Vector embeddings: these numeric vectors capture semantic meaning and allow similarity matching between user questions and stored content.
7. FAISS vector database: the vectors and associated metadata are persisted in `backend/data/vectorstore/` for fast retrieval.

## Why vector embeddings are required in a RAG system

Vector embeddings are required because a large language model does not natively understand document similarity in the way a search system does. Embeddings convert text into high-dimensional numerical representations so the system can compare semantic similarity between a user question and stored document chunks. In a RAG pipeline, the chatbot retrieves the most relevant chunks by embedding both the query and the indexed content, then passes those chunks to the LLM to generate a grounded answer.

## Semantic search vs. keyword search

**Keyword search** looks for exact word matches or partial string overlap. If you search for "how to make coffee", it returns documents containing those exact words, but may miss documents about "brewing espresso" or "preparing a caffeine beverage."

**Semantic search** understands the meaning behind words. It embeds both your query and document chunks into vector space, then finds the closest vectors. A query for "how to make coffee" will retrieve chunks about brewing, preparation, espresso machines, and related concepts—even if those exact words don't appear.

Why semantic search is useful for RAG:
- **Intent matching**: understands what users really mean, not just keywords they typed
- **Paraphrasing**: finds similar content even when worded differently
- **Context awareness**: retrieves documents based on meaning rather than word overlap
- **Better LLM input**: the LLM receives contextually relevant chunks, leading to more accurate answers

Without semantic search, a keyword-based RAG system would miss relevant information and produce lower-quality answers.

## RAG generation pipeline

The RAG (Retrieval-Augmented Generation) pipeline combines retrieval and generation for accurate, grounded answers.

User Question
↓
Conversation History (recent messages only)
↓
Query Embedding
↓
FAISS Semantic Search
↓
Top-K Relevant Chunks
↓
Clean + Deduplicate Chunks
↓
Context Construction (document context separated from chat history)
↓
LLM Prompt with safe instructions
↓
LLM Response
↓
Answer + Sources

1. User asks a natural language question through the chat endpoint.
2. Recent conversation history can be included for follow-up references such as "the second point" or "what about it".
3. The question is embedded using the same OpenAI embedding model as the documents.
4. FAISS semantic search finds the most similar document chunks.
5. The top-K chunks are retrieved and ranked by relevance score.
6. Low-quality or duplicate chunks are filtered before they reach the LLM.
7. A bounded context string is built from the relevant document chunks with source attribution.
8. The prompt keeps document context and conversational history clearly separated to reduce hallucination.
9. OpenAI's chat model generates an answer based only on the provided context.
10. The response includes the answer text and a list of sources (filename, page number).

## Conversation history architecture

The chatbot now stores conversations in SQLite so users can continue previous threads without losing context.

- Conversations are created through `POST /api/conversations`
- Conversation metadata is read through `GET /api/conversations`
- Full conversation details are available at `GET /api/conversations/{conversation_id}`
- Messages are stored via `POST /api/conversations/{conversation_id}/messages`
- The frontend displays a list of previous conversations and lets a user open or start a new one
- Only a small recent slice of previous messages is included in the prompt, which keeps follow-up questions contextual without sending unlimited history to the model

## API endpoints

- `GET /health` - API health check
- `GET /api/documents` - List uploaded documents
- `POST /api/documents/upload` - Upload and process a PDF
- `DELETE /api/documents/{filename}` - Remove a document
- `POST /api/search` - Semantic search with natural language query
- `POST /api/chat` - RAG-based question answering with sources and optional conversation context
- `POST /api/conversations` - Create a new conversation
- `GET /api/conversations` - List conversations
- `GET /api/conversations/{conversation_id}` - Fetch full conversation details
- `POST /api/conversations/{conversation_id}/messages` - Save a user or assistant message
- `DELETE /api/conversations/{conversation_id}` - Delete a conversation and its messages

## What is Retrieval-Augmented Generation (RAG)?

RAG is an approach that combines document retrieval with language model generation. Instead of relying on the model's training data alone, RAG:
1. Retrieves relevant documents or chunks based on the user's question
2. Constructs a context from those documents
3. Passes the context to an LLM to generate an answer

This makes the chatbot:
- **Factual**: answers come from your actual documents, not from training data
- **Traceable**: every answer can be traced to specific source documents and pages
- **Up-to-date**: new documents are automatically indexed and immediately searchable
- **Controllable**: you control what documents the model can use

## Why RAG is better than sending an entire PDF to an LLM

**Sending the entire PDF:**
- Many LLMs have token limits (often 4k-8k tokens, sometimes more)
- Large PDFs quickly exceed these limits, causing truncation or errors
- The model wastes tokens on irrelevant content
- Processing time is longer, increasing latency and cost
- The model may lose important context due to length constraints

**Using RAG:**
- Only the most relevant chunks (typically 500-1000 tokens) are sent to the LLM
- The model focuses on relevant content, improving answer quality
- Faster response times and lower API costs
- Works with documents of any size
- Scales to thousands of documents without token limit issues
- Semantic search finds the right information, even in very long documents

## Running the application
 
### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
# Copy environment template and set your OPENAI_API_KEY
copy .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 3. Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```
