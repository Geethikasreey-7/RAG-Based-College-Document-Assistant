from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.config import DATABASE_PATH


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect() -> sqlite3.Connection:
    db_path = Path(DATABASE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(db_path))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db() -> None:
    with _connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                message_id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations (conversation_id) ON DELETE CASCADE
            )
            """
        )


def create_conversation(title: str | None = None) -> dict:
    conversation_id = str(uuid.uuid4())
    timestamp = _utc_now()
    safe_title = (title or "New conversation").strip() or "New conversation"

    with _connect() as connection:
        connection.execute(
            """
            INSERT INTO conversations (conversation_id, title, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            (conversation_id, safe_title, timestamp, timestamp),
        )

    return get_conversation(conversation_id)


def list_conversations() -> list[dict]:
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT c.conversation_id, c.title, c.created_at, c.updated_at,
                   COUNT(m.message_id) AS message_count,
                   MAX(m.created_at) AS last_message_at
            FROM conversations c
            LEFT JOIN messages m ON m.conversation_id = c.conversation_id
            GROUP BY c.conversation_id, c.title, c.created_at, c.updated_at
            ORDER BY c.updated_at DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def get_conversation(conversation_id: str) -> dict | None:
    with _connect() as connection:
        conversation_row = connection.execute(
            """
            SELECT conversation_id, title, created_at, updated_at
            FROM conversations
            WHERE conversation_id = ?
            """,
            (conversation_id,),
        ).fetchone()

        if not conversation_row:
            return None

        messages = connection.execute(
            """
            SELECT message_id, conversation_id, role, content, created_at
            FROM messages
            WHERE conversation_id = ?
            ORDER BY created_at ASC
            """,
            (conversation_id,),
        ).fetchall()

    conversation = dict(conversation_row)
    conversation["messages"] = [dict(message) for message in messages]
    return conversation


def add_message(conversation_id: str, role: str, content: str) -> dict:
    message_id = str(uuid.uuid4())
    timestamp = _utc_now()

    with _connect() as connection:
        connection.execute(
            """
            INSERT INTO messages (message_id, conversation_id, role, content, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (message_id, conversation_id, role, content, timestamp),
        )
        connection.execute(
            """
            UPDATE conversations
            SET updated_at = ?
            WHERE conversation_id = ?
            """,
            (timestamp, conversation_id),
        )

    return {
        "message_id": message_id,
        "conversation_id": conversation_id,
        "role": role,
        "content": content,
        "created_at": timestamp,
    }


def get_recent_messages(conversation_id: str, limit: int = 5) -> list[dict]:
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT message_id, conversation_id, role, content, created_at
            FROM messages
            WHERE conversation_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (conversation_id, limit),
        ).fetchall()

    return [dict(row) for row in reversed(rows)]


def conversation_exists(conversation_id: str) -> bool:
    with _connect() as connection:
        row = connection.execute(
            "SELECT 1 FROM conversations WHERE conversation_id = ?",
            (conversation_id,),
        ).fetchone()
    return row is not None
