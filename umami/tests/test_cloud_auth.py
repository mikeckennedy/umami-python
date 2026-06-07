from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import umami

# Minimal valid payloads so the wrapped functions can parse a response.
_WEBSITES_JSON = {'data': [], 'count': 0, 'page': 1, 'pageSize': 10}
_STATS_JSON = {
    'pageviews': 10,
    'visitors': 5,
    'visits': 7,
    'bounces': 2,
    'totaltime': 1234,
    'comparison': {
        'pageviews': 9,
        'visitors': 4,
        'visits': 6,
        'bounces': 1,
        'totaltime': 1000,
    },
}

_START = datetime(2025, 1, 1)
_END = datetime(2025, 1, 31)


def _mock_response(payload):
    mock_resp = MagicMock()
    mock_resp.json.return_value = payload
    mock_resp.raise_for_status = MagicMock()
    return mock_resp


def _mock_sync(payload):
    """A MagicMock standing in for httpx.get / httpx.post."""
    return MagicMock(return_value=_mock_response(payload))


def _mock_async_client(payload):
    """An AsyncMock standing in for httpx.AsyncClient (async context manager)."""
    mock_resp = _mock_response(payload)
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=mock_resp)
    mock_client.post = AsyncMock(return_value=mock_resp)
    return mock_client


class TestCloudConfig:
    """set_cloud_api_key / clear_cloud_api_key validation and state."""

    def test_empty_key_raises(self):
        with pytest.raises(umami.errors.ValidationError):
            umami.set_cloud_api_key('')

    def test_whitespace_key_raises(self):
        with pytest.raises(umami.errors.ValidationError):
            umami.set_cloud_api_key('   ')

    def test_bad_region_raises(self):
        with pytest.raises(umami.errors.ValidationError):
            umami.set_cloud_api_key('key', region='mars')

    def test_key_is_stripped(self):
        umami.set_cloud_api_key('  my-key  ')
        assert umami.impl.api_key == 'my-key'

    def test_region_none_is_allowed(self):
        umami.set_cloud_api_key('my-key')
        assert umami.impl.cloud_region is None

    def test_is_logged_in_true_in_cloud_mode(self):
        umami.set_cloud_api_key('my-key')
        assert umami.is_logged_in() is True

    def test_clear_restores_self_hosted(self):
        umami.set_cloud_api_key('my-key', region='eu')
        umami.clear_cloud_api_key()
        assert umami.impl.api_key is None
        assert umami.impl.cloud_region is None


class TestCloudDataRouting:
    """Data/management calls route to api.umami.is/v1 with the x-umami-api-key header."""

    def test_websites_routing_and_headers(self):
        umami.set_cloud_api_key('cloud-key')
        with patch('umami.impl.httpx.get', _mock_sync(_WEBSITES_JSON)) as mock_get:
            umami.websites()
        url = mock_get.call_args.args[0]
        headers = mock_get.call_args.kwargs['headers']
        assert url == 'https://api.umami.is/v1/websites'
        assert headers['x-umami-api-key'] == 'cloud-key'
        assert 'Authorization' not in headers

    def test_region_appears_in_path(self):
        umami.set_cloud_api_key('cloud-key', region='eu')
        with patch('umami.impl.httpx.get', _mock_sync(_WEBSITES_JSON)) as mock_get:
            umami.websites()
        assert mock_get.call_args.args[0] == 'https://api.umami.is/v1/eu/websites'

    def test_active_users_routing(self):
        umami.set_cloud_api_key('cloud-key', region='us')
        with patch('umami.impl.httpx.get', _mock_sync({'visitors': 7})) as mock_get:
            result = umami.active_users()
        assert result == 7
        url = mock_get.call_args.args[0]
        headers = mock_get.call_args.kwargs['headers']
        assert url == 'https://api.umami.is/v1/us/websites/test-website-id/active'
        assert headers['x-umami-api-key'] == 'cloud-key'
        assert 'Authorization' not in headers

    def test_website_stats_routing_and_params(self):
        umami.set_cloud_api_key('cloud-key')
        with patch('umami.impl.httpx.get', _mock_sync(_STATS_JSON)) as mock_get:
            umami.website_stats(start_at=_START, end_at=_END, url='/pricing', host='example.com')
        url = mock_get.call_args.args[0]
        headers = mock_get.call_args.kwargs['headers']
        params = mock_get.call_args.kwargs['params']
        assert url == 'https://api.umami.is/v1/websites/test-website-id/stats'
        assert headers['x-umami-api-key'] == 'cloud-key'
        assert 'Authorization' not in headers
        # Unit 1 wire names still apply in Cloud mode.
        assert params['startAt'] == int(_START.timestamp() * 1000)
        assert params['path'] == '/pricing'
        assert params['hostname'] == 'example.com'

    async def test_websites_async_routing_and_headers(self):
        umami.set_cloud_api_key('cloud-key')
        mock_client = _mock_async_client(_WEBSITES_JSON)
        with patch('umami.impl.httpx.AsyncClient', return_value=mock_client):
            await umami.websites_async()
        url = mock_client.get.call_args.args[0]
        headers = mock_client.get.call_args.kwargs['headers']
        assert url == 'https://api.umami.is/v1/websites'
        assert headers['x-umami-api-key'] == 'cloud-key'
        assert 'Authorization' not in headers


