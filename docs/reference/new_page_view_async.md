## new_page_view_async()


Create a new page view event in Umami for the given website_id and hostname


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


(both fall back to the defaults set via set_website_id() and set_hostname() when omitted). This is equivalent to what happens when a visitor views a page and the JS library records it.

Requires set_url_base() (or set_cloud_api_key() for Cloud mode) and a website_id and hostname, either set globally via set_website_id()/set_hostname() or passed here. Login is not required to send page views. If tracking has been turned off with disable(), the input is validated but no HTTP request is made and an empty dict is returned.


## Parameters


`page_title: str`  
The title of the page view to record (required).

`url: str`  
The URL of the page view to record (e.g. '/account/new').

`hostname: Optional[str] = None`  
Optional hostname identifying the client (e.g. 'example.com'); overrides the set_hostname() value.

`website_id: Optional[str] = None`  
Optional Umami website ID; overrides the set_website_id() value.

`referrer: str = ``""`  
Optional referrer of the client, if any (the location that led them to this page). Defaults to ''.

`language: str = ``"en-US"`  
Optional language of the event/client. Defaults to 'en-US'.

`screen: str = ``"1920x1080"`  
Optional screen resolution of the client. Defaults to '1920x1080'.

`ua: str = event_user_agent`    
Optional user-agent string of the client. Defaults to a browser user-agent because Umami blocks non-browser user agents by default.

`ip_address: Optional[str] = None`  
Optional true IP address of the user, useful when sending page views from server-side request handlers.

`distinct_id: Optional[Union[str, int]] = None`  
Optional Umami distinct ID for the user, as a string or integer, sent to the API as the payload field 'id'. Blank or whitespace-only values are ignored (no id is sent).


## Returns


`dict`  
The JSON response from the Umami API as a dict, or an empty dict if

tracking is disabled.


## Raises


`OperationNotAllowedError`  
If neither set_url_base() nor set_cloud_api_key() has been called.

`ValidationError`  
If hostname or website_id is not set (here or via set_hostname()/set_website_id()), or if distinct_id is a bool or any type other than str or int.

`httpx.HTTPStatusError`  
If Umami returns a non-2xx response (only when tracking is enabled).


## Example

import umami

umami.set_url_base('https://umami.example.com') umami.set_website_id('978435e2-7ba1-4337-9860-ec31ece2db60') umami.set_hostname('example.com') await umami.new_page_view_async(page_title='Home', url='/')
