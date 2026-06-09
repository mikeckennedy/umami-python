---
name: umami
description: >
  Umami Analytics Client for Python. Use when writing Python code that uses the umami package.
license: MIT
compatibility: Requires Python >=3.10.
---

# Umami Analytics

Umami Analytics Client for Python

## Installation

```bash
pip install umami
```

## API overview

### Configuration

One-time setup. `set_url_base()` is required before any operation; Cloud users call `set_cloud_api_key()` instead.

- `set_url_base`: Set the base URL of your self-hosted Umami instance
- `set_website_id`: Set the default website ID used for subsequent calls
- `set_hostname`: Set the default hostname used when sending events and page views
- `set_cloud_api_key`: Authenticate against Umami Cloud with an API key instead of login()
- `clear_cloud_api_key`: Exit Cloud mode and return to self-hosted/token behavior
- `enable`: Enable event and page view tracking
- `disable`: Disable event and page view tracking

### Authentication

Required for the query endpoints and `verify_token`. Not needed to send events.

- `login`: Log into a self-hosted Umami instance and retrieve a temporary auth token
- `login_async`: Log into a self-hosted Umami instance and retrieve a temporary auth token
- `is_logged_in`: Whether a credential is currently set locally
- `verify_token`: Verify that the currently stored credential is still valid
- `verify_token_async`: Verify that the currently stored credential is still valid

### Sending events

Send custom events, revenue, and page views. No login required — only a URL base and a website id/hostname.

- `new_event`: Create a new custom event in Umami for the given website_id and hostname
- `new_event_async`: Create a new custom event in Umami for the given website_id and hostname
- `new_revenue_event`: Create a new revenue event in Umami. This is a convenience wrapper around
- `new_revenue_event_async`: Create a new revenue event in Umami. This is a convenience wrapper around
- `new_page_view`: Create a new page view event in Umami for the given website_id and hostname
- `new_page_view_async`: Create a new page view event in Umami for the given website_id and hostname

### Querying stats

Read analytics back out. Requires login (or a Cloud API key).

- `websites`: All the websites that are registered in your Umami instance
- `websites_async`: All the websites that are registered in your Umami instance
- `website_stats`: Retrieves the statistics for a specific website over a date range
- `website_stats_async`: Retrieves the statistics for a specific website over a date range
- `active_users`: Retrieves the number of currently-active visitors for a specific website
- `active_users_async`: Retrieves the number of currently-active visitors for a specific website

### Health

Check Umami server connectivity.

- `heartbeat`: Check whether the configured Umami server is reachable and healthy
- `heartbeat_async`: Check whether the configured Umami server is reachable and healthy

### Response models

Pydantic models returned by the query functions.

- `models.WebsitesResponse`
- `models.Website`
- `models.WebsiteStats`
- `models.WebsiteStatsCmp`
- `models.LoginResponse`
- `models.User`
- `models.WebsiteUser`

### Errors

Exception hierarchy. `ValidationError` is the base; `OperationNotAllowedError` is raised when required state (url_base, login) is missing.

- `errors.ValidationError`
- `errors.OperationNotAllowedError`

## Resources

- [Full documentation](https://mkennedy.codes/docs/umami-python/)
- [llms.txt](llms.txt) — Indexed API reference for LLMs
- [llms-full.txt](llms-full.txt) — Comprehensive documentation for LLMs
- [Source code](https://github.com/mikeckennedy/umami-python)
