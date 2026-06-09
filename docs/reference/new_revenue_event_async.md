## new_revenue_event_async()


Create a new revenue event in Umami. This is a convenience wrapper around


Usage

``` python
new_revenue_event_async(
    revenue,
    currency="USD",
    event_name="revenue",
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


new_event_async() that automatically includes the revenue and currency properties required by Umami's revenue tracking.

Requires set_url_base() (or set_cloud_api_key() for Cloud mode) and a website_id and hostname, either set globally via set_website_id()/set_hostname() or passed here. Login is not required to send events. If tracking has been turned off with disable(), the inputs are still validated but no HTTP request is made and an empty dict is returned.


## Parameters


`revenue: float`  
The monetary amount of the transaction. Must be a number (int or float) \>= 0.

`currency: str = ``"USD"`  
ISO 4217 currency code (e.g. 'USD', 'EUR'). Must be non-empty. Defaults to 'USD'.

`event_name: str = ``"revenue"`  
The name of your custom event. Defaults to 'revenue'.

`hostname: Optional[str] = None`  
Optional hostname identifying the client (e.g. 'example.com'); overrides the set_hostname() value.

`url: str = ``"/"`  
The URL associated with the event (e.g. '/checkout'). Defaults to '/'.

`website_id: Optional[str] = None`  
Optional Umami website ID; overrides the set_website_id() value.

`title: Optional[str] = None`  
The display title of the event. Defaults to event_name when omitted.

`custom_data: Optional[Dict[str, Any]] = None`  
Additional key/value data sent with the event. The 'revenue' and 'currency' keys are overwritten by the values above.

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
The parsed JSON response from the Umami API as a dict, or an empty dict

if tracking is disabled.


## Raises


`ValidationError`  
If revenue is not a number, revenue is negative, currency is empty, distinct_id is an invalid type, or hostname or website_id is not set (here or via set_hostname()/set_website_id()).

`OperationNotAllowedError`  
If neither set_url_base() nor set_cloud_api_key() has been called.

`httpx.HTTPStatusError`  
If the Umami API returns a non-2xx response.


## Example

import umami

umami.set_url_base('https://umami.example.com') umami.set_website_id('978435e2-7ba1-4337-9860-ec31ece2db60') umami.set_hostname('example.com') await umami.new_revenue_event_async( revenue=19.99, currency='USD', event_name='checkout-cart', url='/checkout', )
