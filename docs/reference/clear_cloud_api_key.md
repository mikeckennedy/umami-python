## clear_cloud_api_key()


Exit Cloud mode and return to self-hosted/token behavior.


Usage

``` python
clear_cloud_api_key()
```


Clears the API key and region set by set_cloud_api_key(). After calling this, self-hosted operations again require set_url_base() and login().
