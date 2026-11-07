## disable()


Disable event and page view tracking.


Usage

``` python
disable()
```


When disabled, the send functions new_event(), new_revenue_event(), and new_page_view() still validate their arguments but then return without making any HTTP request to Umami. This is useful for development and testing environments.

Only the send functions are affected; query and authentication functions (such as login(), websites(), website_stats(), active_users(), verify_token(), and heartbeat()) always run regardless of this setting. Call enable() to turn tracking back on (the default).


## Example

``` python
import umami

umami.set_url_base('https://umami.example.com')
umami.set_website_id('978435e2-7ba1-4337-9860-ec31ece2db60')
umami.set_hostname('example.com')
umami.disable()
umami.new_event(event_name='signup')  # validated, returns {}, no HTTP request
```
