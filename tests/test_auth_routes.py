import pytest
from app import db
from app.models import User, Company, Organization

def longin_superuser(client, superuser):
    """スーパーユーザーをログイン状態にする"""
    res = client.post('/auth/login', json={
                'email': superuser['email'],
                'password': superuser['password']
            })
    assert res.status_code == 200
@pytest.fixture(scope='module')
def create_test_company_data():
    return {"name": "Auth Test Company"}

@pytest.fixture(scope='module')
def test_auth_company(client, create_test_company_data, superuser):
    longin_superuser(client, superuser)
    response = client.post("/companies/", json=create_test_company_data)
    assert response.status_code == 201
    return response.get_json()

@pytest.fixture(scope='module')
def test_auth_organization(client, test_auth_company, superuser):
    longin_superuser(client, superuser)
    org_data = {
        'name': 'Auth Test Organization',
        'org_code': 'auth_test_org',
        'company_id': test_auth_company['id']
    }
    response = client.post('/organizations/', json=org_data)
    assert response.status_code == 201
    return response.get_json()

@pytest.fixture(scope='module')
def test_user_data(test_auth_organization):
    return {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123",
        'organization_id': test_auth_organization['id']
    }

@pytest.fixture(scope='module')
def test_user_with_org_data(test_auth_organization):
    return {
        "name": "Test User with Org",
        "email": "testorg@example.com",
        "password": "testpassword123",
        "organization_id": test_auth_organization['id']
    }

@pytest.fixture(scope='module')
def test_wp_user_data(test_auth_organization):
    return {
        "name": "WP Test User",
        "email": "wpuser@example.com",
        "wp_user_id": 12345,
        "password": "wppassword123",
        "organization_id": test_auth_organization['id']
    }

@pytest.fixture(scope='module')
def registered_user(client, test_user_data, superuser):
    longin_superuser(client, superuser)
    # ユーザー登録エンドポイントを使用してユーザーを作成
    response = client.post("/users", json=test_user_data)
    print("Registered user response:", response.get_json())  # Debugging line
    assert response.status_code == 201
    return response.get_json()

@pytest.fixture(scope='module')
def registered_user_with_org(client, test_user_with_org_data, superuser):
    longin_superuser(client, superuser)
    response = client.post("/users", json=test_user_with_org_data)
    assert response.status_code == 201
    return response.get_json()

@pytest.fixture(scope='module')
def registered_wp_user(client, test_wp_user_data, superuser):
    longin_superuser(client, superuser)
    response = client.post("/users", json=test_wp_user_data)
    assert response.status_code == 201
    return response.get_json()

