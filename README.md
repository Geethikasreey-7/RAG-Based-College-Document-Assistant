# RAG-Based College Document Assistant

**An AI-powered college document assistant that uses Retrieval-Augmented Generation (RAG) to answer questions from uploaded PDF documents with source attribution.**

The system combines a **FastAPI backend**, **React frontend**, **OpenAI embeddings/LLM**, and **FAISS vector search** to provide grounded question answering over college documents.

Users can upload documents, search them using natural language, ask contextual questions, and continue conversations across multiple sessions.

---

## 🎯 What Problem Does It Solve?

College information is often distributed across PDFs such as:

* Academic regulations
* Course handbooks
* Examination guidelines
* Department documents
* Student policies
* Timetables
* Administrative notices
* Placement information

Finding a specific piece of information manually can be slow and frustrating.

This application provides a conversational interface where students can ask questions such as:

> "What is the minimum attendance requirement?"

> "When can I apply for supplementary examinations?"

> "What are the requirements mentioned in the internship policy?"

Instead of relying only on an LLM's general knowledge, the system retrieves relevant content from the uploaded documents and uses that context to generate an answer.

---

## 🏗️ Architecture

```text
                         ┌──────────────────────┐
                         │    React Frontend    │
                         │      Vite + Axios    │
                         └──────────┬───────────┘
                                    │
                              HTTP / REST
                                    │
                         ┌──────────▼───────────┐
                         │     FastAPI Backend   │
                         │                       │
                         │  API Routes / Services│
                         └──────────┬───────────┘
                                    │
                  ┌─────────────────┼─────────────────┐
                  │                 │                 │
                  ▼                 ▼                 ▼
          ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
          │ PDF Pipeline │  │ Conversation │  │  RAG Engine  │
          │              │  │   Storage    │  │              │
          │ PyPDF        │  │   SQLite     │  │ Retrieval    │
          │ Cleaning     │  │   History    │  │ Prompting    │
          │ Chunking     │  │              │  │ Generation   │
          └──────┬───────┘  └──────────────┘  └──────┬───────┘
                 │                                    │
                 ▼                                    ▼
          ┌──────────────┐                    ┌──────────────┐
          │   OpenAI     │                    │ FAISS Vector │
          │  Embeddings  │◄──────────────────►│    Store     │
          └──────────────┘                    └──────────────┘
                                                     │
                                                     ▼
                                              Relevant Chunks
                                                     │
                                                     ▼
                                              ┌──────────────┐
                                              │ OpenAI LLM   │
                                              └──────┬───────┘
                                                     │
                                                     ▼
                                             Answer + Sources
```

---

## ✨ Key Features

### 1. PDF Document Ingestion

Users can upload PDF documents through the web interface.

The ingestion pipeline performs:

```text
PDF Upload
    ↓
Text Extraction
    ↓
Text Cleaning
    ↓
Document Chunking
    ↓
OpenAI Embeddings
    ↓
FAISS Indexing
    ↓
Persistent Vector Store
```

The pipeline handles:

* PDF validation
* Page-level text extraction
* Empty-page handling
* Text normalization
* Configurable chunk size
* Configurable chunk overlap
* Embedding generation
* Vector-store persistence
* Document metadata

---

### 2. Semantic Search

The application uses **vector embeddings** and **FAISS similarity search** instead of relying solely on keyword matching.

A user query is converted into an embedding and compared against indexed document chunks.

```text
User Query
    ↓
Query Embedding
    ↓
FAISS Similarity Search
    ↓
Top-K Relevant Chunks
    ↓
Relevance Filtering
```

This allows the system to retrieve relevant information even when the wording of the question differs from the wording in the original document.

For example:

```text
Question:
"How much attendance do students need?"

Possible document text:
"Students must maintain a minimum attendance percentage..."
```

A semantic search system can recognize the relationship between the two even without an exact keyword match.

---

## 🤖 Retrieval-Augmented Generation Pipeline

