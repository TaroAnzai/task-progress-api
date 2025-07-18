from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request
from flask_login import login_required, current_user
from app.service_errors import (
    ServiceValidationError,
    ServiceAuthenticationError,
    ServicePermissionError,
    ServiceNotFoundError,
)

from app.services import user_service
from app.schemas import (
    UserSchema,
    UserInputSchema,
    UserCreateResponseSchema,
    MessageSchema,
    ErrorResponseSchema,
)

user_bp = Blueprint("Users", __name__, description="ユーザー管理")

@user_bp.errorhandler(ServiceValidationError)
def user_validation_error(e):
    abort(400, message=str(e))

@user_bp.errorhandler(ServiceAuthenticationError)
def user_auth_error(e):
    abort(401, message=str(e))

@user_bp.errorhandler(ServicePermissionError)
def user_permission_error(e):
    abort(403, message=str(e))

@user_bp.errorhandler(ServiceNotFoundError)
def user_not_found_error(e):
    abort(404, message=str(e))


@user_bp.route("/users")
class UsersResource(MethodView):
    @login_required
    @user_bp.arguments(UserInputSchema)
    @user_bp.response(201, UserCreateResponseSchema)
    @user_bp.alt_response(400, {
        "description": "Bad Request",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    @user_bp.alt_response(403, {
        "description": "Forbidden",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def post(self, data):
        """ユーザー作成"""
        result = user_service.create_user(data, current_user)
        return result

    @login_required
    @user_bp.response(200, UserSchema(many=True))
    @user_bp.alt_response(403, {
        "description": "Forbidden",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    @user_bp.alt_response(404, {
        "description": "Not Found",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def get(self):
        """ユーザー一覧取得"""
        user_id = request.args.get("user_id", type=int)
        org_id = request.args.get("organization_id", type=int)
        result = user_service.get_users(user_id, org_id)
        return result

@user_bp.route("/users/<int:user_id>")
class UserResource(MethodView):
    @login_required
    @user_bp.response(200, UserSchema)
    @user_bp.alt_response(403, {
        "description": "Forbidden",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    @user_bp.alt_response(404, {
        "description": "Not Found",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def get(self, user_id):
        """ユーザー取得"""
        result = user_service.get_user_by_id(user_id, current_user)
        return result

    @login_required
    @user_bp.arguments(UserInputSchema)
    @user_bp.response(200, UserSchema)
    @user_bp.alt_response(403, {
        "description": "Forbidden",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    @user_bp.alt_response(404, {
        "description": "Not Found",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def put(self, data, user_id):
        """ユーザー更新"""
        result = user_service.update_user(user_id, data, current_user)
        return result

    @login_required
    @user_bp.response(200, MessageSchema)
    @user_bp.alt_response(403, {
        "description": "Forbidden",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    @user_bp.alt_response(404, {
        "description": "Not Found",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def delete(self, user_id):
        """ユーザー削除"""
        result = user_service.delete_user(user_id, current_user)
        return result

@user_bp.route("/users/by-email")
class UserByEmailResource(MethodView):
    @login_required
    @user_bp.response(200, UserSchema)
    @user_bp.alt_response(403, {
        "description": "Forbidden",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    @user_bp.alt_response(404, {
        "description": "Not Found",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def get(self):
        """メールアドレスでユーザー取得"""
        email = request.args.get("email")
        result = user_service.get_user_by_email(email, current_user)
        return result

@user_bp.route("/users/id-lookup")
class UserByWPIDResource(MethodView):
    @login_required
    @user_bp.response(200, UserSchema)
    @user_bp.alt_response(403, {
        "description": "Forbidden",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    @user_bp.alt_response(404, {
        "description": "Not Found",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def get(self):
        """WordPress IDでユーザー取得"""
        wp_user_id = request.args.get("wp_user_id", type=int)
        result = user_service.get_user_by_wp_user_id(wp_user_id, current_user)
        return result

@user_bp.route("/users/by-org-tree/<int:org_id>")
class UsersByOrgTreeResource(MethodView):
    @login_required
    @user_bp.response(200, UserSchema(many=True))
    @user_bp.alt_response(403, {
        "description": "Forbidden",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def get(self, org_id):
        """組織ツリーでユーザー一覧取得"""
        result = user_service.get_users_by_org_tree(org_id, current_user)
        return result

