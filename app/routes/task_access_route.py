from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request
from flask_login import login_required, current_user
from marshmallow import Schema, fields

from app.services import task_access_service

class AccessUserSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    email = fields.Str()
    access_level = fields.Str()

class OrgAccessSchema(Schema):
    organization_id = fields.Int()
    name = fields.Str()
    access_level = fields.Str()

class AccessLevelInputSchema(Schema):
    user_access = fields.List(fields.Dict(), required=True)
    organization_access = fields.List(fields.Dict(), required=True)

class MessageSchema(Schema):
    message = fields.Str()
    error = fields.Str(load_default=None)

task_access_bp = Blueprint("TaskAccess", __name__, url_prefix="/tasks/<int:task_id>/scope", description="タスクアクセス")

@task_access_bp.route('/access_levels')
class AccessLevelResource(MethodView):
    @login_required
    @task_access_bp.arguments(AccessLevelInputSchema)
    @task_access_bp.response(200, MessageSchema)
    def put(self, data, task_id):
        """アクセスレベル更新"""
        resp = task_access_service.update_access_level(task_id, data, current_user)
        data, status = resp.get_json(), resp.status_code
        return data, status

@task_access_bp.route('/users')
class TaskUsersResource(MethodView):
    @login_required
    @task_access_bp.response(200, AccessUserSchema(many=True))
    def get(self, task_id):
        """タスクユーザー取得"""
        resp = task_access_service.get_task_users(task_id)
        return resp.get_json(), resp.status_code

@task_access_bp.route('/access_users')
class TaskAccessUsersResource(MethodView):
    @login_required
    @task_access_bp.response(200, AccessUserSchema(many=True))
    def get(self, task_id):
        """ユーザーアクセス一覧"""
        resp = task_access_service.get_task_access_users(task_id)
        return resp.get_json(), resp.status_code

@task_access_bp.route('/access_organizations')
class TaskAccessOrganizationsResource(MethodView):
    @login_required
    @task_access_bp.response(200, OrgAccessSchema(many=True))
    def get(self, task_id):
        """組織アクセス一覧"""
        resp = task_access_service.get_task_access_organizations(task_id)
        return resp.get_json(), resp.status_code

