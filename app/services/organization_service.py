from app.models import db, Organization
from sqlalchemy.exc import IntegrityError


def can_create_root_organization(company_id):
    """
    指定された会社にルート組織（parent_id=None）が既に存在するかどうかを確認
    """
    existing = Organization.query.filter_by(company_id=company_id, parent_id=None).first()
    return existing is None


def create_organization(name, org_code, company_id=None, parent_id=None):
    if parent_id:
        parent = db.session.get(Organization, parent_id)
        if not parent:
            raise ValueError("指定された親組織が存在しません。")
        if company_id and company_id != parent.company_id:
            raise ValueError("指定されたcompany_idと親組織のcompany_idが一致しません。")
        company_id = parent.company_id
        level = parent.level + 1
    else:
        if not company_id:
            raise ValueError("ルート組織にはcompany_idが必須です。")
        level = 1

    # org_codeの重複チェック（同一会社内）
    existing = Organization.query.filter_by(company_id=company_id, org_code=org_code).first()
    if existing:
        raise ValueError("同一会社内でこの org_code は既に使用されています。")

    org = Organization(
        name=name,
        org_code=org_code,
        company_id=company_id,
        parent_id=parent_id,
        level=level
    )
    db.session.add(org)
    db.session.commit()
    return org



def get_organization_by_id(org_id):
    org = db.session.get(Organization, org_id)
    return org if org else None


def get_organizations(company_id=None):
    query = Organization.query
    if company_id:
        query = query.filter_by(company_id=company_id)
    return [org for org in query.all()]


def update_organization(org_id, name=None, parent_id=None):
    org = db.session.get(Organization, org_id)
    if not org:
        return None

    if name:
        org.name = name

    if parent_id != org.parent_id:
        if parent_id:
            parent = db.session.get(Organization, parent_id)
            if not parent:
                raise ValueError("指定された親組織が存在しません。")
            org.level = parent.level + 1
        else:
            org.level = 1
        org.parent_id = parent_id

    db.session.commit()
    return org


def delete_organization(org_id):
    org = db.session.get(Organization, org_id)
    if not org:
        return False, "組織が存在しません。"

    has_children = Organization.query.filter_by(parent_id=org_id).first()
    if has_children:
        return False, "子組織が存在するため削除できません。"

    db.session.delete(org)
    db.session.commit()
    return True, "削除成功"


def get_organization_tree(company_id=None):
    """
    Organization.to_dict() を使ってツリー構造を再帰的に構築する
    """
    orgs = Organization.query
    if company_id:
        orgs = orgs.filter_by(company_id=company_id)
    orgs = orgs.all()

    # 各 org を dict に変換し、children を追加
    org_map = {}
    for org in orgs:
        org_dict = org.to_dict()
        org_dict['children'] = []
        org_map[org.id] = org_dict

    # ツリー構造を作成
    root_nodes = []
    for org in org_map.values():
        parent_id = org['parent_id']
        if parent_id and parent_id in org_map:
            org_map[parent_id]['children'].append(org)
        else:
            root_nodes.append(org)

    return root_nodes


def get_children(parent_id):
    """
    指定された親組織IDに属する子組織を返す（モデルオブジェクト）
    """
    return Organization.query.filter_by(parent_id=parent_id).all()
