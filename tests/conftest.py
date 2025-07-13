# tests/conftest.py

import os
import pytest
from app import create_app, db as _db
from app.models import User
from config import Config as BaseConfig


DB_FILE = "test.db"


class TestConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_FILE}"
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test"


@pytest.fixture(scope='session')
def app():
    app = create_app(TestConfig)

    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

        # ✅ テスト完了後に test.db を削除
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)


@pytest.fixture(scope='session')
def client(app):
    return app.test_client()


@pytest.fixture(scope='session')
def superuser(client):
    """スーパーユーザーを作成"""
    user = User(name="Admin", email="admin@example.com", is_superuser=True)
    user.set_password("adminpass")
    _db.session.add(user)
    _db.session.commit()
    return user


@pytest.fixture(scope='module')
def login_superuser(client, superuser):
    """ログイン状態にする"""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(superuser.id)
    return superuser
