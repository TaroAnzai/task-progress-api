# app/routes/access_scope_routes.py

from flask import Blueprint, request, jsonify
from app.services import access_scope_service

access_scope_bp = Blueprint('access_scope', __name__)

@access_scope_bp.route('/users/<int:user_id>/access-scopes', methods=['GET'])
def get_user_access_scopes(user_id):
    result, status = access_scope_service.get_user_scopes(user_id)
    return jsonify(result), status

@access_scope_bp.route('/users/<int:user_id>/access-scopes', methods=['POST'])
def add_access_scope(user_id):
    result, status = access_scope_service.add_access_scope_to_user(user_id, request.json)
    return jsonify(result), status

@access_scope_bp.route('/access-scopes/<int:scope_id>', methods=['DELETE'])
def delete_access_scope(scope_id):
    result, status = access_scope_service.delete_access_scope(scope_id)
    return jsonify(result), status
