## models.WebsiteStatsCmp


Prior-period comparison totals for a website's statistics.


Usage

``` python
models.WebsiteStatsCmp()
```


Appears as the optional comparison attribute of WebsiteStats (returned by website_stats() / website_stats_async()), holding the same totals for the preceding period so they can be compared against the current period.


## Attributes


`pageviews: int`  
Number of page views in the comparison period.

`visitors: int`  
Number of unique visitors in the comparison period.

`visits: int`  
Number of sessions in the comparison period.

`bounces: int`  
Number of single-page sessions in the comparison period.

`totaltime: int`  
Total engagement time in seconds for the comparison period.
