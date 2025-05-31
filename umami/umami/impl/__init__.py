import base64
import json
import sys
from typing import Optional, Any, Dict

import httpx

from umami import models, urls

__version__ = '0.2.20'

from umami.errors import ValidationError, OperationNotAllowedError
from datetime import datetime

url_base: Optional[str] = None
auth_token: Optional[str] = None
default_website_id: Optional[str] = None
default_hostname: Optional[str] = None
tracking_enabled: bool = True
# An actual browser UA is needed to get around the bot detection in Umami
# You can also set DISABLE_BOT_CHECK=true in your Umami environment to disable the bot check entirely:
# https://github.com/umami-software/umami/blob/7a3443cd06772f3cde37bdbb0bf38eabf4515561/pages/api/collect.js#L13
event_user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0'
user_agent = (
    f'Umami-Client v{__version__} / '
    f'Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} / '
    f'{sys.platform.capitalize()}'
)


def set_url_base(url: str) -> None:
    """
    Each Umami instance lives somewhere. This is where yours lives.
    For example, https://somedomain.tech/umami.
    Args:
        url: The base URL of your instance without /api.
    """
    if not url or not url.strip():
        raise ValidationError('URL must not be empty.')

    # noinspection HttpUrlsUsage
    if not url.startswith('http://') and not url.startswith('https://'):
        # noinspection HttpUrlsUsage
        raise ValidationError('The url must start with the HTTP scheme (http:// or https://).')

    if url.endswith('/'):
        url = url.rstrip('/')

    global url_base
    url_base = url.strip()


def set_website_id(website_id: str) -> None:
    """
    Your Umami instance might have many websites registered for various domains you use.
    Call this function to set which website you're working with.
    Args:
        website_id: The ID from Umami for your registered site (e.g. 978435e2-7ba1-4337-9860-ec31ece2db60)
    """
    global default_website_id
    default_website_id = website_id


def set_hostname(hostname: str) -> None:
    """
    The default hostname for sending events (can be overriden in the new_event() function).
    Args:
        hostname: Hostname to use when one is not specified, e.g. 'talkpython.fm'
    """
    global default_hostname
    default_hostname = hostname


def is_logged_in() -> bool:
    return auth_token is not None


async def login_async(username: str, password: str) -> models.LoginResponse:
    """
    Logs into Umami and retrieves a temporary auth token. If the token is expired,
    you'll need to log in again. This can be checked with verify_token().
    Args:
        username: Your Umami username
        password: Your Umami password

    Returns: LoginResponse object which your token and user details (no need to save this).
    """
    global auth_token
    validate_state(url=True)
    validate_login(username, password)

    url = f'{url_base}{urls.login}'
    headers = {'User-Agent': user_agent}
    api_data = {
        'username': username,
        'password': password,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=api_data, headers=headers, follow_redirects=True)
        resp.raise_for_status()

    model = models.LoginResponse(**resp.json())
    auth_token = model.token
    return model


def login(username: str, password: str) -> models.LoginResponse:
    """
    Logs into Umami and retrieves a temporary auth token. If the token is expired,
    you'll need to log in again. This can be checked with verify_token().
    Args:
        username: Your Umami username
        password: Your Umami password

    Returns: LoginResponse object which your token and user details (no need to save this).
    """
    global auth_token

    validate_state(url=True)
    validate_login(username, password)

    url = f'{url_base}{urls.login}'
    headers = {'User-Agent': user_agent}
    api_data = {
        'username': username,
        'password': password,
    }
    resp = httpx.post(url, json=api_data, headers=headers, follow_redirects=True)
    resp.raise_for_status()

    model = models.LoginResponse(**resp.json())
    auth_token = model.token
    return model


