## website_stats()


Retrieves the statistics for a specific website over a date range.


Usage

``` python
website_stats(
    start_at,
    end_at,
    website_id=None,
    url=None,
    referrer=None,
    title=None,
    query=None,
    event=None,
    host=None,
    os=None,
    browser=None,
    device=None,
    country=None,
    region=None,
    city=None
)
```


Requires authentication: call login() (self-hosted) or set_cloud_api_key() (Umami Cloud) first. start_at and end_at are converted to epoch milliseconds for the API.


## Parameters


`start_at: datetime`  
Start of the date range as a datetime object.

`end_at: datetime`  
End of the date range as a datetime object.

`website_id: Optional[str] = None`  
OPTIONAL: The value of your website_id in Umami (overrides the set_website_id() value).

`url: Optional[str] = None`  
OPTIONAL: Filter by URL path.

`referrer: Optional[str] = None`  
OPTIONAL: Filter by referrer.

`title: Optional[str] = None`  
OPTIONAL: Filter by page title.

`query: Optional[str] = None`  
OPTIONAL: Filter by query string.

`event: Optional[str] = None`  
OPTIONAL: Filter by event name.

`host: Optional[str] = None`  
OPTIONAL: Filter by hostname.

`os: Optional[str] = None`  
OPTIONAL: Filter by operating system.

`browser: Optional[str] = None`  
OPTIONAL: Filter by browser.

`device: Optional[str] = None`  
OPTIONAL: Filter by device (e.g. 'Mobile').

`country: Optional[str] = None`  
OPTIONAL: Filter by country.

`region: Optional[str] = None`  
OPTIONAL: Filter by region/state/province.

`city: Optional[str] = None`  
OPTIONAL: Filter by city.


## Returns


`models.WebsiteStats`  
A models.WebsiteStats with the aggregated pageviews, visitors, visits,

bounces, and totaltime for the range, plus an optional comparison.


## Raises


`OperationNotAllowedError`  
If set_url_base() has not been called (and no Cloud API key is set), or if no credential is present (neither a login token nor a Cloud API key).

`httpx.HTTPStatusError`  
If the Umami API returns a non-2xx response.


## Example

``` python
import datetime
import umami

umami.set_url_base('https://umami.example.com')
umami.login(username, password)
stats = umami.website_stats(
    start_at=datetime.datetime.now() - datetime.timedelta(days=7),
    end_at=datetime.datetime.now(),
)
print(stats.pageviews, stats.visitors)
```
