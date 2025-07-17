from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request
from marshmallow import Schema, fields

from app.services import access_scope_service

class AccessScopeSchema(Schema):
    id = fields.Int()
    organization_id = fields.Int()
    role = fields.Str()

class AccessScopeInputSchema(Schema):
    organization_id = fields.Int(required=True)
    role = fields.Str(required=True)

class MessageSchema(Schema):
    message = fields.Str()
    error = fields.Str(load_default=None)

access_scope_bp = Blueprint("AccessScopes", __name__, description="アクセススコープ管理")

@access_scope_bp.route("/users/<int:user_id>/access-scopes")
class UserAccessScopeResource(MethodView):
    @access_scope_bp.response(200, AccessScopeSchema(many=True))
    def get(self, user_id):
        """ユーザーのスコープ一覧"""
        result, status = access_scope_service.get_user_scopes(user_id)
        return result, status

    @access_scope_bp.arguments(AccessScopeInputSchema)
    @access_scope_bp.response(201, MessageSchema)
    def post(self, data, user_id):
        """スコープ追加"""
        result, status = access_scope_service.add_access_scope_to_user(user_id, data)
        return result, status

@access_scope_bp.route("/access-scopes/<int:scope_id>")
class AccessScopeResource(MethodView):
    @access_scope_bp.response(200, MessageSchema)
    def delete(self, scope_id):
        """スコープ削除"""
        result, status = access_scope_service.delete_access_scope(scope_id)
        return result, status

