from unittest.mock import patch

import pytest
from _mocks import END, START, STATS_JSON, make_async_client, make_sync_mock

import umami


class TestWebsiteStatsDateParams:
    """The date range must reach Umami as camelCase startAt/endAt query params.

    Regression for #18: website_stats_async() previously sent snake_case
    start_at/end_at, which the API ignores, silently returning all-time stats.
    """

    def test_sync_sends_camelcase_date_params(self):
        with patch('umami.impl.auth_token', 'fake-token'):
            with patch('umami.impl.httpx.get', make_sync_mock(STATS_JSON)) as mock_get:
                umami.website_stats(start_at=START, end_at=END)
        params = mock_get.call_args.kwargs['params']
        assert params['startAt'] == int(START.timestamp() * 1000)
        assert params['endAt'] == int(END.timestamp() * 1000)
        assert 'start_at' not in params
        assert 'end_at' not in params

    @pytest.mark.asyncio
    async def test_async_sends_camelcase_date_params(self):
        mock_client = make_async_client(STATS_JSON)
        with patch('umami.impl.auth_token', 'fake-token'):
            with patch('umami.impl.httpx.AsyncClient', return_value=mock_client):
                await umami.website_stats_async(start_at=START, end_at=END)
        params = mock_client.get.call_args.kwargs['params']
        assert params['startAt'] == int(START.timestamp() * 1000)
        assert params['endAt'] == int(END.timestamp() * 1000)
        assert 'start_at' not in params
        assert 'end_at' not in params


class TestWebsiteStatsFilterParams:
    """The url/host filter kwargs must reach Umami as path/hostname query params.

    Regression for #20: Umami renamed these filter keys on 2025-10-07
    (url -> path, host -> hostname). The old names are ignored, so filtering
    stats by URL or hostname was a silent no-op. The public kwargs stay url/host.
    """

    def test_sync_maps_url_and_host_to_path_and_hostname(self):
        with patch('umami.impl.auth_token', 'fake-token'):
            with patch('umami.impl.httpx.get', make_sync_mock(STATS_JSON)) as mock_get:
                umami.website_stats(start_at=START, end_at=END, url='/pricing', host='example.com')
        params = mock_get.call_args.kwargs['params']
        assert params['path'] == '/pricing'
        assert params['hostname'] == 'example.com'
        assert 'url' not in params
        assert 'host' not in params

    @pytest.mark.asyncio
    async def test_async_maps_url_and_host_to_path_and_hostname(self):
        mock_client = make_async_client(STATS_JSON)
        with patch('umami.impl.auth_token', 'fake-token'):
            with patch('umami.impl.httpx.AsyncClient', return_value=mock_client):
                await umami.website_stats_async(start_at=START, end_at=END, url='/pricing', host='example.com')
        params = mock_client.get.call_args.kwargs['params']
        assert params['path'] == '/pricing'
        assert params['hostname'] == 'example.com'
        assert 'url' not in params
        assert 'host' not in params
