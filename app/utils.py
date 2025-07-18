# utils.py

from .models import db, TaskAccessUser, TaskAccessOrganization, Organization
from .constants import (
    TaskAccessLevelEnum,
    OrgRoleEnum,
    TASK_ACCESS_PRIORITY,
    ORG_ROLE_PRIORITY,
)

def get_all_child_organizations(org_id):
    """
    指定された org_id の下位すべての組織ID一覧を再帰的に取得するユーティリティ関数
    """
    org_ids = set()
    queue = [org_id]

    while queue:
        current = queue.pop()
        org_ids.add(current)
        children = Organization.query.filter_by(parent_id=current).all()
        for child in children:
            if child.id not in org_ids:
                queue.append(child.id)

    return list(org_ids)

def get_descendant_organizations(root_id, all_orgs):
    """
    root_id を起点に、その下位の組織（自身を含む）をすべて返す
    """
    descendants = []

    # 自身の組織を追加
    root_org = next((org for org in all_orgs if org.id == root_id), None)
    if root_org:
        descendants.append(root_org)

    # 親IDベースのマップを作成
    org_map = {}
    for org in all_orgs:
        parent = org.parent_id
        org_map.setdefault(parent, []).append(org)

    def recurse(parent_id):
        for child in org_map.get(parent_id, []):
            descendants.append(child)
            recurse(child.id)

    recurse(root_id)
    return descendants

def can_view_task(user, task):
    """
    ユーザーが指定されたタスクを閲覧可能かどうかを判定する
    """
    if task.created_by == user.id:
        return True

    if any(s.role == OrgRoleEnum.SYSTEM_ADMIN for s in user.access_scopes):
        return True

    if any(s.role == OrgRoleEnum.ORG_ADMIN for s in user.access_scopes):
        all_orgs = Organization.query.all()
        descendant_orgs = get_descendant_organizations(user.organization_id, all_orgs)
        descendant_ids = [org.id for org in descendant_orgs]
        if task.organization_id in descendant_ids:
            return True

    user_scope = db.session.query(TaskAccessUser).filter_by(task_id=task.id, user_id=user.id).first()
    org_scope = db.session.query(TaskAccessOrganization).filter_by(task_id=task.id, organization_id=user.organization_id).first()

    if user_scope or org_scope:
        return True

    return False

def can_edit_task(user, task):
    """
    ユーザーが指定されたタスクを編集可能かどうかを判定する
    """
    if task.created_by == user.id:
        return True

    if any(s.role == OrgRoleEnum.SYSTEM_ADMIN for s in user.access_scopes):
        return True

    if any(s.role == OrgRoleEnum.ORG_ADMIN for s in user.access_scopes):
        all_orgs = Organization.query.all()
        descendant_orgs = get_descendant_organizations(user.organization_id, all_orgs)
        descendant_ids = [org.id for org in descendant_orgs]
        return task.organization_id in descendant_ids

    return False

def check_task_access(user, task, required_level):
    """
    アクセスレベルに応じてユーザーがタスクにアクセス可能かを判定
    """
    if task.created_by == user.id:
        return True

    for access in task.user_access:
        if access.user_id == user.id:
            if access_level_sufficient(access.access_level, required_level):
                return True

    if user.organization_id:
        for org_access in task.org_access:
            if org_access.organization_id == user.organization_id:
                if access_level_sufficient(org_access.access_level, required_level):
                    return True

    return False

def access_level_sufficient(user_level, required_level):
    """Return ``True`` if ``user_level`` satisfies ``required_level``."""
    if not isinstance(user_level, TaskAccessLevelEnum):
        user_level = TaskAccessLevelEnum(user_level)
    if not isinstance(required_level, TaskAccessLevelEnum):
        required_level = TaskAccessLevelEnum(required_level)

    return (
        TASK_ACCESS_PRIORITY.get(user_level, 0)
        >= TASK_ACCESS_PRIORITY.get(required_level, 0)
    )

def check_org_access(user, organization_id: int, required_role: OrgRoleEnum = OrgRoleEnum.MEMBER) -> bool:
    """Return True if user has required_role for organization_id.

    SYSTEM_ADMIN: 同一会社全組織にアクセス可能
    ORG_ADMIN: 自組織＋子組織にアクセス可能
    MEMBER: 自組織のみ
    """

    if getattr(user, "is_superuser", False):
        return True

    target_org = db.session.get(Organization, organization_id)
    if not target_org:
        return False

    highest_priority = 0

    for scope in user.access_scopes:
        # SYSTEM_ADMIN: 同一会社全組織
        if scope.role == OrgRoleEnum.SYSTEM_ADMIN:
            scope_org = scope.organization or db.session.get(Organization, scope.organization_id)
            if scope_org and scope_org.company_id == target_org.company_id:
                return True  # 早期return

        # ORG_ADMIN: 自組織＋子組織
        elif scope.role == OrgRoleEnum.ORG_ADMIN:
            base_id = scope.organization_id or user.organization_id
            descendant_ids = get_all_child_organizations(base_id)
            if base_id not in descendant_ids:
                descendant_ids.append(base_id)  # 自組織も含める
            if organization_id in descendant_ids:
                highest_priority = max(highest_priority, ORG_ROLE_PRIORITY[OrgRoleEnum.ORG_ADMIN])

        # MEMBER: 自組織のみ
        elif scope.organization_id == organization_id:
            highest_priority = max(highest_priority, ORG_ROLE_PRIORITY[OrgRoleEnum.MEMBER])

    return highest_priority >= ORG_ROLE_PRIORITY.get(required_role, 0)


def require_superuser(user):
    if not getattr(user, 'is_superuser', False):
        from flask import abort
        abort(403, description="This action requires superuser privileges.")


def is_valid_status_id(status_id) -> bool:
    """Return True if status_id exists and is defined in ``StatusEnum``."""
    from app.models import Status
    from .constants import StatusEnum

    status = db.session.get(Status, status_id)
    if not status:
        return False
    try:
        StatusEnum(status.name)
        return True
    except ValueError:
        return False