class TestCloudEventRouting:
    """Ingestion calls route to cloud.umami.is/api/send and are unauthenticated."""

    def test_new_event_routing(self):
        umami.set_cloud_api_key('cloud-key', region='eu')
        with patch('umami.impl.httpx.post', _mock_sync({})) as mock_post:
            umami.new_event(event_name='purchase', url='/checkout')
        url = mock_post.call_args.args[0]
        headers = mock_post.call_args.kwargs['headers']
        # Region never affects the ingestion host.
        assert url == 'https://cloud.umami.is/api/send'
        assert 'Authorization' not in headers
        assert 'x-umami-api-key' not in headers

    def test_new_page_view_routing_preserves_ua(self):
        umami.set_cloud_api_key('cloud-key')
        with patch('umami.impl.httpx.post', _mock_sync({})) as mock_post:
            umami.new_page_view(page_title='Home', url='/')
        url = mock_post.call_args.args[0]
        headers = mock_post.call_args.kwargs['headers']
        assert url == 'https://cloud.umami.is/api/send'
        assert headers['User-Agent'] == umami.impl.event_user_agent
        assert 'Authorization' not in headers
        assert 'x-umami-api-key' not in headers

    async def test_new_event_async_routing(self):
        umami.set_cloud_api_key('cloud-key')
        mock_client = _mock_async_client({})
        with patch('umami.impl.httpx.AsyncClient', return_value=mock_client):
            await umami.new_event_async(event_name='purchase', url='/checkout')
        url = mock_client.post.call_args.args[0]
        headers = mock_client.post.call_args.kwargs['headers']
        assert url == 'https://cloud.umami.is/api/send'
        assert 'Authorization' not in headers
        assert 'x-umami-api-key' not in headers


class TestCloudVerifyToken:
    """verify_token validates a Cloud key against /me instead of /api/auth/verify."""

    def test_verify_token_hits_me_endpoint(self):
        umami.set_cloud_api_key('cloud-key', region='eu')
        # Real /api/me nests username under 'user'; matched by the 'user' in body clause.
        with patch('umami.impl.httpx.get', _mock_sync({'user': {'id': '1', 'username': 'me'}})) as mock_get:
            result = umami.verify_token()
        assert result is True
        url = mock_get.call_args.args[0]
        headers = mock_get.call_args.kwargs['headers']
        assert url == 'https://api.umami.is/v1/eu/me'
        assert headers['x-umami-api-key'] == 'cloud-key'

    def test_verify_token_no_server_returns_true_in_cloud(self):
        umami.set_cloud_api_key('cloud-key')
        assert umami.verify_token(check_server=False) is True

    async def test_verify_token_async_hits_me_endpoint(self):
        umami.set_cloud_api_key('cloud-key')
        mock_client = _mock_async_client({'user': {'id': '1'}})
        with patch('umami.impl.httpx.AsyncClient', return_value=mock_client):
            result = await umami.verify_token_async()
        assert result is True
        assert mock_client.get.call_args.args[0] == 'https://api.umami.is/v1/me'


