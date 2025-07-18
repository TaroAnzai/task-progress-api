from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request
from flask_login import login_required, current_user

from app.services import progress_updates_service
from app.schemas import (
    ProgressInputSchema,
    ProgressSchema,
    MessageSchema,
    ErrorResponseSchema,
)

progress_bp = Blueprint("Progress", __name__, description="進捗更新")

@progress_bp.route("/objectives/<int:objective_id>/progress")
class ProgressListResource(MethodView):
    @login_required
    @progress_bp.arguments(ProgressInputSchema)
    @progress_bp.response(201, MessageSchema)
    @progress_bp.response(400, ErrorResponseSchema)
    @progress_bp.response(403, ErrorResponseSchema)
    @progress_bp.response(404, ErrorResponseSchema)
    def post(self, data, objective_id):
        """進捗追加"""
        result, status = progress_updates_service.add_progress(objective_id, data, current_user)
        return result, status

    @login_required
    @progress_bp.response(200, ProgressSchema(many=True))
    @progress_bp.response(403, ErrorResponseSchema)
    @progress_bp.response(404, ErrorResponseSchema)
    def get(self, objective_id):
        """進捗一覧取得"""
        result, status = progress_updates_service.get_progress_list(objective_id, current_user)
        return result, status

@progress_bp.route("/objectives/<int:objective_id>/latest-progress")
class LatestProgressResource(MethodView):
    @login_required
    @progress_bp.response(200, ProgressSchema)
    @progress_bp.response(403, ErrorResponseSchema)
    @progress_bp.response(404, ErrorResponseSchema)
    def get(self, objective_id):
        """最新進捗取得"""
        result, status = progress_updates_service.get_latest_progress(objective_id, current_user)
        return result, status

@progress_bp.route("/progress/<int:progress_id>")
class ProgressResource(MethodView):
    @login_required
    @progress_bp.response(200, MessageSchema)
    @progress_bp.response(403, ErrorResponseSchema)
    @progress_bp.response(404, ErrorResponseSchema)
    def delete(self, progress_id):
        """進捗削除"""
        result, status = progress_updates_service.delete_progress(progress_id, current_user)
        return result, status