async def websites_async() -> list[models.Website]:
    """
    All the websites that are registered in your Umami instance.
    Returns: A list of Website Pydantic models.
    """
    global auth_token
    validate_state(url=True, user=True)

    url = f'{url_base}{urls.websites}'
    headers = {
        'User-Agent': user_agent,
        'Authorization': f'Bearer {auth_token}',
    }

    async with httpx.AsyncClient() as client:  # type: ignore
        resp = await client.get(url, headers=headers, follow_redirects=True)
        resp.raise_for_status()

    model = models.WebsitesResponse(**resp.json())
    return model.websites


def websites() -> list[models.Website]:
    """
    All the websites that are registered in your Umami instance.
    Returns: A list of Website Pydantic models.
    """
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


def enable() -> None:
    """
    Enable event and page view tracking.

    When enabled, new_event() and new_page_view() functions will send
    data to Umami normally. This is the default state.
    """
    global tracking_enabled
    tracking_enabled = True


def disable() -> None:
    """
    Disable event and page view tracking.

    When disabled, new_event() and new_page_view() functions will return
    immediately without sending data to Umami. This is useful for
    development and testing environments.
    """
    global tracking_enabled
    tracking_enabled = False


async def new_event_async(
    event_name: str,
    hostname: Optional[str] = None,
    url: str = '/',
    website_id: Optional[str] = None,
    title: Optional[str] = None,
    custom_data: Optional[Dict[str, Any]] = None,
    referrer: str = '',
    language: str = 'en-US',
    screen: str = '1920x1080',
    ip_address: Optional[str] = None,
) -> str:
    """
    Creates a new custom event in Umami for the given website_id and hostname (both use the default
    if you have set them with the other functions such as set_hostname()). These events will both
    appear in the traffic related to the specified url and in the events section at the bottom
    of your Umami website page. Login is not required for this method.

    Args:
        event_name: The name of your custom event (e.g. Purchase-Course)
        hostname: OPTIONAL: The value of your hostname simulating the client (e.g. test_domain.com), overrides set_hostname() value.
        url: The simulated URL for the custom event (e.g. if it's account creation, maybe /account/new)
        website_id: OPTIONAL: The value of your website_id in Umami. (overrides set_website_id() value).
        title: The title of the custom event (not sure how this is different from the name), defaults to event_name if empty.
        custom_data: Any additional data to send along with the event. Not visible in the UI but is in the API.
        referrer: The referrer of the client if there is any (what location lead them to this event)
        language: The language of the event / client.
        screen: The screen resolution of the client.
        ip_address: OPTIONAL: The true IP address of the user, used when handling requests in APIs, etc. on the server.

    Returns: The data returned from the Umami API.
    """
    validate_state(url=True, user=False)
    website_id = website_id or default_website_id
    hostname = hostname or default_hostname
    title = title or event_name
    custom_data = custom_data or {}

    validate_event_data(event_name, hostname, website_id)

    # Early return if tracking is disabled
    if not tracking_enabled:
        return ''

    api_url = f'{url_base}{urls.events}'
    headers = {
        'User-Agent': event_user_agent,
        'Authorization': f'Bearer {auth_token}',
    }

    payload = {
        'hostname': hostname,
        'language': language,
        'referrer': referrer,
        'screen': screen,
        'title': title,
        'url': url,
        'website': website_id,
        'name': event_name,
        'data': custom_data,
    }

    if ip_address and ip_address.strip():
        payload['ip'] = ip_address

    event_data = {'payload': payload, 'type': 'event'}

    async with httpx.AsyncClient() as client:
        resp = await client.post(api_url, json=event_data, headers=headers, follow_redirects=True)
        resp.raise_for_status()

    data_str = base64.b64decode(resp.text)
    return json.loads(data_str)


