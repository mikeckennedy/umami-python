## new_event()


Creates a new custom event in Umami for the given website_id and hostname (both use the default


Usage

``` python
new_event(
    event_name,
    hostname=None,
    url="/",
    website_id=None,
    title=None,
    custom_data=None,
    referrer="",
    language="en-US",
    screen="1920x1080",
    ip_address=None,
    distinct_id=None
)
```


if you have set them with the other functions such as set_hostname()). These events will both appear in the traffic related to the specified url and in the events section at the bottom of your Umami website page. Login is not required for this method.


## Parameters


`event_name: str`  
The name of your custom event (e.g. Purchase-Course)

`hostname: Optional[str] = None`  
OPTIONAL: The value of your hostname simulating the client (e.g. test_domain.com), overrides set_hostname() value.

`url: str = ``"/"`  
The simulated URL for the custom event (e.g. if it's account creation, maybe /account/new)

`website_id: Optional[str] = None`  
OPTIONAL: The value of your website_id in Umami. (overrides set_website_id() value).

`title: Optional[str] = None`  
The title of the custom event (not sure how this is different from the name), defaults to event_name if empty.

`custom_data: Optional[Dict[str, Any]] = None`  
Any additional data to send along with the event. Not visible in the UI but is in the API.

`referrer: str = ``""`  
The referrer of the client if there is any (what location lead them to this event)

`language: str = ``"en-US"`  
The language of the event / client.

`screen: str = ``"1920x1080"`  
The screen resolution of the client.

`ip_address: Optional[str] = None`  
OPTIONAL: The true IP address of the user, used when handling requests in APIs, etc. on the server.

`distinct_id: Optional[Union[str, int]] = None`  
OPTIONAL: The Umami distinct ID for the user as a string or integer, sent to the API as payload field id. Blank or whitespace-only values are ignored (no id sent); booleans or other non-string/int types raise a ValidationError.
