# Configuration

All configuration lives on one whiteboard inside the `umami` module. There is no configuration file, no environment variable, and no client object to carry around. A handful of setter functions write on the whiteboard, usually once at startup, and every other function reads from it. This page lists what is on the whiteboard, what it says before you write anything, and who reads each line.


# Settings

| Function | Sets | Default | Required by |
|----|----|----|----|
| `set_url_base(url)` | The instance root for self-hosted mode. Must start with `http://` or `https://`. A trailing slash is removed. `/api` must not be included. | none | Every call in self-hosted mode |
| `set_website_id(website_id)` | Default website for sending and querying. | none | Send functions, [website_stats()](../reference/website_stats.md#umami.website_stats), [active_users()](../reference/active_users.md#umami.active_users) unless passed per call |
| `set_hostname(hostname)` | Default hostname recorded on events and page views. | none | Send functions unless passed per call |
| `set_cloud_api_key(key, region=None)` | Umami Cloud key and optional `'us'` or `'eu'` region. Switches to Cloud mode. | none | Every call in Cloud mode |
| [clear_cloud_api_key()](../reference/clear_cloud_api_key.md#umami.clear_cloud_api_key) | Removes the key and region. Back to self-hosted mode. |  |  |
| `login(username, password)` | Stores the token for query calls. Self-hosted only. | none | [websites()](../reference/websites.md#umami.websites), [website_stats()](../reference/website_stats.md#umami.website_stats), [active_users()](../reference/active_users.md#umami.active_users), [verify_token()](../reference/verify_token.md#umami.verify_token) |
| [enable()](../reference/enable.md#umami.enable) / [disable()](../reference/disable.md#umami.disable) | Whether the send functions make requests. | enabled |  |

The setters are synchronous only. There is no `set_url_base_async()`, because writing on a whiteboard does not need an event loop.


# Per-call defaults

The send functions fill in the session fields Umami expects from a browser, so an event from a Python process looks enough like a visit for Umami to file it. Override any of them per call.

| Argument | [new_event](../reference/new_event.md#umami.new_event) | [new_page_view](../reference/new_page_view.md#umami.new_page_view) | [new_revenue_event](../reference/new_revenue_event.md#umami.new_revenue_event) |
|----|----|----|----|
| `url` | `'/'` | required | `'/'` |
| `title` | the event name | `page_title`, required | the event name |
| `referrer` | `''` | `''` | `''` |
| `language` | `'en-US'` | `'en-US'` | `'en-US'` |
| `screen` | `'1920x1080'` | `'1920x1080'` | `'1920x1080'` |
| `ua` | not accepted | desktop Chrome user agent | not accepted |
| `ip_address` | not sent | not sent | not sent |
| `distinct_id` | not sent | not sent | not sent |
| `custom_data` | `{}` | not accepted | `{}` plus `revenue` and `currency` |
| `event_name` | required | none | `'revenue'` |
| `currency` |  |  | `'USD'` |


# What happens on a second call

Whiteboards get overwritten, and the rules are short:

- [set_url_base()](../reference/set_url_base.md#umami.set_url_base) again replaces the previous value.
- [login()](../reference/login.md#umami.login) again replaces the stored token. There is no logout.
- [set_cloud_api_key()](../reference/set_cloud_api_key.md#umami.set_cloud_api_key) again replaces the key and region.
- [set_cloud_api_key()](../reference/set_cloud_api_key.md#umami.set_cloud_api_key) after [login()](../reference/login.md#umami.login) switches to Cloud mode. The login token is kept but unused until [clear_cloud_api_key()](../reference/clear_cloud_api_key.md#umami.clear_cloud_api_key).
- [set_url_base()](../reference/set_url_base.md#umami.set_url_base) while a Cloud key is set stores the URL but it is ignored until [clear_cloud_api_key()](../reference/clear_cloud_api_key.md#umami.clear_cloud_api_key).
- [clear_cloud_api_key()](../reference/clear_cloud_api_key.md#umami.clear_cloud_api_key) when no key is set does nothing.
- [enable()](../reference/enable.md#umami.enable) and [disable()](../reference/disable.md#umami.disable) are idempotent.


# Precedence

An explicit `website_id` or `hostname` argument on a call always wins over the value set with [set_website_id()](../reference/set_website_id.md#umami.set_website_id) or [set_hostname()](../reference/set_hostname.md#umami.set_hostname). Passing `None` falls back to the default; passing an empty string is treated as missing and raises [ValidationError](../reference/errors.ValidationError.md#umami.errors.ValidationError).


# Reading the current state

The public API has no getters. [is_logged_in()](../reference/is_logged_in.md#umami.is_logged_in) tells you whether a token or Cloud key is present. For anything else, keep your own record of what you configured. If you are in a debugger, the module `umami.impl` holds the values as plain attributes (`url_base`, `default_website_id`, `default_hostname`, `auth_token`, `api_key`, `cloud_region`, `tracking_enabled`), which is handy for a quick look and in tests, but it is an implementation detail rather than a supported interface.


# Version

`umami.__version__` is read from the installed distribution metadata and is `'0.0.0'` when the package is imported from a source checkout that was not installed. `umami.user_agent` is the `User-Agent` sent on query calls and includes the version and Python version.
