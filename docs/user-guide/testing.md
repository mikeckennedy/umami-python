# Testing and CI

Picture Monday morning. The revenue report shows two hundred course purchases over the weekend, every one of them for `test-course`, every one for 1.00 USD, all from a hostname of `localhost`. Nobody bought anything. The CI pipeline ran the checkout tests forty times, and each run dutifully reported its fake purchases to your real Umami website.

Analytics calls in application code are a problem for test suites in exactly this way, and in the opposite way too: a test environment without network access fails on the first event. The package gives you two tools. A module-level switch turns sending off, and a single HTTP boundary is easy to mock.


# Turn sending off with disable()

[umami.disable()](../reference/disable.md#umami.disable) makes [new_event()](../reference/new_event.md#umami.new_event), [new_page_view()](../reference/new_page_view.md#umami.new_page_view), and [new_revenue_event()](../reference/new_revenue_event.md#umami.new_revenue_event) (and their async twins) validate their arguments and then return `{}` without making a request. [umami.enable()](../reference/enable.md#umami.enable) turns sending back on, and enabled is the default.

``` python
import umami

umami.set_url_base('https://umami.example.com')
umami.set_website_id('978435e2-7ba1-4337-9860-ec31ece2db60')
umami.set_hostname('example.com')
umami.disable()

umami.new_event(event_name='signup')  # returns {} and sends nothing
```

Two details matter:

- Validation still runs. A blank event name or a missing website id still raises [ValidationError](../reference/errors.ValidationError.md#umami.errors.ValidationError), so tests catch configuration mistakes without touching the network. Disabled does not mean asleep.
- Only the send functions are affected. [login()](../reference/login.md#umami.login), [websites()](../reference/websites.md#umami.websites), [website_stats()](../reference/website_stats.md#umami.website_stats), [active_users()](../reference/active_users.md#umami.active_users), [verify_token()](../reference/verify_token.md#umami.verify_token), and [heartbeat()](../reference/heartbeat.md#umami.heartbeat) always make their request. Mock those if a test reaches them.

The simplest production pattern is to decide at startup:

``` python
import os
import umami

umami.set_url_base(os.environ['UMAMI_URL'])
umami.set_website_id(os.environ['UMAMI_WEBSITE_ID'])
umami.set_hostname('example.com')

if os.environ.get('APP_ENV') != 'production':
    umami.disable()
```

The variable names are yours. The package reads no environment variables itself.


# A pytest fixture

Because the configuration is module-global, one test can leak state into the next. A test that calls [enable()](../reference/enable.md#umami.enable) to assert on a payload leaves tracking on for every test that runs after it. An autouse fixture that resets everything keeps tests independent:

``` python
# conftest.py
import pytest
import umami


@pytest.fixture(autouse=True)
def _umami_offline():
    umami.set_url_base('https://umami.test')
    umami.set_website_id('test-website-id')
    umami.set_hostname('test.example')
    umami.clear_cloud_api_key()
    umami.disable()
    yield
```

With this in place, application code can call [umami.new_event()](../reference/new_event.md#umami.new_event) freely and nothing leaves the test process. The Monday morning report stays honest.


# Mock the HTTP boundary

When a test needs to assert what would have been sent, or needs a query function to return data, patch `httpx2` where the package uses it. The package does `import httpx2 as httpx` inside `umami.impl` and calls `httpx.post()` and `httpx.get()` for the sync functions and `httpx.AsyncClient()` for the async ones. There is one boundary, and this is how the package's own test suite works.

``` python
from unittest.mock import MagicMock, patch

import umami


def test_purchase_sends_revenue():
    umami.enable()
    response = MagicMock()
    response.json.return_value = {'cache': 'abc'}
    with patch('umami.impl.httpx.post', return_value=response) as post:
        umami.new_revenue_event(revenue=19.99, event_name='purchase', url='/checkout')

    body = post.call_args.kwargs['json']
    assert body['payload']['name'] == 'purchase'
    assert body['payload']['data'] == {'revenue': 19.99, 'currency': 'USD'}
```

For the async twins, patch `umami.impl.httpx.AsyncClient` with an object that works as an async context manager:

``` python
from unittest.mock import AsyncMock, MagicMock, patch

import umami


async def test_async_event():
    umami.enable()
    response = MagicMock()
    response.json.return_value = {}
    client = AsyncMock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=False)
    client.post = AsyncMock(return_value=response)

    with patch('umami.impl.httpx.AsyncClient', return_value=client):
        await umami.new_event_async(event_name='signup')

    assert client.post.call_args.kwargs['json']['payload']['name'] == 'signup'
```

Async tests need `pytest-asyncio`. Setting `asyncio_mode = "auto"` in your pytest configuration removes the need for a marker on each test.

To test a query function, return the shape Umami returns. [websites()](../reference/websites.md#umami.websites) expects `{'data': [...], 'count': n, 'page': 1, 'pageSize': 10}`, [website_stats()](../reference/website_stats.md#umami.website_stats) expects the five integer fields `pageviews`, `visitors`, `visits`, `bounces`, and `totaltime`, and [active_users()](../reference/active_users.md#umami.active_users) expects `{'visitors': n}`.


# Continuous integration

Nothing in the package needs network access when tracking is disabled, so the fixture above is enough for CI. The remaining risk is the mirror image of the weekend story. If the variable that selects [disable()](../reference/disable.md#umami.disable) is set in the test stage and somehow also set in production, every call returns `{}` and no events arrive, which looks exactly like a broken server. A forgotten [disable()](../reference/disable.md#umami.disable) in production is silent. That is why the [Troubleshooting](troubleshooting.md#event-sent-but-nothing-appears) page lists it as the first thing to check.
