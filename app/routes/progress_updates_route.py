from flask_smorest import Blueprint
from flask.views import MethodView
from flask_login import login_required, current_user
from app.service_errors import (
    ServiceValidationError,
    ServiceAuthenticationError,
    ServicePermissionError,
    ServiceNotFoundError,
)

from app.services import progress_updates_service
from app.schemas import (
    ProgressInputSchema,
    ProgressSchema,
    MessageSchema,
    ErrorResponseSchema,
)

progress_bp = Blueprint("Progress", __name__, description="進捗更新")

@progress_bp.errorhandler(ServiceValidationError)
def progress_validation_error(e):
    abort(400, message=str(e))

@progress_bp.errorhandler(ServiceAuthenticationError)
def progress_auth_error(e):
    abort(401, message=str(e))

@progress_bp.errorhandler(ServicePermissionError)
def progress_permission_error(e):
    abort(403, message=str(e))

@progress_bp.errorhandler(ServiceNotFoundError)
def progress_not_found_error(e):
    abort(404, message=str(e))


@progress_bp.route("/objectives/<int:objective_id>/progress")
class ProgressListResource(MethodView):
    @login_required
    @progress_bp.arguments(ProgressInputSchema)
    @progress_bp.response(201, MessageSchema)
    @progress_bp.alt_response(400, {
        "description": "Bad Request",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    @progress_bp.alt_response(403, {
        "description": "Forbidden",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    @progress_bp.alt_response(404, {
        "description": "Not Found",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def post(self, data, objective_id):
        """進捗追加"""
        message = progress_updates_service.add_progress(objective_id, data, current_user)
        return message

    @login_required
    @progress_bp.response(200, ProgressSchema(many=True))
    @progress_bp.alt_response(403, {
        "description": "Forbidden",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    @progress_bp.alt_response(404, {
        "description": "Not Found",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def get(self, objective_id):
        """進捗一覧取得"""
        progress_list = progress_updates_service.get_progress_list(objective_id, current_user)
        return progress_list

@progress_bp.route("/objectives/<int:objective_id>/latest-progress")
class LatestProgressResource(MethodView):
    @login_required
    @progress_bp.response(200, ProgressSchema)
    @progress_bp.alt_response(403, {
        "description": "Forbidden",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    @progress_bp.alt_response(404, {
        "description": "Not Found",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def get(self, objective_id):
        """最新進捗取得"""
        progress = progress_updates_service.get_latest_progress(objective_id, current_user)
        return progress

@progress_bp.route("/progress/<int:progress_id>")
class ProgressResource(MethodView):
    @login_required
    @progress_bp.response(200, MessageSchema)
    @progress_bp.alt_response(403, {
        "description": "Forbidden",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    @progress_bp.alt_response(404, {
        "description": "Not Found",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def delete(self, progress_id):
        """進捗削除"""
        message = progress_updates_service.delete_progress(progress_id, current_user)
        return message

