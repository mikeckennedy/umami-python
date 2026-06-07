from unittest.mock import patch

import pytest
from _mocks import END, START, STATS_JSON, WEBSITES_JSON, make_async_client, make_sync_mock

import umami


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
        with patch('umami.impl.httpx.get', make_sync_mock(WEBSITES_JSON)) as mock_get:
            umami.websites()
        url = mock_get.call_args.args[0]
        headers = mock_get.call_args.kwargs['headers']
        assert url == 'https://api.umami.is/v1/websites'
        assert headers['x-umami-api-key'] == 'cloud-key'
        assert 'Authorization' not in headers

    def test_region_appears_in_path(self):
        umami.set_cloud_api_key('cloud-key', region='eu')
        with patch('umami.impl.httpx.get', make_sync_mock(WEBSITES_JSON)) as mock_get:
            umami.websites()
        assert mock_get.call_args.args[0] == 'https://api.umami.is/v1/eu/websites'

    def test_active_users_routing(self):
        umami.set_cloud_api_key('cloud-key', region='us')
        with patch('umami.impl.httpx.get', make_sync_mock({'visitors': 7})) as mock_get:
            result = umami.active_users()
        assert result == 7
        url = mock_get.call_args.args[0]
        headers = mock_get.call_args.kwargs['headers']
        assert url == 'https://api.umami.is/v1/us/websites/test-website-id/active'
        assert headers['x-umami-api-key'] == 'cloud-key'
        assert 'Authorization' not in headers

    def test_website_stats_routing_and_params(self):
        umami.set_cloud_api_key('cloud-key')
        with patch('umami.impl.httpx.get', make_sync_mock(STATS_JSON)) as mock_get:
            umami.website_stats(start_at=START, end_at=END, url='/pricing', host='example.com')
        url = mock_get.call_args.args[0]
        headers = mock_get.call_args.kwargs['headers']
        params = mock_get.call_args.kwargs['params']
        assert url == 'https://api.umami.is/v1/websites/test-website-id/stats'
        assert headers['x-umami-api-key'] == 'cloud-key'
        assert 'Authorization' not in headers
        # Unit 1 wire names still apply in Cloud mode.
        assert params['startAt'] == int(START.timestamp() * 1000)
        assert params['path'] == '/pricing'
        assert params['hostname'] == 'example.com'

    async def test_websites_async_routing_and_headers(self):
        umami.set_cloud_api_key('cloud-key')
        mock_client = make_async_client(WEBSITES_JSON)
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
        with patch('umami.impl.httpx.post', make_sync_mock({})) as mock_post:
            umami.new_event(event_name='purchase', url='/checkout')
        url = mock_post.call_args.args[0]
        headers = mock_post.call_args.kwargs['headers']
        # Region never affects the ingestion host.
        assert url == 'https://cloud.umami.is/api/send'
        assert 'Authorization' not in headers
        assert 'x-umami-api-key' not in headers

    def test_new_page_view_routing_preserves_ua(self):
        umami.set_cloud_api_key('cloud-key')
        with patch('umami.impl.httpx.post', make_sync_mock({})) as mock_post:
            umami.new_page_view(page_title='Home', url='/')
        url = mock_post.call_args.args[0]
        headers = mock_post.call_args.kwargs['headers']
        assert url == 'https://cloud.umami.is/api/send'
        assert headers['User-Agent'] == umami.impl.event_user_agent
        assert 'Authorization' not in headers
        assert 'x-umami-api-key' not in headers

    async def test_new_event_async_routing(self):
        umami.set_cloud_api_key('cloud-key')
        mock_client = make_async_client({})
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
        with patch('umami.impl.httpx.get', make_sync_mock({'user': {'id': '1', 'username': 'me'}})) as mock_get:
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
        mock_client = make_async_client({'user': {'id': '1'}})
        with patch('umami.impl.httpx.AsyncClient', return_value=mock_client):
            result = await umami.verify_token_async()
        assert result is True
        assert mock_client.get.call_args.args[0] == 'https://api.umami.is/v1/me'


class TestSelfHostedRegression:
    """With no API key, routing and headers are byte-identical to pre-Cloud behavior."""

    def test_stats_url_and_headers_unchanged(self):
        with patch('umami.impl.auth_token', 'fake-token'):
            with patch('umami.impl.httpx.get', make_sync_mock(STATS_JSON)) as mock_get:
                umami.website_stats(start_at=START, end_at=END)
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
            with patch('umami.impl.httpx.post', make_sync_mock({})) as mock_post:
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
        mock_client = make_async_client(STATS_JSON)
        with patch('umami.impl.auth_token', 'fake-token'):
            with patch('umami.impl.httpx.AsyncClient', return_value=mock_client):
                await umami.website_stats_async(start_at=START, end_at=END)
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
        with patch('umami.impl.httpx.get', make_sync_mock({'ok': True})) as mock_get:
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
            with patch('umami.impl.httpx.post', make_sync_mock({'username': 'me'})) as mock_post:
                result = umami.verify_token()
        assert result is True
        url = mock_post.call_args.args[0]
        headers = mock_post.call_args.kwargs['headers']
        assert url == 'https://example.com/api/auth/verify'
        assert headers['Authorization'] == 'Bearer fake-token'
        assert 'x-umami-api-key' not in headers

    async def test_verify_token_async_hits_verify_endpoint(self):
        mock_client = make_async_client({'username': 'me'})
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
        with patch('umami.impl.httpx.get', make_sync_mock({'user': {'id': '1'}})) as mock_get:
            result = umami.heartbeat()
        assert result is True
        url = mock_get.call_args.args[0]
        headers = mock_get.call_args.kwargs['headers']
        assert url == 'https://api.umami.is/v1/eu/me'
        assert headers['x-umami-api-key'] == 'cloud-key'
        assert 'Authorization' not in headers

    async def test_heartbeat_async_hits_me(self):
        umami.set_cloud_api_key('cloud-key')
        mock_client = make_async_client({'user': {'id': '1'}})
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
