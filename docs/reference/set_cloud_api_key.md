## set_cloud_api_key()


Authenticate against Umami Cloud with an API key instead of login().


Usage

``` python
set_cloud_api_key(
    key,
    region=None,
)
```


Enables "Cloud mode": data and management calls are routed to https://api.umami.is/v1 and authenticated with the 'x-umami-api-key' header, and events are sent to https://cloud.umami.is/api/send. You do not need to call set_url_base() or login() in this mode; Cloud mode and self-hosted/token mode are mutually exclusive. Call clear_cloud_api_key() to exit Cloud mode and return to self-hosted/token behavior.


## Parameters


`key: str`  
Your Umami Cloud API key.

`region: Optional[str] = None`  
Optional 'us' or 'eu' to pin the data region. Defaults to the region of the account that owns the key.


## Raises


`ValidationError`  
If key is empty or whitespace-only, or if region is provided but is not 'us' or 'eu'.


## Example

import umami

umami.set_cloud_api_key('your-cloud-api-key', region='us') umami.set_website_id('978435e2-7ba1-4337-9860-ec31ece2db60')
