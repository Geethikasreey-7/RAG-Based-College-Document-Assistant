from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.config import CHUNK_OVERLAP, CHUNK_SIZE, MAX_UPLOAD_SIZE, UPLOAD_DIRECTORY
from app.services.document_processor import DocumentProcessor
from app.services.vectorstore_service import VectorStoreService
from app.utils.file_utils import ensure_directory, resolve_duplicate_filename

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.get("")
async def list_documents() -> dict:
    vector_store = VectorStoreService()
    documents = vector_store.list_documents()
    return {"count": len(documents), "documents": documents}


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)) -> dict:
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file selected.")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are allowed.")

    file_bytes = await file.read()
    if len(file_bytes) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the maximum allowed size of {MAX_UPLOAD_SIZE} bytes.",
        )

    storage_dir = ensure_directory(UPLOAD_DIRECTORY)
    safe_filename = resolve_duplicate_filename(file.filename, storage_dir)
    destination = storage_dir / safe_filename

    try:
        with destination.open("wb") as buffer:
            buffer.write(file_bytes)
    except OSError as exc:
        logger.exception("Failed to save uploaded file: %s", file.filename)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not save the uploaded file.") from exc

    processor = DocumentProcessor(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    vector_store = VectorStoreService()

    try:
        result = processor.process_pdf(destination)
        processed_chunks = vector_store.add_documents(result["chunks"])
        logger.info("Indexed %s document chunks for %s.", len(processed_chunks), result["filename"])
    except ValueError as exc:
        destination.unlink(missing_ok=True)
        logger.exception("Document processing failed for %s", file.filename)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive guard
        destination.unlink(missing_ok=True)
        logger.exception("Unexpected processing error for %s", file.filename)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process the uploaded document.") from exc

    return {
        "filename": result["filename"],
        "page_count": result["page_count"],
        "chunk_count": result["chunk_count"],
        "status": result["status"],
    }


@router.delete("/{filename}")
async def delete_document(filename: str) -> dict:
    safe_filename = Path(filename).name
    if safe_filename != filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid filename.")

    document_path = Path(UPLOAD_DIRECTORY) / safe_filename
    if not document_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    try:
        document_path.unlink(missing_ok=True)
    except OSError as exc:
        logger.exception("Failed to delete uploaded file: %s", safe_filename)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not delete the document.") from exc

    vector_store = VectorStoreService()
    deleted = vector_store.delete_document(safe_filename)
    if not deleted:
        logger.warning("Document was removed from disk but not present in vector metadata: %s", safe_filename)

    return {"filename": safe_filename, "status": "deleted"}
