"""Shared test doubles and fixtures for the umami HTTP boundary.

The SDK does ``import httpx2 as httpx`` and calls module-level ``httpx.get``/``httpx.post`` plus
``httpx.AsyncClient()``. Tests patch ``umami.impl.httpx.*`` and assert on the request that would be
sent. These builders centralize the mock plumbing so every test file shares one response contract.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock


def mock_response(payload=None):
    """A response stand-in exposing .json() and a no-op .raise_for_status()."""
    resp = MagicMock()
    resp.json.return_value = {} if payload is None else payload
    resp.raise_for_status = MagicMock()
    return resp


def make_sync_mock(payload=None):
    """Stand-in for httpx.get / httpx.post (returns the same response object each call)."""
    return MagicMock(return_value=mock_response(payload))


def make_async_client(payload=None):
    """Stand-in for httpx.AsyncClient(); both .get and .post return the same response.

    Wiring both verbs is harmless when a test only uses one, and keeps the helper uniform.
    """
    resp = mock_response(payload)
    client = AsyncMock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=False)
    client.get = AsyncMock(return_value=resp)
    client.post = AsyncMock(return_value=resp)
    return client


# A minimal but valid WebsiteStats payload (see models.WebsiteStats).
STATS_JSON = {
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

# A WebsitesResponse with no rows (enough for routing/header assertions).
WEBSITES_JSON = {'data': [], 'count': 0, 'page': 1, 'pageSize': 10}

START = datetime(2025, 1, 1)
END = datetime(2025, 1, 31)
