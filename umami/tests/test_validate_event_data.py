from unittest.mock import patch

import pytest
from _mocks import make_sync_mock
from umami.errors import ValidationError

import umami


class TestValidateEventData:
    """new_event() delegates required-field checks to validate_event_data(), which raises the
    SDK's ValidationError (not a bare Exception) and treats whitespace-only names as empty.

    Every case must reject BEFORE any HTTP request is made (assert_not_called()).
    """

    def test_missing_hostname_raises_validation_error(self):
        with patch('umami.impl.default_hostname', None):
            with patch('umami.impl.httpx.post', make_sync_mock()) as mock_post:
                with pytest.raises(ValidationError):
                    umami.new_event(event_name='e', hostname=None)
        mock_post.assert_not_called()

    def test_missing_website_id_raises_validation_error(self):
        with patch('umami.impl.default_website_id', None):
            with patch('umami.impl.httpx.post', make_sync_mock()) as mock_post:
                with pytest.raises(ValidationError):
                    umami.new_event(event_name='e', website_id=None)
        mock_post.assert_not_called()

    @pytest.mark.parametrize('name', ['', '   ', '\t'])
    def test_blank_or_whitespace_event_name_raises(self, name):
        # The whitespace-only cases regressed previously (the guard used `and`); now they raise.
        with patch('umami.impl.httpx.post', make_sync_mock()) as mock_post:
            with pytest.raises(ValidationError):
                umami.new_event(event_name=name)
        mock_post.assert_not_called()

    def test_operation_not_allowed_is_a_validation_error(self):
        # OperationNotAllowedError subclasses ValidationError, so catching the base catches both.
        assert issubclass(umami.errors.OperationNotAllowedError, ValidationError)
