# tests/test_company.py

def test_create_company(client, superuser):
    # スーパーユーザーでログイン
    res = client.post("/auth/login", json={"email": superuser["email"], "password": superuser["password"]})
    assert res.status_code == 200
    payload = {'name': 'TestCompany_test_company'}
    response = client.post('/companies', json=payload)
    assert response.status_code == 201
    company_data = response.get_json()
    assert company_data['name'] == 'TestCompany_test_company'

    response = client.get('/companies')
    assert response.status_code == 200




