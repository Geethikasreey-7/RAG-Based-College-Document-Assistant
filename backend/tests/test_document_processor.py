from app.config import MAX_CONTEXT_CHARS
from app.services.document_processor import DocumentProcessor


def test_clean_text_normalizes_whitespace():
    processor = DocumentProcessor(chunk_size=50, chunk_overlap=10)

    cleaned = processor.clean_text("  Hello   world\n\nThis   is   a test.  ")

    assert cleaned == "Hello world This is a test."


def test_chunk_text_adds_required_metadata():
    processor = DocumentProcessor(chunk_size=20, chunk_overlap=5)
    text = "alpha beta gamma delta epsilon zeta eta theta iota kappa"

    chunks = processor.chunk_text(text, source_filename="sample.pdf", page_number=3)

    assert len(chunks) > 0
    assert all(chunk["source_filename"] == "sample.pdf" for chunk in chunks)
    assert all(chunk["page_number"] == 3 for chunk in chunks)
    assert all("chunk_id" in chunk for chunk in chunks)


def test_context_limit_is_configurable():
    assert isinstance(MAX_CONTEXT_CHARS, int)
    assert MAX_CONTEXT_CHARS > 0
