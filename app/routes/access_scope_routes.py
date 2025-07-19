from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request
from flask_login import login_required
from app.services import access_scope_service
from app.service_errors import (
    ServiceValidationError,
    ServiceAuthenticationError,
    ServicePermissionError,
    ServiceNotFoundError,
)
from app.schemas import (
    AccessScopeSchema,
    AccessScopeInputSchema,
    MessageSchema,
    ErrorResponseSchema,
)

access_scope_bp = Blueprint("AccessScopes", __name__, description="アクセススコープ管理")


@access_scope_bp.errorhandler(ServiceValidationError)
def access_scope_validation_error(e):
    return {"message": str(e)}, 400


@access_scope_bp.errorhandler(ServiceAuthenticationError)
def access_scope_auth_error(e):
    return {"message": str(e)}, 401


@access_scope_bp.errorhandler(ServicePermissionError)
def access_scope_permission_error(e):
    return {"message": str(e)}, 403


@access_scope_bp.errorhandler(ServiceNotFoundError)
def access_scope_not_found_error(e):
    return {"message": str(e)}, 404

@access_scope_bp.route("/users/<int:user_id>/access-scopes")
class UserAccessScopeResource(MethodView):
    @login_required
    @access_scope_bp.response(200, AccessScopeSchema(many=True))
    @access_scope_bp.alt_response(404, {
        "description": "Not Found",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def get(self, user_id):
        """ユーザーのスコープ一覧"""
        scopes = access_scope_service.get_user_scopes(user_id)
        return scopes

    @login_required
    @access_scope_bp.arguments(AccessScopeInputSchema)
    @access_scope_bp.response(201, MessageSchema)
    @access_scope_bp.alt_response(200, {
        "description": "OK",
        "schema": MessageSchema,
        "content_type": "application/json"
    })
    @access_scope_bp.alt_response(400, {
        "description": "Bad Request",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    @access_scope_bp.alt_response(404, {
        "description": "Not Found",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def post(self, data, user_id):
        """スコープ追加"""
        message = access_scope_service.add_access_scope_to_user(user_id, data)
        return message

@access_scope_bp.route("/access-scopes/<int:scope_id>")
class AccessScopeResource(MethodView):
    @login_required
    @access_scope_bp.response(200, MessageSchema)
    @access_scope_bp.alt_response(404, {
        "description": "Not Found",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def delete(self, scope_id):
        """スコープ削除"""
        message = access_scope_service.delete_access_scope(scope_id)
        return message

