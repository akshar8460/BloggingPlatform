def test_create_blog(client, initialize_sample_data, jwt_header):
    response = client.post("/api/blogs",
                           json={"topic": "new", "data": "This a new blog created"},
                           headers=jwt_header)
    assert response.status_code == 201


def test_get_all_blogs(client, initialize_sample_data, jwt_header):
    response = client.get("/api/blogs", headers=jwt_header)
    assert response.status_code == 200
