import pytest
from app import db
from app.models import Company

@pytest.fixture
def create_company_data():
    return {"name": "Test Company"}

def test_create_company(client, login_superuser, create_company_data):
    response = client.post("/companies/", json=create_company_data)
    assert response.status_code == 201
    assert response.json["name"] == create_company_data["name"]



def test_list_companies(client, login_superuser):
    response = client.get("/companies/")
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_get_company_by_id(client, login_superuser):
    # 会社作成
    post_response = client.post("/companies/", json={"name": "by_id"})
    assert post_response.status_code == 201
    company_id = post_response.json["id"]

    # 取得
    get_response = client.get(f"/companies/{company_id}")
    assert get_response.status_code == 200
    assert get_response.json["id"] == company_id

def test_update_company(client, login_superuser):
    # 作成
    post_response = client.post("/companies/", json={"name": "Old Name"})
    company_id = post_response.json["id"]

    # 更新
    response = client.put(f"/companies/{company_id}", json={"name": "New Name"})
    assert response.status_code == 200
    assert response.json["name"] == "New Name"

def test_delete_and_restore_company(client, login_superuser):
    # 作成
    post_response = client.post("/companies/", json={"name": "Delete Me"})
    company_id = post_response.json["id"]

    # 論理削除
    delete_response = client.delete(f"/companies/{company_id}")
    assert delete_response.status_code == 200

    # 通常取得で見えない
    get_response = client.get(f"/companies/{company_id}")
    assert get_response.status_code == 404

    # 削除済も含む取得で確認
    with_deleted = client.get(f"/companies/with_deleted/{company_id}")
    assert with_deleted.status_code == 200

    # 復元
    restore = client.post(f"/companies/restore/{company_id}")
    assert restore.status_code == 200

    # 復元後は通常取得で見える
    restored_get = client.get(f"/companies/{company_id}")
    assert restored_get.status_code == 200

def test_permanent_delete_company(client, login_superuser):
    # 作成
    post_response = client.post("/companies/", json={"name": "Permanent Delete"})
    company_id = post_response.json["id"]

    # 物理削除
    response = client.delete(f"/companies/permanent/{company_id}")
    assert response.status_code == 200

    # with_deleted でも見えない
    get_response = client.get(f"/companies/with_deleted/{company_id}")
    assert get_response.status_code == 404
