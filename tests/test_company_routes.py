import pytest
from app import db
from app.models import Company

@pytest.fixture
def create_company_data():
    return {"name": "Test Company"}

def test_create_company(superuser_login, create_company_data):
    response = superuser_login.post("/progress/companies", json=create_company_data)
    assert response.status_code == 201
    assert response.json["name"] == create_company_data["name"]



def test_list_companies(superuser_login):
    response = superuser_login.get("/progress/companies")
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_get_company_by_id(superuser_login):
    # 会社作成
    post_response = superuser_login.post("/progress/companies", json={"name": "by_id"})
    assert post_response.status_code == 201
    company_id = post_response.json["id"]

    # 取得
    get_response = superuser_login.get(f"/progress/companies/{company_id}")
    assert get_response.status_code == 200
    assert get_response.json["id"] == company_id

def test_update_company(superuser_login):
    # 作成
    post_response = superuser_login.post("/progress/companies", json={"name": "Old Name"})
    company_id = post_response.json["id"]

    # 更新
    response = superuser_login.put(f"/progress/companies/{company_id}", json={"name": "New Name"})
    assert response.status_code == 200
    assert response.json["name"] == "New Name"

def test_delete_and_restore_company(superuser_login):
    # 作成
    post_response = superuser_login.post("/progress/companies", json={"name": "Delete Me"})
    company_id = post_response.json["id"]

    # 論理削除
    delete_response = superuser_login.delete(f"/progress/companies/{company_id}")
    assert delete_response.status_code == 200

    # 通常取得で見えない
    get_response = superuser_login.get(f"/progress/companies/{company_id}")
    assert get_response.status_code == 404

    # 削除済も含む取得で確認
    with_deleted = superuser_login.get(f"/progress/companies/{company_id}?with_deleted=true")
    assert with_deleted.status_code == 200

    # 復元
    restore = superuser_login.post(f"/progress/companies/{company_id}/restore")
    assert restore.status_code == 200

    # 復元後は通常取得で見える
    restored_get = superuser_login.get(f"/progress/companies/{company_id}")
    assert restored_get.status_code == 200

def test_permanent_delete_company(superuser_login):
    # 作成
    post_response = superuser_login.post("/progress/companies", json={"name": "Permanent Delete"})
    company_id = post_response.json["id"]

    # 物理削除
    response = superuser_login.delete(f"/progress/companies/{company_id}?force=true")
    assert response.status_code == 200

    # with_deleted でも見えない
    get_response = superuser_login.get(f"/progress/companies/with_deleted/{company_id}")
    assert get_response.status_code == 404
