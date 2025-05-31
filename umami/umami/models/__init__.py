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


class WebsiteUser(pydantic.BaseModel):
    username: str
    id: str


class Website(pydantic.BaseModel):
    id: str
    name: typing.Optional[str] = None
    domain: str
    shareId: typing.Any
    resetAt: typing.Any
    userId: typing.Optional[str] = None
    createdAt: str
    updatedAt: str
    deletedAt: typing.Any
    teamId: typing.Optional[str] = None
    user: WebsiteUser


class Metric(pydantic.BaseModel):
    value: int
    prev: int


class WebsiteStats(pydantic.BaseModel):
    pageviews: Metric
    visitors: Metric
    visits: Metric
    bounces: Metric
    totaltime: Metric


class WebsitesResponse(pydantic.BaseModel):
    websites: list[Website] = pydantic.Field(alias='data')
    count: int
    page: int
    pageSize: int
    orderBy: typing.Optional[str] = None