def new_event(
    event_name: str,
    hostname: Optional[str] = None,
    url: str = '/event-api-endpoint',
    website_id: Optional[str] = None,
    title: Optional[str] = None,
    custom_data: Optional[Dict[str, Any]] = None,
    referrer: str = '',
    language: str = 'en-US',
    screen: str = '1920x1080',
    ip_address: Optional[str] = None,
):
    """
    Creates a new custom event in Umami for the given website_id and hostname (both use the default
    if you have set them with the other functions such as set_hostname()). These events will both
    appear in the traffic related to the specified url and in the events section at the bottom
    of your Umami website page. Login is not required for this method.

    Args:
        event_name: The name of your custom event (e.g. Purchase-Course)
        hostname: OPTIONAL: The value of your hostname simulating the client (e.g. test_domain.com), overrides set_hostname() value.
        url: The simulated URL for the custom event (e.g. if it's account creation, maybe /account/new)
        website_id: OPTIONAL: The value of your website_id in Umami. (overrides set_website_id() value).
        title: The title of the custom event (not sure how this is different from the name), defaults to event_name if empty.
        custom_data: Any additional data to send along with the event. Not visible in the UI but is in the API.
        referrer: The referrer of the client if there is any (what location lead them to this event)
        language: The language of the event / client.
        screen: The screen resolution of the client.
        ip_address: OPTIONAL: The true IP address of the user, used when handling requests in APIs, etc. on the server.
    """
    validate_state(url=True, user=False)
    website_id = website_id or default_website_id
    hostname = hostname or default_hostname
    title = title or event_name
    custom_data = custom_data or {}

    validate_event_data(event_name, hostname, website_id)

    # Early return if tracking is disabled
    if not tracking_enabled:
        return

    api_url = f'{url_base}{urls.events}'
    headers = {
        'User-Agent': event_user_agent,
        'Authorization': f'Bearer {auth_token}',
    }

    payload = {
        'hostname': hostname,
        'language': language,
        'referrer': referrer,
        'screen': screen,
        'title': title,
        'url': url,
        'website': website_id,
        'name': event_name,
        'data': custom_data,
    }

    if ip_address and ip_address.strip():
        payload['ip'] = ip_address

    event_data = {'payload': payload, 'type': 'event'}

    resp = httpx.post(api_url, json=event_data, headers=headers, follow_redirects=True)
    resp.raise_for_status()


async def new_page_view_async(
    page_title: str,
    url: str,
    hostname: Optional[str] = None,
    website_id: Optional[str] = None,
    referrer: str = '',
    language: str = 'en-US',
    screen: str = '1920x1080',
    ua: str = event_user_agent,
    ip_address: Optional[str] = None,
):
    """
    Creates a new page view event in Umami for the given website_id and hostname (both use the default
    if you have set them with the other functions such as set_hostname()). This is equivalent to what
    happens when a visit views a page and the JS library records it.

    Args:
        page_title: The title of the custom event (not sure how this is different from the name), defaults to event_name if empty.
        url: The simulated URL for the custom event (e.g. if it's account creation, maybe /account/new)
        hostname: OPTIONAL: The value of your hostname simulating the client (e.g. test_domain.com), overrides set_hostname() value.
        website_id: OPTIONAL: The value of your website_id in Umami. (overrides set_website_id() value).
        referrer: OPTIONAL: The referrer of the client if there is any (what location lead them to this event)
        language: OPTIONAL: The language of the event / client.
        screen: OPTIONAL: The screen resolution of the client.
        ua: OPTIONAL: The UserAgent resolution of the client. Note umami blocks non browsers by default.
        ip_address: OPTIONAL: The true IP address of the user, used when handling requests in APIs, etc. on the server.
    """
    validate_state(url=True, user=False)
    website_id = website_id or default_website_id
    hostname = hostname or default_hostname

    validate_event_data(event_name='NOT NEEDED', hostname=hostname, website_id=website_id)

    # Early return if tracking is disabled
    if not tracking_enabled:
        return

    api_url = f'{url_base}{urls.events}'
    headers = {
        'User-Agent': ua,
        'Authorization': f'Bearer {auth_token}',
    }

    payload = {
        'hostname': hostname,
        'language': language,
        'referrer': referrer,
        'screen': screen,
        'title': page_title,
        'url': url,
        'website': website_id,
    }

    if ip_address and ip_address.strip():
        payload['ip'] = ip_address

    event_data = {'payload': payload, 'type': 'event'}

    async with httpx.AsyncClient() as client:
        resp = await client.post(api_url, json=event_data, headers=headers, follow_redirects=True)
        resp.raise_for_status()


