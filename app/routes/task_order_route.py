from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request
from flask_login import login_required
from marshmallow import Schema, fields

from app.services import task_order_service

class TaskOrderSchema(Schema):
    task_id = fields.Int()
    title = fields.Str()

class TaskOrderInputSchema(Schema):
    task_ids = fields.List(fields.Int(), required=True)

class MessageSchema(Schema):
    message = fields.Str()


task_order_bp = Blueprint("TaskOrder", __name__, url_prefix="/task_order", description="タスク並び順")

@task_order_bp.route('/<int:user_id>')
class TaskOrderResource(MethodView):
    @login_required
    @task_order_bp.response(200, TaskOrderSchema(many=True))
    def get(self, user_id):
        """タスク並び順取得"""
        resp = task_order_service.get_task_order(user_id)
        return resp.get_json(), resp.status_code

    @login_required
    @task_order_bp.arguments(TaskOrderInputSchema)
    @task_order_bp.response(200, MessageSchema)
    def post(self, data, user_id):
        """タスク並び順保存"""
        resp = task_order_service.save_task_order(user_id, data)
        return resp.get_json(), resp.status_code

