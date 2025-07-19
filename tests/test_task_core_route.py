# tests/test_task_core_route.py

import pytest
from datetime import datetime, date
from app.models import Task, Objective, Status
from app.constants import StatusEnum

@pytest.fixture(scope="function")
def test_task_data():
    """テスト用のタスクデータを返す"""
    return {
        "title": "Test Task",
        "description": "This is a test task",
        "due_date": "2024-12-31"
    }


@pytest.fixture(scope="function")
def created_task(system_admin_client, test_task_data):
    client = system_admin_client
    """エンドポイント経由でテスト用タスクを作成"""
    
    # タスクを作成
    res = client.post("/tasks", json=test_task_data)
    assert res.status_code == 201
    
    task_data = res.get_json()['task']
    task_data.update(test_task_data)  # 元のデータも含める
    return task_data


@pytest.fixture(scope="function")
def created_objective(client, created_task):
    """エンドポイント経由でテスト用オブジェクティブを作成"""
    objective_data = {
        "task_id": created_task["task_id"],
        "title": "Test Objective",
        "due_date": "2024-12-25"
    }
    
    res = client.post("/objectives", json=objective_data)
    assert res.status_code == 201
    
    objective_result = res.get_json()
    objective_result.update(objective_data)
    return objective_result


@pytest.fixture(scope="function")
def multiple_objectives(client, created_task):
    """複数のオブジェクティブを作成（順序テスト用）"""
    objectives = []
    for i in range(3):
        objective_data = {
            "task_id": created_task["id"],
            "title": f"Test Objective {i+1}",
            "due_date": "2024-12-25"
        }
        
        res = client.post("/objectives", json=objective_data)
        assert res.status_code == 201
        
        objective_result = res.get_json()
        objective_result.update(objective_data)
        objectives.append(objective_result)
    
    return objectives

class TestTaskCreation:
    """タスク作成のテスト"""
    
    def test_create_task_success(self, system_admin_client, test_task_data):
        client = system_admin_client
        """正常なタスク作成"""
       
        # タスク作成
        res = client.post("/tasks", json=test_task_data)
        assert res.status_code == 201
        
        data = res.get_json()
        assert data["message"] == "タスクを追加しました"
        assert "id" in data['task']
    
    def test_create_task_without_title(self, system_admin_client):
        client = system_admin_client
        """タイトルなしでタスク作成（エラー）"""
     
        # タイトルなしでタスク作成
        res = client.post("/tasks", json={"description": "Test"})
        assert res.status_code == 422
        
        data = res.get_json()
        assert 'title' in data["errors"]['json']
    
    def test_create_task_invalid_date(self, system_admin_client):
        client = system_admin_client
        """不正な日付でタスク作成（エラー）"""
       
        # 不正な日付でタスク作成
        res = client.post("/tasks", json={
            "title": "Test Task",
            "due_date": "invalid-date"
        })
        assert res.status_code == 400
        
        data = res.get_json()
        assert data["message"] == "日付の形式が正しくありません（YYYY-MM-DD）"
    
    def test_create_task_without_login(self, client, test_task_data):
        """ログインなしでタスク作成（エラー）"""
        res = client.post("/tasks", json=test_task_data)
        assert res.status_code == 401


class TestTaskUpdate:
    """タスク更新のテスト"""
    
    def test_update_task_success(self, client, created_task):
        """正常なタスク更新"""
        update_data = {
            "title": "Updated Task Title",
            "description": "Updated description",
            "due_date": "2025-01-15"
        }
        
        res = client.put(f"/tasks/{created_task['id']}", json=update_data)
        assert res.status_code == 200
        data = res.get_json()
        assert data["message"] == "タスクを更新しました"
    
    def test_update_task_status(self, client, created_task):
        """タスクのステータス更新"""
        # ステータス一覧を取得
        status_res = client.get("/statuses")
        assert status_res.status_code == 200
        statuses = status_res.get_json()
        
        # 最初のステータスIDを使用
        first_status_id = statuses[0]["id"]
        
        update_data = {"status_id": first_status_id}
        
        res = client.put(f"/tasks/{created_task['id']}", json=update_data)
        assert res.status_code == 200
        
        data = res.get_json()
        assert data["message"] == "タスクを更新しました"
    
    def test_update_task_invalid_status(self, client, created_task):
        """不正なステータスIDでタスク更新（エラー）"""
        update_data = {"status_id": 999}  # 存在しないステータスID
        
        res = client.put(f"/tasks/{created_task['id']}", json=update_data)
        assert res.status_code == 400
        
        data = res.get_json()
        assert data["message"] == "ステータスIDが不正です"
    
    def test_update_task_invalid_date(self, client, created_task):
        """不正な日付でタスク更新（エラー）"""
        update_data = {"due_date": "invalid-date"}
        
        res = client.put(f"/tasks/{created_task['id']}", json=update_data)
        assert res.status_code == 400
        
        data = res.get_json()
        assert data["message"] == "日付の形式が正しくありません（YYYY-MM-DD）"
    
    def test_update_nonexistent_task(self, system_admin_client):
        client = system_admin_client
        """存在しないタスクの更新（エラー）"""
       
        res = client.put("/tasks/999", json={"title": "Updated"})
        assert res.status_code == 404
        
        data = res.get_json()
        assert data["message"] == "タスクが見つかりません"


