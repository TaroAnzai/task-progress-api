from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request
from flask_login import login_required, current_user
from marshmallow import Schema, fields

from app.services import organization_service

organization_bp = Blueprint("Organizations", __name__, url_prefix="/organizations", description="組織管理")

class OrganizationSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    org_code = fields.Str()
    company_id = fields.Int()
    parent_id = fields.Int(allow_none=True)
    level = fields.Int()

class OrganizationInputSchema(Schema):
    name = fields.Str(required=True)
    org_code = fields.Str(required=True)
    company_id = fields.Int(load_default=None)
    parent_id = fields.Int(load_default=None)

class OrganizationUpdateSchema(Schema):
    name = fields.Str()
    parent_id = fields.Int(allow_none=True)

class MessageSchema(Schema):
    message = fields.Str()
    error = fields.Str(load_default=None)


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
    def get(self, org_id):
        """組織取得"""
        org = organization_service.get_organization_by_id(org_id)
        if not org:
            return {"error": "組織が見つかりません"}, 404
        return org.to_dict()

    @login_required
    @organization_bp.arguments(OrganizationUpdateSchema)
    @organization_bp.response(200, OrganizationSchema)
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
    def get(self):
        """子組織取得"""
        parent_id = request.args.get("parent_id", type=int)
        if parent_id is None:
            return {"error": "parent_id パラメータが必要です"}, 400
        children = organization_service.get_children(parent_id)
        return [org.to_dict() for org in children]

