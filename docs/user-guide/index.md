# User Guide

Umami records page views and custom events from a small JavaScript tracker in your pages. That works for clicks and form submits, but some of the events you care about most never happen in the browser. A purchase that completes inside a payment webhook, a background job that finishes, or an API call from a mobile app all happen in your Python code, with no HTML element to attach a `data-umami-event` attribute to.

`umami-analytics` is a Python client for the parts of the [Umami API](https://umami.is/docs/api) that a backend needs. It sends custom events, page views, and revenue to a self-hosted Umami instance or to Umami Cloud, and it reads back the basic numbers: your websites, page views and visitors over a date range, and the number of active visitors right now. Every network call has a synchronous function and an `_async` twin.

The package is deliberately a partial wrapper. It covers configuration, authentication, sending events, listing websites, summary stats, and active users. Reports, sessions, event data, and the rest of the Umami API are one HTTP call away with the token the package already holds, and the [How it works](how-it-works.md) page shows how.


# Where to go next

- [Getting started](getting-started.md): install the package, point it at your instance, send your first event, and see where it lands in the dashboard.
- [Sending events](sending-events.md): custom events, page views, revenue, custom data, and per-user `distinct_id`.
- [Authentication](authentication.md): self-hosted login versus an Umami Cloud API key, and when a login is actually required.
- [Querying stats](querying-stats.md): listing websites, page views and visitors for a date range, filters, and active users.
- [Troubleshooting](troubleshooting.md): what each error means and what to do about it, including events that return 200 but never appear.
- [Testing and CI](testing.md): keep test runs out of your analytics with [disable()](../reference/disable.md#umami.disable), and mock the HTTP boundary.
- [Configuration](configuration.md): every setting, its default, and which calls need it.
- [How it works](how-it-works.md): module-global state, request routing, headers, user agents, and what the package does not do.
- [FAQ](faq.md): short answers to the questions that come up most.

The [API Reference](../reference/index.md) documents every public function and model, with the sync and async twins side by side.
