## login_async()


Logs into Umami and retrieves a temporary auth token. If the token is expired,


Usage

``` python
login_async(
    username,
    password,
)
```


you'll need to log in again. This can be checked with verify_token(). Args: username: Your Umami username password: Your Umami password


## Returns


`models.LoginResponse`  
LoginResponse object which your token and user details (no need to save this).
