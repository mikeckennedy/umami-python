## verify_token_async()


Verify that the currently stored credential is still valid.


Usage

``` python
verify_token_async(check_server=True)
```


In self-hosted/token mode this checks the auth token obtained from login(); in Cloud mode it checks the API key set via set_cloud_api_key(). Tokens issued by login() are temporary and eventually expire, after which you must log in again.

This function never raises: any error (network failure, missing credential, expired or rejected token, non-2xx response) results in a return value of False.


## Parameters


`check_server: bool = ``True`  
If True (default), contact the server to confirm the credential is valid -- self-hosted posts to /api/auth/verify, while Cloud mode fetches /api/me. If False, perform only a local check (equivalent to is_logged_in()) with no network request.


## Returns


`bool`  
True if the credential is valid (or, when check_server is False, simply

present), False otherwise.
