import pytest
from unittest.mock import patch, AsyncMock

from tests.conftest import create_test_document_with_chunks
from app import models



def register_and_login(client, email="alice@test.com", password="password123"):
    client.post("/register",
                json={"email": email, "password": password})
    login = client.post("/login",
                        data={"username": email, "password": password})
    return login.json()["access_token"]

def get_user_id_from_email(db_session, email):
    user = db_session.query(models.User).filter(models.User.email == email).first()
    return user.id if user else None

def test_upload_document_title_too_short(client):
    token = register_and_login(client)
    response = client.post("/documents",
                           json={"title": "", "content": "a" * 100},
                           headers={"Authorization": f"Bearer {token}"},
                           )
    assert response.status_code == 422

def test_upload_document_content_too_short(client):
    token = register_and_login(client)
    response = client.post("/documents",
                           json={"title": "Test", "content": "short"},
                           headers= {"Authorization": f"Bearer {token}"},
                           )
    assert response.status_code == 422


def test_upload_document_without_token(client):
    response = client.post("/documents",
                           json={"title": "Test title", "content": "aaa" * 100})
    assert response.status_code == 401

def test_upload_document_success_with_mocks(client, db_session):
    token = register_and_login(client)

    fake_chunks = ["Chunk one text.", "Chunk two text."]
    fake_embeddings = [[0.1] * 1536, [0.2] * 1536]

    with patch(
        "app.llm.chunker.chunk_text",
        return_value=fake_chunks,
    ), patch(
        "app.llm.embedder.embed_texts",
        new=AsyncMock(return_value=fake_embeddings),
    ):
        response = client.post(
            "/documents",
            json={"title": "JWT Guide", "content": "a" * 100},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "JWT Guide"
    assert "id" in data


def test_get_other_users_document_returns_404(client, db_session):
    token_alice = register_and_login(client, email="alice@test.com")
    alice_id = get_user_id_from_email(db_session, "alice@test.com")
    alice_doc = create_test_document_with_chunks(db_session, owner_id=alice_id)

    token_bob = register_and_login(client, email="bob@test.com")
    response = client.get(f"/documents/{alice_doc.id}",
                          headers={"Authorization": f"Bearer {token_bob}"},
                          )
    assert response.status_code == 404

def test_list_documents_shows_only_own(client, db_session):
    token_alice = register_and_login(client, email="alice@test.com")
    alice_id = get_user_id_from_email(db_session, email="alice@test.com")
    create_test_document_with_chunks(db_session, owner_id=alice_id, title="Alice Doc")

    token_bob = register_and_login(client, email="bob@test.com")
    bob_id = get_user_id_from_email(db_session, "bob@test.com")
    create_test_document_with_chunks(db_session, owner_id=bob_id, title="Bob Doc")

    response = client.get(
        "/documents",
        headers={"Authorization": f"Bearer {token_bob}"},
    )
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Bob Doc"


def test_search_without_token(client):
    response = client.post("/documents/search",
                            json={"query": "jwt", "limit": 3})
    assert response.status_code == 401

        
def test_search_returns_only_own_chunks(client, db_session):
    token_alice = register_and_login(client, email="alice@test.com")
    alice_id = get_user_id_from_email(db_session, email="alice@test.com")
    create_test_document_with_chunks(
        db_session=db_session,
        owner_id=alice_id,
        title="Alice Doc",
        chunks_data=[("Alice content about JWT.", [0.1] * 1536)]
    )
    token_bob = register_and_login(client, email="bob@test.com")

    with patch(
        "app.llm.embedder.embed_texts",
        new=AsyncMock(return_value=[[0.1] * 1536]),
    ):
        response = client.post(
            "/documents/search",
            json={"query": "jwt", "limit": 5},
            headers={"Authorization": f"Bearer {token_bob}"}
        )

    assert response.status_code == 200
    assert response.json()["results"] == []



def test_rag_ask_without_token(client):
    response = client.post(
        "/documents/ask",
        json={"question": "test", "top_k": 3}
    )
    assert response.status_code == 401

def test_rag_ask_returns_no_context_message_when_empty(client, db_session):
    token = register_and_login(client)

    with patch(
        "app.llm.embedder.embed_texts",
        new=AsyncMock(return_value=[[0.1] * 1536]),
    ):
        response = client.post(
            "/documents/ask",
            json={"question": "What is JWT?", "top_k": 3},
            headers={"Authorization": f"Bearer {token}"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["sources"] == []
    assert "cannot find" in data["answer"].lower()


def test_rag_ask_calls_llm_when_context_found(client, db_session):
    token = register_and_login(client)
    user_id = get_user_id_from_email(db_session=db_session, email="alice@test.com")
    create_test_document_with_chunks(
        db_session,
        owner_id=user_id,
        chunks_data=[("Text about authentication.", [0.1] * 1536)],
    )

    mock_answer = "According to Source 1, authentication works via tokens."

    with patch(
        "app.llm.embedder.embed_texts",
        new=AsyncMock(return_value=[[0.1] * 1536]),
    ), patch(
        "app.llm.rag.answer_with_context",
        new=AsyncMock(return_value=mock_answer),
    ):
        response = client.post(
            "/documents/ask",
            json={"question": "How does auth work?", "top_k": 3},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == mock_answer
    assert len(data["sources"]) == 1

def _should_not_be_called(*args, **kwargs):
    raise AssertionError("LLM was called but shouldn't have been")

def test_rag_ask_when_context_wasnt_found(client, db_session):
    token = register_and_login(client, email="alice@test.com")
    user_id = get_user_id_from_email(db_session=db_session, email="alice@test.com")
    create_test_document_with_chunks(
        db_session=db_session,
        owner_id=user_id,
        title="Alice Doc",
        chunks_data=[("Some info about pizza", [-0.1] * 1536)]
    )

    with patch("app.llm.embedder.embed_texts", new=AsyncMock(return_value=[[999.0] * 1536])), \
        patch("app.llm.rag.answer_with_context", new=AsyncMock(side_effect=_should_not_be_called)):
        response = client.post("/documents/ask",
                               json={"question": "How does JWT work", "top_k": 3},
                               headers={"Authorization": f"Bearer {token}"})
        
    assert response.status_code == 200
    data = response.json()
    assert "cannot find" in data["answer"].lower()