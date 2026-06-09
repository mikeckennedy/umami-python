## models.User


An authenticated Umami user account.


Usage

``` python
models.User()
```


Returned as the user attribute of the LoginResponse from login() / login_async() (self-hosted/token mode). It is not returned directly by any public function.


## Attributes


`id: str`  
The user's unique identifier.

`username: str`  
The login username.

`role: str`  
The account role (e.g. 'admin', 'user').

`createdAt: str`  
ISO 8601 timestamp of when the account was created.

`isAdmin: bool`  
True if the account has administrator privileges.
