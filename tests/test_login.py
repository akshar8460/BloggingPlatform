import pytest


@pytest.mark.parametrize(
    "email, password, expected_status",
    [
        ("invalid", None, 422),  # Test case for invalid email
        ("admin@test.com", "admin", 200),  # Test case for successful login
        ("admin@test.com", "323", 422),  # Test case for password length limit
        ("admin@test.com", "admin@invalid", 401),  # Test case for 401 error
    ]
)
def test_login(client, initialize_sample_data, email, password, expected_status):
    response = client.post("/api/users/login", json={"email": email, "password": password})
    assert response.status_code == expected_status


def test_user_flow(client, initialize_sample_data, jwt_header):
    response = client.post("/api/users/register",
                           json={"name": "new", "email": "new@new.com", "password": "password"})
    assert response.status_code == 201

    user_id = response.json()["id"]

    response = client.put(f"/api/users/{user_id}",
                          json={"name": "new2", "email": "new@new.com", "password": "password"},
                          headers=jwt_header)
    assert response.status_code == 200
    assert response.json()["name"] == "new2"

    response = client.post("/api/users/register",
                           json={"name": "new", "email": "new@new.com", "password": "password"})
    assert response.status_code == 403

    response = client.post("/api/users/login", json={"email": "new@new.com", "password": "password"})
    assert response.status_code == 200
    response = client.delete(f"/api/users/{user_id}", headers=jwt_header)
    assert response.status_code == 200


def test_get_all_users(client, initialize_sample_data, jwt_header):
    response = client.get("/api/users/", headers=jwt_header)
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_get_user(client, initialize_sample_data, jwt_header):
    response = client.get("/api/users/1", headers=jwt_header)
    assert response.status_code == 200
    assert response.json()["name"] == "john_doe"


def test_create_blog(client, initialize_sample_data, jwt_header):
    response = client.post("/api/blogs",
                           json={"topic": "new", "data": "This a new blog created"},
                           headers=jwt_header)
    assert response.status_code == 201


def test_get_all_blogs(client, initialize_sample_data, jwt_header):
    response = client.get("/api/blogs", headers=jwt_header)
    assert response.status_code == 200
