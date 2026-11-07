# Sending events

Three functions send data to Umami: [new_event()](../reference/new_event.md#umami.new_event) for custom events, [new_page_view()](../reference/new_page_view.md#umami.new_page_view) for page views, and [new_revenue_event()](../reference/new_revenue_event.md#umami.new_revenue_event) for events that carry a monetary amount. Each has an `_async` twin with the same signature and the same return value. None of them require a login. They need [set_url_base()](../reference/set_url_base.md#umami.set_url_base) (or [set_cloud_api_key()](../reference/set_cloud_api_key.md#umami.set_cloud_api_key)), a website id, and a hostname.

All three share a few arguments:

| Argument | Default | Notes |
|----|----|----|
| `hostname` | value from [set_hostname()](../reference/set_hostname.md#umami.set_hostname) | The domain visitors see. Required one way or the other. |
| `website_id` | value from [set_website_id()](../reference/set_website_id.md#umami.set_website_id) | Required one way or the other. |
| `url` | `'/'` for events, required for page views | The page path the event is attributed to. |
| `referrer` | `''` | Shown in the Referrers section when set. |
| `language` | `'en-US'` | Recorded on the session. |
| `screen` | `'1920x1080'` | Recorded on the session. |
| `ip_address` | not sent | Sent as `ip` when non-blank, so Umami geolocates the real visitor instead of your server. |
| `distinct_id` | not sent | A stable per-user id. See below. |

Missing `hostname` or `website_id` raises [umami.errors.ValidationError](../reference/errors.ValidationError.md#umami.errors.ValidationError) before any request is made.


# Custom events

``` python
umami.new_event(
    event_name='checkout-completed',
    url='/checkout',
    title='Checkout',            # defaults to event_name
    custom_data={'plan': 'pro', 'seats': 3},
    referrer='https://news.ycombinator.com',
)
```

`event_name` is required and must not be blank. `title` is the page title Umami records alongside the event and defaults to the event name. `custom_data` becomes the event's properties; it is not shown in the main dashboard view but is available by clicking into the event and through the Umami API.


# Page views

A page view is what the browser tracker records when a page loads. Send one from the server when you render a page for a client that cannot run JavaScript, or when you serve content outside the browser.

``` python
umami.new_page_view(page_title='Account details', url='/account/details', ip_address=request.client.host)
```

`page_title` and `url` are both required. Page views have no event name and no custom data.

[new_page_view()](../reference/new_page_view.md#umami.new_page_view) accepts one extra argument the others do not: `ua`, the user agent recorded for the visitor. It defaults to a desktop Chrome user agent because Umami drops requests whose user agent looks like a bot. Pass the real browser's user agent when you have it so the Browsers and Devices sections stay accurate. [new_event()](../reference/new_event.md#umami.new_event) has no `ua` argument.


# Revenue

[new_revenue_event()](../reference/new_revenue_event.md#umami.new_revenue_event) is [new_event()](../reference/new_event.md#umami.new_event) with two keys added to `custom_data`: `revenue` and `currency`. Umami's revenue report reads those keys.

``` python
umami.new_revenue_event(
    revenue=19.99,
    currency='USD',              # ISO 4217, defaults to 'USD'
    event_name='checkout-cart',  # defaults to 'revenue'
    url='/checkout',
    custom_data={'product': 'widget', 'quantity': 2},
)
```

Validation before the request: `revenue` must be an `int` or `float` greater than or equal to zero, and `currency` must be non-blank. If your `custom_data` already has `revenue` or `currency` keys they are overwritten by the arguments.


# Per-user attribution with distinct_id

Pass `distinct_id` on any of the three functions to attach a stable identifier for the logged-in user. It is sent as the payload field `id`, which Umami uses to tie sessions and events to one visitor across devices.

``` python
umami.new_event(event_name='login', distinct_id=user.id)
```

Rules the package enforces:

- `str` and `int` are accepted. Integers are sent as strings.
- Blank or whitespace-only strings are ignored and no `id` is sent.
- `bool` and any other type raise [ValidationError](../reference/errors.ValidationError.md#umami.errors.ValidationError). The bool check is explicit because `True` is an `int` in Python.

Use an internal user id or a hash, not an email address or other raw personal data.


# What gets sent

Every call makes one `POST` to `/api/send` with a body like this. There is no batching and no retry.

``` json
{
  "type": "event",
  "payload": {
    "website": "978435e2-7ba1-4337-9860-ec31ece2db60",
    "hostname": "example.com",
    "url": "/checkout",
    "title": "checkout-cart",
    "name": "checkout-cart",
    "data": {"product": "widget", "quantity": 2, "revenue": 19.99, "currency": "USD"},
    "referrer": "",
    "language": "en-US",
    "screen": "1920x1080",
    "id": "user-42"
  }
}
```

A page view is the same shape without `name` and `data`. The `ip` field is present only when you pass `ip_address`, and `id` only when you pass `distinct_id`.


# Return values

The functions return the parsed JSON response from Umami as a dict. When tracking has been turned off with [disable()](../reference/disable.md#umami.disable) they validate their arguments and return `{}` without making a request. A non-2xx response raises `httpx2.HTTPStatusError`.


# Async

Each function has an `_async` twin that sends the same payload and returns the same value.

``` python
await umami.new_event_async(event_name='checkout-completed', url='/checkout')
await umami.new_page_view_async(page_title='Home', url='/')
await umami.new_revenue_event_async(revenue=19.99, url='/checkout')
```

The configuration functions are synchronous only. Call [set_url_base()](../reference/set_url_base.md#umami.set_url_base) and friends once at startup, before your event loop starts handling requests.

If an event does not appear in the dashboard, see [Troubleshooting](troubleshooting.md#event-sent-but-nothing-appears).
