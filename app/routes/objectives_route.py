from flask_smorest import Blueprint
from flask.views import MethodView
from flask_login import login_required, current_user
from app.service_errors import (
    ServiceValidationError,
    ServiceAuthenticationError,
    ServicePermissionError,
    ServiceNotFoundError,
)

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

@objectives_bp.errorhandler(ServiceValidationError)
def objectives_validation_error(e):
    abort(400, message=str(e))

@objectives_bp.errorhandler(ServiceAuthenticationError)
def objectives_auth_error(e):
    abort(401, message=str(e))

@objectives_bp.errorhandler(ServicePermissionError)
def objectives_permission_error(e):
    abort(403, message=str(e))

@objectives_bp.errorhandler(ServiceNotFoundError)
def objectives_not_found_error(e):
    abort(404, message=str(e))


@objectives_bp.route('/objectives')
class ObjectiveListResource(MethodView):
    @login_required
    @objectives_bp.arguments(ObjectiveInputSchema)
    @objectives_bp.response(201, ObjectiveResponseSchema)
    @objectives_bp.alt_response(400, {
        "description": "Bad Request",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    @objectives_bp.alt_response(403, {
        "description": "Forbidden",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    @objectives_bp.alt_response(404, {
        "description": "Not Found",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def post(self, data):
        """オブジェクティブ作成"""
        objective = objectives_service.create_objective(data, current_user)
        return objective

@objectives_bp.route('/objectives/<int:objective_id>')
class ObjectiveResource(MethodView):
    @login_required
    @objectives_bp.arguments(ObjectiveInputSchema)
    @objectives_bp.response(200, ObjectiveResponseSchema)
    @objectives_bp.alt_response(400, {
        "description": "Bad Request",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    @objectives_bp.alt_response(403, {
        "description": "Forbidden",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    @objectives_bp.alt_response(404, {
        "description": "Not Found",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def put(self, data, objective_id):
        """オブジェクティブ更新"""
        objective = objectives_service.update_objective(objective_id, data, current_user)
        return objective

    @login_required
    @objectives_bp.response(200, MessageSchema)
    @objectives_bp.alt_response(403, {
        "description": "Forbidden",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    @objectives_bp.alt_response(404, {
        "description": "Not Found",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def delete(self, objective_id):
        """オブジェクティブ削除"""
        message = objectives_service.delete_objective(objective_id, current_user)
        return message

    @login_required
    @objectives_bp.response(200, ObjectiveSchema)
    @objectives_bp.alt_response(403, {
        "description": "Forbidden",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    @objectives_bp.alt_response(404, {
        "description": "Not Found",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def get(self, objective_id):
        """オブジェクティブ詳細取得"""
        objective = objectives_service.get_objective(objective_id, current_user)
        return objective

@objectives_bp.route('/tasks/<int:task_id>/objectives')
class TaskObjectivesResource(MethodView):
    @login_required
    @objectives_bp.response(200, ObjectivesListSchema)
    @objectives_bp.alt_response(403, {
        "description": "Forbidden",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    @objectives_bp.alt_response(404, {
        "description": "Not Found",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def get(self, task_id):
        """タスクのオブジェクティブ一覧"""
        objectives = objectives_service.get_objectives_for_task(task_id, current_user)
        return objectives

@objectives_bp.route('/statuses')
class StatusListResource(MethodView):
    @objectives_bp.response(200, StatusSchema(many=True))
    def get(self):
        """ステータス一覧"""
        result = objectives_service.get_statuses()
        return result

