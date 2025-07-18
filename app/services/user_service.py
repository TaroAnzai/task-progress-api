# services/user_service.py

from flask import current_app
import re
from sqlalchemy.orm import joinedload
from ..models import db, User, Organization, AccessScope
from ..utils import (
    get_all_child_organizations,
    get_descendant_organizations,
    check_org_access,
)
from ..constants import OrgRoleEnum
from ..service_errors import (
    ServiceValidationError,
    ServicePermissionError,
    ServiceNotFoundError,
)

import re

def is_valid_email(email):
    # シンプルな正規表現（RFC全準拠ではなく一般的な形式の検出）
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email)

def create_user(data, current_user):
    #組織の項目のチェック
    org_id = data.get('organization_id')
    if not org_id:
        raise ServiceValidationError('organization_idは必須です')
    # 組織管理権限チェック
    if not check_org_access(current_user, data.get('organization_id'), OrgRoleEnum.ORG_ADMIN):
        raise ServicePermissionError('権限がありません')

    wp_user_id = data.get('wp_user_id')
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', OrgRoleEnum.MEMBER)  # ← デフォルトはMEMBER

    # 必須項目チェック
    if not name or not email or not org_id:
        raise ServiceValidationError('name、emailは必須です')

    if not password:
        raise ServiceValidationError('password は必須です')

    if not is_valid_email(email):
        raise ServiceValidationError('無効なメールアドレス形式です')

    if role not in OrgRoleEnum.__members__.values() and role not in OrgRoleEnum.__members__:
        raise ServiceValidationError(f'指定されたroleが不正です: {role}')

    if wp_user_id and User.query.filter_by(wp_user_id=wp_user_id).first():
        raise ServiceValidationError('この wp_user_id は既に使用されています')

    if User.query.filter_by(email=email).first():
        raise ServiceValidationError('このメールアドレスは既に使用されています')

    org = db.session.get(Organization, org_id)
    if not org:
        raise ServiceValidationError('指定された組織IDが存在しません')

    # --- ユーザー登録 ---
    user = User(
        wp_user_id=wp_user_id,
        name=name,
        email=email,
        organization_id=org_id
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()  # user.id をAccessScope登録に使用するため

    # --- AccessScope登録 ---
    access_scope = AccessScope(
        user_id=user.id,
        organization_id=org_id,
        role=role if isinstance(role, OrgRoleEnum) else OrgRoleEnum(role)
    )
    db.session.add(access_scope)

    db.session.commit()

    return {'message': 'ユーザーを登録しました', 'user': user}




def get_user_by_id(user_id, current_user):
    user = db.session.get(User, user_id)
    if not user:
        raise ServiceNotFoundError('ユーザーが見つかりません')

    if not check_org_access(current_user, user.organization_id, OrgRoleEnum.ORG_ADMIN):
        raise ServicePermissionError('権限がありません')

    return user

def update_user(user_id, data, current_user):
    user = db.session.get(User, user_id)
    if not user:
        raise ServiceNotFoundError('ユーザーが見つかりません')

    if not check_org_access(current_user, user.organization_id, OrgRoleEnum.ORG_ADMIN):
        raise ServicePermissionError('権限がありません')

    if 'name' in data:
        user.name = data['name']
    if 'wp_user_id' in data:
        user.wp_user_id = data['wp_user_id']
    if 'email' in data:
        user.email = data['email']
    if 'organization_id' in data:
        user.organization_id = data['organization_id']

    db.session.commit()
    return user

def delete_user(user_id, current_user):
    user = db.session.get(User, user_id)
    if not user:
        raise ServiceNotFoundError('ユーザーが見つかりません')

    if not check_org_access(current_user, user.organization_id, OrgRoleEnum.ORG_ADMIN):
        raise ServicePermissionError('権限がありません')

    from ..models import AccessScope
    try:
        AccessScope.query.filter_by(user_id=user.id).delete()
        db.session.delete(user)
        db.session.commit()
        return {'message': 'ユーザーと関連スコープを削除しました'}
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"delete_user error: {e}")
        raise ServiceValidationError(f'削除に失敗しました: {e}')

def get_users(requesting_user_id, organization_id=None):
    requester = db.session.get(User, requesting_user_id)
    if not requester:
        return []

    if not check_org_access(requester, organization_id or requester.organization_id, OrgRoleEnum.ORG_ADMIN):
        raise ServicePermissionError('権限がありません')

    all_orgs = Organization.query.all()
    base_org_id = organization_id or requester.organization_id
    base_org = db.session.get(Organization, base_org_id)
    if not base_org:
        raise ServiceNotFoundError('組織が見つかりません')

    descendants = get_descendant_organizations(base_org.id, all_orgs)
    org_ids = [org.id for org in descendants]

    users = (
        User.query
        .options(joinedload(User.organization))
        .filter(User.organization_id.in_(org_ids))
        .all()
    )

    return users

def get_user_by_email(email, current_user):
    user = User.query.filter_by(email=email).first()
    if not user:
        raise ServiceNotFoundError('ユーザーが見つかりません')

    if not check_org_access(current_user, user.organization_id, OrgRoleEnum.ORG_ADMIN):
        raise ServicePermissionError('権限がありません')

    return user

def get_user_by_wp_user_id(wp_user_id, current_user):
    user = User.query.filter_by(wp_user_id=wp_user_id).first()
    if not user:
        raise ServiceNotFoundError('ユーザーが見つかりません')

    if not check_org_access(current_user, user.organization_id, OrgRoleEnum.ORG_ADMIN):
        raise ServicePermissionError('権限がありません')

    return user

def get_users_by_org_tree(org_id, current_user):
    if not check_org_access(current_user, org_id, OrgRoleEnum.ORG_ADMIN):
        raise ServicePermissionError('権限がありません')

    try:
        org_ids = get_all_child_organizations(org_id)
        users = User.query.filter(User.organization_id.in_(org_ids)).all()
        return users
    except Exception as e:
        raise ServiceValidationError(str(e))
