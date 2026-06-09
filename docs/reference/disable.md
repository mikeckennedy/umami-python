## disable()


Disable event and page view tracking.


Usage

``` python
disable()
```


When disabled, the send functions new_event(), new_revenue_event(), and new_page_view() still validate their arguments but then return without making any HTTP request to Umami. This is useful for development and testing environments.

Only the send functions are affected; query and authentication functions (such as login(), websites(), website_stats(), active_users(), verify_token(), and heartbeat()) always run regardless of this setting. Call enable() to turn tracking back on (the default).
