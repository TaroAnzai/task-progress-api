from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request
from flask_login import login_required

from app.services import task_order_service
from app.schemas import (
    TaskOrderSchema,
    TaskOrderInputSchema,
    MessageSchema,
    ErrorResponseSchema,
)


task_order_bp = Blueprint("TaskOrder", __name__, url_prefix="/task_order", description="タスク並び順")

@task_order_bp.route('/<int:user_id>')
class TaskOrderResource(MethodView):
    @login_required
    @task_order_bp.response(200, TaskOrderSchema(many=True))
    @task_order_bp.response(404, ErrorResponseSchema)
    def get(self, user_id):
        """タスク並び順取得"""
        resp = task_order_service.get_task_order(user_id)
        return resp.get_json(), resp.status_code

    @login_required
    @task_order_bp.arguments(TaskOrderInputSchema)
    @task_order_bp.response(200, MessageSchema)
    @task_order_bp.response(400, ErrorResponseSchema)
    def post(self, data, user_id):
        """タスク並び順保存"""
        resp = task_order_service.save_task_order(user_id, data)
        return resp.get_json(), resp.status_code

