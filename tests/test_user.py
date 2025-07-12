def test_create_user(client):
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "securepassword123"
    }

    response = client.post("/users", json=user_data)
    print(response.get_json())
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data["message"] == "ユーザーを登録しました"
    assert json_data["user"]["name"] == "Test User"
    assert json_data["user"]["email"] == "test@example.com"
