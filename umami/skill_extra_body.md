## Install and import (the names differ)

The distribution on PyPI is **`umami-analytics`**, but the import name is **`umami`**. Installing `umami` grabs an unrelated package — always install the analytics client by its full distribution name:

```bash
uv pip install umami-analytics    # NOT `pip install umami`
```

```python
import umami                      # the import name is `umami`
```

There is no client class — everything is a module-level function called as `umami.func(...)`, and configuration (URL base, website id, hostname, credentials) is stored as module-global state.

## End-to-end wiring (self-hosted)

Configure once at startup, then send events from anywhere. `set_url_base()` takes the instance root **without** the trailing `/api`, and a trailing slash is stripped for you.

```python
import umami

umami.set_url_base('https://umami.example.com')   # required first; validates the http(s) scheme
umami.login('admin', 'super-secret')              # only needed for the query/stats calls below
umami.set_website_id('978435e2-7ba1-4337-9860-ec31ece2db60')  # default for later calls
umami.set_hostname('example.com')                 # default hostname for sent events

# Sending events/page views/revenue needs NO login — only url_base + a website_id + hostname.
umami.new_event(event_name='checkout-completed', url='/checkout', custom_data={'plan': 'pro'})
umami.new_revenue_event(revenue=19.99, currency='USD', event_name='checkout-cart', url='/checkout')
umami.new_page_view(page_title='Home', url='/')
```

Login IS required for the read-back calls: `websites()`, `website_stats()`, `active_users()`, and `verify_token()`. Sending functions never require it.

## Self-hosted vs Umami Cloud (mutually exclusive)

Two authentication modes, and you pick exactly one:

- **Self-hosted / token:** `set_url_base(...)` then `login(username, password)`. Calls carry `Authorization: Bearer <token>`.
- **Umami Cloud / API key:** `set_cloud_api_key(key, region=None)` (region is `'us'`, `'eu'`, or `None`). No `set_url_base()` or `login()` needed; data calls route to `https://api.umami.is/v1` with an `x-umami-api-key` header and events go to `https://cloud.umami.is/api/send`.

They do not mix. Calling `login()` while a Cloud API key is set raises `OperationNotAllowedError` — call `clear_cloud_api_key()` first to go back to token mode.

## Sync and async parity

Nearly every network operation has an identically-signed `_async` twin: `new_event` / `new_event_async`, `website_stats` / `website_stats_async`, `login` / `login_async`, and so on. The config setters (`set_url_base`, `set_website_id`, `set_hostname`, `enable`, `disable`) are sync-only — there is no `set_url_base_async`.

## disable() is the intended dev/test switch

`disable()` does not just skip network — the `new_*` functions still **validate** their inputs, then early-return an empty dict `{}` without any HTTP call. `enable()` (the default) turns them back on. Query and auth functions ignore this flag and always run.

```python
umami.disable()                                   # e.g. in tests / local dev
umami.new_event(event_name='x', url='/')          # validates args, returns {}, sends nothing
```

## distinct_id maps to the payload `id`

`distinct_id` (accepted by `new_event`, `new_revenue_event`, `new_page_view`) is sent as the event payload's `id` field for logged-in-user attribution. It accepts a `str` or `int` only; blank/whitespace values are ignored (no id sent), and a `bool` (or any other type) raises `ValidationError`.

## Errors you will actually catch

- `umami.errors.OperationNotAllowedError` — required state is missing (no `url_base`/Cloud key, or a query call before `login()`). It subclasses `ValidationError`.
- `umami.errors.ValidationError` — bad input (empty/non-http url, negative or non-numeric revenue, empty currency, invalid `distinct_id`, missing hostname/website_id).
- `httpx.HTTPStatusError` — a non-2xx server response (the SDK calls `raise_for_status()`). Note `verify_token()` and `heartbeat()` are the exceptions: they never raise and return `bool`.

## This SDK wraps only a subset of the Umami API

It covers config, auth, sending events/page views/revenue, listing websites, summarized `website_stats`, and `active_users`. For everything else — reports (funnel/attribution/journey/retention/revenue), sessions, event-data, metrics/pageview series, realtime, teams, users, links, pixels, shares — call the Umami HTTP API directly with the token you already hold. Two API gotchas the wrapper hides but direct calls do not:

- **Two date conventions:** stats/sessions/events/revenue GET endpoints take `startAt`/`endAt` as **Unix milliseconds**; `POST /api/reports/*` take `startDate`/`endDate` as **ISO 8601 strings** inside `parameters`.
- **Renamed filters (2025-10-07):** the filter formerly `url` is now `path`, and `host` is now `hostname`. (In `website_stats(...)` you still pass `url=`/`host=` kwargs; the SDK maps them to `path`/`hostname` for you.)

The companion agent reference guide documents the complete REST surface.

## Fetching the docs as Markdown

Every page on the documentation site has a plain-Markdown twin: swap the `.html` extension for `.md` to get token-efficient source without the site chrome. For example https://mkennedy.codes/docs/umami-python/reference/new_event.html is also available at https://mkennedy.codes/docs/umami-python/reference/new_event.md. Prefer the `.md` form when reading these docs programmatically.
