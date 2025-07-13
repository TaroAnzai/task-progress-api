from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import event, Column, Boolean, UniqueConstraint
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime, date
import sqlite3
from app import db


# SQLite: enforce foreign key constraint
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# 論理削除対応
class SoftDeleteQuery(db.Query):
    _with_deleted = False

    def with_deleted(self):
        self._with_deleted = True
        return self

    def __iter__(self):
        if self._with_deleted:
            return super().__iter__()
        return super(SoftDeleteQuery, self.filter_by(is_deleted=False)).__iter__()

    def get(self, ident):
        entity = self._only_full_mapper_zero("get").entity
        obj = db.session.get(entity, ident)
        if self._with_deleted:
            return obj
        if obj is not None and getattr(obj, "is_deleted", False):
            return None
        return obj


class SoftDeleteMixin:
    is_deleted = Column(Boolean, default=False, nullable=False, server_default='0')

    def soft_delete(self):
        self.is_deleted = True

    def restore(self):
        self.is_deleted = False

    @declared_attr
    def query_class(cls):
        return SoftDeleteQuery


# 会社
class Company(db.Model, SoftDeleteMixin):
    __tablename__ = 'company'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)

    organizations = db.relationship('Organization', backref='company', cascade="all, delete-orphan")

    def to_dict(self):
        return {'id': self.id, 'name': self.name}


# 組織
class Organization(db.Model):
    __tablename__ = 'organization'
    __table_args__ = (
        UniqueConstraint('company_id', 'org_code', name='uix_company_orgcode'),
        {'sqlite_autoincrement': True},
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    org_code = db.Column(db.String(50), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=True)
    level = db.Column(db.Integer, default=1)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'org_code': self.org_code,
            'company_id': self.company_id,
            'company_name': self.company.name if self.company else None,
            'parent_id': self.parent_id,
            'level': self.level
        }


# ユーザー
class User(db.Model, UserMixin):
    __table_args__ = {'sqlite_autoincrement': True}
    id = db.Column(db.Integer, primary_key=True)
    wp_user_id = db.Column(db.Integer, unique=True, nullable=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    is_superuser = db.Column(db.Boolean, default=False)

    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=True)
    organization = db.relationship('Organization', backref='users')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_org=False):
        user_dict = {
            'id': self.id,
            'wp_user_id': self.wp_user_id,
            'name': self.name,
            'email': self.email,
            'is_superuser': self.is_superuser,
        }

        if include_org:
            user_dict.update({
                'organization_id': self.organization_id,
                'organization_name': self.organization.name if self.organization else None
            })

        return user_dict


# アクセススコープ
class AccessScope(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    user = db.relationship('User', backref='access_scopes')
    organization = db.relationship('Organization', backref='access_scopes')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'organization_id': self.organization_id,
            'role': self.role
        }


# タスク
class Task(db.Model, SoftDeleteMixin):
    __tablename__ = 'task'
    __table_args__ = {'sqlite_autoincrement': True}
    id = db.Column(db.Integer, primary_key=True)
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'), nullable=True)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    due_date = db.Column(db.Date)
    assigned_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    display_order = db.Column(db.Integer, nullable=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))

    creator = db.relationship('User', foreign_keys=[created_by], backref='created_tasks')

    def to_dict(self):
        return {
            'id': self.id,
            'status_id': self.status_id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'assigned_user_id': self.assigned_user_id,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'display_order': self.display_order,
            'organization_id': self.organization_id
        }


# オブジェクティブ
class Objective(db.Model, SoftDeleteMixin):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    title = db.Column(db.String(255))
    due_date = db.Column(db.Date)
    assigned_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    display_order = db.Column(db.Integer, default=0)
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'), default=1)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'title': self.title,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'assigned_user_id': self.assigned_user_id,
            'status_id': self.status_id,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat()
        }


# ステータス
class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def to_dict(self):
        return {'id': self.id, 'name': self.name}


# 進捗
class ProgressUpdate(db.Model, SoftDeleteMixin):
    id = db.Column(db.Integer, primary_key=True)
    objective_id = db.Column(db.Integer, db.ForeignKey('objective.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
    detail = db.Column(db.Text)
    report_date = db.Column(db.Date)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'objective_id': self.objective_id,
            'status_id': self.status_id,
            'detail': self.detail,
            'report_date': self.report_date.isoformat() if self.report_date else None,
            'updated_by': self.updated_by,
            'created_at': self.created_at.isoformat()
        }


# タスクアクセス（ユーザー単位）
class TaskAccessUser(db.Model):
    __tablename__ = 'task_access_user'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    access_level = db.Column(db.String(50), nullable=False, default='view')

    task = db.relationship('Task', backref='user_access')
    user = db.relationship('User', backref='task_access')

    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'user_id': self.user_id,
            'access_level': self.access_level
        }


# タスクアクセス（組織単位）
class TaskAccessOrganization(db.Model):
    __tablename__ = 'task_access_organization'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    access_level = db.Column(db.String(50), nullable=False, default='view')

    task = db.relationship('Task', backref='org_access')
    organization = db.relationship('Organization', backref='task_access')

    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'organization_id': self.organization_id,
            'access_level': self.access_level
        }


# タスク並び順
class UserTaskOrder(db.Model):
    __tablename__ = 'user_task_order'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    display_order = db.Column(db.Integer, nullable=False)

    task = db.relationship('Task', backref='user_orders')
    user = db.relationship('User', backref='task_orders')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'task_id', name='uix_user_task'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'task_id': self.task_id,
            'display_order': self.display_order
        }
