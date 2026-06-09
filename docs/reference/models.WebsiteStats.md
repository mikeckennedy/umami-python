## models.WebsiteStats


Aggregate traffic statistics for a website over a time range.


Usage

``` python
models.WebsiteStats()
```


Returned by website_stats() / website_stats_async() for the requested start/end window and optional filters.


## Attributes


`pageviews: int`  
Total number of page views.

`visitors: int`  
Number of unique visitors.

`visits: int`  
Number of sessions.

`bounces: int`  
Number of single-page sessions.

`totaltime: int`  
Total engagement time in seconds.

`comparison: typing.Optional[WebsiteStatsCmp]`  
Prior-period totals as a WebsiteStatsCmp, or None when the API does not return a comparison block.
