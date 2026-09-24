def test_login_returns_token(client, seed_user):
    response = client.post(
        '/api/auth/login',
        data={'username': 'admin@ai-ntdrs.local', 'password': 'ChangeMe123!'},
    )

    assert response.status_code == 200
    body = response.json()
    assert body['token_type'] == 'bearer'
    assert body['access_token']


def test_me_returns_user_profile(client, seed_user):
    login_response = client.post(
        '/api/auth/login',
        data={'username': 'admin@ai-ntdrs.local', 'password': 'ChangeMe123!'},
    )
    token = login_response.json()['access_token']

    response = client.get('/api/auth/me', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == 200
    assert response.json()['email'] == 'admin@ai-ntdrs.local'