The core chatbot workflow is:

```text
User Question
      ↓
Recent Conversation History
      ↓
Query Embedding
      ↓
FAISS Semantic Search
      ↓
Top-K Relevant Chunks
      ↓
Filtering / Deduplication
      ↓
Context Construction
      ↓
Grounded LLM Prompt
      ↓
LLM Generation
      ↓
Answer + Source References
```

### Step-by-step

1. The user submits a natural-language question.
2. Recent conversation history is optionally included for follow-up questions.
3. The question is converted into an embedding using the same embedding model used during ingestion.
4. FAISS searches for semantically similar document chunks.
5. The top-K relevant chunks are retrieved.
6. Duplicate or low-quality chunks are removed.
7. Retrieved content is converted into a bounded context.
8. Document context and conversation history are kept logically separated.
9. The LLM generates an answer using the retrieved document context.
10. The response includes source metadata such as filename and page number.

---

## 📚 Grounded Answers & Source Attribution

One of the key design goals is **traceability**.

Instead of returning only:

```text
"The attendance requirement is 75%."
```

the system can return the answer together with its source information:

```text
Answer:
Students are required to maintain the specified minimum attendance.

Sources:
- academic_regulations.pdf — Page 12
- student_handbook.pdf — Page 7
```

This makes the system easier to verify and reduces the risk of users accepting unsupported model-generated information.

---

## 🧠 Conversation Memory

The application supports persistent conversations using **SQLite**.

Users can:

* Create conversations
* View previous conversations
* Open an existing conversation
* Continue a previous discussion
* Store user and assistant messages
* Delete conversations

The system does **not** send unlimited conversation history to the LLM.

Instead, only a bounded recent portion of the conversation is included, allowing follow-up questions such as:

> "What about the second requirement?"

to remain contextual without continuously increasing prompt size.

---

## 🗂️ Project Structure

```text
rag-document-chatbot/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/
│   │   │   └── routes/
│   │   ├── services/
│   │   ├── models/
│   │   └── utils/
│   │
│   ├── data/
│   │   ├── documents/
│   │   ├── vectorstore/
│   │   └── chat_history.db
│   │
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

---

## 🛠️ Technology Stack

### Backend

* **Python**
* **FastAPI**
* **LangChain**
* **OpenAI API**
* **PyPDF**
* **FAISS**
* **SQLite**

### Frontend

* **React**
* **Vite**
* **Axios**

### AI / RAG

* OpenAI embeddings
* Vector similarity search
* Top-K retrieval
* Context construction
* LLM-based answer generation
* Source attribution
* Conversation-aware retrieval

---

## 🔐 Configuration & Security

API keys and secrets are not hardcoded into the application.

Configuration is supplied through environment variables.

Example:

```env
OPENAI_API_KEY=your-api-key
```

The repository should keep `.env` files and other secrets outside version control.

---

## 🌐 API Endpoints

### Health

```text
GET /health
```

Checks whether the backend is running.

### Documents

```text
GET    /api/documents
POST   /api/documents/upload
DELETE /api/documents/{filename}
```

Used to list, upload, process, and remove documents.

### Search

```text
POST /api/search
```

Performs semantic search against the indexed document collection.

### Chat

```text
POST /api/chat
```

Performs RAG-based question answering with optional conversation context and source attribution.

### Conversations

```text
POST   /api/conversations
GET    /api/conversations
GET    /api/conversations/{conversation_id}
POST   /api/conversations/{conversation_id}/messages
DELETE /api/conversations/{conversation_id}
```

Used to manage persistent conversation threads and messages.

---

## 🔄 Document Ingestion Example

Suppose a college uploads:

```text
academic_regulations.pdf
```

The system processes it as follows:

```text
academic_regulations.pdf
          ↓
Extract page text
          ↓
Clean text
          ↓
Split into overlapping chunks
          ↓
Generate embeddings
          ↓
Store vectors in FAISS
          ↓
