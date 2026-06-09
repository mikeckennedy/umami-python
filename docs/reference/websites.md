## websites()


All the websites that are registered in your Umami instance.


Usage

``` python
websites()
```


Requires authentication: call login() (self-hosted) or set_cloud_api_key() (Umami Cloud) first. In self-hosted mode you must also have called set_url_base().


## Returns


`list[models.Website]`  
A list of models.Website models, unwrapped from the paged API response.


## Raises


`OperationNotAllowedError`  
If set_url_base() has not been called (and no Cloud API key is set), or if no credential is present (neither a login token nor a Cloud API key).

`httpx.HTTPStatusError`  
If the Umami API returns a non-2xx response.


## Example

``` python
import umami

umami.set_url_base('https://umami.example.com')
umami.login(username, password)
for site in umami.websites():
    print(site.name, site.domain)
```
