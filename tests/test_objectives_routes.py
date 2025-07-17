import pytest

@pytest.fixture(scope="function")
def test_task_data():
    """テスト用のタスクデータを返す"""
    return {
        "title": "Test Task",
        "description": "This is a test task",
        "due_date": "2024-12-31"
    }


@pytest.fixture(scope="function")
def task(system_admin_client, test_task_data):
    client = system_admin_client
    """エンドポイント経由でテスト用タスクを作成"""
    
    # タスクを作成
    res = client.post("/tasks", json=test_task_data)
    assert res.status_code == 201
    
    task_data = res.get_json()['task']
    task_data.update(test_task_data)  # 元のデータも含める
    return task_data
@pytest.fixture
def make_objective_data(task):
    def _make(title="test objective", due_date=None, assigned_user_id=None):
        data = {
            "title": title,
            "task_id": task["id"],
        }
        if due_date:
            data["due_date"] = due_date
        if assigned_user_id:
            data["assigned_user_id"] = assigned_user_id
        return data
    return _make

class TestObjectivesAPI:
    @pytest.fixture(autouse=True)
    def setup(self, task_access_users, task, login_as_user, make_objective_data, setup_task_access):
        # full/edit/viewユーザーをセット
        self.users = task_access_users
        self.task = task
        self.make_objective_data = make_objective_data
        self.login_as_user = login_as_user
        setup_task_access(task)

    def test_get_objectives_for_task_view(self):
        print(self.task)
        user = self.users['view']
        client = self.login_as_user(user['email'], user['password'])
        resp = client.get(f"/tasks/{self.task['id']}/objectives")
        assert resp.status_code == 200

    def test_create_objective_full(self):
        user = self.users['full']
        client = self.login_as_user(user['email'], user['password'])
        data = self.make_objective_data()
        resp = client.post("/objectives", json=data)
        assert resp.status_code == 201

    def test_create_objective_edit(self):
        user = self.users['edit']
        client = self.login_as_user(user['email'], user['password'])
        data = self.make_objective_data()
        resp = client.post("/objectives", json=data)
        assert resp.status_code == 201

    def test_create_objective_view(self):
        user = self.users['view']
        client = self.login_as_user(user['email'], user['password'])
        data = self.make_objective_data()
        resp = client.post("/objectives", json=data)
        assert resp.status_code == 403

    def test_update_objective_full(self, created_objective):
        user = self.users['full']
        client = self.login_as_user(user['email'], user['password'])
        resp = client.put(f"/objectives/{created_objective['id']}", json={"title": "updated"})
        assert resp.status_code == 200

    def test_update_objective_edit(self, created_objective):
        user = self.users['edit']
        client = self.login_as_user(user['email'], user['password'])
        resp = client.put(f"/objectives/{created_objective['id']}", json={"title": "updated"})
        assert resp.status_code == 200

    def test_update_objective_view(self, created_objective):
        user = self.users['view']
        client = self.login_as_user(user['email'], user['password'])
        resp = client.put(f"/objectives/{created_objective['id']}", json={"title": "updated"})
        assert resp.status_code == 403

    def test_delete_objective_full(self, created_objective):
        user = self.users['full']
        client = self.login_as_user(user['email'], user['password'])
        resp = client.delete(f"/objectives/{created_objective['id']}")
        assert resp.status_code == 200

    def test_delete_objective_edit(self, created_objective):
        user = self.users['edit']
        client = self.login_as_user(user['email'], user['password'])
        resp = client.delete(f"/objectives/{created_objective['id']}")
        assert resp.status_code == 200

    def test_delete_objective_view(self, created_objective):
        user = self.users['view']
        client = self.login_as_user(user['email'], user['password'])
        resp = client.delete(f"/objectives/{created_objective['id']}")
        assert resp.status_code == 403

    def test_get_objective_detail_view(self, created_objective):
        user = self.users['view']
        client = self.login_as_user(user['email'], user['password'])
        resp = client.get(f"/objectives/{created_objective['id']}")
        assert resp.status_code == 200

    def test_get_objective_detail_edit(self, created_objective):
        user = self.users['edit']
        client = self.login_as_user(user['email'], user['password'])
        resp = client.get(f"/objectives/{created_objective['id']}")
        assert resp.status_code == 200

    def test_get_objective_detail_full(self, created_objective):
        user = self.users['full']
        client = self.login_as_user(user['email'], user['password'])
        resp = client.get(f"/objectives/{created_objective['id']}")
        assert resp.status_code == 200

@pytest.fixture
def created_objective(client, login_as_user, task_access_users, make_objective_data):
    """full権限でObjectiveを1件作成し、そのdictを返す"""
    user = task_access_users['full']
    client = login_as_user(user['email'], user['password'])
    data = make_objective_data()
    resp = client.post("/objectives", json=data)
    assert resp.status_code == 201
    obj_id = resp.get_json()['objective']["id"]
    return {"id": obj_id}