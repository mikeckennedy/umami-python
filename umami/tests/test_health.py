from unittest.mock import MagicMock, patch

from _mocks import make_async_client, make_sync_mock

import umami


def _raising_sync():
    """A sync httpx stand-in whose response raises on raise_for_status()."""
    resp = MagicMock()
    resp.raise_for_status.side_effect = Exception('boom')
    return MagicMock(return_value=resp)


class TestHeartbeatSelfHostedAsync:
    """heartbeat_async self-hosted parity with the sync twin (GET /api/heartbeat)."""

    async def test_heartbeat_async_uses_get(self):
        client = make_async_client({'ok': True})
        with patch('umami.impl.httpx.AsyncClient', return_value=client):
            result = await umami.heartbeat_async()
        assert result is True
        assert client.get.call_args.args[0] == 'https://example.com/api/heartbeat'
        assert client.get.call_args.kwargs['headers'] == {'User-Agent': umami.impl.user_agent}


class TestHealthFailureBranches:
    """verify_token()/heartbeat() swallow errors and return False rather than raising."""

    def test_heartbeat_returns_false_on_error(self):
        with patch('umami.impl.httpx.get', _raising_sync()):
            assert umami.heartbeat() is False

    def test_verify_token_returns_false_on_error(self):
        with patch('umami.impl.auth_token', 'fake-token'):
            with patch('umami.impl.httpx.post', _raising_sync()):
                assert umami.verify_token() is False

    def test_verify_token_returns_false_when_body_has_no_username(self):
        with patch('umami.impl.auth_token', 'fake-token'):
            with patch('umami.impl.httpx.post', make_sync_mock({'not_username': 'x'})):
                assert umami.verify_token() is False
