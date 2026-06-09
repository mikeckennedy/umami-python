## set_url_base()


Set the base URL of your self-hosted Umami instance.


Usage

``` python
set_url_base(url)
```


Required before any self-hosted operation (login, sending events, or querying stats). Provide the root URL of your instance without the trailing '/api', for example 'https://analytics.example.com'. A trailing slash is stripped automatically. Use this together with login() for self-hosted/token mode; do not combine it with set_cloud_api_key(), which selects Umami Cloud mode instead.


## Parameters


`url: str`  
The base URL of your instance, without '/api'. Must start with 'http://' or 'https://'.


## Raises


`ValidationError`  
If url is empty or whitespace-only, or if it does not start with 'http://' or 'https://'.
