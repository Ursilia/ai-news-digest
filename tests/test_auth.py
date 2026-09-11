import pytest

def test_register_success(client):
    response = client.post(
        "/register",
        json={"email": "alice@test.com", "password": "password123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "alice@test.com"
    assert "id" in data
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_email(client):
    client.post(
        "/register",
        json={"email": "alice@test.com", "password": "password123"},
    )
    response = client.post(
        "/register",
        json={"email": "alice@test.com", "password": "different_pass"}
    )
    assert response.status_code == 409

def test_register_short_password(client):
    response = client.post(
        "/register",
        json={"email": "alice@test.com", "password": "1"}
    )
    assert response.status_code == 422

def test_register_invalid_email(client):
    response = client.post(
        "/register",
        json={"email": "deflynotanemail", "password": "1111111"}
    )
    assert response.status_code ==422

def test_login_success(client):
    client.post(
        "/register",
        json={"email": "alice@test.com", "password": "password123"}
    )
    response = client.post(
        "/login",
        data={"username": "alice@test.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):
    client.post(
        "/register",
        json={"email": "alice@test.com", "password": "password123"}
    )
    response = client.post(
        "/login",
        data={"username":"alice@test.com", "password": "111111111"}
    )
    assert response.status_code == 401

def test_login_nonexistent_email(client):
    response = client.post(
        "/login",
        data={"username":"a@test.com", "password": "anydfsfsd"}
    )
    assert response.status_code == 401

def test_me_without_token(client):
    response = client.get("/me")
    assert response.status_code == 401

def test_me_with_valid_token(client):
    client.post(
        "/register",
        json={"email":"alice@test.com", "password": "password123"}
    )
    login_response = client.post(
        "/login",
        data={"username":"alice@test.com", "password": "password123"}
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "alice@test.com"

def test_me_with_invalid_token(client):
    response = client.get(
        "/me",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == 401

def test_several_wrong_passwords(client):
    client.post(
        "/register",
        json={"email": "alice@test.com", "password": "password123"}
    )
    for _ in range(3):
        assert response.status_code == 401
        response = client.post(
                "/login",
                data={"username": "alice@test.com", "password": "password123"}
            )
    assert response.status_code == 200

    