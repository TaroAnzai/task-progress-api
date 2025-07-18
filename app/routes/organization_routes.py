from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask import request
from flask_login import login_required, current_user
from marshmallow import fields
from app.service_errors import (
    ServiceValidationError,
    ServiceAuthenticationError,
    ServicePermissionError,
    ServiceNotFoundError,
)
from app.services import organization_service
from app.schemas import (
    OrganizationSchema,
    OrganizationInputSchema,
    OrganizationUpdateSchema,
    MessageSchema,
    ErrorResponseSchema,
)

organization_bp = Blueprint("Organizations", __name__, url_prefix="/organizations", description="組織管理")

@organization_bp.errorhandler(ServiceValidationError)
def organization_validation_error(e):
    abort(400, message=str(e))

@organization_bp.errorhandler(ServiceAuthenticationError)
def organization_auth_error(e):
    abort(401, message=str(e))

@organization_bp.errorhandler(ServicePermissionError)
def organization_permission_error(e):
    abort(403, message=str(e))

@organization_bp.errorhandler(ServiceNotFoundError)
def organization_not_found_error(e):
    abort(404, message=str(e))



def resolve_company_id(provided_company_id):
    if provided_company_id:
        return provided_company_id
    if not current_user or not current_user.organization:
        raise ValueError("company_id が指定されていないか、ユーザーに紐づく組織がありません。")
    return current_user.organization.company_id

@organization_bp.route("")
class OrganizationListResource(MethodView):
    @login_required
    @organization_bp.arguments(OrganizationInputSchema)
    @organization_bp.response(201, OrganizationSchema)
    @organization_bp.alt_response(400, {
        "description": "Bad Request",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def post(self, data):
        """組織作成"""
        name = data.get("name")
        org_code = data.get("org_code")
        company_id = data.get("company_id")
        parent_id = data.get("parent_id")
        if not name or not org_code:
            abort(400, message="name と org_code は必須です")
        try:
            resolved_company_id = resolve_company_id(company_id)
            if parent_id is None:
                if not organization_service.can_create_root_organization(resolved_company_id):
                    abort(400, message="この会社にはすでにルート組織が存在します")
            org = organization_service.create_organization(
                name, org_code, resolved_company_id, parent_id
            )
            return org
        except ValueError as e:
            abort(400, message=str(e))

    @login_required
    @organization_bp.response(200, OrganizationSchema(many=True))
    @organization_bp.alt_response(400, {
        "description": "Bad Request",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def get(self):
        """組織一覧取得"""
        company_id = request.args.get("company_id", type=int)
        try:
            resolved_company_id = resolve_company_id(company_id)
            orgs = organization_service.get_organizations(resolved_company_id)
            return orgs
        except ValueError as e:
            abort(400, message=str(e))

@organization_bp.route("/<int:org_id>")
class OrganizationResource(MethodView):
    @login_required
    @organization_bp.response(200, OrganizationSchema)
    @organization_bp.alt_response(404, {
        "description": "Not Found",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def get(self, org_id):
        """組織取得"""
        org = organization_service.get_organization_by_id(org_id)
        if not org:
            abort(404, message="組織が見つかりません")
        return org

    @login_required
    @organization_bp.arguments(OrganizationUpdateSchema)
    @organization_bp.response(200, OrganizationSchema)
    @organization_bp.alt_response(400, {
        "description": "Bad Request",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    @organization_bp.alt_response(404, {
        "description": "Not Found",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def put(self, data, org_id):
        """組織更新"""
        try:
            org = organization_service.update_organization(
                org_id, data.get("name"), data.get("parent_id")
            )
            if not org:
                abort(404, message="組織が見つかりません")
            return org
        except ValueError as e:
            abort(400, message=str(e))

    @login_required
    @organization_bp.response(200, MessageSchema)
    @organization_bp.alt_response(400, {
        "description": "Bad Request",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def delete(self, org_id):
        """組織削除"""
        success, message = organization_service.delete_organization(org_id)
        if not success:
            abort(400, message=message)
        return {"message": message}

@organization_bp.route("/tree")
class OrganizationTreeResource(MethodView):
    @login_required
    @organization_bp.response(200, fields.List(fields.Nested(OrganizationSchema)))
    @organization_bp.alt_response(400, {
        "description": "Bad Request",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def get(self):
        """組織ツリー取得"""
        company_id = request.args.get("company_id", type=int)
        try:
            resolved_company_id = resolve_company_id(company_id)
            tree = organization_service.get_organization_tree(resolved_company_id)
            return tree
        except ValueError as e:
            abort(400, message=str(e))

@organization_bp.route("/children")
class OrganizationChildrenResource(MethodView):
    @login_required
    @organization_bp.response(200, OrganizationSchema(many=True))
    @organization_bp.alt_response(400, {
        "description": "Bad Request",
        "schema": ErrorResponseSchema,
        "content_type": "application/json"
    })
    def get(self):
        """子組織取得"""
        parent_id = request.args.get("parent_id", type=int)
        if parent_id is None:
            abort(400, message="parent_id パラメータが必要です")
        children = organization_service.get_children(parent_id)
        return children

