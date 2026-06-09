## errors.OperationNotAllowedError


Raised when the SDK is missing required state for an operation.


Usage

``` python
errors.OperationNotAllowedError()
```


A subclass of ValidationError. It signals that prerequisite configuration has not been completed, for example calling an operation before set_url_base() in self-hosted mode, querying data before login(), or calling login() while a Cloud API key is configured (login() is not used in Cloud mode).

Resolve it by calling the appropriate setup function first: set_url_base() and login() for self-hosted mode, or set_cloud_api_key() for Umami Cloud.
