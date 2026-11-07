# FAQ

Short answers to the questions that come up most, each with a link to the page that tells the full story.


# Do I need to log in to send events?

No, and this is the one that surprises everyone. [new_event()](../reference/new_event.md#umami.new_event), [new_page_view()](../reference/new_page_view.md#umami.new_page_view), and [new_revenue_event()](../reference/new_revenue_event.md#umami.new_revenue_event) only need [set_url_base()](../reference/set_url_base.md#umami.set_url_base) (or a Cloud key), a website id, and a hostname. Login is required for [websites()](../reference/websites.md#umami.websites), [website_stats()](../reference/website_stats.md#umami.website_stats), [active_users()](../reference/active_users.md#umami.active_users), and [verify_token()](../reference/verify_token.md#umami.verify_token). See [Authentication](authentication.md).


# Why is the package called umami-analytics but imported as umami?

`umami-analytics` is the name on PyPI. `umami` is the import name. A different, unrelated project got to the `umami` name on PyPI first, so `pip install umami` installs the wrong thing.


# Can the same code work for self-hosted and Umami Cloud?

Yes. Only the configuration step differs: [set_url_base()](../reference/set_url_base.md#umami.set_url_base) plus [login()](../reference/login.md#umami.login) for self-hosted, [set_cloud_api_key()](../reference/set_cloud_api_key.md#umami.set_cloud_api_key) for Cloud. Every other call is identical, and the package routes requests and sets headers according to the mode. The two modes are exclusive, and [clear_cloud_api_key()](../reference/clear_cloud_api_key.md#umami.clear_cloud_api_key) switches back.


# My event call returned without an error but nothing is in the dashboard

The usual causes are tracking disabled (the call returned `{}`), a custom user agent that Umami's bot filter rejected, the wrong website id, or looking at the wrong date range. [Troubleshooting](troubleshooting.md#event-sent-but-nothing-appears) walks through them in order.


# How do I keep tests from sending events?

Call [umami.disable()](../reference/disable.md#umami.disable) in a test fixture. The send functions still validate their arguments and return `{}` without a request. [Testing and CI](testing.md) has a fixture and shows how to mock the HTTP layer for the query functions.


# Does it batch events or retry on failure?

No. Each call is one HTTP request with the `httpx2` default five second timeout. Umami has an `/api/batch` endpoint, but the package does not wrap it. If you send events from a hot path, do it in a background task so a slow Umami server cannot slow your request.


# Can I set the user agent on an event?

Only on page views, through the `ua` argument of [new_page_view()](../reference/new_page_view.md#umami.new_page_view). Custom events always use the package's default browser user agent. Umami's bot filter is the reason the default looks like Chrome.


# What does distinct_id do?

It is sent as the payload field `id` and lets Umami attribute sessions and events to one logged-in user. Pass a `str` or `int`; blank values are dropped and other types raise [ValidationError](../reference/errors.ValidationError.md#umami.errors.ValidationError). See [Sending events](sending-events.md#per-user-attribution-with-distinct_id).


# Is it thread safe?

The send and query functions only read module-global configuration, so calling them from many threads or tasks is fine. The setters write that state and are not synchronized, so configure once at startup. See [How it works](how-it-works.md).


# Which Python versions are supported?

Python 3.10 and newer. The runtime dependencies are `httpx2` and `pydantic`.


# Which parts of the Umami API are not covered?

Reports, sessions, event data, metrics and time series, realtime, teams, users, links, pixels, and share pages. [How it works](how-it-works.md#beyond-the-wrapped-endpoints) shows how to call them with the token or key you already have.


# Where can an AI assistant read these docs?

The site publishes [llms.txt](../llms.txt) (an index of the API reference) and [llms-full.txt](../llms-full.txt) (every signature, docstring, and guide page), and an [agent skill](../skills.md) that teaches a coding agent the rules of the package. Every page is also available as Markdown by replacing `.html` with `.md` in its URL.
