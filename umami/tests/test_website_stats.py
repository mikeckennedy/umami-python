from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import umami

# A minimal but valid WebsiteStats payload (see models.WebsiteStats).
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


def _mock_get():
    """A MagicMock standing in for httpx.get with a stats-returning response."""
    mock_resp = MagicMock()
    mock_resp.json.return_value = _STATS_JSON
    mock_resp.raise_for_status = MagicMock()
    return MagicMock(return_value=mock_resp)


def _mock_async_client():
    """An AsyncMock standing in for httpx.AsyncClient (async context manager)."""
    mock_resp = MagicMock()
    mock_resp.json.return_value = _STATS_JSON
    mock_resp.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=mock_resp)
    return mock_client


class TestWebsiteStatsDateParams:
    """The date range must reach Umami as camelCase startAt/endAt query params.

    Regression for #18: website_stats_async() previously sent snake_case
    start_at/end_at, which the API ignores, silently returning all-time stats.
    """

    def test_sync_sends_camelcase_date_params(self):
        with patch('umami.impl.auth_token', 'fake-token'):
            with patch('umami.impl.httpx.get', _mock_get()) as mock_get:
                umami.website_stats(start_at=_START, end_at=_END)
        params = mock_get.call_args.kwargs['params']
        assert params['startAt'] == int(_START.timestamp() * 1000)
        assert params['endAt'] == int(_END.timestamp() * 1000)
        assert 'start_at' not in params
        assert 'end_at' not in params

    @pytest.mark.asyncio
    async def test_async_sends_camelcase_date_params(self):
        mock_client = _mock_async_client()
        with patch('umami.impl.auth_token', 'fake-token'):
            with patch('umami.impl.httpx.AsyncClient', return_value=mock_client):
                await umami.website_stats_async(start_at=_START, end_at=_END)
        params = mock_client.get.call_args.kwargs['params']
        assert params['startAt'] == int(_START.timestamp() * 1000)
        assert params['endAt'] == int(_END.timestamp() * 1000)
        assert 'start_at' not in params
        assert 'end_at' not in params
