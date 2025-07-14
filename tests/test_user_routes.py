import pytest
from typing import Dict, Any

# --- Constants ---
VALID_USER_DATA = {
    'name': 'ValidUser',
    'email': 'valid@example.com',
    'password': 'password123',
    'role': 'member'
}

# --- Helper Functions ---
def create_user_payload(org_id: int, **overrides) -> Dict[str, Any]:
    """ユーザー作成用のペイロードを生成"""
    payload = {**VALID_USER_DATA, 'organization_id': org_id}
    payload.update(overrides)
    return payload

def assert_user_created(response, expected_name: str = None):
    """ユーザー作成レスポンスの共通アサーション"""
    assert response.status_code == 201
    user = response.get_json()['user']
    if expected_name:
        assert user['name'] == expected_name
    return user

def assert_error_response(response, expected_status: int, expected_message: str = None):
    """エラーレスポンスの共通アサーション"""
    assert response.status_code == expected_status
    error_data = response.get_json()
    if expected_message:
        assert expected_message in error_data.get('error', '')
    return error_data

# --- Fixtures ---
@pytest.fixture(scope='module')
def test_company(client, login_superuser):
    """テスト用会社を作成"""
    data = {'name': 'Test Company'}
    res = client.post("/companies/", json=data)
    assert res.status_code == 201
    return res.get_json()

@pytest.fixture(scope='module')
def root_org_data(client, login_superuser, test_company):
    """テスト用組織データ"""
    payload = {
        'name': 'RootOrg',
        'org_code': 'root',
        'company_id': test_company['id']
    }
    res = client.post('/organizations/', json=payload)
    assert res.status_code == 201
    return res.get_json()

@pytest.fixture
def sample_user(client, root_org_data):
    """テスト用サンプルユーザー"""
    payload = create_user_payload(
        root_org_data['id'],
        email='sample@example.com'  # 他のテストと重複しないメール
    )
    res = client.post('/users', json=payload)
    return assert_user_created(res)

# --- Test Classes ---
class TestUserCreation:
    """ユーザー作成に関するテスト"""
    
    def test_create_user_valid(self, client, login_superuser, root_org_data):
        """有効なデータでユーザー作成"""
        payload = create_user_payload(root_org_data['id'])
        res = client.post('/users', json=payload)
        assert_user_created(res, 'ValidUser')
    
    def test_create_user_missing_fields(self, client):
        """必須フィールド不足でユーザー作成失敗"""
        res = client.post('/users', json={'email': 'incomplete@example.com'})
        error_data = assert_error_response(res, 400)
        assert 'name' in error_data['error']
    
    def test_create_user_duplicate_email(self, client, root_org_data):
        """重複メールアドレスでユーザー作成失敗"""
        # まず最初のユーザーを作成
        first_payload = create_user_payload(
            root_org_data['id'],
            name='FirstUser',
            email='duplicate@example.com'
        )
        first_res = client.post('/users', json=first_payload)
        assert_user_created(first_res)
        
        # 同じメールアドレスで2回目の登録を試行
        second_payload = create_user_payload(
            root_org_data['id'],
            name='SecondUser',
            email='duplicate@example.com'  # 重複メール
        )
        res = client.post('/users', json=second_payload)
        assert_error_response(res, 400, '既に使用されています')

class TestUserRetrieval:
    """ユーザー取得に関するテスト"""
    
    def test_get_user_not_found(self, client):
        """存在しないユーザーの取得"""
        res = client.get('/users/999999')
        assert res.status_code == 404
    
    def test_get_user_by_email(self, client, root_org_data):
        """メールアドレスでユーザー取得"""
        # テスト用ユーザーを作成
        email = 'email_lookup@example.com'
        payload = create_user_payload(root_org_data['id'], email=email)
        client.post('/users', json=payload)
        
        # メールアドレスでユーザー取得
        res = client.get(f'/users/by-email?email={email}')
        assert res.status_code == 200
        responce_data = res.get_json()
        assert responce_data['email'] == email
    
    def test_get_user_by_wp_user_id(self, client, root_org_data):
        """WordPress User IDでユーザー取得"""
        wp_user_id = 1001
        payload = create_user_payload(
            root_org_data['id'],
            name='WPID',
            email='wpid@example.com',
            wp_user_id=wp_user_id
        )
        client.post('/users', json=payload)
        
        res = client.get(f'/users/id-lookup?wp_user_id={wp_user_id}')
        assert res.status_code == 200
        responce_data= res.get_json()
        assert responce_data['wp_user_id'] == wp_user_id
    
    def test_get_users_by_org_tree(self, client, root_org_data):
        """組織ツリーでユーザー一覧取得"""
        res = client.get(f'/users/by-org-tree/{root_org_data["id"]}')
        assert res.status_code == 200
        users = res.get_json()
        assert isinstance(users, list)

class TestUserModification:
    """ユーザー更新・削除に関するテスト"""
    
    def test_update_user(self, client, root_org_data):
        """ユーザー情報更新"""
        # テストユーザー作成
        payload = create_user_payload(
            root_org_data['id'],
            name='ToUpdate',
            email='update_me@example.com'
        )
        create_res = client.post('/users', json=payload)
        user_id = assert_user_created(create_res)['id']
        
        # 更新実行
        update_data = {'name': 'UpdatedName'}
        res = client.put(f'/users/{user_id}', json=update_data)
        assert res.status_code == 200
        updated_user = res.get_json()
        assert updated_user['name'] == 'UpdatedName'
    
    def test_delete_user(self, client, root_org_data):
        """ユーザー削除"""
        # テストユーザー作成
        payload = create_user_payload(
            root_org_data['id'],
            name='ToDelete',
            email='delete_me@example.com'
        )
        create_res = client.post('/users', json=payload)
        user_id = assert_user_created(create_res)['id']
        
        # 削除実行
        res = client.delete(f'/users/{user_id}')
        assert res.status_code == 200
        message = res.get_json()['message']
        assert '削除' in message

# --- パラメータ化テストの例 ---
class TestUserCreationParameterized:
    """パラメータ化されたユーザー作成テスト"""
    
    @pytest.mark.parametrize("missing_field", [
        'name', 'email', 'password', 'organization_id'
    ])
    def test_create_user_missing_required_fields(self, client, root_org_data, missing_field):
        """各必須フィールドが不足している場合のテスト"""
        payload = create_user_payload(root_org_data['id'])
        del payload[missing_field]
        
        res = client.post('/users', json=payload)
        error_data = assert_error_response(res, 400)
        assert missing_field in error_data['error']
    
    @pytest.mark.parametrize("invalid_email", [
        'invalid-email',
        'missing@domain',
        '@missing-local.com',
        'spaces in@email.com'
    ])
    def test_create_user_invalid_email_format(self, client, root_org_data, invalid_email):
        """無効なメールアドレス形式のテスト"""
        payload = create_user_payload(root_org_data['id'], email=invalid_email)
        res = client.post('/users', json=payload)
        assert_error_response(res, 400)