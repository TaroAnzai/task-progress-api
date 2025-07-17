from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request
from flask_login import login_required, current_user
from marshmallow import Schema, fields

from app.services import user_service

class UserSchema(Schema):
    id = fields.Int()
    wp_user_id = fields.Int(allow_none=True)
    name = fields.Str()
    email = fields.Str()
    is_superuser = fields.Bool()
    organization_id = fields.Int(allow_none=True)
    organization_name = fields.Str(allow_none=True)

class UserInputSchema(Schema):
    wp_user_id = fields.Int(load_default=None)
    name = fields.Str(required=True)
    email = fields.Str(required=True)
    password = fields.Str(load_default=None)
    role = fields.Str(load_default=None)
    organization_id = fields.Int(required=True)

class MessageSchema(Schema):
    message = fields.Str()

user_bp = Blueprint("Users", __name__, description="ユーザー管理")

@user_bp.route("/users")
class UsersResource(MethodView):
    @login_required
    @user_bp.arguments(UserInputSchema)
    @user_bp.response(201, MessageSchema)
    def post(self, data):
        """ユーザー作成"""
        result, status = user_service.create_user(data, current_user)
        if isinstance(result, dict) and status:
            return result, status
        return result

    @login_required
    @user_bp.response(200, UserSchema(many=True))
    def get(self):
        """ユーザー一覧取得"""
        user_id = request.args.get("user_id", type=int)
        org_id = request.args.get("organization_id", type=int)
        result, status = user_service.get_users(user_id, org_id)
        return result, status

@user_bp.route("/users/<int:user_id>")
class UserResource(MethodView):
    @login_required
    @user_bp.response(200, UserSchema)
    def get(self, user_id):
        """ユーザー取得"""
        result, status = user_service.get_user_by_id(user_id, current_user)
        return result, status

    @login_required
    @user_bp.arguments(UserInputSchema)
    @user_bp.response(200, UserSchema)
    def put(self, data, user_id):
        """ユーザー更新"""
        result, status = user_service.update_user(user_id, data, current_user)
        return result, status

    @login_required
    @user_bp.response(200, MessageSchema)
    def delete(self, user_id):
        """ユーザー削除"""
        result, status = user_service.delete_user(user_id, current_user)
        return result, status

@user_bp.route("/users/by-email")
class UserByEmailResource(MethodView):
    @login_required
    @user_bp.response(200, UserSchema)
    def get(self):
        """メールアドレスでユーザー取得"""
        email = request.args.get("email")
        result, status = user_service.get_user_by_email(email, current_user)
        return result, status

@user_bp.route("/users/id-lookup")
class UserByWPIDResource(MethodView):
    @login_required
    @user_bp.response(200, UserSchema)
    def get(self):
        """WordPress IDでユーザー取得"""
        wp_user_id = request.args.get("wp_user_id", type=int)
        result, status = user_service.get_user_by_wp_user_id(wp_user_id, current_user)
        return result, status

@user_bp.route("/users/by-org-tree/<int:org_id>")
class UsersByOrgTreeResource(MethodView):
    @login_required
    @user_bp.response(200, UserSchema(many=True))
    def get(self, org_id):
        """組織ツリーでユーザー一覧取得"""
        result, status = user_service.get_users_by_org_tree(org_id, current_user)
        return result, status

