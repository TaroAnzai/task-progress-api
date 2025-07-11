# app/routes/auth_routes.py

from flask import Blueprint, request, jsonify
from flask_login import login_required
from app.services import auth_service

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    result, status = auth_service.login_with_email(request.json)
    return jsonify(result), status

@auth_bp.route('/login/by-id', methods=['POST'])
def login_by_wp_user_id():
    result, status = auth_service.login_with_wp_user_id(request.json)
    return jsonify(result), status

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    result, status = auth_service.logout_user_session()
    return jsonify(result), status

@auth_bp.route('/current_user', methods=['GET'])
@login_required
def get_current_user():
    result, status = auth_service.get_current_user_info()
    return jsonify(result), status
