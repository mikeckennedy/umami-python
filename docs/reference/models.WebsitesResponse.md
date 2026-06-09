## models.WebsitesResponse


The paged envelope returned by the Umami /api/websites endpoint.


Usage

``` python
models.WebsitesResponse()
```


The SDK parses this internally; websites() / websites_async() unwrap it and return only the websites list, so you rarely interact with this model directly.


## Note

The websites field is populated from the API's data key (via a pydantic field alias). When constructing this model from raw API JSON, pass data=…, not websites=….


## Attributes


`websites: list[Website]`  
The list of Website records on this page (aliased from API 'data').

`count: int`  
The total number of websites across all pages.

`page: int`  
The current page number.

`pageSize: int`  
The number of records per page.

`orderBy: typing.Optional[str]`  
The field results are ordered by, if specified.
