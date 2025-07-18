from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request
from flask_login import login_required, current_user

from app.services import task_access_service
from app.schemas import (
    AccessUserSchema,
    OrgAccessSchema,
    AccessLevelInputSchema,
    MessageSchema,
    ErrorResponseSchema,
)

task_access_bp = Blueprint("TaskAccess", __name__, url_prefix="/tasks/<int:task_id>/scope", description="タスクアクセス")

@task_access_bp.route('/access_levels')
class AccessLevelResource(MethodView):
    @login_required
    @task_access_bp.arguments(AccessLevelInputSchema)
    @task_access_bp.response(200, MessageSchema)
    @task_access_bp.response(400, ErrorResponseSchema)
    @task_access_bp.response(403, ErrorResponseSchema)
    @task_access_bp.response(404, ErrorResponseSchema)
    def put(self, data, task_id):
        """アクセスレベル更新"""
        resp = task_access_service.update_access_level(task_id, data, current_user)
        data, status = resp.get_json(), resp.status_code
        return data, status

@task_access_bp.route('/users')
class TaskUsersResource(MethodView):
    @login_required
    @task_access_bp.response(200, AccessUserSchema(many=True))
    @task_access_bp.response(401, ErrorResponseSchema)
    def get(self, task_id):
        """タスクユーザー取得"""
        resp = task_access_service.get_task_users(task_id)
        return resp.get_json(), resp.status_code

@task_access_bp.route('/access_users')
class TaskAccessUsersResource(MethodView):
    @login_required
    @task_access_bp.response(200, AccessUserSchema(many=True))
    @task_access_bp.response(401, ErrorResponseSchema)
    def get(self, task_id):
        """ユーザーアクセス一覧"""
        resp = task_access_service.get_task_access_users(task_id)
        return resp.get_json(), resp.status_code

@task_access_bp.route('/access_organizations')
class TaskAccessOrganizationsResource(MethodView):
    @login_required
    @task_access_bp.response(200, OrgAccessSchema(many=True))
    @task_access_bp.response(401, ErrorResponseSchema)
    def get(self, task_id):
        """組織アクセス一覧"""
        resp = task_access_service.get_task_access_organizations(task_id)
        return resp.get_json(), resp.status_code

