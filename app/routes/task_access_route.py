from flask_smorest import Blueprint
from flask.views import MethodView
from flask_login import login_required, current_user
from app.service_errors import (
    ServiceValidationError,
    ServicePermissionError,
    ServiceNotFoundError,
)

from app.services import task_access_service
from app.schemas import (
    AccessUserSchema,
    OrgAccessSchema,
    AccessLevelInputSchema,
    MessageSchema,
    ErrorResponseSchema,
)

task_access_bp = Blueprint("TaskAccess", __name__, url_prefix="/tasks/<int:task_id>/scope", description="タスクアクセス")

@task_access_bp.errorhandler(ServiceValidationError)
def task_access_validation_error(e):
    return {"message": str(e)}, 400


@task_access_bp.errorhandler(ServicePermissionError)
def task_access_permission_error(e):
    return {"message": str(e)}, 403

@task_access_bp.errorhandler(ServiceNotFoundError)
def task_access_not_found_error(e):
    return {"message": str(e)}, 404


@task_access_bp.route('/access_levels')
class AccessLevelResource(MethodView):
    @login_required
    @task_access_bp.arguments(AccessLevelInputSchema)
    @task_access_bp.response(200, MessageSchema)
    @task_access_bp.alt_response(400, {
        "description": "Bad Request",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    @task_access_bp.alt_response(403, {
        "description": "Forbidden",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    @task_access_bp.alt_response(404, {
        "description": "Not Found",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def put(self, data, task_id):
        """アクセスレベル更新"""
        resp = task_access_service.update_access_level(task_id, data, current_user)
        return resp

@task_access_bp.route('/users')
class TaskUsersResource(MethodView):
    @login_required
    @task_access_bp.response(200, AccessUserSchema(many=True))
    @task_access_bp.alt_response(401, {
        "description": "Unauthorized",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def get(self, task_id):
        """タスクユーザー取得"""
        resp = task_access_service.get_task_users(task_id)
        return resp

@task_access_bp.route('/access_users')
class TaskAccessUsersResource(MethodView):
    @login_required
    @task_access_bp.response(200, AccessUserSchema(many=True))
    @task_access_bp.alt_response(401, {
        "description": "Unauthorized",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def get(self, task_id):
        """ユーザーアクセス一覧"""
        resp = task_access_service.get_task_access_users(task_id)
        return resp

@task_access_bp.route('/access_organizations')
class TaskAccessOrganizationsResource(MethodView):
    @login_required
    @task_access_bp.response(200, OrgAccessSchema(many=True))
    @task_access_bp.alt_response(401, {
        "description": "Unauthorized",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def get(self, task_id):
        """組織アクセス一覧"""
        resp = task_access_service.get_task_access_organizations(task_id)
        return resp

