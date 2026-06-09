# API Reference


The public umami-analytics surface: configuration, authentication, sending events, and querying stats. Every network operation has a synchronous function and an identically-signed `_async` twin.


## Configuration


One-time setup. `set_url_base()` is required before any operation; Cloud users call `set_cloud_api_key()` instead.


[set_url_base()](set_url_base.md#umami.set_url_base)  
Each Umami instance lives somewhere. This is where yours lives.

[set_website_id()](set_website_id.md#umami.set_website_id)  
Your Umami instance might have many websites registered for various domains you use.

[set_hostname()](set_hostname.md#umami.set_hostname)  
The default hostname for sending events (can be overriden in the new_event() function).

[set_cloud_api_key()](set_cloud_api_key.md#umami.set_cloud_api_key)  
Authenticate against Umami Cloud with an API key instead of login().

[clear_cloud_api_key()](clear_cloud_api_key.md#umami.clear_cloud_api_key)  
Exit Cloud mode and return to token/self-hosted behavior.

[enable()](enable.md#umami.enable)  
Enable event and page view tracking.

[disable()](disable.md#umami.disable)  
Disable event and page view tracking.


## Authentication


Required for the query endpoints and `verify_token`. Not needed to send events.


[login()](login.md#umami.login)  
Logs into Umami and retrieves a temporary auth token. If the token is expired,

[login_async()](login_async.md#umami.login_async)  
Logs into Umami and retrieves a temporary auth token. If the token is expired,

[is_logged_in()](is_logged_in.md#umami.is_logged_in)  
Whether a credential is currently set locally.

[verify_token()](verify_token.md#umami.verify_token)  
Verifies that the token set when you called login() is still valid. Umami says this token will expire,

[verify_token_async()](verify_token_async.md#umami.verify_token_async)  
Verifies that the token set when you called login() is still valid. Umami says this token will expire,


## Sending events


Send custom events, revenue, and page views. No login required -- only a URL base and a website id/hostname.


[new_event()](new_event.md#umami.new_event)  
Creates a new custom event in Umami for the given website_id and hostname (both use the default

[new_event_async()](new_event_async.md#umami.new_event_async)  
Creates a new custom event in Umami for the given website_id and hostname (both use the default

[new_revenue_event()](new_revenue_event.md#umami.new_revenue_event)  
Creates a new revenue event in Umami. This is a convenience wrapper around new_event()

[new_revenue_event_async()](new_revenue_event_async.md#umami.new_revenue_event_async)  
Creates a new revenue event in Umami. This is a convenience wrapper around new_event_async()

[new_page_view()](new_page_view.md#umami.new_page_view)  
Creates a new page view event in Umami for the given website_id and hostname (both use the default

[new_page_view_async()](new_page_view_async.md#umami.new_page_view_async)  
Creates a new page view event in Umami for the given website_id and hostname (both use the default


## Querying stats


Read analytics back out. Requires login (or a Cloud API key).


[websites()](websites.md#umami.websites)  
All the websites that are registered in your Umami instance.

[websites_async()](websites_async.md#umami.websites_async)  
All the websites that are registered in your Umami instance.

[website_stats()](website_stats.md#umami.website_stats)  
Retrieves the statistics for a specific website.

[website_stats_async()](website_stats_async.md#umami.website_stats_async)  
Retrieves the statistics for a specific website.

[active_users()](active_users.md#umami.active_users)  
Retrieves the active users for a specific website.

[active_users_async()](active_users_async.md#umami.active_users_async)  
Retrieves the active users for a specific website.


## Health


Check Umami server connectivity.


[heartbeat()](heartbeat.md#umami.heartbeat)  
Verifies that the server is reachable via the internet and is healthy.

[heartbeat_async()](heartbeat_async.md#umami.heartbeat_async)  
Verifies that the server is reachable via the internet and is healthy.


## Response models


Pydantic models returned by the query functions.


[models.WebsitesResponse](models.WebsitesResponse.md#umami.models.WebsitesResponse)  

[models.Website](models.Website.md#umami.models.Website)  

[models.WebsiteStats](models.WebsiteStats.md#umami.models.WebsiteStats)  

[models.WebsiteStatsCmp](models.WebsiteStatsCmp.md#umami.models.WebsiteStatsCmp)  

[models.LoginResponse](models.LoginResponse.md#umami.models.LoginResponse)  

[models.User](models.User.md#umami.models.User)  

[models.WebsiteUser](models.WebsiteUser.md#umami.models.WebsiteUser)  


## Errors


Exception hierarchy. `ValidationError` is the base; `OperationNotAllowedError` is raised when required state (url_base, login) is missing.


[errors.ValidationError](errors.ValidationError.md#umami.errors.ValidationError)  

[errors.OperationNotAllowedError](errors.OperationNotAllowedError.md#umami.errors.OperationNotAllowedError)
