## login_async()


Log into a self-hosted Umami instance and retrieve a temporary auth token.


Usage

``` python
login_async(
    username,
    password,
)
```


On success, the returned token is stored internally and used to authenticate subsequent data calls (websites_async(), website_stats_async(), active_users_async(), verify_token_async()). Tokens expire, so you may need to log in again; check validity with verify_token_async().

Requires set_url_base() to have been called first. This is the self-hosted/token authentication path and is not used in Cloud mode; in Cloud mode call set_cloud_api_key() instead.


## Parameters


`username: str`  
Your Umami username.

`password: str`  
Your Umami password.


## Returns


`models.LoginResponse`  
A models.LoginResponse containing the auth token and the logged-in

user's details. You do not need to store this yourself; the token is

retained internally.


## Raises


`OperationNotAllowedError`  
If Cloud mode is active (set_cloud_api_key() was called), or if set_url_base() has not been called.

`ValidationError`  
If username or password is empty.

`httpx.HTTPStatusError`  
If the server returns a non-2xx response, e.g. on invalid credentials.


## Example

import umami

umami.set_url_base('https://umami.example.com') login = await umami.login_async('admin', 'super-secret')
