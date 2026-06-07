from unittest.mock import patch

from _mocks import make_async_client, make_sync_mock

import umami

# One fully-populated Website row so the WebsitesResponse 'data' -> websites alias and the
# Website model (including the nested user) are actually deserialized.
_WEBSITE_ROW = {
    'id': 'w1',
    'name': 'Example',
    'domain': 'example.com',
    'shareId': None,
    'resetAt': None,
    'userId': 'u1',
    'createdAt': '2026-01-01T00:00:00Z',
    'updatedAt': '2026-01-01T00:00:00Z',
    'deletedAt': None,
    'teamId': None,
    'user': {'username': 'mkennedy', 'id': 'u1'},
}
_WEBSITES_JSON = {'data': [_WEBSITE_ROW], 'count': 1, 'page': 1, 'pageSize': 10}


class TestWebsites:
    """websites() deserializes the response (data -> websites alias) and sends Bearer auth."""

    def test_returns_parsed_websites(self):
        with patch('umami.impl.auth_token', 'fake-token'):
            with patch('umami.impl.httpx.get', make_sync_mock(_WEBSITES_JSON)) as mock_get:
                result = umami.websites()
        assert len(result) == 1
        assert result[0].domain == 'example.com'
        assert result[0].user.username == 'mkennedy'
        url = mock_get.call_args.args[0]
        headers = mock_get.call_args.kwargs['headers']
        assert url == 'https://example.com/api/websites'
        assert headers['Authorization'] == 'Bearer fake-token'


class TestWebsitesAsync:
    async def test_returns_parsed_websites(self):
        mock_client = make_async_client(_WEBSITES_JSON)
        with patch('umami.impl.auth_token', 'fake-token'):
            with patch('umami.impl.httpx.AsyncClient', return_value=mock_client):
                result = await umami.websites_async()
        assert len(result) == 1
        assert result[0].domain == 'example.com'
        assert mock_client.get.call_args.args[0] == 'https://example.com/api/websites'
