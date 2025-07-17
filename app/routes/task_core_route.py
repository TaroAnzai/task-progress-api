from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request
from flask_login import login_required, current_user
from marshmallow import Schema, fields

from app.services import task_core_service

class TaskSchema(Schema):
    id = fields.Int()
    status_id = fields.Int(allow_none=True)
    title = fields.Str()
    description = fields.Str()
    due_date = fields.Str(allow_none=True)
    assigned_user_id = fields.Int(allow_none=True)
    created_by = fields.Int()
    created_at = fields.Str()
    display_order = fields.Int(allow_none=True)
    organization_id = fields.Int()

class TaskInputSchema(Schema):
    title = fields.Str(required=True)
    description = fields.Str(load_default="")
    due_date = fields.Str(load_default=None)
    status_id = fields.Int(load_default=None)
    display_order = fields.Int(load_default=None)

class OrderSchema(Schema):
    order = fields.List(fields.Int(), required=True)

class MessageSchema(Schema):
    message = fields.Str()
    error = fields.Str(load_default=None)

task_core_bp = Blueprint("Tasks", __name__, url_prefix="/tasks", description="タスク管理")

@task_core_bp.route("")
class TaskListResource(MethodView):
    @login_required
    @task_core_bp.arguments(TaskInputSchema)
    @task_core_bp.response(201, MessageSchema)
    def post(self, data):
        """タスク作成"""
        resp, status = task_core_service.create_task(data, current_user)
        return resp.get_json(), status

    @login_required
    @task_core_bp.response(200, fields.Dict())
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
    def put(self, data, task_id):
        """タスク更新"""
        resp, status = task_core_service.update_task(task_id, data, current_user)
        return resp.get_json(), status

    @login_required
    @task_core_bp.response(200, MessageSchema)
    def delete(self, task_id):
        """タスク削除"""
        resp, status = task_core_service.delete_task(task_id, current_user)
        return resp.get_json(), status

@task_core_bp.route("/<int:task_id>/objectives/order")
class ObjectiveOrderResource(MethodView):
    @login_required
    @task_core_bp.arguments(OrderSchema)
    @task_core_bp.response(200, MessageSchema)
    def post(self, data, task_id):
        """オブジェクティブ順序更新"""
        resp, status = task_core_service.update_objective_order(task_id, data)
        return resp.get_json(), status

