## is_logged_in()


Whether a credential is currently set locally.


Usage

``` python
is_logged_in()
```


## Returns


`bool`  
True if a self-hosted login token (set by login()) or an Umami Cloud

API key (set by set_cloud_api_key()) is present, False otherwise. This

only reflects that a credential exists in this process, not that it is

still valid on the server -- use verify_token() to confirm validity.
