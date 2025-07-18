from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request
from flask_login import login_required, current_user
from app.services import task_core_service
from app.schemas import (
    TaskSchema,
    TaskInputSchema,
    TaskCreateResponseSchema,
    TaskListResponseSchema,
    OrderSchema,
    MessageSchema,
    ErrorResponseSchema,
)

task_core_bp = Blueprint("Tasks", __name__, url_prefix="/tasks", description="タスク管理")

@task_core_bp.route("")
class TaskListResource(MethodView):
    @login_required
    @task_core_bp.arguments(TaskInputSchema)
    @task_core_bp.response(201, TaskCreateResponseSchema)
    @task_core_bp.response(400, ErrorResponseSchema)
    def post(self, data):
        """タスク作成"""
        resp, status = task_core_service.create_task(data, current_user)
        return resp, status

    @login_required
    @task_core_bp.response(200, TaskListResponseSchema)
    @task_core_bp.response(401, ErrorResponseSchema)
    def get(self):
        """タスク一覧"""
        resp, status = task_core_service.get_tasks(current_user)
        if isinstance(resp, dict):
            return resp, status
        return resp.get_json(), status

@task_core_bp.route("/<int:task_id>")
class TaskResource(MethodView):
    @login_required
    @task_core_bp.arguments(TaskInputSchema)
    @task_core_bp.response(200, MessageSchema)
    @task_core_bp.response(400, ErrorResponseSchema)
    @task_core_bp.response(403, ErrorResponseSchema)
    @task_core_bp.response(404, ErrorResponseSchema)
    def put(self, data, task_id):
        """タスク更新"""
        resp, status = task_core_service.update_task(task_id, data, current_user)
        return resp.get_json(), status

    @login_required
    @task_core_bp.response(200, MessageSchema)
    @task_core_bp.response(403, ErrorResponseSchema)
    @task_core_bp.response(404, ErrorResponseSchema)
    def delete(self, task_id):
        """タスク削除"""
        resp, status = task_core_service.delete_task(task_id, current_user)
        return resp.get_json(), status

@task_core_bp.route("/<int:task_id>/objectives/order")
class ObjectiveOrderResource(MethodView):
    @login_required
    @task_core_bp.arguments(OrderSchema)
    @task_core_bp.response(200, MessageSchema)
    @task_core_bp.response(400, ErrorResponseSchema)
    @task_core_bp.response(404, ErrorResponseSchema)
    def post(self, data, task_id):
        """オブジェクティブ順序更新"""
        resp, status = task_core_service.update_objective_order(task_id, data)
        return resp.get_json(), status