class TestSelfHostedRegression:
    """With no API key, routing and headers are byte-identical to pre-Cloud behavior."""

    def test_stats_url_and_headers_unchanged(self):
        with patch('umami.impl.auth_token', 'fake-token'):
            with patch('umami.impl.httpx.get', _mock_sync(_STATS_JSON)) as mock_get:
                umami.website_stats(start_at=_START, end_at=_END)
        url = mock_get.call_args.args[0]
        headers = mock_get.call_args.kwargs['headers']
        assert url == 'https://example.com/api/websites/test-website-id/stats'
        assert headers == {
            'User-Agent': umami.impl.user_agent,
            'Authorization': 'Bearer fake-token',
        }
        assert 'x-umami-api-key' not in headers

    def test_event_url_and_headers_unchanged(self):
        with patch('umami.impl.auth_token', 'fake-token'):
            with patch('umami.impl.httpx.post', _mock_sync({})) as mock_post:
                umami.new_event(event_name='e', url='/x')
        url = mock_post.call_args.args[0]
        headers = mock_post.call_args.kwargs['headers']
        assert url == 'https://example.com/api/send'
        assert headers == {
            'User-Agent': umami.impl.event_user_agent,
            'Authorization': 'Bearer fake-token',
        }
        assert 'x-umami-api-key' not in headers

    async def test_stats_async_url_and_headers_unchanged(self):
        mock_client = _mock_async_client(_STATS_JSON)
        with patch('umami.impl.auth_token', 'fake-token'):
            with patch('umami.impl.httpx.AsyncClient', return_value=mock_client):
                await umami.website_stats_async(start_at=_START, end_at=_END)
        url = mock_client.get.call_args.args[0]
        headers = mock_client.get.call_args.kwargs['headers']
        assert url == 'https://example.com/api/websites/test-website-id/stats'
        assert headers == {
            'User-Agent': umami.impl.user_agent,
            'Authorization': 'Bearer fake-token',
        }
        assert 'x-umami-api-key' not in headers

    def test_heartbeat_self_hosted_uses_get(self):
        # Umami's /api/heartbeat is a GET (POST returns 405); see regression note in changelog.
        with patch('umami.impl.httpx.get', _mock_sync({'ok': True})) as mock_get:
            result = umami.heartbeat()
        assert result is True
        url = mock_get.call_args.args[0]
        headers = mock_get.call_args.kwargs['headers']
        assert url == 'https://example.com/api/heartbeat'
        assert headers == {'User-Agent': umami.impl.user_agent}


class TestSelfHostedVerifyToken:
    """The self-hosted verify_token path is unchanged: POST /api/auth/verify with Bearer."""

    def test_verify_token_hits_verify_endpoint(self):
        with patch('umami.impl.auth_token', 'fake-token'):
            with patch('umami.impl.httpx.post', _mock_sync({'username': 'me'})) as mock_post:
                result = umami.verify_token()
        assert result is True
        url = mock_post.call_args.args[0]
        headers = mock_post.call_args.kwargs['headers']
        assert url == 'https://example.com/api/auth/verify'
        assert headers['Authorization'] == 'Bearer fake-token'
        assert 'x-umami-api-key' not in headers

    async def test_verify_token_async_hits_verify_endpoint(self):
        mock_client = _mock_async_client({'username': 'me'})
        with patch('umami.impl.auth_token', 'fake-token'):
            with patch('umami.impl.httpx.AsyncClient', return_value=mock_client):
                result = await umami.verify_token_async()
        assert result is True
        url = mock_client.post.call_args.args[0]
        headers = mock_client.post.call_args.kwargs['headers']
        assert url == 'https://example.com/api/auth/verify'
        assert headers['Authorization'] == 'Bearer fake-token'

    def test_verify_token_no_server_returns_true_when_logged_in(self):
        with patch('umami.impl.auth_token', 'fake-token'):
            assert umami.verify_token(check_server=False) is True


class TestCloudHeartbeat:
    """In Cloud mode heartbeat checks liveness via the authenticated /me endpoint."""

    def test_heartbeat_hits_me(self):
        umami.set_cloud_api_key('cloud-key', region='eu')
        with patch('umami.impl.httpx.get', _mock_sync({'user': {'id': '1'}})) as mock_get:
            result = umami.heartbeat()
        assert result is True
        url = mock_get.call_args.args[0]
        headers = mock_get.call_args.kwargs['headers']
        assert url == 'https://api.umami.is/v1/eu/me'
        assert headers['x-umami-api-key'] == 'cloud-key'
        assert 'Authorization' not in headers

    async def test_heartbeat_async_hits_me(self):
        umami.set_cloud_api_key('cloud-key')
        mock_client = _mock_async_client({'user': {'id': '1'}})
        with patch('umami.impl.httpx.AsyncClient', return_value=mock_client):
            result = await umami.heartbeat_async()
        assert result is True
        url = mock_client.get.call_args.args[0]
        headers = mock_client.get.call_args.kwargs['headers']
        assert url == 'https://api.umami.is/v1/me'
        assert headers['x-umami-api-key'] == 'cloud-key'


class TestCloudLoginGuard:
    """login() is rejected in Cloud mode (the API key is the credential)."""

    def test_login_raises_in_cloud_mode(self):
        umami.set_cloud_api_key('cloud-key')
        with pytest.raises(umami.errors.OperationNotAllowedError):
            umami.login('user', 'pass')

    async def test_login_async_raises_in_cloud_mode(self):
        umami.set_cloud_api_key('cloud-key')
        with pytest.raises(umami.errors.OperationNotAllowedError):
            await umami.login_async('user', 'pass')
