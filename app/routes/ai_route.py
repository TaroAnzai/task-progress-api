from flask_smorest import Blueprint
from flask.views import MethodView
from flask_login import login_required
from app.services import ai_service
from app.schemas import (
    AISuggestInputSchema,
    JobIdSchema,
    AIResultSchema,
    ErrorResponseSchema,
)
from app.service_errors import (
    ServiceValidationError,
    ServiceAuthenticationError,
    ServicePermissionError,
    ServiceNotFoundError,
)

ai_bp = Blueprint("AI", __name__, url_prefix="/ai", description="AI 提案")

@ai_bp.errorhandler(ServiceValidationError)
def ai_validation_error(e):
    abort(400, message=str(e))

@ai_bp.errorhandler(ServiceAuthenticationError)
def ai_auth_error(e):
    abort(401, message=str(e))

@ai_bp.errorhandler(ServicePermissionError)
def ai_permission_error(e):
    abort(403, message=str(e))

@ai_bp.errorhandler(ServiceNotFoundError)
def ai_not_found_error(e):
    abort(404, message=str(e))


@ai_bp.route("/suggest")
class AISuggestResource(MethodView):
    @login_required
    @ai_bp.arguments(AISuggestInputSchema)
    @ai_bp.response(202, JobIdSchema)
    @ai_bp.alt_response(400, {
        "description": "Bad Request",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def post(self, data):
        """AI提案実行"""
        job = ai_service.enqueue_ai_task(data)
        return job

@ai_bp.route("/result/<job_id>")
class AIResultResource(MethodView):
    @login_required
    @ai_bp.response(200, AIResultSchema)
    @ai_bp.alt_response(202, {
        "description": "Accepted",
        "schema": AIResultSchema,
        "content_type": "application/json"
    })
    @ai_bp.alt_response(500, {
        "description": "Internal Server Error",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def get(self, job_id):
        """AI結果取得"""
        ai_result = ai_service.get_ai_task_result(job_id)
        return ai_result

