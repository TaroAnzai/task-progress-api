from typing import Any, Dict

import pytest

from tests.utils import check_response_message

# --- Constants ---
VALID_USER_DATA = {
    'name': 'ValidUser',
    'email': 'valid@example.com',
    'password': 'password123',
    'role': 'MEMBER'
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


# --- Fixtures ---

@pytest.fixture
def sample_user(system_related_users, login_as_user, root_org_data):
    system_admin = system_related_users['system_admin']
    client = login_as_user(system_admin['email'], system_admin['password'])
    """テスト用サンプルユーザー"""
    payload = create_user_payload(
        root_org_data['id'],
        email='sample@example.com'  # 他のテストと重複しないメール
    )
    res = client.post('/progress/users', json=payload)
    return assert_user_created(res)



# --- Test Classes ---
class TestUserCreation:
    """ユーザー作成に関するテスト"""
    def test_create_user_valid(self, login_as_user, system_related_users, root_org):
        system_admin = system_related_users['system_admin']
        client = login_as_user(system_admin['email'], system_admin['password'])
        """有効なデータでユーザー作成"""
        payload = create_user_payload(root_org['id'])
        res = client.post('/progress/users', json=payload)
        assert_user_created(res, 'ValidUser')
    
    def test_create_user_missing_fields(self, login_as_user, system_related_users):
        system_admin = system_related_users['system_admin']
        client = login_as_user(system_admin['email'], system_admin['password'])
        """必須フィールド不足でユーザー作成失敗"""
        res = client.post('/progress/users', json={'email': 'incomplete@example.com'})
        assert res.status_code == 422
        data = res.get_json()
        for field in ['name', 'password', 'organization_id']:
            assert check_response_message('Missing data for required field.', data, field)
    
    def test_create_user_duplicate_email(self, login_as_user, system_related_users, root_org):
        system_admin = system_related_users['system_admin']
        client = login_as_user(system_admin['email'], system_admin['password'])
        """重複メールアドレスでユーザー作成失敗"""
        # まず最初のユーザーを作成
        first_payload = create_user_payload(
            root_org['id'],
            name='FirstUser',
            email='duplicate@example.com'
        )
        first_res = client.post('/progress/users', json=first_payload)
        assert_user_created(first_res)
        
        # 同じメールアドレスで2回目の登録を試行
        second_payload = create_user_payload(
            root_org['id'],
            name='SecondUser',
            email='duplicate@example.com'  # 重複メール
        )
        res = client.post('/progress/users', json=second_payload)
        assert res.status_code == 400
        assert check_response_message('同じ会社内に同じメールアドレスのユーザーが既に存在します。', res.get_json())

class TestUserRetrieval:
    """ユーザー取得に関するテスト"""
    
    def test_get_user_not_found(self, login_as_user, system_related_users):
        system_admin = system_related_users['system_admin']
        client = login_as_user(system_admin['email'], system_admin['password'])
        """存在しないユーザーの取得"""
        res = client.get('/progress/users/999999')
        assert res.status_code == 404
    
    def test_get_user_by_email(self, login_as_user, system_related_users, root_org):
        system_admin = system_related_users['system_admin']
        client = login_as_user(system_admin['email'], system_admin['password'])
        """メールアドレスでユーザー取得"""
        # テスト用ユーザーを作成
        email = 'email_lookup@example.com'
        payload = create_user_payload(root_org['id'], email=email)
        client.post('/progress/users', json=payload)
        
        # メールアドレスでユーザー取得
        res = client.get(f'/progress/users/email/{email}')
        assert res.status_code == 200
        responce_data = res.get_json()
        assert responce_data['name'] == payload['name']
    
    def test_get_user_by_wp_user_id(self, login_as_user, system_related_users, root_org):
        system_admin = system_related_users['system_admin']
        client = login_as_user(system_admin['email'], system_admin['password'])
        """WordPress User IDでユーザー取得"""
        wp_user_id = 1001
        payload = create_user_payload(
            root_org['id'],
            name='WPID',
            email='wpid@example.com',
            wp_user_id=wp_user_id
        )
        client.post('/progress/users', json=payload)
        
        res = client.get(f'/progress/users/wp/{wp_user_id}')
        assert res.status_code == 200
        responce_data= res.get_json()
        assert responce_data['wp_user_id'] == wp_user_id
    
    def test_get_users_by_org_tree(self, login_as_user, system_related_users, root_org):
        system_admin = system_related_users['system_admin']
        client = login_as_user(system_admin['email'], system_admin['password'])
        """組織ツリーでユーザー一覧取得"""
        res = client.get(f'/progress/users/by-org-tree/{root_org["id"]}')
        assert res.status_code == 200
        users = res.get_json()
        assert isinstance(users, list)

class TestUserModification:
    """ユーザー更新・削除に関するテスト"""
    
    def test_update_user(self, login_as_user, system_related_users, root_org):
        system_admin = system_related_users['system_admin']
        client = login_as_user(system_admin['email'], system_admin['password'])
        """ユーザー情報更新"""
        # テストユーザー作成
        payload = create_user_payload(
            root_org['id'],
            name='ToUpdate',
            email='update_me@example.com'
        )
        create_res = client.post('/progress/users', json=payload)
        user_id = assert_user_created(create_res)['id']
        
        # 更新実行
        update_data = {'name': 'UpdatedName'}
        res = client.put(f'/progress/users/{user_id}', json=update_data)
        assert res.status_code == 200
        updated_user = res.get_json()
        assert updated_user['name'] == 'UpdatedName'
    
    def test_delete_user(self, login_as_user, system_related_users, root_org):
        system_admin = system_related_users['system_admin']
        client = login_as_user(system_admin['email'], system_admin['password'])
        """ユーザー削除"""
        # テストユーザー作成
        payload = create_user_payload(
            root_org['id'],
            name='ToDelete',
            email='delete_me@example.com'
        )
        create_res = client.post('/progress/users', json=payload)
        user_id = assert_user_created(create_res)['id']
        
        # 削除実行
        res = client.delete(f'/progress/users/{user_id}')
        assert res.status_code == 200
        message = res.get_json()['message']
        assert '削除' in message

# --- パラメータ化テストの例 ---
class TestUserCreationParameterized:
    """パラメータ化されたユーザー作成テスト"""
    
    @pytest.mark.parametrize("missing_field", [
        'name', 'email', 'password', 'organization_id'
    ])
    def test_create_user_missing_required_fields(self, login_as_user, system_related_users, root_org, missing_field):
        system_admin = system_related_users['system_admin']
        client = login_as_user(system_admin['email'], system_admin['password'])
        """各必須フィールドが不足している場合のテスト"""
        payload = create_user_payload(root_org['id'])
        del payload[missing_field]
        
        res = client.post('/progress/users', json=payload)
        assert res.status_code == 422
        data = res.get_json()
        assert check_response_message('Missing data for required field.', data, missing_field)
    
    @pytest.mark.parametrize("invalid_email", [
        'invalid-email',
        'missing@domain',
        '@missing-local.com',
        'spaces in@email.com'
    ])
    def test_create_user_invalid_email_format(self, login_as_user, system_related_users, root_org, invalid_email):
        system_admin = system_related_users['system_admin']
        client = login_as_user(system_admin['email'], system_admin['password'])
        """無効なメールアドレス形式のテスト"""
        payload = create_user_payload(root_org['id'], email=invalid_email)
        res = client.post('/progress/users', json=payload)
        assert res.status_code == 400
        assert check_response_message('無効なメールアドレス形式です', res.get_json())
    


EXPECTED_USER_KEYS = {
    "id",
    "wp_user_id",
    "name",
    "is_superuser",
    "organization_id",
    "organization_name",
    "company_id",
    "access_scopes"
}

def test_user_fields_in_response(login_as_user, root_org, system_related_users):
    system_admin = system_related_users['system_admin']
    client = login_as_user(system_admin['email'], system_admin['password'])

    # ユーザー作成
    email = 'data_item_lookup@example.com'
    payload = create_user_payload(root_org['id'], email=email)
    res = client.post('/progress/users', json=payload)
    assert res.status_code == 201

    # ユーザー取得
    res = client.get(f'/progress/users/email/{email}')
    assert res.status_code == 200

    user_data = res.json
    assert isinstance(user_data, dict), "Response is not a dictionary"

    missing_keys = EXPECTED_USER_KEYS - user_data.keys()
    extra_keys = user_data.keys() - EXPECTED_USER_KEYS

    assert not missing_keys, f"Missing keys in user data: {missing_keys}"
    assert not extra_keys, f"Unexpected extra keys in user data: {extra_keys}"

def test_create_user_duplicate_email_other_company(superuser_login, root_org,other_root_org):
    client = superuser_login
    """別の会社で重複メールアドレスでユーザー作成成功"""
    # まず最初のユーザーを作成
    first_payload = create_user_payload(
        root_org['id'],
        name='FirstUser',
        email='OtherCompany@example.com'
    )
    first_res = client.post('/progress/users', json=first_payload)
    assert_user_created(first_res)
    
    # 同じメールアドレスで2回目の登録を試行
    second_payload = create_user_payload(
        root_org['id'],
        name='SecondUser',
        email='OtherCompany@example.com'  # 重複メール
    )
    res = client.post('/progress/users', json=second_payload)
    assert res.status_code == 400
    assert check_response_message('同じ会社内に同じメールアドレスのユーザーが既に存在します。', res.get_json())

    # 同じメールアドレスで別の会社で登録を試行
    second_payload = create_user_payload(
        other_root_org['id'],
        name='SecondUser',
        email='OtherCompany@example.com'  # 重複メール
    )
    res = client.post('/progress/users', json=second_payload)
    assert res.status_code == 201




