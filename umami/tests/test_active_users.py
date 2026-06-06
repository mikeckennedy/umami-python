from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import umami


def _mock_get(payload):
    """A MagicMock standing in for httpx.get returning the given JSON payload."""
    mock_resp = MagicMock()
    mock_resp.json.return_value = payload
    mock_resp.raise_for_status = MagicMock()
    return MagicMock(return_value=mock_resp)


def _mock_async_client(payload):
    """An AsyncMock standing in for httpx.AsyncClient (async context manager)."""
    mock_resp = MagicMock()
    mock_resp.json.return_value = payload
    mock_resp.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=mock_resp)
    return mock_client


class TestActiveUsers:
    """active_users() must read the count from Umami's response.

    Regression for #19: both variants previously read a non-existent 'x' key,
    so they always returned 0. Current Umami returns {"visitors": N}; the old
    'x' key is still tolerated for backwards compatibility.
    """

    def test_sync_reads_visitors_key(self):
        with patch('umami.impl.auth_token', 'fake-token'):
            with patch('umami.impl.httpx.get', _mock_get({'visitors': 5})):
                assert umami.active_users() == 5

    @pytest.mark.asyncio
    async def test_async_reads_visitors_key(self):
        mock_client = _mock_async_client({'visitors': 5})
        with patch('umami.impl.auth_token', 'fake-token'):
            with patch('umami.impl.httpx.AsyncClient', return_value=mock_client):
                assert await umami.active_users_async() == 5

    def test_sync_tolerates_legacy_x_key(self):
        with patch('umami.impl.auth_token', 'fake-token'):
            with patch('umami.impl.httpx.get', _mock_get({'x': 3})):
                assert umami.active_users() == 3

    @pytest.mark.asyncio
    async def test_async_tolerates_legacy_x_key(self):
        mock_client = _mock_async_client({'x': 3})
        with patch('umami.impl.auth_token', 'fake-token'):
            with patch('umami.impl.httpx.AsyncClient', return_value=mock_client):
                assert await umami.active_users_async() == 3

    def test_sync_defaults_to_zero_when_absent(self):
        with patch('umami.impl.auth_token', 'fake-token'):
            with patch('umami.impl.httpx.get', _mock_get({})):
                assert umami.active_users() == 0
