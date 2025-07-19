from sqlalchemy.exc import IntegrityError
from app.models import db, Company
from app.service_errors import (
    ServiceValidationError,
    ServiceAuthenticationError,
    ServicePermissionError,
    ServiceNotFoundError,
)

# Create
def create_company(name):
    existing = Company.query.filter_by(name=name, is_deleted=False).first()
    if existing:
        raise ServiceValidationError("Company with the same name already exists.")
    company = Company(name=name)
    db.session.add(company)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ServiceValidationError("Failed to create company due to DB constraint.")
    return company


# Read: 全件取得（論理削除除く）
def get_all_companies():
    companies = Company.query.filter_by(is_deleted=False).all()
    if not companies:
        raise ServiceNotFoundError("Companies not found")
    return companies


# Read: IDで取得（論理削除除く）
def get_company_by_id(company_id):
    company = Company.query.filter_by(id=company_id, is_deleted=False).first()
    if not company:
        raise ServiceNotFoundError("Company not found")
    return company


# Read: 削除済も含めて取得
def get_company_by_id_with_deleted(company_id):
    company = db.session.get(Company, company_id)
    if not company:
        raise ServiceNotFoundError("Company not found")
    return company


# Update
def update_company(company_id, new_name):
    company = get_company_by_id(company_id)
    if not company:
        raise ServiceNotFoundError("Company not found")
    company.name = new_name
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ServiceValidationError("Failed to update company name due to DB constraint.")

    return company


# 論理削除
def delete_company(company_id):
    company = get_company_by_id(company_id)
    if not company:
        raise ServiceNotFoundError("Company not found")

    company.soft_delete()
    db.session.commit()
    return True


# 論理削除から復元
def restore_company(company_id):
    company = get_company_by_id_with_deleted(company_id)
    if not company:
        raise ServiceNotFoundError("Company not found")

    company.restore()
    db.session.commit()
    return True


# （任意）物理削除
def delete_company_permanently(company_id):
    company = get_company_by_id_with_deleted(company_id)
    if not company:
        raise ServiceNotFoundError("Company not found")

    db.session.delete(company)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ServiceValidationError("Cannot delete company due to foreign key constraint.")
    return True
