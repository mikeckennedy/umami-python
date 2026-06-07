from unittest.mock import patch

from _mocks import make_async_client, make_sync_mock

import umami


class TestEventUrlDefault:
    """new_event / new_revenue_event default url is '/' across both sync and async twins.

    Regression for the sync/async default mismatch: the sync functions previously defaulted
    url to '/event-api-endpoint', surfacing a placeholder path in dashboards, while the async
    twins used '/'. All four now agree on '/'.
    """

    def test_new_event_defaults_url_to_root(self):
        with patch('umami.impl.httpx.post', make_sync_mock()) as mock_post:
            umami.new_event(event_name='e')
        assert mock_post.call_args.kwargs['json']['payload']['url'] == '/'

    async def test_new_event_async_defaults_url_to_root(self):
        mock_client = make_async_client()
        with patch('umami.impl.httpx.AsyncClient', return_value=mock_client):
            await umami.new_event_async(event_name='e')
        assert mock_client.post.call_args.kwargs['json']['payload']['url'] == '/'

    def test_new_revenue_event_defaults_url_to_root(self):
        with patch('umami.impl.httpx.post', make_sync_mock()) as mock_post:
            umami.new_revenue_event(revenue=9.99)
        assert mock_post.call_args.kwargs['json']['payload']['url'] == '/'

    async def test_new_revenue_event_async_defaults_url_to_root(self):
        mock_client = make_async_client()
        with patch('umami.impl.httpx.AsyncClient', return_value=mock_client):
            await umami.new_revenue_event_async(revenue=9.99)
        assert mock_client.post.call_args.kwargs['json']['payload']['url'] == '/'
