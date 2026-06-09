## verify_token_async()


Verifies that the token set when you called login() is still valid. Umami says this token will expire,


Usage

``` python
verify_token_async(check_server=True)
```


but I'm not sure if that's minutes, hours, or years.


## Parameters


`check_server: bool = ``True`  
If true, we will contact the server and verify that the token is valid. If false, this only checks that an auth token has been stored from a previous successful login.


## Returns


`bool`  
True if the token is still valid, False otherwise.
