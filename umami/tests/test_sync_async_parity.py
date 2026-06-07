from unittest.mock import patch

import pytest
from _mocks import END, START, STATS_JSON, make_async_client, make_sync_mock

import umami

# Each test drives the sync twin directly and the async twin via await, then asserts the two
# produce the SAME request. This makes drift between a sync function and its _async twin a test
# failure by construction, complementing (not replacing) the per-function behavioral tests.


class TestSendPayloadParity:
    @pytest.mark.parametrize(
        'sync_fn, async_fn, kwargs',
        [
            ('new_event', 'new_event_async', dict(event_name='e', url='/x', custom_data={'a': 1})),
            ('new_page_view', 'new_page_view_async', dict(page_title='T', url='/x')),
            ('new_revenue_event', 'new_revenue_event_async', dict(revenue=5.0, url='/x')),
        ],
    )
    async def test_send_payload_parity(self, sync_fn, async_fn, kwargs):
        with patch('umami.impl.httpx.post', make_sync_mock()) as mock_post:
            getattr(umami, sync_fn)(**kwargs)
        sync_body = mock_post.call_args.kwargs['json']

        client = make_async_client()
        with patch('umami.impl.httpx.AsyncClient', return_value=client):
            await getattr(umami, async_fn)(**kwargs)
        async_body = client.post.call_args.kwargs['json']

        assert sync_body == async_body


class TestQueryRequestParity:
    async def test_website_stats_parity(self):
        kwargs = dict(start_at=START, end_at=END, url='/p', host='h.com')
        with patch('umami.impl.auth_token', 'fake-token'):
            with patch('umami.impl.httpx.get', make_sync_mock(STATS_JSON)) as mock_get:
                umami.website_stats(**kwargs)
            sync_url = mock_get.call_args.args[0]
            sync_params = mock_get.call_args.kwargs['params']

            client = make_async_client(STATS_JSON)
            with patch('umami.impl.httpx.AsyncClient', return_value=client):
                await umami.website_stats_async(**kwargs)
            async_url = client.get.call_args.args[0]
            async_params = client.get.call_args.kwargs['params']
        assert sync_url == async_url
        assert sync_params == async_params

    async def test_active_users_parity(self):
        with patch('umami.impl.auth_token', 'fake-token'):
            with patch('umami.impl.httpx.get', make_sync_mock({'visitors': 3})) as mock_get:
                sync_result = umami.active_users()
            sync_url = mock_get.call_args.args[0]

            client = make_async_client({'visitors': 3})
            with patch('umami.impl.httpx.AsyncClient', return_value=client):
                async_result = await umami.active_users_async()
            async_url = client.get.call_args.args[0]
        assert sync_url == async_url
        assert sync_result == async_result == 3
