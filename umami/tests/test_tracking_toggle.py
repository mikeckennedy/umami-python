from unittest.mock import patch

import pytest
from _mocks import make_async_client, make_sync_mock

import umami


class TestTrackingDisabled:
    """disable() makes the new_* functions validate and then early-return WITHOUT any HTTP call.

    The real contract is "no network request" — asserted with assert_not_called(), not just the
    return value. (conftest re-enables tracking before each test.)
    """

    def test_new_event_makes_no_request(self):
        umami.disable()
        with patch('umami.impl.httpx.post', make_sync_mock()) as mock_post:
            result = umami.new_event(event_name='e')
        assert result is None
        mock_post.assert_not_called()

    def test_new_page_view_makes_no_request(self):
        umami.disable()
        with patch('umami.impl.httpx.post', make_sync_mock()) as mock_post:
            result = umami.new_page_view('Home', '/')
        assert result is None
        mock_post.assert_not_called()

    async def test_new_event_async_makes_no_request(self):
        umami.disable()
        mock_client = make_async_client()
        with patch('umami.impl.httpx.AsyncClient', return_value=mock_client):
            result = await umami.new_event_async(event_name='e')
        assert result == {}
        mock_client.post.assert_not_called()

    async def test_new_page_view_async_makes_no_request(self):
        umami.disable()
        mock_client = make_async_client()
        with patch('umami.impl.httpx.AsyncClient', return_value=mock_client):
            result = await umami.new_page_view_async('Home', '/')
        assert result is None
        mock_client.post.assert_not_called()

    def test_validation_still_runs_when_disabled(self):
        # Disabling silences the network call, but validate_event_data still runs first.
        # Clear the conftest defaults so the missing hostname/website_id actually trips validation.
        umami.disable()
        with patch('umami.impl.default_website_id', None), patch('umami.impl.default_hostname', None):
            with patch('umami.impl.httpx.post', make_sync_mock()) as mock_post:
                with pytest.raises(Exception):
                    umami.new_event(event_name='e')
        mock_post.assert_not_called()
