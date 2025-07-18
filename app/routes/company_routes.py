from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request, jsonify, send_file
from flask_login import login_required, current_user

from app.services import company_service
from app.utils import require_superuser
from app.schemas import (
    CompanySchema,
    CompanyInputSchema,
    MessageSchema,
    ErrorResponseSchema,
)

company_bp = Blueprint("Companies", __name__, url_prefix="/companies", description="会社管理")

@company_bp.route("")
class CompanyListResource(MethodView):
    @login_required
    @company_bp.response(200, CompanySchema(many=True))
    @company_bp.response(403, ErrorResponseSchema)
    def get(self):
        """会社一覧取得"""
        require_superuser(current_user)
        companies = company_service.get_all_companies()
        return [c.to_dict() for c in companies]

    @login_required
    @company_bp.arguments(CompanyInputSchema)
    @company_bp.response(201, CompanySchema)
    @company_bp.response(400, ErrorResponseSchema)
    @company_bp.response(403, ErrorResponseSchema)
    def post(self, data):
        """会社作成"""
        require_superuser(current_user)
        try:
            company = company_service.create_company(data.get("name"))
            return company.to_dict(), 201
        except ValueError as e:
            return {"error": str(e)}, 400

@company_bp.route("/<int:company_id>")
class CompanyResource(MethodView):
    @login_required
    @company_bp.response(200, CompanySchema)
    @company_bp.response(404, ErrorResponseSchema)
    @company_bp.response(403, ErrorResponseSchema)
    def get(self, company_id):
        """会社詳細取得"""
        require_superuser(current_user)
        company = company_service.get_company_by_id(company_id)
        if not company:
            return {"error": "Company not found"}, 404
        return company.to_dict()

    @login_required
    @company_bp.arguments(CompanyInputSchema)
    @company_bp.response(200, CompanySchema)
    @company_bp.response(400, ErrorResponseSchema)
    @company_bp.response(404, ErrorResponseSchema)
    @company_bp.response(403, ErrorResponseSchema)
    def put(self, data, company_id):
        """会社更新"""
        require_superuser(current_user)
        new_name = data.get("name")
        if not new_name:
            return {"error": "New name is required"}, 400
        try:
            company = company_service.update_company(company_id, new_name)
            if not company:
                return {"error": "Company not found"}, 404
            return company.to_dict()
        except ValueError as e:
            return {"error": str(e)}, 400

    @login_required
    @company_bp.response(200, MessageSchema)
    @company_bp.response(404, ErrorResponseSchema)
    @company_bp.response(403, ErrorResponseSchema)
    def delete(self, company_id):
        """会社の論理削除"""
        require_superuser(current_user)
        success = company_service.delete_company(company_id)
        if not success:
            return {"error": "Company not found"}, 404
        return {"message": "Company deleted (soft)"}

@company_bp.route("/with_deleted/<int:company_id>")
class CompanyWithDeletedResource(MethodView):
    @login_required
    @company_bp.response(200, CompanySchema)
    @company_bp.response(404, ErrorResponseSchema)
    @company_bp.response(403, ErrorResponseSchema)
    def get(self, company_id):
        """削除済み含む会社詳細取得"""
        require_superuser(current_user)
        company = company_service.get_company_by_id_with_deleted(company_id)
        if not company:
            return {"error": "Company not found"}, 404
        return company.to_dict()

@company_bp.route("/restore/<int:company_id>")
class CompanyRestoreResource(MethodView):
    @login_required
    @company_bp.response(200, MessageSchema)
    @company_bp.response(404, ErrorResponseSchema)
    @company_bp.response(403, ErrorResponseSchema)
    def post(self, company_id):
        """会社復元"""
        require_superuser(current_user)
        success = company_service.restore_company(company_id)
        if not success:
            return {"error": "Company not found"}, 404
        return {"message": "Company restored"}

@company_bp.route("/permanent/<int:company_id>")
class CompanyPermanentDeleteResource(MethodView):
    @login_required
    @company_bp.response(200, MessageSchema)
    @company_bp.response(404, ErrorResponseSchema)
    @company_bp.response(403, ErrorResponseSchema)
    def delete(self, company_id):
        """会社物理削除"""
        require_superuser(current_user)
        success = company_service.delete_company_permanently(company_id)
        if not success:
            return {"error": "Company not found or cannot be deleted"}, 404
        return {"message": "Company permanently deleted"}

