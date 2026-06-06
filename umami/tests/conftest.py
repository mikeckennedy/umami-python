import pytest

import umami


@pytest.fixture(autouse=True)
def _setup_umami():
    """Set up default umami state for all tests."""
    umami.set_url_base('https://example.com')
    umami.set_hostname('test.com')
    umami.set_website_id('test-website-id')
    umami.enable()
    yield
