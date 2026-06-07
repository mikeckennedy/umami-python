from unittest.mock import patch

import pytest
from _mocks import make_async_client, make_sync_mock

import umami

_LOGIN_JSON = {
    'token': 'tok-123',
    'user': {
        'id': 'u1',
        'username': 'mkennedy',
        'role': 'admin',
        'createdAt': '2026-01-01T00:00:00Z',
        'isAdmin': True,
    },
}


class TestLogin:
    """login() posts credentials, parses LoginResponse, and caches the token."""

    def test_login_posts_and_caches_token(self):
        with patch('umami.impl.auth_token', None):
            with patch('umami.impl.httpx.post', make_sync_mock(_LOGIN_JSON)) as mock_post:
                result = umami.login('mkennedy', 'pw')
            assert result.token == 'tok-123'
            assert result.user.username == 'mkennedy'
            assert result.user.isAdmin is True
            assert umami.impl.auth_token == 'tok-123'  # token cached for later calls
        url = mock_post.call_args.args[0]
        assert url == 'https://example.com/api/auth/login'
        assert mock_post.call_args.kwargs['json'] == {'username': 'mkennedy', 'password': 'pw'}
        assert mock_post.call_args.kwargs['headers'] == {'User-Agent': umami.impl.user_agent}

    @pytest.mark.parametrize('user,password', [('', 'pw'), ('mkennedy', '')])
    def test_empty_credentials_raise(self, user, password):
        with pytest.raises(umami.errors.ValidationError):
            umami.login(user, password)


class TestLoginAsync:
    async def test_login_async_caches_token(self):
        mock_client = make_async_client(_LOGIN_JSON)
        with patch('umami.impl.auth_token', None):
            with patch('umami.impl.httpx.AsyncClient', return_value=mock_client):
                result = await umami.login_async('mkennedy', 'pw')
            assert result.token == 'tok-123'
            assert umami.impl.auth_token == 'tok-123'
        assert mock_client.post.call_args.args[0] == 'https://example.com/api/auth/login'
        assert mock_client.post.call_args.kwargs['json'] == {'username': 'mkennedy', 'password': 'pw'}
