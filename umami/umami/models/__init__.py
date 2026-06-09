import typing

import pydantic


class User(pydantic.BaseModel):
    """
    An authenticated Umami user account.

    Returned as the user attribute of the LoginResponse from login() /
    login_async() (self-hosted/token mode). It is not returned directly by any
    public function.

    Attributes:
        id: The user's unique identifier.
        username: The login username.
        role: The account role (e.g. 'admin', 'user').
        createdAt: ISO 8601 timestamp of when the account was created.
        isAdmin: True if the account has administrator privileges.
    """

    id: str = pydantic.Field(description="The user's unique identifier.")
    username: str = pydantic.Field(description='The login username.')
    role: str = pydantic.Field(description="The account role (e.g. 'admin', 'user').")
    createdAt: str = pydantic.Field(description='ISO 8601 timestamp of when the account was created.')
    isAdmin: bool = pydantic.Field(description='True if the account has administrator privileges.')


class LoginResponse(pydantic.BaseModel):
    """
    The result of authenticating against a self-hosted Umami instance.

    Returned by login() / login_async(). The SDK stores the token internally
    after a successful login, so you typically do not need to read it yourself.
    Not used in Umami Cloud mode (set_cloud_api_key()), where the API key is the
    credential.

    Attributes:
        token: The bearer token used to authenticate subsequent data and
            management calls.
        user: The authenticated User account details.
    """

    token: str = pydantic.Field(
        description='The bearer token used to authenticate subsequent data and management calls.'
    )
    user: User = pydantic.Field(description='The authenticated User account details.')


class WebsiteUser(pydantic.BaseModel):
    """
    A minimal reference to the user who owns or created a website.

    Appears as the user attribute (and, for team-website listings, the
    createUser attribute) of a Website returned by websites() /
    websites_async().

    Attributes:
        username: The referenced user's login username.
        id: The referenced user's unique identifier.
    """

    username: str = pydantic.Field(description="The referenced user's login username.")
    id: str = pydantic.Field(description="The referenced user's unique identifier.")


class Website(pydantic.BaseModel):
    """
    A website registered in your Umami instance.

    Returned as the elements of the list from websites() / websites_async().
    Many fields are optional or may be null depending on the endpoint and the
    website's configuration.

    Note:
        The personal websites listing populates user and userId. The
        team-website listing (GET /api/teams/:id/websites) instead populates
        createUser and leaves userId null.

    Attributes:
        id: The website's unique identifier (use this as the website_id
            elsewhere).
        name: The display name of the website, if set.
        domain: The website's domain (e.g. 'talkpython.fm').
        shareId: The public share identifier, or null when sharing is disabled.
        resetAt: Timestamp of the last stats reset, or null.
        userId: The owning user's id; null for team-website listings.
        createdAt: ISO 8601 timestamp of when the website was created.
        updatedAt: ISO 8601 timestamp of the last update.
        deletedAt: Soft-delete timestamp, or null if not deleted.
        teamId: The owning team's id, if the website belongs to a team.
        user: The owning user, populated for personal website listings.
        createUser: The creating user, populated for team-website listings.
    """

    id: str = pydantic.Field(description="The website's unique identifier (use this as the website_id elsewhere).")
    name: typing.Optional[str] = pydantic.Field(default=None, description='The display name of the website, if set.')
    domain: str = pydantic.Field(description="The website's domain (e.g. 'talkpython.fm').")
    shareId: typing.Any = pydantic.Field(
        default=None, description='The public share identifier, or null when sharing is disabled.'
    )
    resetAt: typing.Any = pydantic.Field(default=None, description='Timestamp of the last stats reset, or null.')
    userId: typing.Optional[str] = pydantic.Field(
        default=None, description="The owning user's id; null for team-website listings."
    )
    createdAt: str = pydantic.Field(description='ISO 8601 timestamp of when the website was created.')
    updatedAt: str = pydantic.Field(description='ISO 8601 timestamp of the last update.')
    deletedAt: typing.Any = pydantic.Field(default=None, description='Soft-delete timestamp, or null if not deleted.')
    teamId: typing.Optional[str] = pydantic.Field(
        default=None, description="The owning team's id, if the website belongs to a team."
    )
    user: typing.Optional[WebsiteUser] = pydantic.Field(
        default=None, description='The owning user, populated for personal website listings.'
    )
    # GET /api/teams/:id/websites returns createUser instead of user (and userId is null there).
    createUser: typing.Optional[WebsiteUser] = pydantic.Field(
        default=None, description='The creating user, populated for team-website listings.'
    )


class WebsiteStatsCmp(pydantic.BaseModel):
    """
    Prior-period comparison totals for a website's statistics.

    Appears as the optional comparison attribute of WebsiteStats (returned by
    website_stats() / website_stats_async()), holding the same totals for the
    preceding period so they can be compared against the current period.

    Attributes:
        pageviews: Number of page views in the comparison period.
        visitors: Number of unique visitors in the comparison period.
        visits: Number of sessions in the comparison period.
        bounces: Number of single-page sessions in the comparison period.
        totaltime: Total engagement time in seconds for the comparison period.
    """

    pageviews: int = pydantic.Field(description='Number of page views in the comparison period.')
    visitors: int = pydantic.Field(description='Number of unique visitors in the comparison period.')
    visits: int = pydantic.Field(description='Number of sessions in the comparison period.')
    bounces: int = pydantic.Field(description='Number of single-page sessions in the comparison period.')
    totaltime: int = pydantic.Field(description='Total engagement time in seconds for the comparison period.')


class WebsiteStats(pydantic.BaseModel):
    """
    Aggregate traffic statistics for a website over a time range.

    Returned by website_stats() / website_stats_async() for the requested
    start/end window and optional filters.

    Attributes:
        pageviews: Total number of page views.
        visitors: Number of unique visitors.
        visits: Number of sessions.
        bounces: Number of single-page sessions.
        totaltime: Total engagement time in seconds.
        comparison: Prior-period totals as a WebsiteStatsCmp, or None when the
            API does not return a comparison block.
    """

    pageviews: int = pydantic.Field(description='Total number of page views.')
    visitors: int = pydantic.Field(description='Number of unique visitors.')
    visits: int = pydantic.Field(description='Number of sessions.')
    bounces: int = pydantic.Field(description='Number of single-page sessions.')
    totaltime: int = pydantic.Field(description='Total engagement time in seconds.')
    comparison: typing.Optional[WebsiteStatsCmp] = pydantic.Field(
        default=None,
        description='Prior-period totals as a WebsiteStatsCmp, or None when the API returns no comparison block.',
    )


class WebsitesResponse(pydantic.BaseModel):
    """
    The paged envelope returned by the Umami /api/websites endpoint.

    The SDK parses this internally; websites() / websites_async() unwrap it and
    return only the websites list, so you rarely interact with this model
    directly.

    Note:
        The websites field is populated from the API's data key (via a pydantic
        field alias). When constructing this model from raw API JSON, pass
        data=..., not websites=....

    Attributes:
        websites: The list of Website records on this page (aliased from API
            'data').
        count: The total number of websites across all pages.
        page: The current page number.
        pageSize: The number of records per page.
        orderBy: The field results are ordered by, if specified.
    """

    websites: list[Website] = pydantic.Field(
        alias='data', description="The list of Website records on this page (aliased from API 'data')."
    )
    count: int = pydantic.Field(description='The total number of websites across all pages.')
    page: int = pydantic.Field(description='The current page number.')
    pageSize: int = pydantic.Field(description='The number of records per page.')
    orderBy: typing.Optional[str] = pydantic.Field(
        default=None, description='The field results are ordered by, if specified.'
    )
