from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_email_invalid():
    response = client.post("/login", json={"email": "invalid"})
    assert response.status_code == 422


def test_email_success():
    response = client.post("/login", json={"email": "admin@test.com", "password": "admin"})
    assert response.status_code == 200


def test_email_password_limit():
    response = client.post("/login", json={"email": "admin@test.com", "password": "323"})
    assert response.status_code == 422


def test_email_404():
    response = client.post("/login", json={"email": "admin@test.com", "password": "adminr2"})
    assert response.status_code == 404
