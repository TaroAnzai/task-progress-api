import pytest
from app import create_app, db
from flask import Flask
from dotenv import load_dotenv
from app.extensions import db
from app.models import User, Organization
from werkzeug.security import generate_password_hash

@pytest.fixture
def app():
    load_dotenv()
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "WTF_CSRF_ENABLED": False,  # フォーム使ってる場合
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()



@pytest.fixture
def superuser(app):
    with app.app_context():
        # スーパーユーザーを作成（organization_id=None, is_superuser=True）
        user = User(
            name="Admin Test User",
            email="admin@example.com",
            password_hash=generate_password_hash("adminpass"),
            is_superuser=True,
            organization_id=None  # 明示的にnullを指定
        )
        db.session.add(user)
        db.session.commit()

        return user