def new_page_view(
    page_title: str,
    url: str,
    hostname: Optional[str] = None,
    website_id: Optional[str] = None,
    referrer: str = '',
    language: str = 'en-US',
    screen: str = '1920x1080',
    ua: str = event_user_agent,
    ip_address: Optional[str] = None,
):
    """
    Creates a new page view event in Umami for the given website_id and hostname (both use the default
    if you have set them with the other functions such as set_hostname()). This is equivalent to what
    happens when a visit views a page and the JS library records it.

    Args:
        page_title: The title of the custom event (not sure how this is different from the name), defaults to event_name if empty.
        url: The simulated URL for the custom event (e.g. if it's account creation, maybe /account/new)
        hostname: OPTIONAL: The value of your hostname simulating the client (e.g. test_domain.com), overrides set_hostname() value.
        website_id: OPTIONAL: The value of your website_id in Umami. (overrides set_website_id() value).
        referrer: OPTIONAL: The referrer of the client if there is any (what location lead them to this event)
        language: OPTIONAL: The language of the event / client.
        screen: OPTIONAL: The screen resolution of the client.
        ua: OPTIONAL: The UserAgent resolution of the client. Note umami blocks non browsers by default.
        ip_address: OPTIONAL: The true IP address of the user, used when handling requests in APIs, etc. on the server.
    """
    validate_state(url=True, user=False)
    website_id = website_id or default_website_id
    hostname = hostname or default_hostname

    validate_event_data(event_name='NOT NEEDED', hostname=hostname, website_id=website_id)

    # Early return if tracking is disabled
    if not tracking_enabled:
        return

    api_url = f'{url_base}{urls.events}'
    headers = {
        'User-Agent': ua,
        'Authorization': f'Bearer {auth_token}',
    }

    payload = {
        'hostname': hostname,
        'language': language,
        'referrer': referrer,
        'screen': screen,
        'title': page_title,
        'url': url,
        'website': website_id,
    }

    if ip_address and ip_address.strip():
        payload['ip'] = ip_address

    event_data = {'payload': payload, 'type': 'event'}

    resp = httpx.post(api_url, json=event_data, headers=headers, follow_redirects=True)
    resp.raise_for_status()


def validate_event_data(event_name: str, hostname: Optional[str], website_id: Optional[str]):
    """
    Internal use only.
    """
    if not hostname:
        raise Exception('The hostname must be set, either as a parameter here or via set_hostname().')
    if not website_id:
        raise Exception('The website_id must be set, either as a parameter here or via set_website_id().')
    if not event_name and not event_name.strip():
        raise Exception('The event_name is required.')


async def verify_token_async(check_server: bool = True) -> bool:
    """
    Verifies that the token set when you called login() is still valid. Umami says this token will expire,
    but I'm not sure if that's minutes, hours, or years.

    Args:
        check_server: If true, we will contact the server and verify that the token is valid.
                      If false, this only checks that an auth token has been stored from a previous successful login.

    Returns: True if the token is still valid, False otherwise.
    """
    # noinspection PyBroadException
    try:
        global auth_token
        validate_state(url=True, user=True)

        if not check_server:
            return True

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


def verify_token(check_server: bool = True) -> bool:
    """
    Verifies that the token set when you called login() is still valid. Umami says this token will expire,
    but I'm not sure if that's minutes, hours, or years.

    Args:
        check_server: If true, we will contact the server and verify that the token is valid.
                      If false, this only checks that an auth token has been stored from a previous successful login.

    Returns: True if the token is still valid, False otherwise.
    """
    # noinspection PyBroadException
    try:
        global auth_token
        validate_state(url=True, user=True)

        if not check_server:
            return True

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


