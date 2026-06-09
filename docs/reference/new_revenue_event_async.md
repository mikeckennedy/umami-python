## new_revenue_event_async()


Creates a new revenue event in Umami. This is a convenience wrapper around new_event_async()


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


that automatically includes the revenue and currency properties required by Umami's revenue tracking.


## Parameters


`revenue: float`  
The monetary amount of the transaction (must be \>= 0).

`currency: str = ``"USD"`  
ISO 4217 currency code (e.g. 'USD', 'EUR'). Defaults to 'USD'.

`event_name: str = ``"revenue"`  
The name of your custom event. Defaults to 'revenue'.

`hostname: Optional[str] = None`  
OPTIONAL: The value of your hostname simulating the client, overrides set_hostname() value.

`url: str = ``"/"`  
The simulated URL for the custom event.

`website_id: Optional[str] = None`  
OPTIONAL: The value of your website_id in Umami (overrides set_website_id() value).

`title: Optional[str] = None`  
The title of the custom event, defaults to event_name if empty.

`custom_data: Optional[Dict[str, Any]] = None`  
Any additional data to send along with the event. Revenue and currency keys will be overwritten.

`referrer: str = ``""`  
The referrer of the client if there is any.

`language: str = ``"en-US"`  
The language of the event / client.

`screen: str = ``"1920x1080"`  
The screen resolution of the client.

`ip_address: Optional[str] = None`  
OPTIONAL: The true IP address of the user.

`distinct_id: Optional[Union[str, int]] = None`  
OPTIONAL: The Umami distinct ID for the user as a string or integer, sent to the API as payload field id. Blank or whitespace-only values are ignored (no id sent); booleans or other non-string/int types raise a ValidationError.


## Returns


`dict`  
The data returned from the Umami API.
