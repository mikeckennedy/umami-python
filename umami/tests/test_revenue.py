from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from umami.errors import ValidationError

import umami


class TestNewRevenueEvent:
    """Tests for the sync new_revenue_event function."""

    @patch('umami.impl.httpx.post')
    def test_default_revenue_event(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {}
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        umami.new_revenue_event(revenue=19.99)

        call_kwargs = mock_post.call_args
        payload = call_kwargs.kwargs['json']['payload']
        assert payload['name'] == 'revenue'
        assert payload['data']['revenue'] == 19.99
        assert payload['data']['currency'] == 'USD'

    @patch('umami.impl.httpx.post')
    def test_custom_currency(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {}
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        umami.new_revenue_event(revenue=49.00, currency='EUR')

        payload = mock_post.call_args.kwargs['json']['payload']
        assert payload['data']['currency'] == 'EUR'

    @patch('umami.impl.httpx.post')
    def test_custom_event_name(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {}
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        umami.new_revenue_event(revenue=10.00, event_name='checkout-cart')

        payload = mock_post.call_args.kwargs['json']['payload']
        assert payload['name'] == 'checkout-cart'

    @patch('umami.impl.httpx.post')
    def test_additional_custom_data_preserved(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {}
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        umami.new_revenue_event(revenue=25.00, custom_data={'product': 'widget', 'quantity': 2})

        payload = mock_post.call_args.kwargs['json']['payload']
        assert payload['data']['product'] == 'widget'
        assert payload['data']['quantity'] == 2
        assert payload['data']['revenue'] == 25.00
        assert payload['data']['currency'] == 'USD'

    @patch('umami.impl.httpx.post')
    def test_revenue_currency_override_custom_data(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {}
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        umami.new_revenue_event(
            revenue=30.00,
            currency='GBP',
            custom_data={
                'revenue': 'should_be_overridden',
                'currency': 'should_be_overridden',
            },
        )

        payload = mock_post.call_args.kwargs['json']['payload']
        assert payload['data']['revenue'] == 30.00
        assert payload['data']['currency'] == 'GBP'

    @patch('umami.impl.httpx.post')
    def test_zero_revenue_allowed(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {}
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        umami.new_revenue_event(revenue=0)

        payload = mock_post.call_args.kwargs['json']['payload']
        assert payload['data']['revenue'] == 0

    def test_negative_revenue_raises(self):
        with pytest.raises(ValidationError, match='must be >= 0'):
            umami.new_revenue_event(revenue=-5.00)

    def test_non_numeric_revenue_raises(self):
        with pytest.raises(ValidationError, match='must be a number'):
            umami.new_revenue_event(revenue='not_a_number')  # type: ignore

    def test_empty_currency_raises(self):
        with pytest.raises(ValidationError, match='non-empty string'):
            umami.new_revenue_event(revenue=10.00, currency='')

    def test_tracking_disabled_returns_early(self):
        umami.disable()
        result = umami.new_revenue_event(revenue=19.99)
        # Should return without making any HTTP call
        assert result is None

    @patch('umami.impl.httpx.post')
    def test_integer_revenue(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {}
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        umami.new_revenue_event(revenue=100)

        payload = mock_post.call_args.kwargs['json']['payload']
        assert payload['data']['revenue'] == 100


class TestNewRevenueEventAsync:
    """Tests for the async new_revenue_event_async function."""

    @pytest.mark.asyncio
    async def test_default_revenue_event_async(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {}
        mock_resp.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_resp)

        with patch('umami.impl.httpx.AsyncClient', return_value=mock_client):
            result = await umami.new_revenue_event_async(revenue=19.99)

        call_kwargs = mock_client.post.call_args
        payload = call_kwargs.kwargs['json']['payload']
        assert payload['name'] == 'revenue'
        assert payload['data']['revenue'] == 19.99
        assert payload['data']['currency'] == 'USD'
        assert result == {}

    @pytest.mark.asyncio
    async def test_custom_params_async(self):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {}
        mock_resp.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_resp)

        with patch('umami.impl.httpx.AsyncClient', return_value=mock_client):
            await umami.new_revenue_event_async(
                revenue=49.00,
                currency='EUR',
                event_name='checkout-cart',
                url='/checkout',
            )

        payload = mock_client.post.call_args.kwargs['json']['payload']
        assert payload['name'] == 'checkout-cart'
        assert payload['data']['revenue'] == 49.00
        assert payload['data']['currency'] == 'EUR'
        assert payload['url'] == '/checkout'

    @pytest.mark.asyncio
    async def test_tracking_disabled_async(self):
        umami.disable()
        result = await umami.new_revenue_event_async(revenue=19.99)
        assert result == {}

    @pytest.mark.asyncio
    async def test_negative_revenue_raises_async(self):
        with pytest.raises(ValidationError, match='must be >= 0'):
            await umami.new_revenue_event_async(revenue=-5.00)
