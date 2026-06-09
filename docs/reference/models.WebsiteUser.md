## models.WebsiteUser


A minimal reference to the user who owns or created a website.


Usage

``` python
models.WebsiteUser()
```


Appears as the user attribute (and, for team-website listings, the createUser attribute) of a Website returned by websites() / websites_async().


## Attributes


`username: str`  
The referenced user's login username.

`id: str`  
The referenced user's unique identifier.
