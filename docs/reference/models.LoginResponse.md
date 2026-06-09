## models.LoginResponse


The result of authenticating against a self-hosted Umami instance.


Usage

``` python
models.LoginResponse()
```


Returned by login() / login_async(). The SDK stores the token internally after a successful login, so you typically do not need to read it yourself. Not used in Umami Cloud mode (set_cloud_api_key()), where the API key is the credential.


## Attributes


`token: str`  
The bearer token used to authenticate subsequent data and management calls.

`user: User`  
The authenticated User account details.
