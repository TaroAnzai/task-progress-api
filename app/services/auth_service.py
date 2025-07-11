# app/services/auth_service.py

from flask import current_app
from flask_login import login_user, logout_user, current_user
from ..models import User
from werkzeug.security import check_password_hash

def login_with_email(data):
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return {'error': 'email と password は必須です'}, 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return {'error': 'メールアドレスまたはパスワードが無効です'}, 401

    login_user(user)
    return {'message': 'ログイン成功', 'user': user.to_dict()}, 200

def login_with_wp_user_id(data):
    wp_user_id = data.get('wp_user_id')
    if not wp_user_id:
        return {'error': 'wp_user_id は必須です'}, 400

    user = User.query.filter_by(wp_user_id=wp_user_id).first()
    if not user:
        return {'error': 'ユーザーが見つかりません'}, 404

    login_user(user)
    return {'message': 'ログイン成功', 'user': user.to_dict()}, 200

def logout_user_session():
    logout_user()
    return {'message': 'ログアウトしました'}, 200

def get_current_user_info():
    if not current_user.is_authenticated:
        return {'error': '未認証です'}, 401

    return current_user.to_dict(include_org=True), 200
