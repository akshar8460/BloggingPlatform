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


def test_register_user(client, initialize_sample_data):
    response = client.post("/api/users/register",
                           json={"name": "new", "email": "new@new.com", "password": "password"})
    assert response.status_code == 201

    response = client.post("/api/users/register",
                           json={"name": "new", "email": "new@new.com", "password": "password"})
    assert response.status_code == 403

    response = client.post("/api/users/login", json={"email": "new@new.com", "password": "password"})
    assert response.status_code == 200


def test_get_all_users(client, initialize_sample_data, jwt_header):
    response = client.get("/api/users/", headers=jwt_header)
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_get_user(client, initialize_sample_data, jwt_header):
    response = client.get("/api/users/1", headers=jwt_header)
    assert response.status_code == 200


# @pytest.mark.parametrize(
#     "id, email, name, password, expected_status",
#     [
#         (1, "invalid", None, None, 422),  # Test case for invalid email
#         (3, "admin@test.com", None, "admin", 400),  # Test case for invalid id
#         (1, "admin@test.com", None, "admin", 400),  # Test case for missing parameter
#         (1, "admin@test.com", "New", "323", 422),  # Test case for password length limit
#         (1, "admin@test.com", "new", "admin@invalid", 401),  # Test case for 401 error
#         (1, "admin@test.com", "test1", "admin", 200)  # Test case for successful update operation
#     ]
# )
# def test_update_user(client, initialize_sample_data, jwt_header, id, email, name, password, expected_status):
#     response = client.post(f"/api/users/{id}", headers=jwt_header)
#     assert response.status_code == expected_status


def test_delete_user(client, initialize_sample_data, jwt_header):
    response = client.delete("/api/users/1", headers=jwt_header)
    assert response.status_code == 200


def test_get_all_blogs(client, initialize_sample_data, jwt_header):
    response = client.get("/api/blogs", headers=jwt_header)
    assert response.status_code == 200
    assert len(response.json()) == 0
