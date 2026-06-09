## website_stats_async()


Retrieves the statistics for a specific website.


Usage

``` python
website_stats_async(
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


## Parameters


`start_at: datetime`  
Starting date as a datetime object.

`end_at: datetime`  
End date as a datetime object.

`website_id: Optional[str] = None`  
OPTIONAL: The value of your website_id in Umami. (overrides set_website_id() value).

`url: Optional[str] = None`  
OPTIONAL: Name of URL.

`referrer: Optional[str] = None`  
OPTIONAL: Name of referrer.

`title: Optional[str] = None`  
OPTIONAL: Name of page title.

`query: Optional[str] = None`  
OPTIONAL: Name of query.

`event: Optional[str] = None`  
OPTIONAL: Name of event.

`host: Optional[str] = None`  
OPTIONAL: Name of hostname.

`os: Optional[str] = None`  
OPTIONAL: Name of operating system.

`browser: Optional[str] = None`  
OPTIONAL: Name of browser.

`device: Optional[str] = None`  
OPTIONAL: Name of device (ex. Mobile)

`country: Optional[str] = None`  
OPTIONAL: Name of country.

`region: Optional[str] = None`  
OPTIONAL: Name of region/state/province.

`city: Optional[str] = None`  
OPTIONAL: Name of city.


## Returns


`models.WebsiteStats`  
A WebsiteStatsResponse model containing the website statistics data.
