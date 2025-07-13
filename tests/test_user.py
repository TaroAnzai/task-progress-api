def test_superuser_login(client, superuser):
    login_data = {
        "email": "admin@example.com",
        "password": "adminpass"
    }
    res = client.post("/login", json=login_data)
    assert res.status_code == 200

    data = res.get_json()
    assert "user" in data
    assert data["user"]["email"] == "admin@example.com"
    assert data["user"]["is_superuser"] is True
