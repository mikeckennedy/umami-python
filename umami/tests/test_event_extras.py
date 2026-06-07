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
