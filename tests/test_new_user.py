def test_full_user_creation_flow(client, login_superuser):
    # ① Company を作成
    company_payload = {'name': 'TestCompanyX'}
    company_res = client.post('/companies/', json=company_payload)
    assert company_res.status_code == 201
    company = company_res.json
    assert company['name'] == 'TestCompanyX'

    # ② Organization を作成
    org_payload = {
        'name': 'DevelopmentDept',
        'org_code': 'DEV01',
        'company_id': company['id'],
        'parent_id': None,
        'level': 1
    }
    org_res = client.post('/organizations/', json=org_payload)
    assert org_res.status_code == 201
    org = org_res.json
    assert org['name'] == 'DevelopmentDept'
    assert org['company_id'] == company['id']

    # ③ ユーザーを作成
    user_payload = {
        'name': 'testuser1',
        'email': 'testuser1@example.com',
        'password': 'testpass123',
        'organization_id': org['id'],
        'is_superuser': False
    }
    user_res = client.post('/users', json=user_payload)
    assert user_res.status_code == 201
    user = user_res.json['user']
    assert user['email'] == 'testuser1@example.com'
    assert user['organization_id'] == org['id']
