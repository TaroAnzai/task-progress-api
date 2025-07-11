# app/services/access_scope_service.py

from ..models import db, User, AccessScope, Organization

def get_user_scopes(user_id):
    user = User.query.get(user_id)
    if not user:
        return {'error': 'ユーザーが見つかりません'}, 404

    scopes = [
        {
            'id': scope.id,
            'organization_id': scope.organization_id,
            'role': scope.role
        } for scope in user.access_scopes
    ]
    return scopes, 200

def add_access_scope_to_user(user_id, data):
    user = User.query.get(user_id)
    if not user:
        return {'error': 'ユーザーが見つかりません'}, 404

    org_id = data.get('organization_id')
    role = data.get('role')

    if not org_id or not role:
        return {'error': 'organization_id と role は必須です'}, 400

    existing_scope = AccessScope.query.filter_by(user_id=user.id, organization_id=org_id).first()
    if existing_scope:
        if existing_scope.role != role:
            existing_scope.role = role
            db.session.commit()
            return {'message': 'アクセススコープを更新しました'}, 200
        return {'message': 'すでにこのアクセススコープは登録されています'}, 200

    new_scope = AccessScope(user_id=user.id, organization_id=org_id, role=role)
    db.session.add(new_scope)
    db.session.commit()
    return {'message': 'アクセススコープを追加しました'}, 201

def delete_access_scope(scope_id):
    scope = AccessScope.query.get(scope_id)
    if not scope:
        return {'error': 'スコープが見つかりません'}, 404

    db.session.delete(scope)
    db.session.commit()
    return {'message': 'アクセススコープを削除しました'}, 200
