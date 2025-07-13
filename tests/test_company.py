# tests/test_company.py

def test_create_company(client, login_superuser):
    payload = {'name': 'TestCompany'}
    response = client.post('/companies/', json=payload)

    assert response.status_code == 201
    assert response.json['name'] == 'TestCompany'

    response = client.get('/companies/')
    assert response.status_code == 200




