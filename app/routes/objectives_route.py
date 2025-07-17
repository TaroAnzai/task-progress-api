from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request
from flask_login import login_required, current_user
from marshmallow import Schema, fields

from app.services import objectives_service

class ObjectiveSchema(Schema):
    id = fields.Int()
    task_id = fields.Int()
    title = fields.Str()
    due_date = fields.Str(allow_none=True)
    assigned_user_id = fields.Int(allow_none=True)
    status_id = fields.Int()
    created_by = fields.Int()
    created_at = fields.Str()

class ObjectiveInputSchema(Schema):
    task_id = fields.Int(required=True)
    title = fields.Str(required=True)
    due_date = fields.Str(load_default=None)
    assigned_user_id = fields.Int(load_default=None)
    status_id = fields.Int(load_default=None)

class MessageSchema(Schema):
    message = fields.Str()
    error = fields.Str(load_default=None)

class StatusSchema(Schema):
    id = fields.Int()
    label = fields.Str()

objectives_bp = Blueprint("Objectives", __name__, description="オブジェクティブ管理")

@objectives_bp.route('/objectives')
class ObjectiveListResource(MethodView):
    @login_required
    @objectives_bp.arguments(ObjectiveInputSchema)
    @objectives_bp.response(201, MessageSchema)
    def post(self, data):
        """オブジェクティブ作成"""
        result, status = objectives_service.create_objective(data, current_user)
        return result, status

@objectives_bp.route('/objectives/<int:objective_id>')
class ObjectiveResource(MethodView):
    @login_required
    @objectives_bp.arguments(ObjectiveInputSchema)
    @objectives_bp.response(200, MessageSchema)
    def put(self, data, objective_id):
        """オブジェクティブ更新"""
        result, status = objectives_service.update_objective(objective_id, data, current_user)
        return result, status

    @login_required
    @objectives_bp.response(200, MessageSchema)
    def delete(self, objective_id):
        """オブジェクティブ削除"""
        result, status = objectives_service.delete_objective(objective_id, current_user)
        return result, status

    @login_required
    @objectives_bp.response(200, ObjectiveSchema)
    def get(self, objective_id):
        """オブジェクティブ詳細取得"""
        result, status = objectives_service.get_objective(objective_id, current_user)
        return result, status

@objectives_bp.route('/tasks/<int:task_id>/objectives')
class TaskObjectivesResource(MethodView):
    @login_required
    @objectives_bp.response(200, fields.Dict())
    def get(self, task_id):
        """タスクのオブジェクティブ一覧"""
        result, status = objectives_service.get_objectives_for_task(task_id, current_user)
        return result, status

@objectives_bp.route('/statuses')
class StatusListResource(MethodView):
    @objectives_bp.response(200, StatusSchema(many=True))
    def get(self):
        """ステータス一覧"""
        result = objectives_service.get_statuses()
        return result

