from unittest.mock import AsyncMock, MagicMock, patch

import umami


def _mock_sync():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {}
    mock_resp.raise_for_status = MagicMock()
    return MagicMock(return_value=mock_resp)


def _mock_async_client():
    mock_resp = MagicMock()
    mock_resp.json.return_value = {}
    mock_resp.raise_for_status = MagicMock()
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.post = AsyncMock(return_value=mock_resp)
    return mock_client


class TestEventUrlDefault:
    """new_event / new_revenue_event default url is '/' across both sync and async twins.

    Regression for the sync/async default mismatch: the sync functions previously defaulted
    url to '/event-api-endpoint', surfacing a placeholder path in dashboards, while the async
    twins used '/'. All four now agree on '/'.
    """

    def test_new_event_defaults_url_to_root(self):
        with patch('umami.impl.httpx.post', _mock_sync()) as mock_post:
            umami.new_event(event_name='e')
        assert mock_post.call_args.kwargs['json']['payload']['url'] == '/'

    async def test_new_event_async_defaults_url_to_root(self):
        mock_client = _mock_async_client()
        with patch('umami.impl.httpx.AsyncClient', return_value=mock_client):
            await umami.new_event_async(event_name='e')
        assert mock_client.post.call_args.kwargs['json']['payload']['url'] == '/'

    def test_new_revenue_event_defaults_url_to_root(self):
        with patch('umami.impl.httpx.post', _mock_sync()) as mock_post:
            umami.new_revenue_event(revenue=9.99)
        assert mock_post.call_args.kwargs['json']['payload']['url'] == '/'

    async def test_new_revenue_event_async_defaults_url_to_root(self):
        mock_client = _mock_async_client()
        with patch('umami.impl.httpx.AsyncClient', return_value=mock_client):
            await umami.new_revenue_event_async(revenue=9.99)
        assert mock_client.post.call_args.kwargs['json']['payload']['url'] == '/'
