from flask_smorest import Blueprint
from flask.views import MethodView
from flask_login import login_required
from app.service_errors import (
    ServiceValidationError,
    ServicePermissionError,
    ServiceNotFoundError,
)

from app.services import task_order_service
from app.schemas import (
    TaskOrderSchema,
    TaskOrderInputSchema,
    MessageSchema,
    ErrorResponseSchema,
)


task_order_bp = Blueprint("TaskOrder", __name__, url_prefix="/task_order", description="タスク並び順")

@task_order_bp.errorhandler(ServiceValidationError)
def task_order_validation_error(e):
    return {"message": str(e)}, 400


@task_order_bp.errorhandler(ServicePermissionError)
def task_order_permission_error(e):
    return {"message": str(e)}, 403

@task_order_bp.errorhandler(ServiceNotFoundError)
def task_order_not_found_error(e):
    return {"message": str(e)}, 404


@task_order_bp.route('/<int:user_id>')
class TaskOrderResource(MethodView):
    @login_required
    @task_order_bp.response(200, TaskOrderSchema(many=True))
    @task_order_bp.alt_response(404, {
        "description": "Not Found",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def get(self, user_id):
        """タスク並び順取得"""
        resp = task_order_service.get_task_order(user_id)
        return resp

    @login_required
    @task_order_bp.arguments(TaskOrderInputSchema)
    @task_order_bp.response(200, MessageSchema)
    @task_order_bp.alt_response(400, {
        "description": "Bad Request",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def post(self, data, user_id):
        """タスク並び順保存"""
        resp = task_order_service.save_task_order(user_id, data)
        return resp

