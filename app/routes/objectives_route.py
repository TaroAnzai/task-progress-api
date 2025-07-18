from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request
from flask_login import login_required, current_user

from app.services import objectives_service
from app.schemas import (
    ObjectiveSchema,
    ObjectiveInputSchema,
    ObjectiveResponseSchema,
    ObjectivesListSchema,
    StatusSchema,
    MessageSchema,
    ErrorResponseSchema,
)

objectives_bp = Blueprint("Objectives", __name__, description="オブジェクティブ管理")

@objectives_bp.route('/objectives')
class ObjectiveListResource(MethodView):
    @login_required
    @objectives_bp.arguments(ObjectiveInputSchema)
    @objectives_bp.response(201, ObjectiveResponseSchema)
    @objectives_bp.response(400, ErrorResponseSchema)
    @objectives_bp.response(403, ErrorResponseSchema)
    @objectives_bp.response(404, ErrorResponseSchema)
    def post(self, data):
        """オブジェクティブ作成"""
        result, status = objectives_service.create_objective(data, current_user)
        return result, status

@objectives_bp.route('/objectives/<int:objective_id>')
class ObjectiveResource(MethodView):
    @login_required
    @objectives_bp.arguments(ObjectiveInputSchema)
    @objectives_bp.response(200, ObjectiveResponseSchema)
    @objectives_bp.response(400, ErrorResponseSchema)
    @objectives_bp.response(403, ErrorResponseSchema)
    @objectives_bp.response(404, ErrorResponseSchema)
    def put(self, data, objective_id):
        """オブジェクティブ更新"""
        result, status = objectives_service.update_objective(objective_id, data, current_user)
        return result, status

    @login_required
    @objectives_bp.response(200, MessageSchema)
    @objectives_bp.response(403, ErrorResponseSchema)
    @objectives_bp.response(404, ErrorResponseSchema)
    def delete(self, objective_id):
        """オブジェクティブ削除"""
        result, status = objectives_service.delete_objective(objective_id, current_user)
        return result, status

    @login_required
    @objectives_bp.response(200, ObjectiveSchema)
    @objectives_bp.response(403, ErrorResponseSchema)
    @objectives_bp.response(404, ErrorResponseSchema)
    def get(self, objective_id):
        """オブジェクティブ詳細取得"""
        result, status = objectives_service.get_objective(objective_id, current_user)
        return result, status

@objectives_bp.route('/tasks/<int:task_id>/objectives')
class TaskObjectivesResource(MethodView):
    @login_required
    @objectives_bp.response(200, ObjectivesListSchema)
    @objectives_bp.response(403, ErrorResponseSchema)
    @objectives_bp.response(404, ErrorResponseSchema)
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

