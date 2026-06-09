## enable()


Enable event and page view tracking.


Usage

``` python
enable()
```


When enabled, the send functions new_event(), new_revenue_event(), and new_page_view() send data to Umami normally. This is the default state.

Only the send functions are affected; query and authentication functions (such as login(), websites(), website_stats(), active_users(), verify_token(), and heartbeat()) always run regardless of this setting. Call disable() to turn tracking off.
