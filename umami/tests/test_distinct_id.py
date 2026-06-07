from unittest.mock import patch

import pytest
from _mocks import make_async_client, make_sync_mock
from umami.errors import ValidationError
from umami.impl import normalize_distinct_id

import umami


class TestDistinctIdSync:
    """distinct_id handling for the sync event / page_view / revenue functions."""

    def test_new_event_includes_distinct_id(self):
        with patch('umami.impl.httpx.post', make_sync_mock()) as mock_post:
            umami.new_event(event_name='signup', distinct_id='user-123')
        payload = mock_post.call_args.kwargs['json']['payload']
        assert payload['id'] == 'user-123'

    def test_new_event_normalizes_integer_distinct_id(self):
        with patch('umami.impl.httpx.post', make_sync_mock()) as mock_post:
            umami.new_event(event_name='signup', distinct_id=12345)
        payload = mock_post.call_args.kwargs['json']['payload']
        assert payload['id'] == '12345'

    def test_new_event_rejects_invalid_distinct_id_type(self):
        with pytest.raises(ValidationError, match='string or integer'):
            umami.new_event(event_name='signup', distinct_id=['bad-type'])  # type: ignore[arg-type]

    def test_new_page_view_includes_distinct_id(self):
        with patch('umami.impl.httpx.post', make_sync_mock()) as mock_post:
            umami.new_page_view(page_title='Account', url='/account', distinct_id='user-456')
        payload = mock_post.call_args.kwargs['json']['payload']
        assert payload['id'] == 'user-456'

    def test_new_revenue_event_includes_distinct_id(self):
        with patch('umami.impl.httpx.post', make_sync_mock()) as mock_post:
            umami.new_revenue_event(revenue=19.99, distinct_id='user-789')
        payload = mock_post.call_args.kwargs['json']['payload']
        assert payload['id'] == 'user-789'

    def test_new_revenue_event_normalizes_integer_distinct_id(self):
        with patch('umami.impl.httpx.post', make_sync_mock()) as mock_post:
            umami.new_revenue_event(revenue=19.99, distinct_id=42)
        payload = mock_post.call_args.kwargs['json']['payload']
        assert payload['id'] == '42'

    def test_new_event_omits_id_when_distinct_id_default(self):
        # Backward-compat: legacy callers who never pass distinct_id must get no 'id' field.
        with patch('umami.impl.httpx.post', make_sync_mock()) as mock_post:
            umami.new_event(event_name='signup')
        payload = mock_post.call_args.kwargs['json']['payload']
        assert 'id' not in payload

    @pytest.mark.parametrize('blank', ['', '   '])
    def test_new_event_omits_id_for_blank_distinct_id(self, blank):
        with patch('umami.impl.httpx.post', make_sync_mock()) as mock_post:
            umami.new_event(event_name='signup', distinct_id=blank)
        payload = mock_post.call_args.kwargs['json']['payload']
        assert 'id' not in payload

    def test_new_event_strips_whitespace_from_distinct_id(self):
        with patch('umami.impl.httpx.post', make_sync_mock()) as mock_post:
            umami.new_event(event_name='signup', distinct_id='  user-1  ')
        payload = mock_post.call_args.kwargs['json']['payload']
        assert payload['id'] == 'user-1'

    def test_new_event_zero_distinct_id(self):
        # 0 is a valid integer id that must survive as the string '0' (falsy-value trap).
        with patch('umami.impl.httpx.post', make_sync_mock()) as mock_post:
            umami.new_event(event_name='signup', distinct_id=0)
        payload = mock_post.call_args.kwargs['json']['payload']
        assert payload['id'] == '0'

    @pytest.mark.parametrize('bad', [True, False])
    def test_new_event_rejects_bool_distinct_id(self, bad):
        # bool is an int subclass; the explicit guard must keep it from coercing to a string.
        with pytest.raises(ValidationError, match='string or integer'):
            umami.new_event(event_name='signup', distinct_id=bad)  # type: ignore[arg-type]


class TestDistinctIdAsync:
    """distinct_id handling for the async event / page_view / revenue functions."""

    @pytest.mark.asyncio
    async def test_new_event_async_includes_distinct_id(self):
        mock_client = make_async_client()
        with patch('umami.impl.httpx.AsyncClient', return_value=mock_client):
            await umami.new_event_async(event_name='signup', distinct_id='user-123')
        payload = mock_client.post.call_args.kwargs['json']['payload']
        assert payload['id'] == 'user-123'

    @pytest.mark.asyncio
    async def test_new_page_view_async_includes_distinct_id(self):
        mock_client = make_async_client()
        with patch('umami.impl.httpx.AsyncClient', return_value=mock_client):
            await umami.new_page_view_async(page_title='Account', url='/account', distinct_id='user-456')
        payload = mock_client.post.call_args.kwargs['json']['payload']
        assert payload['id'] == 'user-456'

    @pytest.mark.asyncio
    async def test_new_page_view_async_normalizes_integer_distinct_id(self):
        mock_client = make_async_client()
        with patch('umami.impl.httpx.AsyncClient', return_value=mock_client):
            await umami.new_page_view_async(page_title='Account', url='/account', distinct_id=67890)
        payload = mock_client.post.call_args.kwargs['json']['payload']
        assert payload['id'] == '67890'

    @pytest.mark.asyncio
    async def test_new_revenue_event_async_includes_distinct_id(self):
        mock_client = make_async_client()
        with patch('umami.impl.httpx.AsyncClient', return_value=mock_client):
            await umami.new_revenue_event_async(revenue=19.99, distinct_id='user-789')
        payload = mock_client.post.call_args.kwargs['json']['payload']
        assert payload['id'] == 'user-789'

    @pytest.mark.asyncio
    async def test_new_event_async_omits_id_when_distinct_id_default(self):
        mock_client = make_async_client()
        with patch('umami.impl.httpx.AsyncClient', return_value=mock_client):
            await umami.new_event_async(event_name='signup')
        payload = mock_client.post.call_args.kwargs['json']['payload']
        assert 'id' not in payload


class TestNormalizeDistinctId:
    """Direct unit tests for the shared normalize_distinct_id helper (the single
    source of truth all six event/page_view/revenue functions delegate to)."""

    @pytest.mark.parametrize(
        'raw, expected',
        [
            (None, None),
            ('', None),
            ('   ', None),
            ('user-1', 'user-1'),
            ('  user-1  ', 'user-1'),
            (12345, '12345'),
            (0, '0'),
        ],
    )
    def test_normalizes_valid_values(self, raw, expected):
        assert normalize_distinct_id(raw) == expected

    @pytest.mark.parametrize('bad', [True, False, ['x'], 1.5, {'a': 1}])
    def test_rejects_invalid_types(self, bad):
        with pytest.raises(ValidationError, match='string or integer'):
            normalize_distinct_id(bad)  # type: ignore[arg-type]
