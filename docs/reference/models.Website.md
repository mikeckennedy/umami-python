## models.Website


A website registered in your Umami instance.


Usage

``` python
models.Website()
```


Returned as the elements of the list from websites() / websites_async(). Many fields are optional or may be null depending on the endpoint and the website's configuration.


## Note

The personal websites listing populates user and userId. The team-website listing (GET /api/teams/:id/websites) instead populates createUser and leaves userId null.


## Attributes


`id: str`  
The website's unique identifier (use this as the website_id elsewhere).

`name: typing.Optional[str]`  
The display name of the website, if set.

`domain: str`  
The website's domain (e.g. 'talkpython.fm').

`shareId: typing.Any`  
The public share identifier, or null when sharing is disabled.

`resetAt: typing.Any`  
Timestamp of the last stats reset, or null.

`userId: typing.Optional[str]`  
The owning user's id; null for team-website listings.

`createdAt: str`  
ISO 8601 timestamp of when the website was created.

`updatedAt: str`  
ISO 8601 timestamp of the last update.

`deletedAt: typing.Any`  
Soft-delete timestamp, or null if not deleted.

`teamId: typing.Optional[str]`  
The owning team's id, if the website belongs to a team.

`user: typing.Optional[WebsiteUser]`  
The owning user, populated for personal website listings.

`createUser: typing.Optional[WebsiteUser]`  
The creating user, populated for team-website listings.
