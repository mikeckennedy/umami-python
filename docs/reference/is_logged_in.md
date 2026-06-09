## is_logged_in()


Whether a credential is currently set locally.


Usage

``` python
is_logged_in()
```


## Returns


`bool`  
True if a self-hosted login token or an Umami Cloud API key has been set, False otherwise.

This only reflects that a credential exists in this process, not that it is still valid on

the server -- use verify_token() to confirm validity.
