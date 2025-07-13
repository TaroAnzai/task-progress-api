from sqlalchemy.exc import IntegrityError
from app.models import db, Company

# Create
def create_company(name):
    existing = Company.query.filter_by(name=name, is_deleted=False).first()
    if existing:
        raise ValueError("Company with the same name already exists.")

    company = Company(name=name)
    db.session.add(company)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ValueError("Failed to create company due to DB constraint.")
    return company


# Read: 全件取得（論理削除除く）
def get_all_companies():
    return Company.query.filter_by(is_deleted=False).all()


# Read: IDで取得（論理削除除く）
def get_company_by_id(company_id):
    return Company.query.filter_by(id=company_id, is_deleted=False).first()


# Read: 削除済も含めて取得
def get_company_by_id_with_deleted(company_id):
    return db.session.get(Company, company_id)


# Update
def update_company(company_id, new_name):
    company = get_company_by_id(company_id)
    if not company:
        return None

    company.name = new_name
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ValueError("Failed to update company name due to DB constraint.")

    return company


# 論理削除
def delete_company(company_id):
    company = get_company_by_id(company_id)
    if not company:
        return False

    company.soft_delete()
    db.session.commit()
    return True


# 論理削除から復元
def restore_company(company_id):
    company = get_company_by_id_with_deleted(company_id)
    if not company:
        return False

    company.restore()
    db.session.commit()
    return True


# （任意）物理削除
def delete_company_permanently(company_id):
    company = get_company_by_id_with_deleted(company_id)
    if not company:
        return False

    db.session.delete(company)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ValueError("Cannot delete company due to foreign key constraint.")
    return True
