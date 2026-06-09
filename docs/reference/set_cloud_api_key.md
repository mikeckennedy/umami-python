## set_cloud_api_key()


Authenticate against Umami Cloud with an API key instead of login().


Usage

``` python
set_cloud_api_key(
    key,
    region=None,
)
```


Enables "Cloud mode": data/management calls are routed to https://api.umami.is/v1 and authenticated with the `x-umami-api-key` header, and events are sent to https://cloud.umami.is/api/send. You do NOT need to call set_url_base() or login() in this mode.


## Parameters


`key: str`  
Your Umami Cloud API key.

`region: Optional[str] = None`  
Optional 'us' or 'eu' to pin the data region. Defaults to the region of the account that owns the key.
