from unittest.mock import patch

import pytest

import umami


class TestValidateState:
    """The shared validate_state guards gate every operation; they must raise when
    required state (url_base / login) is missing and Cloud mode is not active."""

    def test_authenticated_op_requires_login(self):
        # url_base is seeded by conftest; with no auth token and no cloud key, websites() must refuse.
        with patch('umami.impl.auth_token', None):
            with pytest.raises(umami.errors.OperationNotAllowedError):
                umami.websites()

    def test_send_op_requires_url_base(self):
        with patch('umami.impl.url_base', None):
            with pytest.raises(umami.errors.OperationNotAllowedError):
                umami.new_event(event_name='e')

    def test_cloud_key_satisfies_login_requirement(self):
        # In Cloud mode the user guard is satisfied without a token (no HTTP should be reached
        # because the guard passes, so a missing mock would surface as a different error).
        with patch('umami.impl.auth_token', None):
            umami.set_cloud_api_key('cloud-key')
            # validate_state(user=True) must NOT raise OperationNotAllowedError now.
            try:
                umami.impl.validate_state(url=True, user=True)
            except umami.errors.OperationNotAllowedError:
                pytest.fail('Cloud mode should satisfy the login requirement')
