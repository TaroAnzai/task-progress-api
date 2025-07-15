# tests/test_company.py

def test_create_company(superuser_login):
    payload = {'name': 'TestCompany'}
    response = superuser_login.post('/companies/', json=payload)

    assert response.status_code == 201
    assert response.json['name'] == 'TestCompany'

    response = superuser_login.get('/companies/')
    assert response.status_code == 200




