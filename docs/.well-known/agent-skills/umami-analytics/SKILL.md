---
name: umami-analytics
description: >
  Python client for the Umami web analytics API (self-hosted or Umami Cloud). Sends custom events, page views, and revenue from backend code, and reads back websites, summary stats, and active users, with sync and async twins for every call. Use when adding Umami tracking to a Python app, when code imports `umami` or installs `umami-analytics`, when choosing between self-hosted login and a Cloud API key, when `umami.errors.OperationNotAllowedError`, `umami.errors.ValidationError`, or an `httpx2.HTTPStatusError` from an Umami call appears, when events are sent but never show in the dashboard, or when tests must not send real analytics.
license: MIT
compatibility: Requires Python >=3.10 and a reachable Umami instance or Umami Cloud key. Depends on httpx2 and pydantic.
---

# umami-analytics

Umami's browser tracker cannot see events that happen inside server code, such as a purchase completed by a webhook. `umami-analytics` sends those as Umami custom events, page views, or revenue, and reads back basic stats. It is a module of functions with module-global configuration; there is no client class, no CLI, and it reads no environment variables. Bad arguments raise `umami.errors.ValidationError`, missing setup raises `umami.errors.OperationNotAllowedError`, and non-2xx responses raise `httpx2.HTTPStatusError`.

## Install

```bash
uv add umami-analytics   # or: pip install umami-analytics   (import name is `umami`; never `pip install umami`)
```

## Use

```python
import umami

umami.set_url_base('https://umami.example.com')  # must be first; instance root, no /api
umami.set_website_id('978435e2-7ba1-4337-9860-ec31ece2db60')
umami.set_hostname('example.com')  # the domain visitors see

umami.new_event(event_name='purchase-course', url='/courses/python', custom_data={'plan': 'pro'})
umami.new_revenue_event(revenue=19.99, currency='USD', event_name='checkout', url='/checkout', distinct_id=user.id)
await umami.new_event_async(event_name='signup')  # every network call has an _async twin
```

In tests or local development, after the setters: `umami.disable()`. The send functions then validate and return `{}` with no request. In CI, select that with your own setting, for example `if os.environ.get('APP_ENV') != 'production': umami.disable()`.

For Umami Cloud, replace `set_url_base()` with `umami.set_cloud_api_key(key, region=None)`; never call `login()` in Cloud mode.

## Rules

- `set_url_base()` or `set_cloud_api_key()` must run before any other call, including `heartbeat()`. Setters are sync only and not thread-safe; call them once at startup.
- Sending events needs no login. `websites()`, `website_stats()`, `active_users()`, and `verify_token()` need `login()` (self-hosted) or a Cloud key.
- The two modes are exclusive. A Cloud key wins over `set_url_base()`; `login()` raises `OperationNotAllowedError` while a key is set; `clear_cloud_api_key()` switches back and keeps any earlier login token.
- `login()` tokens expire. `verify_token()` returns `False` instead of raising; log in again when it does. `login()` twice replaces the token; there is no logout.
- `disable()` silences only the three send functions. Query and auth functions always hit the network. A forgotten `disable()` in production is silent: calls return `{}`.
- `hostname` and `website_id` must come from the setters or the call, or `ValidationError` is raised before any request. Empty strings count as missing. An explicit argument beats the setter.
- `event_name` is required and non-blank for `new_event()`. `new_page_view()` requires `page_title` and `url` and has no `event_name` or `custom_data`. `url` defaults to `'/'` on events and is required on page views.
- `distinct_id` accepts `str` or `int` and is sent as payload `id`. Blank strings are dropped. `bool` and other types raise `ValidationError`.
- `new_revenue_event()` requires `revenue >= 0` as `int` or `float` and a non-blank `currency` (default `'USD'`); it overwrites `revenue` and `currency` keys in `custom_data`.
- Only `new_page_view()` accepts `ua`. Passing `ua` to `new_event()` is a `TypeError`. The default is a Chrome user agent because Umami drops bot-like user agents, often while still returning 200.
- `website_stats()` takes `datetime` objects and converts them with `timestamp()`, so naive datetimes mean local time. Its `url` and `host` filters are sent as `path` and `hostname`. `websites()` follows every page and returns the full list.
- One HTTP request per call (`websites()` makes one per page), five second timeout, no retry, no batching, no connection pool. `heartbeat()` and `verify_token()` never raise.
- `umami.models` are Pydantic models (`Website`, `WebsiteStats`, `LoginResponse`). `OperationNotAllowedError` subclasses `ValidationError`.

## Decision table

