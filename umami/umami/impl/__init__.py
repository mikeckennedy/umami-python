import sys
from pprint import pprint
from typing import Optional

import httpx

from umami import models, urls  # noqa: F401

__version__ = '0.1.9'

url_base: Optional[str] = None
auth_token: Optional[str] = None
default_website_id: Optional[str] = None
default_hostname: Optional[str] = None
event_user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0'
user_agent = (f'Umami-Client v{__version__} / '
              f'Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')


def set_url_base(url: str):
    if not url or not url.strip():
        raise Exception("URL must not be empty")

    global url_base
    url_base = url.strip()


def set_website_id(website: str):
    global default_website_id
    default_website_id = website


def set_hostname(hostname: str):
    global default_hostname
    default_hostname = hostname


async def login_async(username: str, password: str) -> models.LoginResponse:
    global auth_token
    validate_state(url=True)
    validate_login(username, password)

    url = f'{url_base}{urls.login}'
    headers = {'User-Agent': user_agent}
    api_data = {
        "username": username,
        "password": password,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, data=api_data, headers=headers, follow_redirects=True)
        resp.raise_for_status()

    model = models.LoginResponse(**resp.json())
    auth_token = model.token
    return model


def login(username: str, password: str) -> models.LoginResponse:
    global auth_token

    validate_state(url=True)
    validate_login(username, password)

    url = f'{url_base}{urls.login}'
    headers = {'User-Agent': user_agent}
    api_data = {
        "username": username,
        "password": password,
    }
    resp = httpx.post(url, data=api_data, headers=headers, follow_redirects=True)
    resp.raise_for_status()

    model = models.LoginResponse(**resp.json())
    auth_token = model.token
    return model


async def websites_async() -> list[models.Website]:
    global auth_token
    validate_state(url=True, user=True)

    url = f'{url_base}{urls.websites}'
    headers = {
        'User-Agent': user_agent,
        'Authorization': f'Bearer {auth_token}',
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers, follow_redirects=True)
        resp.raise_for_status()

    model = models.WebsitesResponse(**resp.json())
    return model.websites


def websites() -> list[models.Website]:
    global auth_token
    validate_state(url=True, user=True)

    url = f'{url_base}{urls.websites}'
    headers = {
        'User-Agent': user_agent,
        'Authorization': f'Bearer {auth_token}',
    }
    resp = httpx.get(url, headers=headers, follow_redirects=True)
    resp.raise_for_status()

    data = resp.json()
    model = models.WebsitesResponse(**data)
    return model.websites


async def new_event_async(event_name: str, hostname: Optional[str] = None, url: str = '/',
                          website_id: Optional[str] = None, title: Optional[str] = None,
                          custom_data=None, referrer: str = '', language: str = 'en-US',
                          screen: str = "1920x1080") -> str:
    website_id = website_id or default_website_id
    hostname = hostname or default_hostname
    title = title or event_name
    custom_data = custom_data or {}

    api_url = f'{url_base}{urls.events}'
    headers = {
        'User-Agent': event_user_agent,
        'Authorization': f'Bearer {auth_token}',
    }

    payload = {
        "hostname": hostname,
        "language": language,
        "referrer": referrer,
        "screen": screen,
        "title": title,
        "url": url,
        "website": website_id,
        "name": event_name,
        "data": custom_data
    }

    event_data = {
        'payload': payload,
        'type': 'event'
    }

    print("POSTING NEW EVENT")
    print()
    print("URL:")
    pprint(api_url)
    print()
    print("Headers:")
    pprint(headers)
    print()
    print("event_data:")
    pprint(event_data)

    async with httpx.AsyncClient() as client:
        resp = await client.post(api_url, json=event_data, headers=headers, follow_redirects=True)
        resp.raise_for_status()

    return resp.text


def new_event(event_name: str, hostname: Optional[str] = None, url: str = '/event-api-endpoint',
              website_id: Optional[str] = None, title: Optional[str] = None,
              custom_data=None, referrer: str = '', language: str = 'en-US',
              screen: str = "1920x1080") -> str:
    website_id = website_id or default_website_id
    hostname = hostname or default_hostname
    title = title or event_name
    custom_data = custom_data or {}

    api_url = f'{url_base}{urls.events}'
    headers = {
        'User-Agent': event_user_agent,
        'Authorization': f'Bearer {auth_token}',
    }

    payload = {
        "hostname": hostname,
        "language": language,
        "referrer": referrer,
        "screen": screen,
        "title": title,
        "url": url,
        "website": website_id,
        "name": event_name,
        "data": custom_data
    }

    event_data = {
        'payload': payload,
        'type': 'event'
    }

    resp = httpx.post(api_url, json=event_data, headers=headers, follow_redirects=True)
    resp.raise_for_status()

    return resp.text


async def verify_token_async() -> bool:
    # noinspection PyBroadException
    try:
        global auth_token
        validate_state(url=True, user=True)

        url = f'{url_base}{urls.verify}'
        headers = {
            'User-Agent': event_user_agent,
            'Authorization': f'Bearer {auth_token}',
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, follow_redirects=True)
            resp.raise_for_status()

        return 'username' in resp.json()
    except Exception:
        return False


def verify_token() -> bool:
    # noinspection PyBroadException
    try:
        global auth_token
        validate_state(url=True, user=True)

        url = f'{url_base}{urls.verify}'
        headers = {
            'User-Agent': event_user_agent,
            'Authorization': f'Bearer {auth_token}',
        }
        resp = httpx.post(url, headers=headers, follow_redirects=True)
        resp.raise_for_status()

        return 'username' in resp.json()
    except Exception:
        return False


def validate_login(email, password):
    if not email:
        raise Exception("Email cannot be empty")
    if not password:
        raise Exception("Password cannot be empty")


def validate_state(url=False, user=False):
    if url and not url_base:
        raise Exception("URL Base must be set to proceed.")

    if user and not auth_token:
        raise Exception("You must login before proceeding.")