class TestTaskDeletion:
    """タスク削除のテスト"""
    
    def test_delete_task_success(self, client, created_task):
        """正常なタスク削除"""
        res = client.delete(f"/tasks/{created_task['id']}")
        assert res.status_code == 200
        
        data = res.get_json()
        assert data["message"] == "タスクを削除しました"
    
    def test_delete_nonexistent_task(self, system_admin_client):
        client = system_admin_client

        """存在しないタスクの削除（エラー）"""
       
        res = client.delete("/tasks/999")
        assert res.status_code == 404
        
        data = res.get_json()
        assert data["error"] == "タスクが見つかりません"


class TestTaskList:
    """タスク一覧取得のテスト"""
    
    def test_get_tasks_success(self, client, created_task):
        """正常なタスク一覧取得"""
        res = client.get("/tasks")
        assert res.status_code == 200
        
        data = res.get_json()['tasks']
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # 作成したタスクが含まれているか確認
        task_ids = [task["id"] for task in data]
        assert created_task["id"] in task_ids
    
    def test_get_tasks_without_login(self, client):
        """ログインなしでタスク一覧取得（エラー）"""
        client.post("/auth/logout")  # ログアウト
        
        res = client.get("/tasks")
        assert res.status_code == 401
    
    def test_get_tasks_empty_list(self, system_admin_client):
        client = system_admin_client
        """タスクがない場合の一覧取得"""
       
        res = client.get("/tasks")
        assert res.status_code == 200
        
        data = res.get_json()['tasks']
        assert isinstance(data, list)


class TestObjectiveOrder:
    """オブジェクティブ順序更新のテスト"""
    
    def test_update_objective_order_success(self, client, multiple_objectives):
        """正常なオブジェクティブ順序更新"""
        task_id = multiple_objectives[0]["task_id"]
        
        # 順序を逆転
        objective_ids = [obj['objective']["id"] for obj in multiple_objectives]
        reversed_order = list(reversed(objective_ids))
        
        res = client.post(f"/tasks/{task_id}/objectives/order", json={
            "order": reversed_order
        })
        assert res.status_code == 200
        
        data = res.get_json()
        assert data["message"] == "表示順を更新しました"
    
    def test_update_objective_order_invalid_data(self, client, multiple_objectives):
        """不正なデータでオブジェクティブ順序更新（エラー）"""
        task_id = multiple_objectives[0]["task_id"]
        
        # orderが文字列（不正）
        res = client.post(f"/tasks/{task_id}/objectives/order", json={
            "order": "invalid"
        })
        assert res.status_code == 400
        
        data = res.get_json()
        assert data["error"] == "order はオブジェクティブIDのリストである必要があります"
    
    def test_update_objective_order_missing_objective(self, client, multiple_objectives):
        """存在しないオブジェクティブIDで順序更新（エラー）"""
        task_id = multiple_objectives[0]["task_id"]
        
        # 存在しないオブジェクティブIDを含む
        res = client.post(f"/tasks/{task_id}/objectives/order", json={
            "order": [999, 1000, 1001]
        })
        assert res.status_code == 404
        
        data = res.get_json()
        assert "が見つかりません" in data["error"]
    
    def test_update_objective_order_empty_list(self, client, created_task):
        """空のリストでオブジェクティブ順序更新"""
        res = client.post(f"/tasks/{created_task['id']}/objectives/order", json={
            "order": []
        })
        assert res.status_code == 400
        
   
    def test_update_objective_order_without_order_field(self, client, created_task):
        """orderフィールドなしでオブジェクティブ順序更新（エラー）"""
        res = client.post(f"/tasks/{created_task['id']}/objectives/order", json={})
        assert res.status_code == 400
        
        data = res.get_json()
        assert data["error"] == "order はオブジェクティブIDのリストである必要があります"


class TestIntegration:
    """統合テスト"""
    
    def test_task_lifecycle(self, system_admin_client):
        client = system_admin_client
        """タスクのライフサイクル全体をテスト"""
      
        # 1. タスク作成
        task_data = {
            "title": "Integration Test Task",
            "description": "Test task for integration",
            "due_date": "2024-12-31"
        }
        
        create_res = client.post("/tasks", json=task_data)
        assert create_res.status_code == 201
        
        created_task = create_res.get_json()['task']
        task_id = created_task["id"]
        
        # 2. タスク一覧で確認
        list_res = client.get("/tasks")
        assert list_res.status_code == 200
        
        tasks = list_res.get_json()['tasks']
        task_ids = [task["id"] for task in tasks]
        assert task_id in task_ids
        
        # 3. タスク更新
        update_data = {"title": "Updated Integration Task"}
        update_res = client.put(f"/tasks/{task_id}", json=update_data)
        assert update_res.status_code == 200
        
        # 4. オブジェクティブ作成
        objective_data = {
            "task_id": task_id,
            "title": "Integration Objective"
        }
        
        obj_res = client.post("/objectives", json=objective_data)
        assert obj_res.status_code == 201
        
        objective = obj_res.get_json()['objective']
        objective_id = objective["id"]
        
        # 5. オブジェクティブ順序更新
        order_res = client.post(f"/tasks/{task_id}/objectives/order", json={
            "order": [objective_id]
        })
        assert order_res.status_code == 200
        
        # 6. タスク削除
        delete_res = client.delete(f"/tasks/{task_id}")
        assert delete_res.status_code == 200
        
        # 7. 削除後の一覧確認
        final_list_res = client.get("/tasks")
        assert final_list_res.status_code == 200
        
        final_tasks = final_list_res.get_json()['tasks']
        final_task_ids = [task["id"] for task in final_tasks]
        assert task_id not in final_task_ids  # 削除されたタスクは含まれない