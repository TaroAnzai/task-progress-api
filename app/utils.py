# utils.py

from .models import db, TaskAccessUser, TaskAccessOrganization, Organization

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

    if any(s.role == 'system_admin' for s in user.access_scopes):
        return True

    if any(s.role == 'org_admin' for s in user.access_scopes):
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

    if any(s.role == 'system_admin' for s in user.access_scopes):
        return True

    if any(s.role == 'org_admin' for s in user.access_scopes):
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
    """
    アクセスレベルの優先順位を比較して十分かどうかを判定
    """
    priority = {
        'view': 1,
        'edit': 2,
        'full': 3,
        'owner': 4
    }
    return priority.get(user_level, 0) >= priority.get(required_level, 0)
