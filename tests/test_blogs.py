def test_blog_flow(client, initialize_sample_data, jwt_header):
    response = client.post("/api/blogs",
                           json={"topic": "new", "data": "This a new blog created"},
                           headers=jwt_header)
    assert response.status_code == 201
    blog_id = response.json()["id"]

    response = client.put(f"/api/blogs/{blog_id}",
                          json={"topic": "new2", "data": "This a new2 blog created"},
                          headers=jwt_header)
    assert response.status_code == 200

    response = client.get(f"/api/blogs/{blog_id}", headers=jwt_header)
    assert response.status_code == 200
    assert response.json()["topic"] == "new2"

    response = client.delete(f"/api/blogs/{blog_id}", headers=jwt_header)
    assert response.status_code == 200


def test_get_all_blogs(client, initialize_sample_data, jwt_header):
    response = client.get("/api/blogs", headers=jwt_header)
    assert response.status_code == 200
