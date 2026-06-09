# API Reference


The public umami-analytics surface: configuration, authentication, sending events, and querying stats. Every network operation has a synchronous function and an identically-signed `_async` twin.


## Configuration


One-time setup. `set_url_base()` is required before any operation; Cloud users call `set_cloud_api_key()` instead.


[set_url_base()](set_url_base.md#umami.set_url_base)  
Set the base URL of your self-hosted Umami instance.

[set_website_id()](set_website_id.md#umami.set_website_id)  
Set the default website ID used for subsequent calls.

[set_hostname()](set_hostname.md#umami.set_hostname)  
Set the default hostname used when sending events and page views.

[set_cloud_api_key()](set_cloud_api_key.md#umami.set_cloud_api_key)  
Authenticate against Umami Cloud with an API key instead of login().

[clear_cloud_api_key()](clear_cloud_api_key.md#umami.clear_cloud_api_key)  
Exit Cloud mode and return to self-hosted/token behavior.

[enable()](enable.md#umami.enable)  
Enable event and page view tracking.

[disable()](disable.md#umami.disable)  
Disable event and page view tracking.


## Authentication


Required for the query endpoints and `verify_token`. Not needed to send events.


[login()](login.md#umami.login)  
Log into a self-hosted Umami instance and retrieve a temporary auth token.

[login_async()](login_async.md#umami.login_async)  
Log into a self-hosted Umami instance and retrieve a temporary auth token.

[is_logged_in()](is_logged_in.md#umami.is_logged_in)  
Whether a credential is currently set locally.

[verify_token()](verify_token.md#umami.verify_token)  
Verify that the currently stored credential is still valid.

[verify_token_async()](verify_token_async.md#umami.verify_token_async)  
Verify that the currently stored credential is still valid.


## Sending events


Send custom events, revenue, and page views. No login required -- only a URL base and a website id/hostname.


[new_event()](new_event.md#umami.new_event)  
Create a new custom event in Umami for the given website_id and hostname

[new_event_async()](new_event_async.md#umami.new_event_async)  
Create a new custom event in Umami for the given website_id and hostname

[new_revenue_event()](new_revenue_event.md#umami.new_revenue_event)  
Create a new revenue event in Umami. This is a convenience wrapper around

[new_revenue_event_async()](new_revenue_event_async.md#umami.new_revenue_event_async)  
Create a new revenue event in Umami. This is a convenience wrapper around

[new_page_view()](new_page_view.md#umami.new_page_view)  
Create a new page view event in Umami for the given website_id and hostname

[new_page_view_async()](new_page_view_async.md#umami.new_page_view_async)  
Create a new page view event in Umami for the given website_id and hostname


## Querying stats


Read analytics back out. Requires login (or a Cloud API key).


[websites()](websites.md#umami.websites)  
All the websites that are registered in your Umami instance.

[websites_async()](websites_async.md#umami.websites_async)  
All the websites that are registered in your Umami instance.

[website_stats()](website_stats.md#umami.website_stats)  
Retrieves the statistics for a specific website over a date range.

[website_stats_async()](website_stats_async.md#umami.website_stats_async)  
Retrieves the statistics for a specific website over a date range.

[active_users()](active_users.md#umami.active_users)  
Retrieves the number of currently-active visitors for a specific website.

[active_users_async()](active_users_async.md#umami.active_users_async)  
Retrieves the number of currently-active visitors for a specific website.


## Health


Check Umami server connectivity.


[heartbeat()](heartbeat.md#umami.heartbeat)  
Check whether the configured Umami server is reachable and healthy.

[heartbeat_async()](heartbeat_async.md#umami.heartbeat_async)  
Check whether the configured Umami server is reachable and healthy.


## Response models


Pydantic models returned by the query functions.


[models.WebsitesResponse](models.WebsitesResponse.md#umami.models.WebsitesResponse)  
The paged envelope returned by the Umami /api/websites endpoint.

[models.Website](models.Website.md#umami.models.Website)  
A website registered in your Umami instance.

[models.WebsiteStats](models.WebsiteStats.md#umami.models.WebsiteStats)  
Aggregate traffic statistics for a website over a time range.

[models.WebsiteStatsCmp](models.WebsiteStatsCmp.md#umami.models.WebsiteStatsCmp)  
Prior-period comparison totals for a website's statistics.

[models.LoginResponse](models.LoginResponse.md#umami.models.LoginResponse)  
The result of authenticating against a self-hosted Umami instance.

[models.User](models.User.md#umami.models.User)  
An authenticated Umami user account.

[models.WebsiteUser](models.WebsiteUser.md#umami.models.WebsiteUser)  
A minimal reference to the user who owns or created a website.


## Errors


Exception hierarchy. `ValidationError` is the base; `OperationNotAllowedError` is raised when required state (url_base, login) is missing.


[errors.ValidationError](errors.ValidationError.md#umami.errors.ValidationError)  
Base exception raised when an input or argument fails validation.

[errors.OperationNotAllowedError](errors.OperationNotAllowedError.md#umami.errors.OperationNotAllowedError)  
Raised when the SDK is missing required state for an operation.
