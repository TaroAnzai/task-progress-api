# app/routes/auth_routes.py
from flask import Blueprint, jsonify
from app.extensions import login_manager
from app.models import User

auth_bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({'error': 'ログインが必要です'}), 401
