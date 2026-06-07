from datetime import datetime
from unittest.mock import MagicMock, patch

import umami
from umami import models


class TestWebsiteStatsComparisonOptional:
    """WebsiteStats tolerates a /stats response with no comparison block (3.2)."""

    def test_model_constructs_without_comparison(self):
        stats = models.WebsiteStats(pageviews=10, visitors=5, visits=7, bounces=2, totaltime=100)
        assert stats.comparison is None

    def test_website_stats_parses_without_comparison(self):
        payload = {'pageviews': 10, 'visitors': 5, 'visits': 7, 'bounces': 2, 'totaltime': 100}
        mock_resp = MagicMock()
        mock_resp.json.return_value = payload
        mock_resp.raise_for_status = MagicMock()
        with patch('umami.impl.auth_token', 'fake-token'):
            with patch('umami.impl.httpx.get', MagicMock(return_value=mock_resp)):
                stats = umami.website_stats(start_at=datetime(2025, 1, 1), end_at=datetime(2025, 1, 31))
        assert stats.comparison is None
        assert stats.visitors == 5


class TestWebsiteUserOptional:
    """Website tolerates createUser instead of user, e.g. team-website listings (3.2)."""

    def _record(self, **overrides):
        base = {
            'id': 'w1',
            'domain': 'example.com',
            'shareId': None,
            'resetAt': None,
            'userId': None,
            'createdAt': '2026-01-01T00:00:00Z',
            'updatedAt': '2026-01-01T00:00:00Z',
            'deletedAt': None,
        }
        base.update(overrides)
        return base

    def test_website_with_create_user_instead_of_user(self):
        site = models.Website(**self._record(createUser={'username': 'mkennedy', 'id': 'u1'}))
        assert site.user is None
        assert site.createUser is not None
        assert site.createUser.username == 'mkennedy'

    def test_website_with_user(self):
        site = models.Website(**self._record(user={'username': 'mkennedy', 'id': 'u1'}))
        assert site.user is not None
        assert site.user.username == 'mkennedy'
        assert site.createUser is None
