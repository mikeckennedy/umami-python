## new_event_async()


Create a new custom event in Umami for the given website_id and hostname


Usage

``` python
new_event_async(
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


(both fall back to the defaults set via set_website_id() and set_hostname() when omitted). The event appears in the traffic for the given url and in the events section of your Umami website page. Login is not required; you only need set_url_base() (self-hosted) or set_cloud_api_key() (Cloud), plus a website_id and hostname.

If tracking has been turned off with disable(), the inputs are still validated but no HTTP request is made and an empty dict is returned.


## Parameters


`event_name: str`  
The name of your custom event (e.g. 'Purchase-Course').

`hostname: Optional[str] = None`  
Optional hostname identifying the client (e.g. 'test_domain.com'); overrides the set_hostname() value.

`url: str = ``"/"`  
The URL associated with the event (e.g. '/account/new'). Defaults to '/'.

`website_id: Optional[str] = None`  
Optional Umami website ID; overrides the set_website_id() value.

`title: Optional[str] = None`  
The display title of the event. Defaults to event_name when omitted.

`custom_data: Optional[Dict[str, Any]] = None`  
Additional key/value data sent with the event. Not shown in the UI but available through the API. Defaults to an empty dict.

`referrer: str = ``""`  
The referrer of the client, if any. Defaults to ''.

`language: str = ``"en-US"`  
The language of the event/client. Defaults to 'en-US'.

`screen: str = ``"1920x1080"`  
The screen resolution of the client. Defaults to '1920x1080'.

`ip_address: Optional[str] = None`  
Optional true IP address of the user, useful when sending events from server-side request handlers.

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

umami.set_url_base('https://umami.example.com') umami.set_website_id('978435e2-7ba1-4337-9860-ec31ece2db60') umami.set_hostname('example.com') await umami.new_event_async( event_name='Purchase-Course', url='/checkout', custom_data={'plan': 'pro'}, )
