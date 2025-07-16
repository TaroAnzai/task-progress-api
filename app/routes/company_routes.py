from flask import Blueprint, request, jsonify
from app.services import company_service
from flask_login import current_user, login_required
from app.utils import require_superuser

company_bp = Blueprint('company', __name__, url_prefix='/companies')


# 会社一覧（論理削除除く）
@company_bp.route('', methods=['GET'])
@login_required
def list_companies():
    require_superuser(current_user)
    companies = company_service.get_all_companies()
    return jsonify([c.to_dict() for c in companies])


# 会社の詳細（論理削除除く）
@company_bp.route('/<int:company_id>', methods=['GET'])
@login_required
def get_company_by_id(company_id):
    require_superuser(current_user)
    company = company_service.get_company_by_id(company_id)
    if not company:
        return jsonify({'error': 'Company not found'}), 404
    return jsonify(company.to_dict())


# 会社の詳細（削除済も含む）
@company_bp.route('/with_deleted/<int:company_id>', methods=['GET'])
@login_required
def get_company_by_id_with_deleted(company_id):
    require_superuser(current_user)
    company = company_service.get_company_by_id_with_deleted(company_id)
    if not company:
        return jsonify({'error': 'Company not found'}), 404
    return jsonify(company.to_dict())


# 会社作成
@company_bp.route('', methods=['POST'])
@login_required
def create_company():
    require_superuser(current_user)
    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({'error': 'Company name is required'}), 400
    try:
        company = company_service.create_company(name)
        return jsonify(company.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


# 会社名の更新
@company_bp.route('/<int:company_id>', methods=['PUT'])
@login_required
def update_company(company_id):
    require_superuser(current_user)
    data = request.get_json()
    new_name = data.get('name')
    if not new_name:
        return jsonify({'error': 'New name is required'}), 400
    try:
        company = company_service.update_company(company_id, new_name)
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        return jsonify(company.to_dict())
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


# 論理削除
@company_bp.route('/<int:company_id>', methods=['DELETE'])
@login_required
def delete_company(company_id):
    require_superuser(current_user)
    success = company_service.delete_company(company_id)
    if not success:
        return jsonify({'error': 'Company not found'}), 404
    return jsonify({'message': 'Company deleted (soft)'})


# 復元
@company_bp.route('/restore/<int:company_id>', methods=['POST'])
@login_required
def restore_company(company_id):
    require_superuser(current_user)
    success = company_service.restore_company(company_id)
    if not success:
        return jsonify({'error': 'Company not found'}), 404
    return jsonify({'message': 'Company restored'})


# 物理削除（必要な場合のみ）
@company_bp.route('/permanent/<int:company_id>', methods=['DELETE'])
@login_required
def delete_company_permanently(company_id):
    require_superuser(current_user)
    success = company_service.delete_company_permanently(company_id)
    if not success:
        return jsonify({'error': 'Company not found or cannot be deleted'}), 404
    return jsonify({'message': 'Company permanently deleted'})
