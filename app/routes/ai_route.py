from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request
from flask_login import login_required
from marshmallow import Schema, fields

from app.services import ai_service

class AISuggestInputSchema(Schema):
    task_info = fields.Dict(required=True)
    mode = fields.Str(load_default="task_name")

class JobIdSchema(Schema):
    job_id = fields.Str()

class AIResultSchema(Schema):
    job_id = fields.Str()
    status = fields.Str()
    message = fields.Str(load_default=None)

ai_bp = Blueprint("AI", __name__, url_prefix="/ai", description="AI 提案")

@ai_bp.route("/suggest")
class AISuggestResource(MethodView):
    @login_required
    @ai_bp.arguments(AISuggestInputSchema)
    @ai_bp.response(202, JobIdSchema)
    def post(self, data):
        """AI提案実行"""
        result, status = ai_service.enqueue_ai_task(data)
        return result, status

@ai_bp.route("/result/<job_id>")
class AIResultResource(MethodView):
    @login_required
    @ai_bp.response(200, AIResultSchema)
    def get(self, job_id):
        """AI結果取得"""
        result, status = ai_service.get_ai_task_result(job_id)
        return result, status

