import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


@pytest.mark.parametrize(
    "email, password, expected_status",
    [
        ("invalid", None, 422),  # Test case for invalid email
        ("admin@admin.com", "admin", 200),  # Test case for successful login
        ("admin@test.com", "323", 422),  # Test case for password length limit
        ("admin@test.com", "admin@invalid", 401),  # Test case for 401 error
    ]
)
def test_login(email, password, expected_status):
    response = client.post("/api/users/login", json={"email": email, "password": password})
    assert response.status_code == expected_status
