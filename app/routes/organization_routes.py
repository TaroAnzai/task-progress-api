from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request
from flask_login import login_required, current_user

from app.services import organization_service
from app.schemas import (
    OrganizationSchema,
    OrganizationInputSchema,
    OrganizationUpdateSchema,
    MessageSchema,
    ErrorResponseSchema,
)

organization_bp = Blueprint("Organizations", __name__, url_prefix="/organizations", description="組織管理")


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
    @organization_bp.response(400, ErrorResponseSchema)
    def post(self, data):
        """組織作成"""
        name = data.get("name")
        org_code = data.get("org_code")
        company_id = data.get("company_id")
        parent_id = data.get("parent_id")
        if not name or not org_code:
            return {"error": "name と org_code は必須です"}, 400
        try:
            resolved_company_id = resolve_company_id(company_id)
            if parent_id is None:
                if not organization_service.can_create_root_organization(resolved_company_id):
                    return {"error": "この会社にはすでにルート組織が存在します"}, 400
            org = organization_service.create_organization(name, org_code, resolved_company_id, parent_id)
            return org.to_dict(), 201
        except ValueError as e:
            return {"error": str(e)}, 400

    @login_required
    @organization_bp.response(200, OrganizationSchema(many=True))
    @organization_bp.response(400, ErrorResponseSchema)
    def get(self):
        """組織一覧取得"""
        company_id = request.args.get("company_id", type=int)
        try:
            resolved_company_id = resolve_company_id(company_id)
            orgs = organization_service.get_organizations(resolved_company_id)
            return [org.to_dict() for org in orgs]
        except ValueError as e:
            return {"error": str(e)}, 400

@organization_bp.route("/<int:org_id>")
class OrganizationResource(MethodView):
    @login_required
    @organization_bp.response(200, OrganizationSchema)
    @organization_bp.response(404, ErrorResponseSchema)
    def get(self, org_id):
        """組織取得"""
        org = organization_service.get_organization_by_id(org_id)
        if not org:
            return {"error": "組織が見つかりません"}, 404
        return org.to_dict()

    @login_required
    @organization_bp.arguments(OrganizationUpdateSchema)
    @organization_bp.response(200, OrganizationSchema)
    @organization_bp.response(400, ErrorResponseSchema)
    @organization_bp.response(404, ErrorResponseSchema)
    def put(self, data, org_id):
        """組織更新"""
        try:
            org = organization_service.update_organization(org_id, data.get("name"), data.get("parent_id"))
            if not org:
                return {"error": "組織が見つかりません"}, 404
            return org.to_dict()
        except ValueError as e:
            return {"error": str(e)}, 400

    @login_required
    @organization_bp.response(200, MessageSchema)
    @organization_bp.response(400, ErrorResponseSchema)
    def delete(self, org_id):
        """組織削除"""
        success, message = organization_service.delete_organization(org_id)
        if not success:
            return {"error": message}, 400
        return {"message": message}

@organization_bp.route("/tree")
class OrganizationTreeResource(MethodView):
    @login_required
    @organization_bp.response(200, fields.List(fields.Nested(OrganizationSchema)))
    @organization_bp.response(400, ErrorResponseSchema)
    def get(self):
        """組織ツリー取得"""
        company_id = request.args.get("company_id", type=int)
        try:
            resolved_company_id = resolve_company_id(company_id)
            tree = organization_service.get_organization_tree(resolved_company_id)
            return tree
        except ValueError as e:
            return {"error": str(e)}, 400

@organization_bp.route("/children")
class OrganizationChildrenResource(MethodView):
    @login_required
    @organization_bp.response(200, OrganizationSchema(many=True))
    @organization_bp.response(400, ErrorResponseSchema)
    def get(self):
        """子組織取得"""
        parent_id = request.args.get("parent_id", type=int)
        if parent_id is None:
            return {"error": "parent_id パラメータが必要です"}, 400
        children = organization_service.get_children(parent_id)
        return [org.to_dict() for org in children]

