from unittest.mock import patch

import pytest
from _mocks import make_async_client, make_sync_mock

import umami


class TestIpAddressPayload:
    """ip_address is added to the payload only when a non-blank value is given."""

    def test_ip_included_when_provided(self):
        with patch('umami.impl.httpx.post', make_sync_mock()) as mock_post:
            umami.new_event(event_name='e', ip_address='1.2.3.4')
        assert mock_post.call_args.kwargs['json']['payload']['ip'] == '1.2.3.4'

    @pytest.mark.parametrize('ip', [None, '', '   '])
    def test_ip_omitted_when_absent_or_blank(self, ip):
        with patch('umami.impl.httpx.post', make_sync_mock()) as mock_post:
            umami.new_event(event_name='e', ip_address=ip)
        assert 'ip' not in mock_post.call_args.kwargs['json']['payload']

    async def test_ip_included_async(self):
        client = make_async_client()
        with patch('umami.impl.httpx.AsyncClient', return_value=client):
            await umami.new_event_async(event_name='e', ip_address='9.9.9.9')
        assert client.post.call_args.kwargs['json']['payload']['ip'] == '9.9.9.9'


class TestDefaultOverrides:
    """Explicit website_id/hostname args beat the values set via set_website_id/set_hostname."""

    def test_explicit_args_override_configured_defaults(self):
        # conftest seeds website_id='test-website-id', hostname='test.com'.
        with patch('umami.impl.httpx.post', make_sync_mock()) as mock_post:
            umami.new_event(event_name='e', website_id='override-id', hostname='override.com')
        payload = mock_post.call_args.kwargs['json']['payload']
        assert payload['website'] == 'override-id'
        assert payload['hostname'] == 'override.com'

    def test_configured_defaults_used_when_not_overridden(self):
        with patch('umami.impl.httpx.post', make_sync_mock()) as mock_post:
            umami.new_event(event_name='e')
        payload = mock_post.call_args.kwargs['json']['payload']
        assert payload['website'] == 'test-website-id'
        assert payload['hostname'] == 'test.com'


class TestSendAuthorizationHeader:
    """Self-hosted sends carry the Bearer token only when someone has logged in.

    Umami's /api/send ignores the header, and the old behaviour sent the literal string
    'Bearer None' for callers who never called login().
    """

    @pytest.mark.parametrize('send', [lambda: umami.new_event(event_name='e'), lambda: umami.new_page_view('T', '/')])
    def test_no_authorization_header_without_login(self, send):
        with patch('umami.impl.auth_token', None):
            with patch('umami.impl.httpx.post', make_sync_mock()) as mock_post:
                send()
        headers = mock_post.call_args.kwargs['headers']
        assert 'Authorization' not in headers
        assert headers['User-Agent'] == umami.impl.event_user_agent

    def test_authorization_header_with_login(self):
        with patch('umami.impl.auth_token', 'tok'):
            with patch('umami.impl.httpx.post', make_sync_mock()) as mock_post:
                umami.new_event(event_name='e')
        assert mock_post.call_args.kwargs['headers']['Authorization'] == 'Bearer tok'

    async def test_async_no_authorization_header_without_login(self):
        client = make_async_client()
        with patch('umami.impl.auth_token', None):
            with patch('umami.impl.httpx.AsyncClient', return_value=client):
                await umami.new_event_async(event_name='e')
        assert 'Authorization' not in client.post.call_args.kwargs['headers']
