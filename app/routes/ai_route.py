from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request
from flask_login import login_required
from app.services import ai_service
from app.schemas import (
    AISuggestInputSchema,
    JobIdSchema,
    AIResultSchema,
    ErrorResponseSchema,
)

ai_bp = Blueprint("AI", __name__, url_prefix="/ai", description="AI 提案")

@ai_bp.route("/suggest")
class AISuggestResource(MethodView):
    @login_required
    @ai_bp.arguments(AISuggestInputSchema)
    @ai_bp.response(202, JobIdSchema)
    @ai_bp.response(400, ErrorResponseSchema)
    def post(self, data):
        """AI提案実行"""
        result, status = ai_service.enqueue_ai_task(data)
        return result, status

@ai_bp.route("/result/<job_id>")
class AIResultResource(MethodView):
    @login_required
    @ai_bp.response(200, AIResultSchema)
    @ai_bp.response(202, AIResultSchema)
    @ai_bp.response(500, ErrorResponseSchema)
    def get(self, job_id):
        """AI結果取得"""
        result, status = ai_service.get_ai_task_result(job_id)
        return result, status

