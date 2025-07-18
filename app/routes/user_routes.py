from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request
from flask_login import login_required, current_user

from app.services import user_service
from app.schemas import (
    UserSchema,
    UserInputSchema,
    UserCreateResponseSchema,
    MessageSchema,
    ErrorResponseSchema,
)

user_bp = Blueprint("Users", __name__, description="ユーザー管理")

@user_bp.route("/users")
class UsersResource(MethodView):
    @login_required
    @user_bp.arguments(UserInputSchema)
    @user_bp.response(201, UserCreateResponseSchema)
    @user_bp.response(400, ErrorResponseSchema)
    @user_bp.response(403, ErrorResponseSchema)
    def post(self, data):
        """ユーザー作成"""
        result, status = user_service.create_user(data, current_user)
        if isinstance(result, dict) and status:
            return result, status
        return result

    @login_required
    @user_bp.response(200, UserSchema(many=True))
    @user_bp.response(403, ErrorResponseSchema)
    @user_bp.response(404, ErrorResponseSchema)
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
    @user_bp.response(403, ErrorResponseSchema)
    @user_bp.response(404, ErrorResponseSchema)
    def get(self, user_id):
        """ユーザー取得"""
        result, status = user_service.get_user_by_id(user_id, current_user)
        return result, status

    @login_required
    @user_bp.arguments(UserInputSchema)
    @user_bp.response(200, UserSchema)
    @user_bp.response(403, ErrorResponseSchema)
    @user_bp.response(404, ErrorResponseSchema)
    def put(self, data, user_id):
        """ユーザー更新"""
        result, status = user_service.update_user(user_id, data, current_user)
        return result, status

    @login_required
    @user_bp.response(200, MessageSchema)
    @user_bp.response(403, ErrorResponseSchema)
    @user_bp.response(404, ErrorResponseSchema)
    def delete(self, user_id):
        """ユーザー削除"""
        result, status = user_service.delete_user(user_id, current_user)
        return result, status

@user_bp.route("/users/by-email")
class UserByEmailResource(MethodView):
    @login_required
    @user_bp.response(200, UserSchema)
    @user_bp.response(403, ErrorResponseSchema)
    @user_bp.response(404, ErrorResponseSchema)
    def get(self):
        """メールアドレスでユーザー取得"""
        email = request.args.get("email")
        result, status = user_service.get_user_by_email(email, current_user)
        return result, status

@user_bp.route("/users/id-lookup")
class UserByWPIDResource(MethodView):
    @login_required
    @user_bp.response(200, UserSchema)
    @user_bp.response(403, ErrorResponseSchema)
    @user_bp.response(404, ErrorResponseSchema)
    def get(self):
        """WordPress IDでユーザー取得"""
        wp_user_id = request.args.get("wp_user_id", type=int)
        result, status = user_service.get_user_by_wp_user_id(wp_user_id, current_user)
        return result, status

@user_bp.route("/users/by-org-tree/<int:org_id>")
class UsersByOrgTreeResource(MethodView):
    @login_required
    @user_bp.response(200, UserSchema(many=True))
    @user_bp.response(403, ErrorResponseSchema)
    def get(self, org_id):
        """組織ツリーでユーザー一覧取得"""
        result, status = user_service.get_users_by_org_tree(org_id, current_user)
        return result, status