async def heartbeat_async() -> bool:
    """
    Verifies that the server is reachable via the internet and is healthy.

    Returns: True if the server is healthy and accessible.
    """
    # noinspection PyBroadException
    try:
        global auth_token
        validate_state(url=True, user=False)

        url = f'{url_base}{urls.heartbeat}'
        headers = {
            'User-Agent': user_agent,
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, follow_redirects=True)
            resp.raise_for_status()

        return True
    except Exception:
        return False


def heartbeat() -> bool:
    """
    Verifies that the server is reachable via the internet and is healthy.

    Returns: True if the server is healthy and accessible.
    """
    # noinspection PyBroadException
    try:
        global auth_token
        validate_state(url=True, user=False)

        url = f'{url_base}{urls.heartbeat}'
        headers = {
            'User-Agent': user_agent,
        }
        resp = httpx.post(url, headers=headers, follow_redirects=True)
        resp.raise_for_status()

        return True
    except Exception:
        return False


def validate_login(email: str, password: str) -> None:
    """
    Internal helper function, not need to use this.
    """
    if not email:
        raise ValidationError('Email cannot be empty')
    if not password:
        raise ValidationError('Password cannot be empty')


async def active_users_async(website_id: Optional[str] = None) -> int:
    """
    Retrieves the active users for a specific website.

    Args:
        website_id: OPTIONAL: The value of your website_id in Umami. (overrides set_website_id() value).


    Returns: The number of active users.
    """
    validate_state(url=True, user=True)

    website_id = website_id or default_website_id

    url = f'{url_base}{urls.websites}/{website_id}/active'
    headers = {
        'User-Agent': user_agent,
        'Authorization': f'Bearer {auth_token}',
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers, follow_redirects=True)
        resp.raise_for_status()

    return int(resp.json().get('x', 0))


def active_users(website_id: Optional[str] = None) -> int:
    """
    Retrieves the active users for a specific website.

    Args:
        website_id: OPTIONAL: The value of your website_id in Umami. (overrides set_website_id() value).


    Returns: The number of active users.
    """
    validate_state(url=True, user=True)

    website_id = website_id or default_website_id

    url = f'{url_base}{urls.websites}/{website_id}/active'
    headers = {
        'User-Agent': user_agent,
        'Authorization': f'Bearer {auth_token}',
    }

    resp = httpx.get(url, headers=headers, follow_redirects=True)
    resp.raise_for_status()

    return int(resp.json().get('x', 0))


