# Frontend README

This folder contains the React + Vite frontend for the RAG document chatbot.

## Initial setup

1. Install dependencies:

```bash
npm install
```

2. Create a `.env` file from the example:

```bash
cp .env.example .env
```

3. Update `.env` with your backend URL (default is `http://localhost:8000`).

4. Start the development server:

```bash
npm run dev
```

The app will open at `http://localhost:5173` by default.

## Component structure

The frontend follows a modular component architecture for clean separation of concerns:

```
src/
├── components/           # React components
│   ├── Navbar.jsx       # Top navigation bar
│   ├── DocumentUpload.jsx    # PDF upload form with progress
│   ├── DocumentList.jsx      # Display and manage uploaded documents
│   ├── ChatWindow.jsx        # Message display area
│   ├── ChatInput.jsx         # Message input with send button
│   └── SourceReferences.jsx  # Display citation sources
├── services/            # API communication
│   └── api.js           # Axios API client
├── styles/              # Component-specific CSS
│   ├── App.css
│   ├── Navbar.css
│   ├── DocumentUpload.css
│   ├── DocumentList.css
│   ├── ChatWindow.css
│   ├── ChatInput.css
│   └── SourceReferences.css
├── App.jsx              # Main application component
└── main.jsx             # Vite entry point
```

## Component overview

### Navbar
- Displays the application title and tagline
- Responsive gradient header

### DocumentUpload
- Accepts PDF file selection
- Shows upload progress bar
- Displays success/error messages
- Handles file validation

### DocumentList
- Lists all uploaded documents
- Shows chunk count for each document
- Allows document deletion with confirmation
- Empty state when no documents exist

### ChatWindow
- Displays message history
- Alternates between user (right) and assistant (left) messages
- Shows loading indicator while waiting for response
- Displays error messages
- Shows empty state with tips when no messages

### ChatInput
- Text input area for user questions
- Send button with loading state
- Enter key sends message (Shift+Enter for newline)
- Disabled when no documents are uploaded

### SourceReferences
- Shows document sources used to answer the question
- Displays filename and page number
- Styled as a highlighted references box

### API Service (services/api.js)
- Centralized Axios client
- Reads backend URL from `VITE_API_URL` environment variable
- Exports three API modules:
  - `documentAPI`: upload, list, delete operations
  - `searchAPI`: semantic search (optional frontend use)
  - `chatAPI`: RAG generation with sources

## State management

The main `App.jsx` component manages:
- `documents`: list of uploaded documents
- `messages`: chat message history
- `isLoadingDocuments`: document list loading state
- `isLoadingChat`: chat response loading state
- `chatError`: error messages for chat operations

## Key features

- **Responsive design**: Works on desktop, tablet, and mobile
- **Real-time upload progress**: Visual feedback during file upload
- **Error handling**: User-friendly error messages throughout
- **Empty states**: Helpful messages when no documents or no chat
- **Modern UI**: Gradient colors, smooth animations, professional styling
- **Keyboard shortcuts**: Enter to send, Shift+Enter for newline
- **Source attribution**: Every answer shows the documents used

## Environment variables

- `VITE_API_URL`: Backend API URL (default: `http://localhost:8000`)

## Build for production

```bash
npm run build
```

This creates a `dist` folder with optimized production files.

## Preview production build

```bash
npm run preview
```

