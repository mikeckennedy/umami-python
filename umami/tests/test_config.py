import pytest

import umami


class TestSetUrlBase:
    """set_url_base validates the scheme and normalizes a trailing slash."""

    @pytest.mark.parametrize('bad', ['', '   '])
    def test_empty_or_whitespace_raises(self, bad):
        with pytest.raises(umami.errors.ValidationError):
            umami.set_url_base(bad)

    @pytest.mark.parametrize('bad', ['example.com', 'ftp://example.com'])
    def test_missing_http_scheme_raises(self, bad):
        with pytest.raises(umami.errors.ValidationError):
            umami.set_url_base(bad)

    def test_trailing_slash_is_stripped(self):
        umami.set_url_base('https://x.com/')
        assert umami.impl.url_base == 'https://x.com'

    def test_http_scheme_is_accepted(self):
        umami.set_url_base('http://x.com')
        assert umami.impl.url_base == 'http://x.com'

    def test_https_scheme_is_accepted(self):
        umami.set_url_base('https://x.com')
        assert umami.impl.url_base == 'https://x.com'