Store document/page metadata
```

A later question such as:

> "How many attempts are allowed for a failed course?"

is converted into an embedding and matched against the indexed chunks.

The most relevant chunks are then provided to the LLM as context.

---

## 💬 Example Chat Flow

```text
Student:
"What is the minimum attendance requirement?"

        ↓

Query Embedding

        ↓

FAISS Search

        ↓

Relevant chunks:
academic_regulations.pdf
Page 12

        ↓

Context Construction

        ↓

OpenAI LLM

        ↓

Response:
"According to the academic regulations, students must
maintain the required minimum attendance."

        ↓

Sources:
academic_regulations.pdf — Page 12
```

---

## 🧪 Testing

### Backend

```bash
cd backend
pytest
```

### Frontend

```bash
cd frontend
npm test
```

The test suite is intended to validate backend functionality and frontend behavior.

---

## 🚀 Running the Application

### 1. Backend Setup

```bash
cd backend

pip install -r requirements.txt

# Create environment configuration
copy .env.example .env

# Add your OpenAI API key to .env

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at:

```text
http://localhost:8000
```

---

### 2. Frontend Setup

Open a second terminal:

```bash
cd frontend

npm install
npm run dev
```

The Vite development server will provide the frontend URL in the terminal.

---

## 📈 Why RAG?

A traditional chatbot relies primarily on the knowledge contained within the LLM.

This creates a problem when users need answers from **private or recently uploaded documents**.

RAG solves this by separating the problem into two stages:

```text
RETRIEVAL
Find relevant information
        +
GENERATION
Use that information to produce an answer
```

The LLM therefore receives relevant document context rather than being expected to know the contents of every uploaded document.

### Benefits

* **Grounded answers** — responses are based on retrieved document content
* **Source traceability** — answers can reference document/page metadata
* **Private knowledge base** — organizations can provide their own documents
* **Incremental updates** — new documents can be indexed without retraining the LLM
* **Lower context usage** — only relevant chunks are passed to the model
* **Semantic retrieval** — queries can match conceptually related content

---

## ⚖️ RAG vs. Sending the Entire PDF

### Entire PDF

```text
PDF
 ↓
Entire document
 ↓
LLM
 ↓
Answer
```

Potential problems:

* Large context requirements
* Higher token consumption
* Higher API cost
* Increased latency
* Irrelevant information in the prompt
* Context-window limitations

### RAG

```text
PDF
 ↓
Chunks → Embeddings → FAISS
                         ↑
                         │
                    User Query
                         │
                         ↓
                  Relevant Chunks
                         ↓
                        LLM
                         ↓
                      Answer
```

The model receives a smaller, more relevant context instead of the entire document.

---

## 🔮 Future Improvements

Potential improvements include:

* [ ] Hybrid search — BM25 + vector search
* [ ] Cross-encoder reranking
* [ ] Streaming LLM responses
* [ ] Multi-document collection management
* [ ] Document versioning
* [ ] OCR support for scanned PDFs
* [ ] Table-aware document extraction
* [ ] Metadata filtering
* [ ] Improved citation formatting
* [ ] Evaluation framework for retrieval quality
* [ ] RAGAS-based RAG evaluation
* [ ] Authentication and multi-user support
* [ ] PostgreSQL for production conversation storage
* [ ] Docker / Docker Compose deployment
* [ ] CI/CD pipeline
* [ ] Observability and request tracing
* [ ] Rate limiting and API security

---

## 🎓 Project Objective

This project explores the intersection of:

**Generative AI + Information Retrieval + Backend Engineering + Full-Stack Development**

The primary goal is to demonstrate how a production-style RAG pipeline can be designed to ingest private documents, perform semantic retrieval, maintain conversational context, and generate grounded answers with source attribution.

---

## 📌 Disclaimer

This project is intended for **educational, portfolio, and demonstration purposes**.

LLM-generated responses may still contain errors. Retrieved documents and source references should be verified for high-stakes academic or administrative decisions.

