from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request
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

auth_bp = Blueprint("Auth", __name__, url_prefix="/auth", description="認証")

@auth_bp.route("/login")
class LoginResource(MethodView):
    @auth_bp.arguments(LoginSchema)
    @auth_bp.response(200, LoginResponseSchema)
    @auth_bp.response(400, ErrorResponseSchema)
    @auth_bp.response(401, ErrorResponseSchema)
    def post(self, data):
        """メールでログイン"""
        result, status = auth_service.login_with_email(data)
        return result, status

@auth_bp.route("/login/by-id")
class LoginByIDResource(MethodView):
    @auth_bp.arguments(WPLoginSchema)
    @auth_bp.response(200, LoginResponseSchema)
    @auth_bp.response(400, ErrorResponseSchema)
    @auth_bp.response(404, ErrorResponseSchema)
    def post(self, data):
        """WP IDでログイン"""
        result, status = auth_service.login_with_wp_user_id(data)
        return result, status

@auth_bp.route("/logout")
class LogoutResource(MethodView):
    @login_required
    @auth_bp.response(200, MessageSchema)
    @auth_bp.response(401, ErrorResponseSchema)
    def post(self):
        """ログアウト"""
        result, status = auth_service.logout_user_session()
        return result, status

@auth_bp.route("/current_user")
class CurrentUserResource(MethodView):
    @login_required
    @auth_bp.response(200, UserSchema)
    @auth_bp.response(401, ErrorResponseSchema)
    def get(self):
        """現在のユーザー取得"""
        result, status = auth_service.get_current_user_info()
        return result, status

