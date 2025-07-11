# services/user_service.py

from flask import current_app, jsonify
from sqlalchemy.orm import joinedload
from ..models import db, User, Organization
from ..utils import get_all_child_organizations, get_descendant_organizations

def create_user(data):
    wp_user_id = data.get('wp_user_id')
    name = data.get('name')
    email = data.get('email')
    org_id = data.get('organization_id')

    if not name or not email or not org_id:
        return {'error': 'name、email、organization_idは必須です'}, 400

    if wp_user_id and User.query.filter_by(wp_user_id=wp_user_id).first():
        return {'error': 'この wp_user_id は既に使用されています'}, 400

    if User.query.filter_by(email=email).first():
        return {'error': 'このメールアドレスは既に使用されています'}, 400

    org = Organization.query.get(org_id)
    if not org:
        return {'error': '指定された組織IDが存在しません'}, 400

    user = User(wp_user_id=wp_user_id, name=name, email=email, organization_id=org_id)
    db.session.add(user)
    db.session.commit()

    return {'message': 'ユーザーを登録しました', 'user': user.to_dict(include_org=True)}, 201

def get_user_by_id(user_id):
    user = User.query.get(user_id)
    if not user:
        return {'error': 'ユーザーが見つかりません'}, 404
    return user.to_dict(include_org=True), 200

def update_user(user_id, data):
    user = User.query.get(user_id)
    if not user:
        return {'error': 'ユーザーが見つかりません'}, 404

    if 'name' in data:
        user.name = data['name']
    if 'wp_user_id' in data:
        user.wp_user_id = data['wp_user_id']
    if 'email' in data:
        user.email = data['email']
    if 'organization_id' in data:
        user.organization_id = data['organization_id']

    db.session.commit()
    return user.to_dict(include_org=True), 200

def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return {'error': 'ユーザーが見つかりません'}, 404

    from ..models import AccessScope
    try:
        AccessScope.query.filter_by(user_id=user.id).delete()
        db.session.delete(user)
        db.session.commit()
        return {'message': 'ユーザーと関連スコープを削除しました'}, 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"delete_user error: {e}")
        return {'error': '削除に失敗しました', 'details': str(e)}, 500

def get_users(requesting_user_id, organization_id=None):
    requester = User.query.get(requesting_user_id)
    if not requester:
        return []

    all_orgs = Organization.query.all()
    base_org_id = organization_id or requester.organization_id
    base_org = Organization.query.get(base_org_id)
    if not base_org:
        return {'error': '組織が見つかりません'}, 404

    descendants = get_descendant_organizations(base_org.id, all_orgs)
    org_ids = [org.id for org in descendants]

    users = (
        User.query
        .options(joinedload(User.organization))
        .filter(User.organization_id.in_(org_ids))
        .all()
    )

    return [u.to_dict(include_org=True) for u in users], 200

def get_user_by_email(email):
    user = User.query.filter_by(email=email).first()
    if not user:
        return {'error': 'ユーザーが見つかりません'}, 404
    return user.to_dict(include_org=True), 200

def get_user_by_wp_user_id(wp_user_id):
    user = User.query.filter_by(wp_user_id=wp_user_id).first()
    if not user:
        return {'error': 'ユーザーが見つかりません'}, 404
    return user.to_dict(include_org=True), 200

def get_users_by_org_tree(org_id):
    try:
        org_ids = get_all_child_organizations(org_id)
        users = User.query.filter(User.organization_id.in_(org_ids)).all()
        return [u.to_dict() for u in users], 200
    except Exception as e:
        return {'error': str(e)}, 500
