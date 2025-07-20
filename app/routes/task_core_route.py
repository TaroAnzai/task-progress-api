from flask_smorest import Blueprint
from flask.views import MethodView
from flask_login import login_required, current_user
from app.service_errors import ServiceError
from app.decorators import with_common_error_responses
from app.services import task_core_service
from app.schemas import (
    TaskSchema,
    TaskInputSchema,
    TaskUpdateSchema,
    TaskCreateResponseSchema,
    TaskListResponseSchema,
    OrderSchema,
    MessageSchema,
    ErrorResponseSchema,
)

task_core_bp = Blueprint("Tasks", __name__, url_prefix="/tasks", description="タスク管理")

@task_core_bp.errorhandler(ServiceError)
def handle_service_error(e: ServiceError):
    return {"message": str(e)}, e.status_code


@task_core_bp.route("")
class TaskListResource(MethodView):
    @login_required
    @task_core_bp.arguments(TaskInputSchema)
    @task_core_bp.response(201, TaskCreateResponseSchema)
    @with_common_error_responses(task_core_bp)
    def post(self, data):
        """タスク作成"""
        resp = task_core_service.create_task(data, current_user)
        return {"message":"タスクを追加しました", "task":resp}

    @login_required
    @task_core_bp.response(200, TaskListResponseSchema)
    @with_common_error_responses(task_core_bp)
    def get(self):
        """タスク一覧"""
        resp = task_core_service.get_tasks(current_user)
        return {"tasks": resp} 

@task_core_bp.route("/<int:task_id>")
class TaskResource(MethodView):
    @login_required
    @task_core_bp.arguments(TaskUpdateSchema)
    @task_core_bp.response(200, MessageSchema)
    @with_common_error_responses(task_core_bp)
    def put(self, data, task_id):
        """タスク更新"""
        resp = task_core_service.update_task(task_id, data, current_user)
        return {'message':'タスクを更新しました', 'task':resp}

    @login_required
    @task_core_bp.response(200, MessageSchema)
    @with_common_error_responses(task_core_bp)
    def delete(self, task_id):
        """タスク削除"""
        task_core_service.delete_task(task_id, current_user)
        return {'message':'タスクを削除しました'}

@task_core_bp.route("/<int:task_id>/objectives/order")
class ObjectiveOrderResource(MethodView):
    @login_required
    @task_core_bp.arguments(OrderSchema)
    @task_core_bp.response(200, MessageSchema)
    @with_common_error_responses(task_core_bp)
    def post(self, data, task_id):
        """オブジェクティブ順序更新"""
        resp = task_core_service.update_objective_order(task_id, data)
        return resp

