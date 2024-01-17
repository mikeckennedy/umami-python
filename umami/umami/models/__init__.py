import typing

import pydantic


class User(pydantic.BaseModel):
    id: str
    username: str
    role: str
    createdAt: str
    isAdmin: bool


class LoginResponse(pydantic.BaseModel):
    token: str
    user: User


class TokenVerification(pydantic.BaseModel):
    id: str
    username: str
    role: str
    createdAt: str
    isAdmin: bool


class WebsiteTeam(pydantic.BaseModel):
    name: str


class WebsiteUser(pydantic.BaseModel):
    username: str
    id: str


class TeamSiteDetails(pydantic.BaseModel):
    id: str
    teamId: str
    websiteId: str
    createdAt: str
    team: WebsiteTeam


class Website(pydantic.BaseModel):
    id: str
    name: typing.Optional[str] = None
    domain: str
    shareId: typing.Any
    resetAt: typing.Any
    userId: str
    createdAt: str
    updatedAt: str
    deletedAt: typing.Any
    teamWebsite: list[TeamSiteDetails]
    user: WebsiteUser


class WebsitesResponse(pydantic.BaseModel):
    websites: list[Website] = pydantic.Field(alias="data")
    count: int
    page: int
    pageSize: int
    orderBy: typing.Optional[str] = None