| Need | Use |
|---|---|
| Self-hosted instance | `set_url_base(url)`, then `login(user, pw)` only if you will query |
| Umami Cloud | `set_cloud_api_key(key, region='us' or 'eu' or None)`; no `set_url_base()`, no `login()` |
| Record a business event | `new_event(event_name, url=..., custom_data={...})` |
| Record money | `new_revenue_event(revenue, currency='USD', event_name=..., url=...)` |
| Record a server-rendered page load | `new_page_view(page_title, url, ua=request_user_agent, ip_address=client_ip)` |
| Tie events to a logged-in user | `distinct_id=user.id` on any send call |
| Silence analytics in tests or dev | `umami.disable()` after the setters |
| Check the token still works | `verify_token()`; `check_server=False` for a local presence check |
| Check the server is up | `heartbeat()` |
| Visitors, views, bounces for a range | `website_stats(start_at, end_at, website_id=None, url=..., country=...)` |
| Visitors on the site right now | `active_users(website_id=None)` |
| Anything else in the Umami API | Call it with `httpx2` using `login().token` or the Cloud key |

## API

- `set_url_base(url) -> None`: raises `ValidationError` unless `url` starts with `http://` or `https://`; strips a trailing slash.
- `set_website_id(website_id) -> None`, `set_hostname(hostname) -> None`: defaults for later calls; not validated until a send.
- `set_cloud_api_key(key, region=None) -> None`: raises `ValidationError` on a blank key or a region other than `'us'`, `'eu'`, `None`. `clear_cloud_api_key() -> None`.
- `enable() -> None`, `disable() -> None`: toggle the send functions. `is_logged_in() -> bool`: token or key present, no network.
- `login(username, password) -> models.LoginResponse` / `login_async`: raises `OperationNotAllowedError` in Cloud mode or without `set_url_base()`, `ValidationError` on empty fields, `HTTPStatusError` on bad credentials.
- `verify_token(check_server=True) -> bool` / `verify_token_async`: never raises.
- `new_event(event_name, hostname=None, url='/', website_id=None, title=None, custom_data=None, referrer='', language='en-US', screen='1920x1080', ip_address=None, distinct_id=None) -> dict` / `new_event_async`: `{}` when disabled.
- `new_revenue_event(revenue, currency='USD', event_name='revenue', ...same as new_event...) -> dict` / `new_revenue_event_async`.
- `new_page_view(page_title, url, hostname=None, website_id=None, referrer='', language='en-US', screen='1920x1080', ua=<chrome>, ip_address=None, distinct_id=None) -> dict` / `new_page_view_async`.
- `websites() -> list[models.Website]` / `websites_async`: `Website.id` is the website id; `user` or `createUser` may be `None`.
- `website_stats(start_at, end_at, website_id=None, url=None, referrer=None, title=None, query=None, event=None, host=None, os=None, browser=None, device=None, country=None, region=None, city=None) -> models.WebsiteStats` / `website_stats_async`: fields `pageviews`, `visitors`, `visits`, `bounces`, `totaltime`, optional `comparison`.
- `active_users(website_id=None) -> int` / `active_users_async`.
- `heartbeat() -> bool` / `heartbeat_async`: `False` on any failure, including missing configuration.

## What a send looks like

`new_revenue_event(revenue=19.99, event_name='checkout', url='/checkout', custom_data={'plan': 'pro'}, distinct_id=42)` makes one `POST` to `{url_base}/api/send` with:

```json
{"type": "event",
 "payload": {"website": "978435e2-...", "hostname": "example.com", "url": "/checkout",
             "title": "checkout", "name": "checkout",
             "data": {"plan": "pro", "revenue": 19.99, "currency": "USD"},
             "referrer": "", "language": "en-US", "screen": "1920x1080", "id": "42"}}
```

The return value is Umami's JSON, typically `{"cache": "...", "sessionId": "...", "visitId": "..."}`, or `{}` when disabled. In the dashboard the event appears under Events as `checkout`, the page under Pages as `/checkout`, and the amount in the Revenue report. If nothing appears, fix in this order: configuration (the `ValidationError` and `OperationNotAllowedError` messages name the missing piece), then `heartbeat()`, then `verify_token()`, then the bot filter (custom `ua`), website id, mode, and dashboard date range.

## Resources

- Docs: <https://mkennedy.codes/docs/umami-python/>
- Getting started: <https://mkennedy.codes/docs/umami-python/user-guide/getting-started.html>
- Authentication (self-hosted vs Cloud): <https://mkennedy.codes/docs/umami-python/user-guide/authentication.html>
- Troubleshooting: <https://mkennedy.codes/docs/umami-python/user-guide/troubleshooting.html>
- Testing and CI: <https://mkennedy.codes/docs/umami-python/user-guide/testing.html>
- API reference: <https://mkennedy.codes/docs/umami-python/reference/> (append `.md` instead of `.html` to any page for Markdown)
- llms.txt: <https://mkennedy.codes/docs/umami-python/llms.txt>, llms-full.txt: <https://mkennedy.codes/docs/umami-python/llms-full.txt>
- Source: <https://github.com/mikeckennedy/umami-python>
