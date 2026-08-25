from __future__ import annotations

from fastapi import status


def test_conversation_lifecycle(client):
    # 1. Create a new conversation
    response = client.post("/api/conversations", json={"title": "Test Chat"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Test Chat"
    conversation_id = data["conversation_id"]
    assert conversation_id
    assert data["messages"] == []

    # 2. List conversations
    list_response = client.get("/api/conversations")
    assert list_response.status_code == status.HTTP_200_OK
    conversations = list_response.json()
    assert any(c["conversation_id"] == conversation_id for c in conversations)

    # 3. Add a user message
    msg_response = client.post(
        f"/api/conversations/{conversation_id}/messages",
        json={"role": "user", "content": "What is RAG?"},
    )
    assert msg_response.status_code == status.HTTP_200_OK
    msg_data = msg_response.json()
    assert msg_data["role"] == "user"
    assert msg_data["content"] == "What is RAG?"

    # 4. Add an assistant message
    asst_response = client.post(
        f"/api/conversations/{conversation_id}/messages",
        json={"role": "assistant", "content": "RAG stands for Retrieval-Augmented Generation."},
    )
    assert asst_response.status_code == status.HTTP_200_OK

    # 5. Fetch conversation details
    detail_response = client.get(f"/api/conversations/{conversation_id}")
    assert detail_response.status_code == status.HTTP_200_OK
    detail = detail_response.json()
    assert len(detail["messages"]) == 2
    assert detail["messages"][0]["role"] == "user"
    assert detail["messages"][1]["role"] == "assistant"

    # 6. Delete conversation
    del_response = client.delete(f"/api/conversations/{conversation_id}")
    assert del_response.status_code == status.HTTP_200_OK
    assert del_response.json()["deleted"] is True

    # 7. Verify conversation is gone
    get_again = client.get(f"/api/conversations/{conversation_id}")
    assert get_again.status_code == status.HTTP_404_NOT_FOUND


def test_nonexistent_conversation_endpoints(client):
    fake_id = "nonexistent-id-12345"
    assert client.get(f"/api/conversations/{fake_id}").status_code == status.HTTP_404_NOT_FOUND
    assert client.delete(f"/api/conversations/{fake_id}").status_code == status.HTTP_404_NOT_FOUND
    assert client.post(f"/api/conversations/{fake_id}/messages", json={"role": "user", "content": "hi"}).status_code == status.HTTP_404_NOT_FOUND

