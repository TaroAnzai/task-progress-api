from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import Organization
from app.services import organization_service

organization_bp = Blueprint('organization', __name__, url_prefix='/organizations')


def resolve_company_id(provided_company_id):
    if provided_company_id:
        return provided_company_id
    if not current_user or not current_user.organization:
        raise ValueError("company_id が指定されていないか、ユーザーに紐づく組織がありません。")
    return current_user.organization.company_id


@organization_bp.route('', methods=['POST'])
@login_required
def create_organization():
    data = request.get_json()
    name = data.get('name')
    org_code = data.get('org_code')
    company_id = data.get('company_id')
    parent_id = data.get('parent_id')

    if not name or not org_code:
        return jsonify({'error': 'name と org_code は必須です'}), 400

    try:
        resolved_company_id = resolve_company_id(company_id)

        if parent_id is None:
            if not organization_service.can_create_root_organization(resolved_company_id):
                return jsonify({'error': 'この会社にはすでにルート組織が存在します'}), 400

        org = organization_service.create_organization(name, org_code, resolved_company_id, parent_id)
        return jsonify(org.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@organization_bp.route('/', methods=['GET'])
@login_required
def get_organizations():
    company_id = request.args.get('company_id', type=int)
    try:
        resolved_company_id = resolve_company_id(company_id)
        orgs = organization_service.get_organizations(resolved_company_id)
        return jsonify([org.to_dict() for org in orgs])
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@organization_bp.route('/<int:org_id>', methods=['GET'])
@login_required
def get_organization_by_id(org_id):
    org = organization_service.get_organization_by_id(org_id)
    if not org:
        return jsonify({'error': '組織が見つかりません'}), 404
    return jsonify(org.to_dict())


@organization_bp.route('/<int:org_id>', methods=['PUT'])
@login_required
def update_organization(org_id):
    data = request.get_json()
    name = data.get('name')
    parent_id = data.get('parent_id')

    try:
        org = organization_service.update_organization(org_id, name, parent_id)
        if not org:
            return jsonify({'error': '組織が見つかりません'}), 404
        return jsonify(org.to_dict())
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@organization_bp.route('/<int:org_id>', methods=['DELETE'])
@login_required
def delete_organization(org_id):
    success, message = organization_service.delete_organization(org_id)
    if not success:
        return jsonify({'error': message}), 400
    return jsonify({'message': message})


@organization_bp.route('/tree', methods=['GET'])
@login_required
def get_organization_tree():
    company_id = request.args.get('company_id', type=int)
    try:
        resolved_company_id = resolve_company_id(company_id)
        tree = organization_service.get_organization_tree(resolved_company_id)
        return jsonify(tree)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@organization_bp.route('/children', methods=['GET'])
@login_required
def get_children():
    parent_id = request.args.get('parent_id', type=int)
    if parent_id is None:
        return jsonify({'error': 'parent_id パラメータが必要です'}), 400

    children = organization_service.get_children(parent_id)
    return jsonify([org.to_dict() for org in children])