async def website_stats_async(
    start_at: datetime,
    end_at: datetime,
    website_id: Optional[str] = None,
    url: Optional[str] = None,
    referrer: Optional[str] = None,
    title: Optional[str] = None,
    query: Optional[str] = None,
    event: Optional[str] = None,
    host: Optional[str] = None,
    os: Optional[str] = None,
    browser: Optional[str] = None,
    device: Optional[str] = None,
    country: Optional[str] = None,
    region: Optional[str] = None,
    city: Optional[str] = None,
) -> models.WebsiteStats:
    """
    Retrieves the statistics for a specific website.

    Args:
        start_at: Starting date as a datetime object.
        end_at: End date as a datetime object.
        website_id: OPTIONAL: The value of your website_id in Umami. (overrides set_website_id() value).
        url: OPTIONAL: Name of URL.
        referrer: OPTIONAL: Name of referrer.
        title: OPTIONAL: Name of page title.
        query: OPTIONAL: Name of query.
        event: OPTIONAL: Name of event.
        host: OPTIONAL: Name of hostname.
        os: OPTIONAL: Name of operating system.
        browser: OPTIONAL: Name of browser.
        device: OPTIONAL: Name of device (ex. Mobile)
        country: OPTIONAL: Name of country.
        region: OPTIONAL: Name of region/state/province.
        city: OPTIONAL: Name of city.

    Returns: A WebsiteStatsResponse model containing the website statistics data.
    """
    validate_state(url=True, user=True)

    website_id = website_id or default_website_id

    api_url = f'{url_base}{urls.websites}/{website_id}/stats'

    headers = {
        'User-Agent': user_agent,
        'Authorization': f'Bearer {auth_token}',
    }
    params = {
        'start_at': int(start_at.timestamp() * 1000),
        'end_at': int(end_at.timestamp() * 1000),
    }
    optional_params: dict[str, Any] = {
        'url': url,
        'referrer': referrer,
        'title': title,
        'query': query,
        'event': event,
        'host': host,
        'os': os,
        'browser': browser,
        'device': device,
        'country': country,
        'region': region,
        'city': city,
    }
    params.update({k: v for k, v in optional_params.items() if v is not None})

    async with httpx.AsyncClient() as client:
        resp = await client.get(api_url, headers=headers, params=params, follow_redirects=True)
        resp.raise_for_status()

    return models.WebsiteStats(**resp.json())


def website_stats(
    start_at: datetime,
    end_at: datetime,
    website_id: Optional[str] = None,
    url: Optional[str] = None,
    referrer: Optional[str] = None,
    title: Optional[str] = None,
    query: Optional[str] = None,
    event: Optional[str] = None,
    host: Optional[str] = None,
    os: Optional[str] = None,
    browser: Optional[str] = None,
    device: Optional[str] = None,
    country: Optional[str] = None,
    region: Optional[str] = None,
    city: Optional[str] = None,
) -> models.WebsiteStats:
    """
    Retrieves the statistics for a specific website.

    Args:
        start_at: Starting date as a datetime object.
        end_at: End date as a datetime object.
        url: OPTIONAL: Name of URL.
        website_id: OPTIONAL: The value of your website_id in Umami. (overrides set_website_id() value).
        referrer: OPTIONAL: Name of referrer.
        title: (OPTIONAL: Name of page title.
        query: OPTIONAL: Name of query.
        event: OPTIONAL: Name of event.
        host: OPTIONAL: Name of hostname.
        os: OPTIONAL: Name of operating system.
        browser: OPTIONAL: Name of browser.
        device: OPTIONAL: Name of device (ex. Mobile)
        country: OPTIONAL: Name of country.
        region: OPTIONAL: Name of region/state/province.
        city: OPTIONAL: Name of city.

    Returns: A WebsiteStatsResponse model containing the website statistics data.
    """
    validate_state(url=True, user=True)

    website_id = website_id or default_website_id

    api_url = f'{url_base}{urls.websites}/{website_id}/stats'

    headers = {
        'User-Agent': user_agent,
        'Authorization': f'Bearer {auth_token}',
    }
    params = {
        'startAt': int(start_at.timestamp() * 1000),
        'endAt': int(end_at.timestamp() * 1000),
    }
    optional_params: dict[str, Any] = {
        'url': url,
        'referrer': referrer,
        'title': title,
        'query': query,
        'event': event,
        'host': host,
        'os': os,
        'browser': browser,
        'device': device,
        'country': country,
        'region': region,
        'city': city,
    }
    params.update({k: v for k, v in optional_params.items() if v is not None})

    resp = httpx.get(api_url, headers=headers, params=params, follow_redirects=True)
    resp.raise_for_status()

    return models.WebsiteStats(**resp.json())


def validate_state(url: bool = False, user: bool = False):
    """
    Internal helper function, not need to use this.
    """
    if url and not url_base:
        raise OperationNotAllowedError('URL Base must be set to proceed.')

    if user and not auth_token:
        raise OperationNotAllowedError('You must login before proceeding.')
