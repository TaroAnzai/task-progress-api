from flask_smorest import Blueprint
from flask.views import MethodView
from flask_login import login_required, current_user
from app.service_errors import (
    ServiceValidationError,
    ServiceAuthenticationError,
    ServicePermissionError,
    ServiceNotFoundError,
)
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

@task_core_bp.errorhandler(ServiceValidationError)
def task_core_validation_error(e):
    return {"message": str(e)}, 400

@task_core_bp.errorhandler(ServiceAuthenticationError)
def task_core_auth_error(e):
    return {"message": str(e)}, 401

@task_core_bp.errorhandler(ServicePermissionError)
def task_core_permission_error(e):
    return {"message": str(e)}, 403

@task_core_bp.errorhandler(ServiceNotFoundError)
def task_core_not_found_error(e):
    return {"message": str(e)}, 404


@task_core_bp.route("")
class TaskListResource(MethodView):
    @login_required
    @task_core_bp.arguments(TaskInputSchema)
    @task_core_bp.response(201, TaskCreateResponseSchema)
    @task_core_bp.alt_response(400, {
        "description": "Bad Request",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def post(self, data):
        """タスク作成"""
        resp = task_core_service.create_task(data, current_user)
        return resp

    @login_required
    @task_core_bp.response(200, TaskListResponseSchema)
    @task_core_bp.alt_response(401, {
        "description": "Unauthorized",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def get(self):
        """タスク一覧"""
        resp = task_core_service.get_tasks(current_user)
        return resp

@task_core_bp.route("/<int:task_id>")
class TaskResource(MethodView):
    @login_required
    @task_core_bp.arguments(TaskInputSchema)
    @task_core_bp.response(200, MessageSchema)
    @task_core_bp.alt_response(400, {
        "description": "Bad Request",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    @task_core_bp.alt_response(403, {
        "description": "Forbidden",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    @task_core_bp.alt_response(404, {
        "description": "Not Found",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def put(self, data, task_id):
        """タスク更新"""
        resp = task_core_service.update_task(task_id, data, current_user)
        return resp

    @login_required
    @task_core_bp.response(200, MessageSchema)
    @task_core_bp.alt_response(403, {
        "description": "Forbidden",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    @task_core_bp.alt_response(404, {
        "description": "Not Found",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def delete(self, task_id):
        """タスク削除"""
        resp = task_core_service.delete_task(task_id, current_user)
        return resp

@task_core_bp.route("/<int:task_id>/objectives/order")
class ObjectiveOrderResource(MethodView):
    @login_required
    @task_core_bp.arguments(OrderSchema)
    @task_core_bp.response(200, MessageSchema)
    @task_core_bp.alt_response(400, {
        "description": "Bad Request",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    @task_core_bp.alt_response(404, {
        "description": "Not Found",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def post(self, data, task_id):
        """オブジェクティブ順序更新"""
        resp = task_core_service.update_objective_order(task_id, data)
        return resp

