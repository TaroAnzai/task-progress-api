# tests/test_task_access_route.py

import pytest
from app.constants import TaskAccessLevelEnum

@pytest.fixture(scope="function")
def system_admin_client(systemadmin_user, login_as_user):
    """システム管理者でログインしたクライアントを返す"""
    client = login_as_user(systemadmin_user["user"]["email"], "adminpass")
    return client
@pytest.fixture(scope="function")
def test_task_data():
    """テスト用のタスクデータを返す"""
    return {
        "title": "Test Task",
        "description": "This is a test task",
        "due_date": "2024-12-31"
    }
@pytest.fixture(scope="function")
def created_task_for_access(system_admin_client, test_task_data):
    """アクセス権限テスト用にタスクを作成"""
    res = system_admin_client.post("/progress/tasks", json=test_task_data)
    assert res.status_code == 201
    return res.get_json()["task"]


@pytest.fixture(scope="function")
def setup_task_access(system_admin_client, task_access_users, created_task_for_access):
    """タスクに対して各ユーザーのアクセス権限を設定"""
    task_id = created_task_for_access['id']

    user_access = [
        {"user_id": task_access_users[level]["id"], "access_level": level}
        for level in ["view", "edit", "full", "owner"]
    ]
    org_access = []  # 必要に応じて組織アクセスも設定可能

    res = system_admin_client.put(
        f"/progress/tasks/{task_id}/scope/access_levels",
        json={"user_access": user_access, "organization_access": org_access}
    )
    assert res.status_code == 200
    return task_id


class TestTaskAccessLevelUpdate:
    """update_access_levelエンドポイントのテスト"""

    def test_update_access_level_success(self, system_admin_client, created_task_for_access, task_access_users):
        task_id = created_task_for_access['id']
        user = task_access_users['full']
        res = system_admin_client.put(
            f"/progress/tasks/{task_id}/scope/access_levels",
            json={
                "user_access": [{"user_id": user["id"], "access_level": "full"}],
                "organization_access": []
            }
        )
        assert res.status_code == 200
        assert res.get_json()["message"] == "アクセス設定を更新しました"

    def test_update_access_level_not_found(self, system_admin_client):
        res = system_admin_client.put(
            "/progress/tasks/9999/scope/access_levels",
            json={"user_access": [], "organization_access": []}
        )
        assert res.status_code == 404

    def test_update_access_level_forbidden(self, login_as_user, task_access_users, created_task_for_access):
        """FULL権限がないユーザーが更新しようとした場合403"""
        user = task_access_users["edit"]
        client = login_as_user(user["email"], "testpass")
        res = client.put(
            f"/progress/tasks/{created_task_for_access['id']}/scope/access_levels",
            json={"user_access": [], "organization_access": []}
        )
        assert res.status_code == 403


class TestTaskCorePermission:
    """タスク操作のアクセス権限テスト"""

    def test_view_user_permissions(self, login_as_user, task_access_users, setup_task_access):
        user = task_access_users["view"]
        client = login_as_user(user["email"], 'testpass')
        task_id = setup_task_access

        # タスク取得は成功
        res = client.get("/progress/tasks")
        assert res.status_code == 200

        # 更新・削除は403
        assert client.put(f"/progress/tasks/{task_id}", json={"title": "x"}).status_code == 403
        assert client.delete(f"/progress/tasks/{task_id}").status_code == 403

    def test_edit_user_permissions(self, login_as_user, task_access_users, setup_task_access):
        user = task_access_users["edit"]
        client = login_as_user(user["email"], 'testpass')
        task_id = setup_task_access

        # タスク取得成功
        assert client.get("/progress/tasks").status_code == 200

        # 更新・削除は403
        assert client.put(f"/progress/tasks/{task_id}", json={"title": "x"}).status_code == 403
        assert client.delete(f"/progress/tasks/{task_id}").status_code == 403

    def test_full_user_permissions(self, login_as_user, task_access_users, setup_task_access):
        user = task_access_users["full"]
        client = login_as_user(user["email"], 'testpass')
        task_id = setup_task_access

        # 更新成功
        assert client.put(f"/progress/tasks/{task_id}", json={"title": "updated"}).status_code == 200

        # 削除成功
        assert client.delete(f"/progress/tasks/{task_id}").status_code == 200

    def test_owner_user_permissions(self, login_as_user, task_access_users, setup_task_access):
        user = task_access_users["owner"]
        client = login_as_user(user["email"], 'testpass')
        task_id = setup_task_access

        # 更新成功
        assert client.put(f"/progress/tasks/{task_id}", json={"title": "updated"}).status_code == 200

        # 削除成功
        assert client.delete(f"/progress/tasks/{task_id}").status_code == 200


class TestTaskAccessList:
    """アクセス情報取得のテスト"""

    def test_get_task_users(self, system_admin_client, setup_task_access):
        res = system_admin_client.get(f"/progress/tasks/{setup_task_access}/scope/users")
        assert res.status_code == 200
        data = res.get_json()
        assert any(u for u in data if u["name"].startswith("TaskUser_"))

    def test_get_task_access_users(self, system_admin_client, setup_task_access):
        res = system_admin_client.get(f"/progress/tasks/{setup_task_access}/scope/access_users")
        assert res.status_code == 200
        data = res.get_json()
        assert all("access_level" in u for u in data)

    def test_get_task_access_organizations(self, system_admin_client, setup_task_access):
        res = system_admin_client.get(f"/progress/tasks/{setup_task_access}/scope/access_organizations")
        assert res.status_code == 200
        assert isinstance(res.get_json(), list)