def test_login_with_email_success(client, registered_user, test_user_data):
    """メールアドレスでのログイン成功テスト"""
    login_data = {
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "ログイン成功"
    assert data["user"]["email"] == test_user_data["email"]
    assert data["user"]["name"] == test_user_data["name"]

def test_login_with_email_invalid_email(client):
    """存在しないメールアドレスでのログイン失敗テスト"""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "anypassword"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 401
    data = response.get_json()
    assert "無効" in data["error"]

def test_login_with_email_invalid_password(client, registered_user, test_user_data):
    """間違ったパスワードでのログイン失敗テスト"""
    login_data = {
        "email": test_user_data["email"],
        "password": "wrongpassword"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 401
    data = response.get_json()
    assert "無効" in data["error"]

def test_login_with_email_missing_fields(client):
    """必須フィールドが不足している場合のテスト"""
    # emailが不足
    response = client.post("/auth/login", json={"password": "testpassword"})
    assert response.status_code == 400
    data = response.get_json()
    assert "必須" in data["error"]

    # passwordが不足
    response = client.post("/auth/login", json={"email": "test@example.com"})
    assert response.status_code == 400
    data = response.get_json()
    assert "必須" in data["error"]

def test_login_with_wp_user_id_success(client, registered_wp_user, test_wp_user_data):
    """wp_user_idでのログイン成功テスト"""
    login_data = {
        "wp_user_id": test_wp_user_data["wp_user_id"]
    }
    response = client.post("/auth/login/by-id", json=login_data)
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "ログイン成功"
    assert data["user"]["wp_user_id"] == test_wp_user_data["wp_user_id"]
    assert data["user"]["name"] == test_wp_user_data["name"]

def test_login_with_wp_user_id_not_found(client):
    """存在しないwp_user_idでのログイン失敗テスト"""
    login_data = {
        "wp_user_id": 99999
    }
    response = client.post("/auth/login/by-id", json=login_data)
    assert response.status_code == 404
    data = response.get_json()
    assert "見つかりません" in data["error"]

def test_login_with_wp_user_id_missing_field(client):
    """wp_user_idが不足している場合のテスト"""
    response = client.post("/auth/login/by-id", json={})
    assert response.status_code == 400
    data = response.get_json()
    assert "必須" in data["error"]

def test_get_current_user_authenticated(client, registered_user_with_org, test_user_with_org_data):
    """認証済みユーザーの現在のユーザー情報取得テスト"""
    # まずログイン
    login_data = {
        "email": test_user_with_org_data["email"],
        "password": test_user_with_org_data["password"]
    }
    login_response = client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200

    # 現在のユーザー情報を取得
    response = client.get("/auth/current_user")
    assert response.status_code == 200
    data = response.get_json()
    assert data["email"] == test_user_with_org_data["email"]
    assert data["name"] == test_user_with_org_data["name"]
    assert data["organization_id"] == test_user_with_org_data["organization_id"]
    assert "organization_name" in data

def test_get_current_user_unauthenticated(client):
    """未認証状態での現在のユーザー情報取得テスト"""
    # 念のためログアウトしてセッションを初期化
    client.post("/auth/logout")
    """未認証状態での現在のユーザー情報取得テスト"""

    response = client.get("/auth/current_user")
    assert response.status_code == 401
    data = response.get_json()
    assert "ログインが必要です" in data["error"]

def test_logout_authenticated(client, registered_user, test_user_data):
    """認証済みユーザーのログアウトテスト"""
    # まずログイン
    login_data = {
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    }
    login_response = client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200

    # ログアウト
    response = client.post("/auth/logout")
    assert response.status_code == 200
    data = response.get_json()
    assert "ログアウト" in data["message"]

    # ログアウト後は現在のユーザー情報が取得できない
    response = client.get("/auth/current_user")
    assert response.status_code == 401

def test_logout_unauthenticated(client):
    """未認証状態でのログアウトテスト"""
    response = client.post("/auth/logout")
    assert response.status_code == 401
    data = response.get_json()
    assert "ログインが必要" in data["error"]

def test_login_logout_flow(client, registered_user, test_user_data):
    """ログイン→ユーザー情報取得→ログアウトの一連の流れをテスト"""
    # 1. ログイン
    login_data = {
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    }
    login_response = client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200

    # 2. 現在のユーザー情報取得
    current_user_response = client.get("/auth/current_user")
    assert current_user_response.status_code == 200
    user_data = current_user_response.get_json()
    assert user_data["email"] == test_user_data["email"]

    # 3. ログアウト
    logout_response = client.post("/auth/logout")
    assert logout_response.status_code == 200

    # 4. ログアウト後は認証が必要なエンドポイントにアクセスできない
    current_user_response = client.get("/auth/current_user")
    assert current_user_response.status_code == 401

def test_multiple_login_attempts(client, registered_user, test_user_data):
    """複数回のログイン試行テスト"""
    login_data = {
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    }
    
    # 複数回ログインしても成功する
    for i in range(3):
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "ログイン成功"

def test_login_with_different_methods(client, registered_wp_user, test_wp_user_data):
    """異なるログイン方法でのテスト"""
    # wp_user_idでログイン
    wp_login_data = {
        "wp_user_id": test_wp_user_data["wp_user_id"]
    }
    wp_response = client.post("/auth/login/by-id", json=wp_login_data)
    assert wp_response.status_code == 200

    # ログアウト
    logout_response = client.post("/auth/logout")
    assert logout_response.status_code == 200

    # 今度はメールアドレスでログイン
    email_login_data = {
        "email": test_wp_user_data["email"],
        "password": test_wp_user_data["password"]
    }
    email_response = client.post("/auth/login", json=email_login_data)
    assert email_response.status_code == 200