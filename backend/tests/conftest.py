import os
from pathlib import Path

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("DATABASE_PATH", str(Path(__file__).resolve().parent / "test_chat_history.db"))

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
