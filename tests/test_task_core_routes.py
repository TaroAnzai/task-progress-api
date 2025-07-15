import pytest
from app import db
from app.models import Task, Objective


@pytest.fixture(scope="module")
def task_data():
    return {"title": "テストタスク", "description": "テスト用の説明"}


@pytest.fixture(scope="module")
def created_task(client, superuser_login, task_data):
    res = superuser_login.post("/tasks", json=task_data)
    assert res.status_code == 201
    data = res.get_json()
    assert "task_id" in data
    return data  # {'message': 'タスクを追加しました', 'task_id': 1}


def test_create_task(client, superuser_login):
    res = superuser_login.post("/tasks", json={"title": "新規タスク"})
    assert res.status_code == 201
    data = res.get_json()
    assert data["message"] == "タスクを追加しました"
    assert isinstance(data["task_id"], int)


def test_create_task_invalid_date(client, superuser_login):
    res = superuser_login.post("/tasks", json={"title": "日付エラー", "due_date": "2025-99-99"})
    assert res.status_code == 400
    assert "日付の形式" in res.get_json()["error"]


def test_get_tasks(client, superuser_login, created_task):
    res = superuser_login.get("/tasks")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
    assert any(t["id"] == created_task["task_id"] for t in data)


def test_update_task(client, superuser_login, created_task):
    res = superuser_login.put(f"/tasks/{created_task['task_id']}", json={"title": "更新後タスク"})
    assert res.status_code == 200
    assert "タスクを更新しました" in res.get_json()["message"]

    # 更新結果確認
    updated_task = db.session.get(Task, created_task["task_id"])
    assert updated_task.title == "更新後タスク"


def test_update_task_invalid_date(client, superuser_login, created_task):
    res = superuser_login.put(f"/tasks/{created_task['task_id']}", json={"due_date": "2025-99-99"})
    assert res.status_code == 400
    assert "日付の形式" in res.get_json()["error"]


def test_update_objective_order(client, superuser_login, created_task):
    # 1. オブジェクティブを追加
    obj1 = Objective(task_id=created_task["task_id"], title="obj1")
    obj2 = Objective(task_id=created_task["task_id"], title="obj2")
    db.session.add_all([obj1, obj2])
    db.session.commit()

    # 2. 順序更新
    res = superuser_login.post(
        f"/tasks/{created_task['task_id']}/objectives/order",
        json={"order": [obj2.id, obj1.id]},
    )
    assert res.status_code == 200
    assert "表示順を更新しました" in res.get_json()["message"]

    # 3. DB上の順序確認
    db.session.refresh(obj1)
    db.session.refresh(obj2)
    assert obj2.display_order == 0
    assert obj1.display_order == 1


def test_update_objective_order_invalid(client, superuser_login, created_task):
    res = superuser_login.post(
        f"/tasks/{created_task['task_id']}/objectives/order",
        json={"order": [99999]},
    )
    assert res.status_code == 404
    assert "見つかりません" in res.get_json()["error"]


def test_delete_task(client, superuser_login, created_task):
    res = superuser_login.delete(f"/tasks/{created_task['task_id']}")
    assert res.status_code == 200
    assert "タスクを削除しました" in res.get_json()["message"]

    # 論理削除されているか確認
    deleted_task = db.session.get(Task, created_task["task_id"])
    assert deleted_task.is_deleted
