# tests/conftest.py

import os
import pytest
from app import create_app, db as _db
from app.models import User
from config import Config as BaseConfig
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

DB_FILE = "test.db"


class TestConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_FILE}"
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test"

    
# ✅ pytest実行時のみ .env.test を自動で読み込む
def pytest_configure(config):
    # すでに本番用 .env が読み込まれている場合は上書きする
    env_file = ".env.test"
    if os.path.exists(env_file):
        print(f"\n[pytest] Loading environment from {env_file} ...")
        load_dotenv(env_file, override=True)
    else:
        print("\n[pytest] WARNING: .env.test file not found!")


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


@pytest.fixture(scope="session")
def superuser(app):
    with app.app_context():
        user = User(
            name="SuperAdmin",
            email="superadmin@example.com",
            is_superuser=True,
            password_hash=generate_password_hash("superpass")
        )
        _db.session.add(user)
        _db.session.commit()
        return {"id": user.id, "email": user.email, "password": "superpass"}


# 2. テスト用会社の登録（エンドポイント）
@pytest.fixture(scope="session")
def test_company(client, superuser):
    # スーパーユーザーでログイン
    res = client.post("/auth/login", json={"email": superuser["email"], "password": superuser["password"]})
    assert res.status_code == 200
    res = client.post("/companies", json={"name": "TestCompany"})
    assert res.status_code == 201
    return res.get_json()

# 3. テスト用ルート組織の登録（エンドポイント）
@pytest.fixture(scope="session")
def root_org(client, test_company):
    res = client.post("/organizations", json={
        "name": "RootOrg",
        "org_code": "root",
        "company_id": test_company["id"]
    })
    assert res.status_code == 201
    return res.get_json()

# 4. テスト用ユーザー（systemadmin）をルート組織に登録（エンドポイント）
@pytest.fixture(scope="session")
def systemadmin_user(client, root_org, superuser):
        # スーパーユーザーでログイン
    res = client.post("/auth/login", json={"email": superuser["email"], "password": superuser["password"]})
    assert res.status_code == 200
    res = client.post("/users", json={
        "name": "SystemAdmin",
        "email": "systemadmin@example.com",
        "password": "adminpass",
        "organization_id": root_org["id"],
        "role": "system_admin"
    })
    assert res.status_code == 201
    return res.get_json()

@pytest.fixture(scope="session")
def task_access_users(client, systemadmin_user, root_org):
    res = client.post("/auth/login", json={"email": systemadmin_user['user']['email'], "password": 'adminpass'})
    assert res.status_code == 200
    access_levels = ["view", "edit", "full", "owner"]
    created_users = {}

    for level in access_levels:
        res = client.post("/users", json={
            "name": f"TaskUser_{level}",
            "email": f"taskuser_{level}@example.com",
            "password": "testpass",
            "organization_id": root_org["id"],
            "role": "member"  # 組織上の役割はmemberでもOK、タスクアクセスレベルは別テーブルで管理
        })
        assert res.status_code == 201
        user_data = res.get_json()

        # ★タスクアクセス権限の付与エンドポイント（例）
        client.post("/task_access", json={
            "task_id": 1,  # テスト用タスクID（別fixtureで事前作成が必要）
            "user_id": user_data['user']["id"],
            "access_level": level
        })

        created_users[level] = user_data['user']
        created_users[level]['password'] = 'testpass'

    return created_users

@pytest.fixture(scope="session")
def system_related_users(client, root_org):
    """
    システム関連のユーザー（member, org_admin, system_admin）を作成して返す。
    戻り値: {"member": {...}, "org_admin": {...}, "system_admin": {...}}
    ※ {...} は userデータ + "password" を含む
    """
    roles = ["member", "org_admin", "system_admin"]
    created_users = {}

    for role in roles:
        res = client.post("/users", json={
            "name": f"SystemUser_{role}",
            "email": f"systemuser_{role}@example.com",
            "password": "testpass",
            "organization_id": root_org["id"],
            "role": role
        })
        assert res.status_code == 201
        user_data = res.get_json().get("user", res.get_json())  # userキーがあれば抽出
        user_data["password"] = "testpass"  # ログイン用に追加
        created_users[role] = user_data

    return created_users


@pytest.fixture(scope="module")
def superuser_login(client, superuser):
    """スーパーユーザーでログインした状態を返す"""
    res = client.post("/auth/login", json={
        "email": superuser["email"],
        "password": superuser["password"]
    })
    assert res.status_code == 200
    yield client
    client.post("/auth/logout")

@pytest.fixture(scope="function")
def login_as_user(client):
    """任意ユーザーでログインするためのヘルパー"""
    def _login(email, password):
        client.post("/auth/logout")  # 念のためログアウト
        res = client.post("/auth/login", json={"email": email, "password": password})
        assert res.status_code == 200
        return client
    yield _login
    client.post("/auth/logout")

@pytest.fixture(scope="function")
def system_admin_client(systemadmin_user, login_as_user):
    """システム管理者でログインしたクライアントを返す"""
    client = login_as_user(systemadmin_user["user"]["email"], "adminpass")
    return client

@pytest.fixture(scope="function")
def setup_task_access(system_admin_client, task_access_users):
    def _setup_task_access(task):
        """タスクに対して各ユーザーのアクセス権限を設定"""
        task_id = task["id"]

        user_access = [
            {"user_id": task_access_users[level]["id"], "access_level": level}
            for level in ["view", "edit", "full", "owner"]
        ]
        org_access = []  # 必要に応じて組織アクセスも設定可能

        res = system_admin_client.put(
            f"/tasks/{task_id}/scope/access_levels",
            json={"user_access": user_access, "organization_access": org_access}
        )
        assert res.status_code == 200
        return task_id
    return _setup_task_access