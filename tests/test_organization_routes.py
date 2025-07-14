import pytest
from app import db
from app.models import Company, Organization

@pytest.fixture(scope='module')
def create_company_data():
    return {"name": "Test2 Company"}

@pytest.fixture(scope='module')
def test_company(client, login_superuser, create_company_data):
    response = client.post("/companies/", json=create_company_data)
    assert response.status_code == 201
    return response.get_json()  # ← JSON データにして返す（例：{'id': 1, 'name': 'Test Company'})

@pytest.fixture(scope='module')
def root_org(client, login_superuser, test_company):
    org = Organization(name="RootOrg", org_code="root", company_id=test_company['id'])
    return org

@pytest.fixture(scope='module')
def root_org_data(client, login_superuser, test_company, root_org):
    responce = client.post('/organizations/',json={
        'name': root_org.name,
        'org_code': root_org.org_code,
        'company_id':root_org.company_id
    })
    assert responce.status_code == 201
    return responce.get_json()

def test_create_organization(client, login_superuser, test_company, root_org, root_org_data):
    res = client.post('/organizations/', json={
        'name': '営業部',
        'org_code': 'sales',
        'company_id': test_company['id'],
        'parent_id': root_org_data['id']
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data['name'] == '営業部'
    assert data['org_code'] == 'sales'

def test_create_root_organization_twice(client, login_superuser):
    company_res = response = client.post("/companies/", json={'name':'test_create_root_organization_twice'})
    assert company_res.status_code == 201
    company_res = company_res.get_json()
    # 最初のルート組織作成
    res1 = client.post('/organizations/', json={
        'name': 'root',
        'org_code': 'code',
        'company_id': company_res['id'],
    })
    assert res1.status_code == 201

    # 2つ目はエラー
    res2 = client.post('/organizations/', json={
        'name': 'AnotherRoot',
        'org_code': 'root2',
        'company_id': company_res['id']
    })
    assert res2.status_code == 400
    assert 'ルート組織' in res2.get_json()['error']

def test_get_organizations(client, login_superuser, root_org):
    res = client.get(f'/organizations/?company_id={root_org.company_id}')
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
    assert any(org['name'] == root_org.name for org in data)

def test_get_organization_by_id(client, login_superuser, root_org_data):
    res = client.get(f'/organizations/{root_org_data['id']}')
    assert res.status_code == 200
    assert res.get_json()['name'] == root_org_data['name']

def test_update_organization(client, login_superuser, root_org_data):
    res = client.put(f'/organizations/{root_org_data['id']}', json={
        'name': '新しい名前',
        'parent_id': None
    })
    assert res.status_code == 200
    assert res.get_json()['name'] == '新しい名前'

def test_delete_organization_with_children(client, login_superuser, root_org_data):
    parent_id = root_org_data['id']
    company_id = root_org_data['company_id']

    # 1. 子組織を作成
    res_create_child = client.post('/organizations/', json={
        'name': '子組織',
        'org_code': 'child01',
        'company_id': company_id,
        'parent_id': parent_id
    })
    assert res_create_child.status_code == 201
    child_org = res_create_child.get_json()
    child_id = child_org['id']

    # 2. ルート組織の削除（失敗するはず）
    res_delete_root = client.delete(f'/organizations/{parent_id}')
    assert res_delete_root.status_code == 400
    assert '削除できません' in res_delete_root.get_json()['error'] or '子' in res_delete_root.get_json()['error']

    # 3. 子組織を削除（成功するはず）
    res_delete_child = client.delete(f'/organizations/{child_id}')
    assert res_delete_child.status_code == 200

    # 4. 子組織が削除されたか確認（/children）
    res_check_children = client.get(f'/organizations/children?parent_id={parent_id}')
    assert res_check_children.status_code == 200
    children = res_check_children.get_json()
    assert all(c['id'] != child_id for c in children)

def test_get_organization_tree(client, login_superuser, root_org_data):
    res = client.get(f'/organizations/tree?company_id={root_org_data['company_id']}')
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)

def test_get_children(client, login_superuser, root_org_data):
    child = Organization(
        name="子組織",
        org_code="child",
        parent_id=root_org_data['id'],
        company_id=root_org_data['company_id']
    )
    db.session.add(child)
    db.session.commit()

    res = client.get(f'/organizations/children?parent_id={root_org_data['id']}')
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
    assert any(org['name'] == '子組織' for org in data)
