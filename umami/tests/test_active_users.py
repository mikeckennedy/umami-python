from unittest.mock import patch

import pytest
from _mocks import make_async_client, make_sync_mock

import umami


class TestActiveUsers:
    """active_users() must read the count from Umami's response.

    Regression for #19: both variants previously read a non-existent 'x' key,
    so they always returned 0. Current Umami returns {"visitors": N}; the old
    'x' key is still tolerated for backwards compatibility.
    """

    def test_sync_reads_visitors_key(self):
        with patch('umami.impl.auth_token', 'fake-token'):
            with patch('umami.impl.httpx.get', make_sync_mock({'visitors': 5})):
                assert umami.active_users() == 5

    @pytest.mark.asyncio
    async def test_async_reads_visitors_key(self):
        mock_client = make_async_client({'visitors': 5})
        with patch('umami.impl.auth_token', 'fake-token'):
            with patch('umami.impl.httpx.AsyncClient', return_value=mock_client):
                assert await umami.active_users_async() == 5

    def test_sync_tolerates_legacy_x_key(self):
        with patch('umami.impl.auth_token', 'fake-token'):
            with patch('umami.impl.httpx.get', make_sync_mock({'x': 3})):
                assert umami.active_users() == 3

    @pytest.mark.asyncio
    async def test_async_tolerates_legacy_x_key(self):
        mock_client = make_async_client({'x': 3})
        with patch('umami.impl.auth_token', 'fake-token'):
            with patch('umami.impl.httpx.AsyncClient', return_value=mock_client):
                assert await umami.active_users_async() == 3

    def test_sync_defaults_to_zero_when_absent(self):
        with patch('umami.impl.auth_token', 'fake-token'):
            with patch('umami.impl.httpx.get', make_sync_mock({})):
                assert umami.active_users() == 0
