from unittest.mock import AsyncMock, MagicMock, patch

from _mocks import make_async_client, make_sync_mock, mock_response

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
        assert result[0].user is not None
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


def _row(i):
    return dict(_WEBSITE_ROW, id=f'w{i}', domain=f'site{i}.example')


def _page(rows, count, page):
    return {'data': rows, 'count': count, 'page': page, 'pageSize': 2}


class TestWebsitesPaging:
    """websites() follows Umami's page parameter until it holds every website.

    Umami pages /api/websites, so a single request silently truncates the list for anyone with
    more sites than one page. The loop must also terminate against a server that ignores `page`.
    """

    def test_follows_pages_until_count_reached(self):
        pages = [_page([_row(1), _row(2)], count=3, page=1), _page([_row(3)], count=3, page=2)]
        with patch('umami.impl.auth_token', 'fake-token'):
            with patch('umami.impl.httpx.get', MagicMock(side_effect=[mock_response(p) for p in pages])) as mock_get:
                result = umami.websites()
        assert [s.id for s in result] == ['w1', 'w2', 'w3']
        assert [c.kwargs['params'] for c in mock_get.call_args_list] == [{'page': 1}, {'page': 2}]

    def test_single_page_makes_one_request(self):
        with patch('umami.impl.auth_token', 'fake-token'):
            with patch('umami.impl.httpx.get', make_sync_mock(_WEBSITES_JSON)) as mock_get:
                umami.websites()
        assert mock_get.call_count == 1

    def test_stops_when_server_ignores_page(self):
        # Same two rows on every page with count=3: a second request adds nothing new, so stop.
        same = _page([_row(1), _row(2)], count=3, page=1)
        with patch('umami.impl.auth_token', 'fake-token'):
            with patch('umami.impl.httpx.get', make_sync_mock(same)) as mock_get:
                result = umami.websites()
        assert [s.id for s in result] == ['w1', 'w2']
        assert mock_get.call_count == 2

    def test_stops_on_empty_page(self):
        pages = [_page([_row(1)], count=5, page=1), _page([], count=5, page=2)]
        with patch('umami.impl.auth_token', 'fake-token'):
            with patch('umami.impl.httpx.get', MagicMock(side_effect=[mock_response(p) for p in pages])) as mock_get:
                result = umami.websites()
        assert len(result) == 1
        assert mock_get.call_count == 2

    async def test_async_follows_pages(self):
        pages = [_page([_row(1), _row(2)], count=3, page=1), _page([_row(3)], count=3, page=2)]
        client = make_async_client()
        client.get = AsyncMock(side_effect=[mock_response(p) for p in pages])
        with patch('umami.impl.auth_token', 'fake-token'):
            with patch('umami.impl.httpx.AsyncClient', return_value=client):
                result = await umami.websites_async()
        assert [s.id for s in result] == ['w1', 'w2', 'w3']
        assert [c.kwargs['params'] for c in client.get.call_args_list] == [{'page': 1}, {'page': 2}]
