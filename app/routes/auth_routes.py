from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask_login import login_required
from app.services import auth_service
from app.schemas import (
    LoginSchema,
    WPLoginSchema,
    UserSchema,
    UserCreateResponseSchema,
    LoginResponseSchema,
    MessageSchema,
    ErrorResponseSchema,
)
from app.service_errors import (
    ServiceValidationError,
    ServiceAuthenticationError,
    ServicePermissionError,
    ServiceNotFoundError,
)

auth_bp = Blueprint("Auth", __name__, url_prefix="/auth", description="認証")

@auth_bp.errorhandler(ServiceValidationError)
def auth_validation_error(e):
    abort(400, message=str(e))

@auth_bp.errorhandler(ServiceAuthenticationError)
def auth_auth_error(e):
    abort(401, message=str(e))

@auth_bp.errorhandler(ServicePermissionError)
def auth_permission_error(e):
    abort(403, message=str(e))

@auth_bp.errorhandler(ServiceNotFoundError)
def auth_not_found_error(e):
    abort(404, message=str(e))


@auth_bp.route("/login")
class LoginResource(MethodView):
    @auth_bp.arguments(LoginSchema)
    @auth_bp.response(200, LoginResponseSchema)
    @auth_bp.alt_response(400, {
        "description": "Bad Request",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    @auth_bp.alt_response(401, {
        "description": "Unauthorized",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def post(self, data):
        """メールでログイン"""
        user_info = auth_service.login_with_email(data)
        return user_info

@auth_bp.route("/login/by-id")
class LoginByIDResource(MethodView):
    @auth_bp.arguments(WPLoginSchema)
    @auth_bp.response(200, LoginResponseSchema)
    @auth_bp.alt_response(400, {
        "description": "Bad Request",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    @auth_bp.alt_response(404, {
        "description": "Not Found",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def post(self, data):
        """WP IDでログイン"""
        user_info = auth_service.login_with_wp_user_id(data)
        return user_info

@auth_bp.route("/logout")
class LogoutResource(MethodView):
    @login_required
    @auth_bp.response(200, MessageSchema)
    @auth_bp.alt_response(401, {
        "description": "Unauthorized",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def post(self):
        """ログアウト"""
        message = auth_service.logout_user_session()
        return message

@auth_bp.route("/current_user")
class CurrentUserResource(MethodView):
    @login_required
    @auth_bp.response(200, UserSchema)
    @auth_bp.alt_response(401, {
        "description": "Unauthorized",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def get(self):
        """現在のユーザー取得"""
        user = auth_service.get_current_user_info()
        return user

