from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request
from flask_login import login_required
from marshmallow import Schema, fields

from app.services import auth_service

class LoginSchema(Schema):
    email = fields.Str(required=True)
    password = fields.Str(required=True)

class WPLoginSchema(Schema):
    wp_user_id = fields.Int(required=True)

class UserSchema(Schema):
    id = fields.Int()
    wp_user_id = fields.Int(allow_none=True)
    name = fields.Str()
    email = fields.Str()
    is_superuser = fields.Bool()
    organization_id = fields.Int(allow_none=True)
    organization_name = fields.Str(allow_none=True)

class MessageSchema(Schema):
    message = fields.Str()

auth_bp = Blueprint("Auth", __name__, url_prefix="/auth", description="認証")

@auth_bp.route("/login")
class LoginResource(MethodView):
    @auth_bp.arguments(LoginSchema)
    @auth_bp.response(200, UserSchema)
    def post(self, data):
        """メールでログイン"""
        result, status = auth_service.login_with_email(data)
        return result, status

@auth_bp.route("/login/by-id")
class LoginByIDResource(MethodView):
    @auth_bp.arguments(WPLoginSchema)
    @auth_bp.response(200, UserSchema)
    def post(self, data):
        """WP IDでログイン"""
        result, status = auth_service.login_with_wp_user_id(data)
        return result, status

@auth_bp.route("/logout")
class LogoutResource(MethodView):
    @login_required
    @auth_bp.response(200, MessageSchema)
    def post(self):
        """ログアウト"""
        result, status = auth_service.logout_user_session()
        return result, status

@auth_bp.route("/current_user")
class CurrentUserResource(MethodView):
    @login_required
    @auth_bp.response(200, UserSchema)
    def get(self):
        """現在のユーザー取得"""
        result, status = auth_service.get_current_user_info()
        return result, status

