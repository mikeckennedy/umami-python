## heartbeat()


Check whether the configured Umami server is reachable and healthy.


Usage

``` python
heartbeat()
```


In self-hosted mode this issues a GET to {url_base}/api/heartbeat. In Cloud mode (after set_cloud_api_key()), Umami Cloud has no /api/heartbeat endpoint, so this performs an authenticated GET on the /me endpoint as a liveness check instead.

Requires set_url_base() (self-hosted) or set_cloud_api_key() (Cloud) to have been called first; login() is not required. This function never raises: any failure (missing configuration, connection error, or a non-2xx response) is caught and reported as False.


## Returns


`bool`  
True if the server is reachable and responded successfully; False on

any error, including when no url_base or Cloud API key has been

configured.


## Example

import umami

umami.set_url_base('https://umami.example.com') if not umami.heartbeat(): print('Umami is unavailable')
