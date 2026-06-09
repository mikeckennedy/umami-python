## set_hostname()


Set the default hostname used when sending events and page views.


Usage

``` python
set_hostname(hostname)
```


Used as the hostname for new_event(), new_revenue_event(), and new_page_view() when one is not passed explicitly. Individual calls can override it via their hostname parameter.


## Parameters


`hostname: str`  
The hostname to use when one is not specified (e.g. 'talkpython.fm').
