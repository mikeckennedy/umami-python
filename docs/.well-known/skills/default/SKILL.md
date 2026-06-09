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

- `set_url_base`: Each Umami instance lives somewhere. This is where yours lives
- `set_website_id`: Your Umami instance might have many websites registered for various domains you use
- `set_hostname`: The default hostname for sending events (can be overriden in the new_event() function)
- `set_cloud_api_key`: Authenticate against Umami Cloud with an API key instead of login()
- `clear_cloud_api_key`: Exit Cloud mode and return to token/self-hosted behavior
- `enable`: Enable event and page view tracking
- `disable`: Disable event and page view tracking

### Authentication

Required for the query endpoints and `verify_token`. Not needed to send events.

- `login`: Logs into Umami and retrieves a temporary auth token. If the token is expired,
- `login_async`: Logs into Umami and retrieves a temporary auth token. If the token is expired,
- `is_logged_in`: Whether a credential is currently set locally
- `verify_token`: Verifies that the token set when you called login() is still valid. Umami says this token will expire,
- `verify_token_async`: Verifies that the token set when you called login() is still valid. Umami says this token will expire,

### Sending events

Send custom events, revenue, and page views. No login required — only a URL base and a website id/hostname.

- `new_event`: Creates a new custom event in Umami for the given website_id and hostname (both use the default
- `new_event_async`: Creates a new custom event in Umami for the given website_id and hostname (both use the default
- `new_revenue_event`: Creates a new revenue event in Umami. This is a convenience wrapper around new_event()
- `new_revenue_event_async`: Creates a new revenue event in Umami. This is a convenience wrapper around new_event_async()
- `new_page_view`: Creates a new page view event in Umami for the given website_id and hostname (both use the default
- `new_page_view_async`: Creates a new page view event in Umami for the given website_id and hostname (both use the default

### Querying stats

Read analytics back out. Requires login (or a Cloud API key).

- `websites`: All the websites that are registered in your Umami instance
- `websites_async`: All the websites that are registered in your Umami instance
- `website_stats`: Retrieves the statistics for a specific website
- `website_stats_async`: Retrieves the statistics for a specific website
- `active_users`: Retrieves the active users for a specific website
- `active_users_async`: Retrieves the active users for a specific website

### Health

Check Umami server connectivity.

- `heartbeat`: Verifies that the server is reachable via the internet and is healthy
- `heartbeat_async`: Verifies that the server is reachable via the internet and is healthy

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
