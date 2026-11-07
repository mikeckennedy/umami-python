## clear_cloud_api_key()


Exit Cloud mode and return to self-hosted/token behavior.


Usage

``` python
clear_cloud_api_key()
```


Clears the API key and region set by set_cloud_api_key(). After calling this, self-hosted operations again require set_url_base() and login(). A token from an earlier login() is kept, so if you logged in before switching to Cloud mode you do not need to log in again.


## Example

``` python
import umami

umami.set_cloud_api_key('your-cloud-api-key')
# ... later, go back to a self-hosted instance:
umami.clear_cloud_api_key()
umami.set_url_base('https://umami.example.com')
umami.login('admin', 'super-secret')
```
