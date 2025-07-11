# routes/user_routes.py

from flask import Blueprint, request, jsonify
from flask_login import login_required
from app.services import user_service

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['POST'])
def create_user():
    result, status = user_service.create_user(request.json)
    return jsonify(result), status

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    result, status = user_service.get_user_by_id(user_id)
    return jsonify(result), status

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    result, status = user_service.update_user(user_id, request.json)
    return jsonify(result), status

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    result, status = user_service.delete_user(user_id)
    return jsonify(result), status

@user_bp.route('/users', methods=['GET'])
def get_users():
    user_id = request.args.get('user_id', type=int)
    org_id = request.args.get('organization_id', type=int)
    result, status = user_service.get_users(user_id, org_id)
    return jsonify(result), status

@user_bp.route('/users/by-email', methods=['GET'])
def get_user_by_email():
    email = request.args.get('email')
    result, status = user_service.get_user_by_email(email)
    return jsonify(result), status

@user_bp.route('/users/id-lookup', methods=['GET'])
def get_user_by_wp_user_id():
    wp_user_id = request.args.get('wp_user_id', type=int)
    result, status = user_service.get_user_by_wp_user_id(wp_user_id)
    return jsonify(result), status

@user_bp.route('/users/by-org-tree/<int:org_id>', methods=['GET'])
def get_users_by_org_tree(org_id):
    result, status = user_service.get_users_by_org_tree(org_id)
    return jsonify(result), status
