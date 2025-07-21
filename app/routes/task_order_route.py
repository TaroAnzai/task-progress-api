from app.service_errors import format_error_response
from flask import jsonify, request
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask_login import login_required
from app.service_errors import ServiceError
from app.decorators import with_common_error_responses
from app.services import task_order_service
from app.schemas import (
    TaskOrderSchema,
    TaskOrderInputSchema,
    MessageSchema,
    ErrorResponseSchema,
)


task_order_bp = Blueprint("TaskOrder", __name__, url_prefix="/task_orders", description="タスク並び順")

@task_order_bp.errorhandler(ServiceError)
def handle_service_error(e: ServiceError):
    return jsonify(format_error_response(e.code, e.name, e.description)), e.code


@task_order_bp.route('')
class TaskOrderResource(MethodView):
    @login_required
    @task_order_bp.response(200, TaskOrderSchema(many=True))
    @with_common_error_responses(task_order_bp)
    def get(self):
        """タスク並び順取得"""
        user_id = request.args.get("user_id", type=int)
        if not user_id:
            abort(400, description='user_id requires ?user_id=user_id')
        resp = task_order_service.get_task_order(user_id)
        return resp

    @login_required
    @task_order_bp.arguments(TaskOrderInputSchema)
    @task_order_bp.response(200, MessageSchema)
    @with_common_error_responses(task_order_bp)
    def post(self, data, user_id):
        """タスク並び順保存"""
        resp = task_order_service.save_task_order(user_id, data)
        return resp

