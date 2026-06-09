## active_users()


Retrieves the number of currently-active visitors for a specific website.


Usage

``` python
active_users(website_id=None)
```


Requires authentication: call login() (self-hosted) or set_cloud_api_key() (Umami Cloud) first.


## Parameters


`website_id: Optional[str] = None`  
OPTIONAL: The value of your website_id in Umami (overrides the set_website_id() value).


## Returns


`int`  
The count of visitors currently active on the website.


## Raises


`OperationNotAllowedError`  
If set_url_base() has not been called (and no Cloud API key is set), or if no credential is present (neither a login token nor a Cloud API key).

`httpx.HTTPStatusError`  
If the Umami API returns a non-2xx response.
