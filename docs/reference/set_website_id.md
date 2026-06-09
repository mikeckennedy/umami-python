## set_website_id()


Set the default website ID used for subsequent calls.


Usage

``` python
set_website_id(website_id)
```


An Umami instance can have many registered websites. Call this once to choose which website later calls (new_event(), new_page_view(), website_stats(), active_users()) target by default. Individual calls can override it via their website_id parameter.


## Parameters


`website_id: str`  
The website ID from Umami for your registered site (e.g. '978435e2-7ba1-4337-9860-ec31ece2db60').
