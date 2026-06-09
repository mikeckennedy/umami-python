## new_page_view_async()


Creates a new page view event in Umami for the given website_id and hostname (both use the default


Usage

``` python
new_page_view_async(
    page_title,
    url,
    hostname=None,
    website_id=None,
    referrer="",
    language="en-US",
    screen="1920x1080",
    ua=event_user_agent,
    ip_address=None,
    distinct_id=None
)
```


if you have set them with the other functions such as set_hostname()). This is equivalent to what happens when a visit views a page and the JS library records it.


## Parameters


`page_title: str`  
The title of the page view to record (required).

`url: str`  
The simulated URL for the custom event (e.g. if it's account creation, maybe /account/new)

`hostname: Optional[str] = None`  
OPTIONAL: The value of your hostname simulating the client (e.g. test_domain.com), overrides set_hostname() value.

`website_id: Optional[str] = None`  
OPTIONAL: The value of your website_id in Umami. (overrides set_website_id() value).

`referrer: str = ``""`  
OPTIONAL: The referrer of the client if there is any (what location lead them to this event)

`language: str = ``"en-US"`  
OPTIONAL: The language of the event / client.

`screen: str = ``"1920x1080"`  
OPTIONAL: The screen resolution of the client.

`ua: str = event_user_agent`    
OPTIONAL: The UserAgent resolution of the client. Note umami blocks non browsers by default.

`ip_address: Optional[str] = None`  
OPTIONAL: The true IP address of the user, used when handling requests in APIs, etc. on the server.

`distinct_id: Optional[Union[str, int]] = None`  
OPTIONAL: The Umami distinct ID for the user as a string or integer, sent to the API as payload field id. Blank or whitespace-only values are ignored (no id sent); booleans or other non-string/int types raise a ValidationError.
