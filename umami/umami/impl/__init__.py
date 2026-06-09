"""
Internal implementation of the umami SDK.

This module contains all client functions and the module-global configuration
state (url_base, auth_token, default_website_id, default_hostname, api_key,
cloud_region, tracking_enabled). The public package re-exports the relevant
functions from here; import and call them as umami.func(...) rather than
reaching into this module directly.
"""

import sys
from datetime import datetime
from typing import Any, Dict, Optional, Union

import httpx2 as httpx

from umami import models, urls
from umami.errors import OperationNotAllowedError, ValidationError

try:
    from importlib.metadata import version

    __version__ = version('umami-analytics')
except Exception:
    __version__ = '0.0.0'  # Fallback for development environments


url_base: Optional[str] = None
auth_token: Optional[str] = None
default_website_id: Optional[str] = None
default_hostname: Optional[str] = None
tracking_enabled: bool = True

# Umami Cloud API-key auth (see set_cloud_api_key). When api_key is None we are in
# self-hosted/token mode and every code path behaves exactly as before.
api_key: Optional[str] = None
cloud_region: Optional[str] = None  # None | 'us' | 'eu'

# Official Umami Cloud hosts
_CLOUD_DATA_BASE = 'https://api.umami.is/v1'  # data/management API (x-umami-api-key)
_CLOUD_SEND_BASE = 'https://cloud.umami.is/api'  # public ingestion (/send, /batch)
# An actual browser UA is needed to get around the bot detection in Umami
# You can also set DISABLE_BOT_CHECK=true in your Umami environment to disable the bot check entirely:
# https://github.com/umami-software/umami/blob/7a3443cd06772f3cde37bdbb0bf38eabf4515561/pages/api/collect.js#L13
event_user_agent = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/142.0.0.0 Safari/537.36'
)
user_agent = (
    f'Umami-Client v{__version__} / '
    f'Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} / '
    f'{sys.platform.capitalize()}'
)


def normalize_distinct_id(distinct_id: Optional[Union[str, int]]) -> Optional[str]:
    """
    Normalize a distinct_id value for the event payload's 'id' field.

    Internal helper. Returns None for None, blank, or whitespace-only input;
    otherwise returns the value stringified and stripped.

    Args:
        distinct_id: A string or integer identifier, or None.

    Returns:
        The normalized identifier as a stripped string, or None if the input
        was None or reduced to an empty string.

    Raises:
        ValidationError: If distinct_id is a bool or any type other than str,
            int, or None.
    """
    if distinct_id is None:
        return None

    if isinstance(distinct_id, bool) or not isinstance(distinct_id, (str, int)):
        raise ValidationError('distinct_id must be a string or integer.')

    normalized_distinct_id = str(distinct_id).strip()
    return normalized_distinct_id or None


def set_url_base(url: str) -> None:
    """
    Set the base URL of your self-hosted Umami instance.

    Required before any self-hosted operation (login, sending events, or
    querying stats). Provide the root URL of your instance without the trailing
    '/api', for example 'https://analytics.example.com'. A trailing slash is
    stripped automatically. Use this together with login() for
    self-hosted/token mode; do not combine it with set_cloud_api_key(), which
    selects Umami Cloud mode instead.

    Args:
        url: The base URL of your instance, without '/api'. Must start with
            'http://' or 'https://'.

    Raises:
        ValidationError: If url is empty or whitespace-only, or if it does not
            start with 'http://' or 'https://'.
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
    Set the default website ID used for subsequent calls.

    An Umami instance can have many registered websites. Call this once to
    choose which website later calls (new_event(), new_page_view(),
    website_stats(), active_users()) target by default. Individual calls can
    override it via their website_id parameter.

    Args:
        website_id: The website ID from Umami for your registered site
            (e.g. '978435e2-7ba1-4337-9860-ec31ece2db60').
    """
    global default_website_id
    default_website_id = website_id


def set_hostname(hostname: str) -> None:
    """
    Set the default hostname used when sending events and page views.

    Used as the hostname for new_event(), new_revenue_event(), and
    new_page_view() when one is not passed explicitly. Individual calls can
    override it via their hostname parameter.

    Args:
        hostname: The hostname to use when one is not specified
            (e.g. 'talkpython.fm').
    """
    global default_hostname
    default_hostname = hostname


def set_cloud_api_key(key: str, region: Optional[str] = None) -> None:
    """
    Authenticate against Umami Cloud with an API key instead of login().

    Enables "Cloud mode": data and management calls are routed to
    https://api.umami.is/v1 and authenticated with the 'x-umami-api-key'
    header, and events are sent to https://cloud.umami.is/api/send. You do not
    need to call set_url_base() or login() in this mode; Cloud mode and
    self-hosted/token mode are mutually exclusive. Call clear_cloud_api_key()
    to exit Cloud mode and return to self-hosted/token behavior.

    Args:
        key: Your Umami Cloud API key.
        region: Optional 'us' or 'eu' to pin the data region. Defaults to the
            region of the account that owns the key.

    Raises:
        ValidationError: If key is empty or whitespace-only, or if region is
            provided but is not 'us' or 'eu'.

    Example:
        ```python
        import umami

        umami.set_cloud_api_key('your-cloud-api-key', region='us')
        umami.set_website_id('978435e2-7ba1-4337-9860-ec31ece2db60')
        ```
    """
    global api_key, cloud_region
    if not key or not key.strip():
        raise ValidationError('API key must not be empty.')
    if region is not None and region not in ('us', 'eu'):
        raise ValidationError("region must be 'us', 'eu', or None.")
    api_key = key.strip()
    cloud_region = region


def clear_cloud_api_key() -> None:
    """
    Exit Cloud mode and return to self-hosted/token behavior.

    Clears the API key and region set by set_cloud_api_key(). After calling
    this, self-hosted operations again require set_url_base() and login().
    """
    global api_key, cloud_region
    api_key = None
    cloud_region = None


def _is_cloud() -> bool:
    return api_key is not None


def _data_url(path_const: str, suffix: str = '') -> str:
    """
    Full URL for a data/auth endpoint in the active mode.
    `path_const` is a value from urls.py (e.g. urls.websites == '/api/websites').
    """
    if _is_cloud():
        region = f'/{cloud_region}' if cloud_region else ''
        rel = path_const[4:] if path_const.startswith('/api') else path_const  # '/api/x' -> '/x'
        return f'{_CLOUD_DATA_BASE}{region}{rel}{suffix}'  # .../v1[/region]/x
    return f'{url_base}{path_const}{suffix}'  # unchanged self-hosted


def _send_url() -> str:
    """Full URL for the ingestion endpoint (/api/send) in the active mode."""
    if _is_cloud():
        return f'{_CLOUD_SEND_BASE}/send'  # https://cloud.umami.is/api/send
    return f'{url_base}{urls.events}'  # unchanged self-hosted (or cloud-events via set_url_base)


def _data_headers() -> dict:
    """Auth headers for data/management calls in the active mode."""
    headers = {'User-Agent': user_agent}
    if _is_cloud():
        headers['x-umami-api-key'] = api_key  # type: ignore[assignment]
    else:
        headers['Authorization'] = f'Bearer {auth_token}'  # identical to today
    return headers


def _send_headers(ua: str = event_user_agent) -> dict:
    """Headers for ingestion calls. Self-hosted unchanged; Cloud send is unauthenticated."""
    headers = {'User-Agent': ua}
    if not _is_cloud():
        headers['Authorization'] = f'Bearer {auth_token}'  # identical to today (may be 'Bearer None')
    return headers


def is_logged_in() -> bool:
    """
    Whether a credential is currently set locally.

    Returns:
        True if a self-hosted login token (set by login()) or an Umami Cloud
        API key (set by set_cloud_api_key()) is present, False otherwise. This
        only reflects that a credential exists in this process, not that it is
        still valid on the server — use verify_token() to confirm validity.
    """
    return auth_token is not None or api_key is not None


async def login_async(username: str, password: str) -> models.LoginResponse:
    """
    Log into a self-hosted Umami instance and retrieve a temporary auth token.

    On success, the returned token is stored internally and used to
    authenticate subsequent data calls (websites_async(),
    website_stats_async(), active_users_async(), verify_token_async()). Tokens
    expire, so you may need to log in again; check validity with
    verify_token_async().

    Requires set_url_base() to have been called first. This is the
    self-hosted/token authentication path and is not used in Cloud mode; in
    Cloud mode call set_cloud_api_key() instead.

    Args:
        username: Your Umami username.
        password: Your Umami password.

    Returns:
        A models.LoginResponse containing the auth token and the logged-in
        user's details. You do not need to store this yourself; the token is
        retained internally.

    Raises:
        OperationNotAllowedError: If Cloud mode is active (set_cloud_api_key()
            was called), or if set_url_base() has not been called.
        ValidationError: If username or password is empty.
        httpx.HTTPStatusError: If the server returns a non-2xx response, e.g.
            on invalid credentials.

    Example:
        ```python
        import umami

        umami.set_url_base('https://umami.example.com')
        login = await umami.login_async('admin', 'super-secret')
        ```
    """
    global auth_token
    if _is_cloud():
        raise OperationNotAllowedError(
            'login() is not used in Cloud mode; your API key from set_cloud_api_key() is the '
            'credential. Call clear_cloud_api_key() first to use username/password login.'
        )
    validate_state(url=True)
    validate_login(username, password)

    url = _data_url(urls.login)
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
    Log into a self-hosted Umami instance and retrieve a temporary auth token.

    On success, the returned token is stored internally and used to
    authenticate subsequent data calls (websites(), website_stats(),
    active_users(), verify_token()). Tokens expire, so you may need to log in
    again; check validity with verify_token().

    Requires set_url_base() to have been called first. This is the
    self-hosted/token authentication path and is not used in Cloud mode; in
    Cloud mode call set_cloud_api_key() instead.

    Args:
        username: Your Umami username.
        password: Your Umami password.

    Returns:
        A models.LoginResponse containing the auth token and the logged-in
        user's details. You do not need to store this yourself; the token is
        retained internally.

    Raises:
        OperationNotAllowedError: If Cloud mode is active (set_cloud_api_key()
            was called), or if set_url_base() has not been called.
        ValidationError: If username or password is empty.
        httpx.HTTPStatusError: If the server returns a non-2xx response, e.g.
            on invalid credentials.

    Example:
        ```python
        import umami

        umami.set_url_base('https://umami.example.com')
        login = umami.login('admin', 'super-secret')
        ```
    """
    global auth_token

    if _is_cloud():
        raise OperationNotAllowedError(
            'login() is not used in Cloud mode; your API key from set_cloud_api_key() is the '
            'credential. Call clear_cloud_api_key() first to use username/password login.'
        )
    validate_state(url=True)
    validate_login(username, password)

    url = _data_url(urls.login)
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

    Requires authentication: call login() (self-hosted) or set_cloud_api_key()
    (Umami Cloud) first. In self-hosted mode you must also have called
    set_url_base().

    Returns:
        A list of models.Website models, unwrapped from the paged API response.

    Raises:
        OperationNotAllowedError: If set_url_base() has not been called (and no
            Cloud API key is set), or if no credential is present (neither a
            login token nor a Cloud API key).
        httpx.HTTPStatusError: If the Umami API returns a non-2xx response.

    Example:
        ```python
        import umami

        umami.set_url_base('https://umami.example.com')
        await umami.login_async(username, password)
        for site in await umami.websites_async():
            print(site.name, site.domain)
        ```
    """
    global auth_token
    validate_state(url=True, user=True)

    url = _data_url(urls.websites)
    headers = _data_headers()

    async with httpx.AsyncClient() as client:  # type: ignore
        resp = await client.get(url, headers=headers, follow_redirects=True)
        resp.raise_for_status()

    model = models.WebsitesResponse(**resp.json())
    return model.websites


def websites() -> list[models.Website]:
    """
    All the websites that are registered in your Umami instance.

    Requires authentication: call login() (self-hosted) or set_cloud_api_key()
    (Umami Cloud) first. In self-hosted mode you must also have called
    set_url_base().

    Returns:
        A list of models.Website models, unwrapped from the paged API response.

    Raises:
        OperationNotAllowedError: If set_url_base() has not been called (and no
            Cloud API key is set), or if no credential is present (neither a
            login token nor a Cloud API key).
        httpx.HTTPStatusError: If the Umami API returns a non-2xx response.

    Example:
        ```python
        import umami

        umami.set_url_base('https://umami.example.com')
        umami.login(username, password)
        for site in umami.websites():
            print(site.name, site.domain)
        ```
    """
    global auth_token
    validate_state(url=True, user=True)

    url = _data_url(urls.websites)
    headers = _data_headers()
    resp = httpx.get(url, headers=headers, follow_redirects=True)
    resp.raise_for_status()

    data = resp.json()
    model = models.WebsitesResponse(**data)
    return model.websites


def enable() -> None:
    """
    Enable event and page view tracking.

    When enabled, the send functions new_event(), new_revenue_event(), and
    new_page_view() send data to Umami normally. This is the default state.

    Only the send functions are affected; query and authentication functions
    (such as login(), websites(), website_stats(), active_users(),
    verify_token(), and heartbeat()) always run regardless of this setting.
    Call disable() to turn tracking off.
    """
    global tracking_enabled
    tracking_enabled = True


def disable() -> None:
    """
    Disable event and page view tracking.

    When disabled, the send functions new_event(), new_revenue_event(), and
    new_page_view() still validate their arguments but then return without
    making any HTTP request to Umami. This is useful for development and
    testing environments.

    Only the send functions are affected; query and authentication functions
    (such as login(), websites(), website_stats(), active_users(),
    verify_token(), and heartbeat()) always run regardless of this setting.
    Call enable() to turn tracking back on (the default).
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
    distinct_id: Optional[Union[str, int]] = None,
) -> dict:
    """
    Create a new custom event in Umami for the given website_id and hostname
    (both fall back to the defaults set via set_website_id() and set_hostname()
    when omitted). The event appears in the traffic for the given url and in
    the events section of your Umami website page. Login is not required; you
    only need set_url_base() (self-hosted) or set_cloud_api_key() (Cloud), plus
    a website_id and hostname.

    If tracking has been turned off with disable(), the inputs are still
    validated but no HTTP request is made and an empty dict is returned.

    Args:
        event_name: The name of your custom event (e.g. 'Purchase-Course').
        hostname: Optional hostname identifying the client
            (e.g. 'test_domain.com'); overrides the set_hostname() value.
        url: The URL associated with the event (e.g. '/account/new').
            Defaults to '/'.
        website_id: Optional Umami website ID; overrides the set_website_id()
            value.
        title: The display title of the event. Defaults to event_name when
            omitted.
        custom_data: Additional key/value data sent with the event. Not shown
            in the UI but available through the API. Defaults to an empty dict.
        referrer: The referrer of the client, if any. Defaults to ''.
        language: The language of the event/client. Defaults to 'en-US'.
        screen: The screen resolution of the client. Defaults to '1920x1080'.
        ip_address: Optional true IP address of the user, useful when sending
            events from server-side request handlers.
        distinct_id: Optional Umami distinct ID for the user, as a string or
            integer, sent to the API as the payload field 'id'. Blank or
            whitespace-only values are ignored (no id is sent).

    Returns:
        The JSON response from the Umami API as a dict, or an empty dict if
        tracking is disabled.

    Raises:
        OperationNotAllowedError: If neither set_url_base() nor
            set_cloud_api_key() has been called.
        ValidationError: If hostname or website_id is not set (here or via
            set_hostname()/set_website_id()), or if distinct_id is a bool or
            any type other than str or int.
        httpx.HTTPStatusError: If Umami returns a non-2xx response (only when
            tracking is enabled).

    Example:
        ```python
        import umami

        umami.set_url_base('https://umami.example.com')
        umami.set_website_id('978435e2-7ba1-4337-9860-ec31ece2db60')
        umami.set_hostname('example.com')
        await umami.new_event_async(
            event_name='Purchase-Course',
            url='/checkout',
            custom_data={'plan': 'pro'},
        )
        ```
    """
    validate_state(url=True, user=False)
    website_id = website_id or default_website_id
    hostname = hostname or default_hostname
    title = title or event_name
    custom_data = custom_data or {}
    normalized_distinct_id = normalize_distinct_id(distinct_id)

    validate_event_data(event_name, hostname, website_id)

    # Early return if tracking is disabled
    if not tracking_enabled:
        return {}

    api_url = _send_url()
    headers = _send_headers()

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

    if normalized_distinct_id:
        payload['id'] = normalized_distinct_id

    event_data = {'payload': payload, 'type': 'event'}

    async with httpx.AsyncClient() as client:
        resp = await client.post(api_url, json=event_data, headers=headers, follow_redirects=True)
        resp.raise_for_status()

    return resp.json()


def new_event(
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
    distinct_id: Optional[Union[str, int]] = None,
) -> dict:
    """
    Create a new custom event in Umami for the given website_id and hostname
    (both fall back to the defaults set via set_website_id() and set_hostname()
    when omitted). The event appears in the traffic for the given url and in
    the events section of your Umami website page. Login is not required; you
    only need set_url_base() (self-hosted) or set_cloud_api_key() (Cloud), plus
    a website_id and hostname.

    If tracking has been turned off with disable(), the inputs are still
    validated but no HTTP request is made and an empty dict is returned.

    Args:
        event_name: The name of your custom event (e.g. 'Purchase-Course').
        hostname: Optional hostname identifying the client
            (e.g. 'test_domain.com'); overrides the set_hostname() value.
        url: The URL associated with the event (e.g. '/account/new').
            Defaults to '/'.
        website_id: Optional Umami website ID; overrides the set_website_id()
            value.
        title: The display title of the event. Defaults to event_name when
            omitted.
        custom_data: Additional key/value data sent with the event. Not shown
            in the UI but available through the API. Defaults to an empty dict.
        referrer: The referrer of the client, if any. Defaults to ''.
        language: The language of the event/client. Defaults to 'en-US'.
        screen: The screen resolution of the client. Defaults to '1920x1080'.
        ip_address: Optional true IP address of the user, useful when sending
            events from server-side request handlers.
        distinct_id: Optional Umami distinct ID for the user, as a string or
            integer, sent to the API as the payload field 'id'. Blank or
            whitespace-only values are ignored (no id is sent).

    Returns:
        The JSON response from the Umami API as a dict, or an empty dict if
        tracking is disabled.

    Raises:
        OperationNotAllowedError: If neither set_url_base() nor
            set_cloud_api_key() has been called.
        ValidationError: If hostname or website_id is not set (here or via
            set_hostname()/set_website_id()), or if distinct_id is a bool or
            any type other than str or int.
        httpx.HTTPStatusError: If Umami returns a non-2xx response (only when
            tracking is enabled).

    Example:
        ```python
        import umami

        umami.set_url_base('https://umami.example.com')
        umami.set_website_id('978435e2-7ba1-4337-9860-ec31ece2db60')
        umami.set_hostname('example.com')
        umami.new_event(
            event_name='Purchase-Course',
            url='/checkout',
            custom_data={'plan': 'pro'},
        )
        ```
    """
    validate_state(url=True, user=False)
    website_id = website_id or default_website_id
    hostname = hostname or default_hostname
    title = title or event_name
    custom_data = custom_data or {}
    normalized_distinct_id = normalize_distinct_id(distinct_id)

    validate_event_data(event_name, hostname, website_id)

    # Early return if tracking is disabled
    if not tracking_enabled:
        return {}

    api_url = _send_url()
    headers = _send_headers()

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

    if normalized_distinct_id:
        payload['id'] = normalized_distinct_id

    event_data = {'payload': payload, 'type': 'event'}

    resp = httpx.post(api_url, json=event_data, headers=headers, follow_redirects=True)
    resp.raise_for_status()

    return resp.json()


async def new_revenue_event_async(
    revenue: float,
    currency: str = 'USD',
    event_name: str = 'revenue',
    hostname: Optional[str] = None,
    url: str = '/',
    website_id: Optional[str] = None,
    title: Optional[str] = None,
    custom_data: Optional[Dict[str, Any]] = None,
    referrer: str = '',
    language: str = 'en-US',
    screen: str = '1920x1080',
    ip_address: Optional[str] = None,
    distinct_id: Optional[Union[str, int]] = None,
) -> dict:
    """
    Create a new revenue event in Umami. This is a convenience wrapper around
    new_event_async() that automatically includes the revenue and currency
    properties required by Umami's revenue tracking.

    Requires set_url_base() (or set_cloud_api_key() for Cloud mode) and a
    website_id and hostname, either set globally via
    set_website_id()/set_hostname() or passed here. Login is not required to
    send events. If tracking has been turned off with disable(), the inputs are
    still validated but no HTTP request is made and an empty dict is returned.

    Args:
        revenue: The monetary amount of the transaction. Must be a number
            (int or float) >= 0.
        currency: ISO 4217 currency code (e.g. 'USD', 'EUR'). Must be
            non-empty. Defaults to 'USD'.
        event_name: The name of your custom event. Defaults to 'revenue'.
        hostname: Optional hostname identifying the client (e.g. 'example.com');
            overrides the set_hostname() value.
        url: The URL associated with the event (e.g. '/checkout').
            Defaults to '/'.
        website_id: Optional Umami website ID; overrides the set_website_id()
            value.
        title: The display title of the event. Defaults to event_name when
            omitted.
        custom_data: Additional key/value data sent with the event. The
            'revenue' and 'currency' keys are overwritten by the values above.
        referrer: The referrer of the client, if any. Defaults to ''.
        language: The language of the event/client. Defaults to 'en-US'.
        screen: The screen resolution of the client. Defaults to '1920x1080'.
        ip_address: Optional true IP address of the user, useful when sending
            events from server-side request handlers.
        distinct_id: Optional Umami distinct ID for the user, as a string or
            integer, sent to the API as the payload field 'id'. Blank or
            whitespace-only values are ignored (no id is sent).

    Returns:
        The parsed JSON response from the Umami API as a dict, or an empty dict
        if tracking is disabled.

    Raises:
        ValidationError: If revenue is not a number, revenue is negative,
            currency is empty, distinct_id is an invalid type, or hostname or
            website_id is not set (here or via set_hostname()/set_website_id()).
        OperationNotAllowedError: If neither set_url_base() nor
            set_cloud_api_key() has been called.
        httpx.HTTPStatusError: If the Umami API returns a non-2xx response.

    Example:
        ```python
        import umami

        umami.set_url_base('https://umami.example.com')
        umami.set_website_id('978435e2-7ba1-4337-9860-ec31ece2db60')
        umami.set_hostname('example.com')
        await umami.new_revenue_event_async(
            revenue=19.99,
            currency='USD',
            event_name='checkout-cart',
            url='/checkout',
        )
        ```
    """
    if not isinstance(revenue, (int, float)):
        raise ValidationError('Revenue must be a number (int or float).')
    if revenue < 0:
        raise ValidationError('Revenue must be >= 0.')
    if not currency or not currency.strip():
        raise ValidationError('Currency must be a non-empty string.')

    merged_data = dict(custom_data or {})
    merged_data['revenue'] = revenue
    merged_data['currency'] = currency

    return await new_event_async(
        event_name=event_name,
        hostname=hostname,
        url=url,
        website_id=website_id,
        title=title,
        custom_data=merged_data,
        referrer=referrer,
        language=language,
        screen=screen,
        ip_address=ip_address,
        distinct_id=distinct_id,
    )


def new_revenue_event(
    revenue: float,
    currency: str = 'USD',
    event_name: str = 'revenue',
    hostname: Optional[str] = None,
    url: str = '/',
    website_id: Optional[str] = None,
    title: Optional[str] = None,
    custom_data: Optional[Dict[str, Any]] = None,
    referrer: str = '',
    language: str = 'en-US',
    screen: str = '1920x1080',
    ip_address: Optional[str] = None,
    distinct_id: Optional[Union[str, int]] = None,
) -> dict:
    """
    Create a new revenue event in Umami. This is a convenience wrapper around
    new_event() that automatically includes the revenue and currency
    properties required by Umami's revenue tracking.

    Requires set_url_base() (or set_cloud_api_key() for Cloud mode) and a
    website_id and hostname, either set globally via
    set_website_id()/set_hostname() or passed here. Login is not required to
    send events. If tracking has been turned off with disable(), the inputs are
    still validated but no HTTP request is made and an empty dict is returned.

    Args:
        revenue: The monetary amount of the transaction. Must be a number
            (int or float) >= 0.
        currency: ISO 4217 currency code (e.g. 'USD', 'EUR'). Must be
            non-empty. Defaults to 'USD'.
        event_name: The name of your custom event. Defaults to 'revenue'.
        hostname: Optional hostname identifying the client (e.g. 'example.com');
            overrides the set_hostname() value.
        url: The URL associated with the event (e.g. '/checkout').
            Defaults to '/'.
        website_id: Optional Umami website ID; overrides the set_website_id()
            value.
        title: The display title of the event. Defaults to event_name when
            omitted.
        custom_data: Additional key/value data sent with the event. The
            'revenue' and 'currency' keys are overwritten by the values above.
        referrer: The referrer of the client, if any. Defaults to ''.
        language: The language of the event/client. Defaults to 'en-US'.
        screen: The screen resolution of the client. Defaults to '1920x1080'.
        ip_address: Optional true IP address of the user, useful when sending
            events from server-side request handlers.
        distinct_id: Optional Umami distinct ID for the user, as a string or
            integer, sent to the API as the payload field 'id'. Blank or
            whitespace-only values are ignored (no id is sent).

    Returns:
        The parsed JSON response from the Umami API as a dict, or an empty dict
        if tracking is disabled.

    Raises:
        ValidationError: If revenue is not a number, revenue is negative,
            currency is empty, distinct_id is an invalid type, or hostname or
            website_id is not set (here or via set_hostname()/set_website_id()).
        OperationNotAllowedError: If neither set_url_base() nor
            set_cloud_api_key() has been called.
        httpx.HTTPStatusError: If the Umami API returns a non-2xx response.

    Example:
        ```python
        import umami

        umami.set_url_base('https://umami.example.com')
        umami.set_website_id('978435e2-7ba1-4337-9860-ec31ece2db60')
        umami.set_hostname('example.com')
        umami.new_revenue_event(
            revenue=19.99,
            currency='USD',
            event_name='checkout-cart',
            url='/checkout',
        )
        ```
    """
    if not isinstance(revenue, (int, float)):
        raise ValidationError('Revenue must be a number (int or float).')
    if revenue < 0:
        raise ValidationError('Revenue must be >= 0.')
    if not currency or not currency.strip():
        raise ValidationError('Currency must be a non-empty string.')

    merged_data = dict(custom_data or {})
    merged_data['revenue'] = revenue
    merged_data['currency'] = currency

    return new_event(
        event_name=event_name,
        hostname=hostname,
        url=url,
        website_id=website_id,
        title=title,
        custom_data=merged_data,
        referrer=referrer,
        language=language,
        screen=screen,
        ip_address=ip_address,
        distinct_id=distinct_id,
    )


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
    distinct_id: Optional[Union[str, int]] = None,
) -> dict:
    """
    Create a new page view event in Umami for the given website_id and hostname
    (both fall back to the defaults set via set_website_id() and set_hostname()
    when omitted). This is equivalent to what happens when a visitor views a
    page and the JS library records it.

    Requires set_url_base() (or set_cloud_api_key() for Cloud mode) and a
    website_id and hostname, either set globally via
    set_website_id()/set_hostname() or passed here. Login is not required to
    send page views. If tracking has been turned off with disable(), the input
    is validated but no HTTP request is made and an empty dict is returned.

    Args:
        page_title: The title of the page view to record (required).
        url: The URL of the page view to record (e.g. '/account/new').
        hostname: Optional hostname identifying the client (e.g. 'example.com');
            overrides the set_hostname() value.
        website_id: Optional Umami website ID; overrides the set_website_id()
            value.
        referrer: Optional referrer of the client, if any (the location that
            led them to this page). Defaults to ''.
        language: Optional language of the event/client. Defaults to 'en-US'.
        screen: Optional screen resolution of the client. Defaults to
            '1920x1080'.
        ua: Optional user-agent string of the client. Defaults to a browser
            user-agent because Umami blocks non-browser user agents by default.
        ip_address: Optional true IP address of the user, useful when sending
            page views from server-side request handlers.
        distinct_id: Optional Umami distinct ID for the user, as a string or
            integer, sent to the API as the payload field 'id'. Blank or
            whitespace-only values are ignored (no id is sent).

    Returns:
        The JSON response from the Umami API as a dict, or an empty dict if
        tracking is disabled.

    Raises:
        OperationNotAllowedError: If neither set_url_base() nor
            set_cloud_api_key() has been called.
        ValidationError: If hostname or website_id is not set (here or via
            set_hostname()/set_website_id()), or if distinct_id is a bool or
            any type other than str or int.
        httpx.HTTPStatusError: If Umami returns a non-2xx response (only when
            tracking is enabled).

    Example:
        ```python
        import umami

        umami.set_url_base('https://umami.example.com')
        umami.set_website_id('978435e2-7ba1-4337-9860-ec31ece2db60')
        umami.set_hostname('example.com')
        await umami.new_page_view_async(page_title='Home', url='/')
        ```
    """
    validate_state(url=True, user=False)
    website_id = website_id or default_website_id
    hostname = hostname or default_hostname
    normalized_distinct_id = normalize_distinct_id(distinct_id)

    validate_event_data(event_name='NOT NEEDED', hostname=hostname, website_id=website_id)

    # Early return if tracking is disabled
    if not tracking_enabled:
        return {}

    api_url = _send_url()
    headers = _send_headers(ua=ua)

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

    if normalized_distinct_id:
        payload['id'] = normalized_distinct_id

    event_data = {'payload': payload, 'type': 'event'}

    async with httpx.AsyncClient() as client:
        resp = await client.post(api_url, json=event_data, headers=headers, follow_redirects=True)
        resp.raise_for_status()

    return resp.json()


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
    distinct_id: Optional[Union[str, int]] = None,
) -> dict:
    """
    Create a new page view event in Umami for the given website_id and hostname
    (both fall back to the defaults set via set_website_id() and set_hostname()
    when omitted). This is equivalent to what happens when a visitor views a
    page and the JS library records it.

    Requires set_url_base() (or set_cloud_api_key() for Cloud mode) and a
    website_id and hostname, either set globally via
    set_website_id()/set_hostname() or passed here. Login is not required to
    send page views. If tracking has been turned off with disable(), the input
    is validated but no HTTP request is made and an empty dict is returned.

    Args:
        page_title: The title of the page view to record (required).
        url: The URL of the page view to record (e.g. '/account/new').
        hostname: Optional hostname identifying the client (e.g. 'example.com');
            overrides the set_hostname() value.
        website_id: Optional Umami website ID; overrides the set_website_id()
            value.
        referrer: Optional referrer of the client, if any (the location that
            led them to this page). Defaults to ''.
        language: Optional language of the event/client. Defaults to 'en-US'.
        screen: Optional screen resolution of the client. Defaults to
            '1920x1080'.
        ua: Optional user-agent string of the client. Defaults to a browser
            user-agent because Umami blocks non-browser user agents by default.
        ip_address: Optional true IP address of the user, useful when sending
            page views from server-side request handlers.
        distinct_id: Optional Umami distinct ID for the user, as a string or
            integer, sent to the API as the payload field 'id'. Blank or
            whitespace-only values are ignored (no id is sent).

    Returns:
        The JSON response from the Umami API as a dict, or an empty dict if
        tracking is disabled.

    Raises:
        OperationNotAllowedError: If neither set_url_base() nor
            set_cloud_api_key() has been called.
        ValidationError: If hostname or website_id is not set (here or via
            set_hostname()/set_website_id()), or if distinct_id is a bool or
            any type other than str or int.
        httpx.HTTPStatusError: If Umami returns a non-2xx response (only when
            tracking is enabled).

    Example:
        ```python
        import umami

        umami.set_url_base('https://umami.example.com')
        umami.set_website_id('978435e2-7ba1-4337-9860-ec31ece2db60')
        umami.set_hostname('example.com')
        umami.new_page_view(page_title='Home', url='/')
        ```
    """
    validate_state(url=True, user=False)
    website_id = website_id or default_website_id
    hostname = hostname or default_hostname
    normalized_distinct_id = normalize_distinct_id(distinct_id)

    validate_event_data(event_name='NOT NEEDED', hostname=hostname, website_id=website_id)

    # Early return if tracking is disabled
    if not tracking_enabled:
        return {}

    api_url = _send_url()
    headers = _send_headers(ua=ua)

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

    if normalized_distinct_id:
        payload['id'] = normalized_distinct_id

    event_data = {'payload': payload, 'type': 'event'}

    resp = httpx.post(api_url, json=event_data, headers=headers, follow_redirects=True)
    resp.raise_for_status()

    return resp.json()


def validate_event_data(event_name: str, hostname: Optional[str], website_id: Optional[str]):
    """
    Internal use only.
    """
    if not hostname:
        raise ValidationError('The hostname must be set, either as a parameter here or via set_hostname().')
    if not website_id:
        raise ValidationError('The website_id must be set, either as a parameter here or via set_website_id().')
    if not event_name or not event_name.strip():
        raise ValidationError('The event_name is required.')


async def verify_token_async(check_server: bool = True) -> bool:
    """
    Verify that the currently stored credential is still valid.

    In self-hosted/token mode this checks the auth token obtained from login();
    in Cloud mode it checks the API key set via set_cloud_api_key(). Tokens
    issued by login() are temporary and eventually expire, after which you must
    log in again.

    This function never raises: any error (network failure, missing credential,
    expired or rejected token, non-2xx response) results in a return value of
    False.

    Args:
        check_server: If True (default), contact the server to confirm the
            credential is valid — self-hosted posts to /api/auth/verify, while
            Cloud mode fetches /api/me. If False, perform only a local check
            (equivalent to is_logged_in()) with no network request.

    Returns:
        True if the credential is valid (or, when check_server is False, simply
        present), False otherwise.
    """
    # noinspection PyBroadException
    try:
        global auth_token
        validate_state(url=True, user=True)

        if not check_server:
            return is_logged_in()

        if _is_cloud():
            url = _data_url(urls.me)
            async with httpx.AsyncClient() as client:
                resp = await client.get(url, headers=_data_headers(), follow_redirects=True)
                resp.raise_for_status()
            body = resp.json()
            # /api/me nests username under 'user'; the 'username' check is a defensive fallback.
            return 'user' in body or 'username' in body

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
    Verify that the currently stored credential is still valid.

    In self-hosted/token mode this checks the auth token obtained from login();
    in Cloud mode it checks the API key set via set_cloud_api_key(). Tokens
    issued by login() are temporary and eventually expire, after which you must
    log in again.

    This function never raises: any error (network failure, missing credential,
    expired or rejected token, non-2xx response) results in a return value of
    False.

    Args:
        check_server: If True (default), contact the server to confirm the
            credential is valid — self-hosted posts to /api/auth/verify, while
            Cloud mode fetches /api/me. If False, perform only a local check
            (equivalent to is_logged_in()) with no network request.

    Returns:
        True if the credential is valid (or, when check_server is False, simply
        present), False otherwise.
    """
    # noinspection PyBroadException
    try:
        global auth_token
        validate_state(url=True, user=True)

        if not check_server:
            return is_logged_in()

        if _is_cloud():
            url = _data_url(urls.me)
            resp = httpx.get(url, headers=_data_headers(), follow_redirects=True)
            resp.raise_for_status()
            body = resp.json()
            # /api/me nests username under 'user'; the 'username' check is a defensive fallback.
            return 'user' in body or 'username' in body

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
    Check whether the configured Umami server is reachable and healthy.

    In self-hosted mode this issues a GET to {url_base}/api/heartbeat. In Cloud
    mode (after set_cloud_api_key()), Umami Cloud has no /api/heartbeat
    endpoint, so this performs an authenticated GET on the /me endpoint as a
    liveness check instead.

    Requires set_url_base() (self-hosted) or set_cloud_api_key() (Cloud) to
    have been called first; login() is not required. This function never
    raises: any failure (missing configuration, connection error, or a non-2xx
    response) is caught and reported as False.

    Returns:
        True if the server is reachable and responded successfully; False on
        any error, including when no url_base or Cloud API key has been
        configured.

    Example:
        ```python
        import umami

        umami.set_url_base('https://umami.example.com')
        if not await umami.heartbeat_async():
            print('Umami is unavailable')
        ```
    """
    # noinspection PyBroadException
    try:
        global auth_token
        validate_state(url=True, user=False)

        if _is_cloud():
            # Cloud has no /api/heartbeat; use the authenticated /me endpoint as a liveness check.
            url = _data_url(urls.me)
            async with httpx.AsyncClient() as client:
                resp = await client.get(url, headers=_data_headers(), follow_redirects=True)
                resp.raise_for_status()
            return True

        url = f'{url_base}{urls.heartbeat}'
        headers = {
            'User-Agent': user_agent,
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers, follow_redirects=True)
            resp.raise_for_status()

        return True
    except Exception:
        return False


def heartbeat() -> bool:
    """
    Check whether the configured Umami server is reachable and healthy.

    In self-hosted mode this issues a GET to {url_base}/api/heartbeat. In Cloud
    mode (after set_cloud_api_key()), Umami Cloud has no /api/heartbeat
    endpoint, so this performs an authenticated GET on the /me endpoint as a
    liveness check instead.

    Requires set_url_base() (self-hosted) or set_cloud_api_key() (Cloud) to
    have been called first; login() is not required. This function never
    raises: any failure (missing configuration, connection error, or a non-2xx
    response) is caught and reported as False.

    Returns:
        True if the server is reachable and responded successfully; False on
        any error, including when no url_base or Cloud API key has been
        configured.

    Example:
        ```python
        import umami

        umami.set_url_base('https://umami.example.com')
        if not umami.heartbeat():
            print('Umami is unavailable')
        ```
    """
    # noinspection PyBroadException
    try:
        global auth_token
        validate_state(url=True, user=False)

        if _is_cloud():
            # Cloud has no /api/heartbeat; use the authenticated /me endpoint as a liveness check.
            url = _data_url(urls.me)
            resp = httpx.get(url, headers=_data_headers(), follow_redirects=True)
            resp.raise_for_status()
            return True

        url = f'{url_base}{urls.heartbeat}'
        headers = {
            'User-Agent': user_agent,
        }
        resp = httpx.get(url, headers=headers, follow_redirects=True)
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
    Retrieves the number of currently-active visitors for a specific website.

    Requires authentication: call login() (self-hosted) or set_cloud_api_key()
    (Umami Cloud) first.

    Args:
        website_id: OPTIONAL: The value of your website_id in Umami (overrides
            the set_website_id() value).

    Returns:
        The count of visitors currently active on the website.

    Raises:
        OperationNotAllowedError: If set_url_base() has not been called (and no
            Cloud API key is set), or if no credential is present (neither a
            login token nor a Cloud API key).
        httpx.HTTPStatusError: If the Umami API returns a non-2xx response.
    """
    validate_state(url=True, user=True)

    website_id = website_id or default_website_id

    url = _data_url(urls.websites, f'/{website_id}/active')
    headers = _data_headers()

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers, follow_redirects=True)
        resp.raise_for_status()

    data = resp.json()
    return int(data.get('visitors', data.get('x', 0)))


def active_users(website_id: Optional[str] = None) -> int:
    """
    Retrieves the number of currently-active visitors for a specific website.

    Requires authentication: call login() (self-hosted) or set_cloud_api_key()
    (Umami Cloud) first.

    Args:
        website_id: OPTIONAL: The value of your website_id in Umami (overrides
            the set_website_id() value).

    Returns:
        The count of visitors currently active on the website.

    Raises:
        OperationNotAllowedError: If set_url_base() has not been called (and no
            Cloud API key is set), or if no credential is present (neither a
            login token nor a Cloud API key).
        httpx.HTTPStatusError: If the Umami API returns a non-2xx response.
    """
    validate_state(url=True, user=True)

    website_id = website_id or default_website_id

    url = _data_url(urls.websites, f'/{website_id}/active')
    headers = _data_headers()

    resp = httpx.get(url, headers=headers, follow_redirects=True)
    resp.raise_for_status()

    data = resp.json()
    return int(data.get('visitors', data.get('x', 0)))


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
    Retrieves the statistics for a specific website over a date range.

    Requires authentication: call login() (self-hosted) or set_cloud_api_key()
    (Umami Cloud) first. start_at and end_at are converted to epoch
    milliseconds for the API.

    Args:
        start_at: Start of the date range as a datetime object.
        end_at: End of the date range as a datetime object.
        website_id: OPTIONAL: The value of your website_id in Umami (overrides
            the set_website_id() value).
        url: OPTIONAL: Filter by URL path.
        referrer: OPTIONAL: Filter by referrer.
        title: OPTIONAL: Filter by page title.
        query: OPTIONAL: Filter by query string.
        event: OPTIONAL: Filter by event name.
        host: OPTIONAL: Filter by hostname.
        os: OPTIONAL: Filter by operating system.
        browser: OPTIONAL: Filter by browser.
        device: OPTIONAL: Filter by device (e.g. 'Mobile').
        country: OPTIONAL: Filter by country.
        region: OPTIONAL: Filter by region/state/province.
        city: OPTIONAL: Filter by city.

    Returns:
        A models.WebsiteStats with the aggregated pageviews, visitors, visits,
        bounces, and totaltime for the range, plus an optional comparison.

    Raises:
        OperationNotAllowedError: If set_url_base() has not been called (and no
            Cloud API key is set), or if no credential is present (neither a
            login token nor a Cloud API key).
        httpx.HTTPStatusError: If the Umami API returns a non-2xx response.

    Example:
        ```python
        import datetime
        import umami

        umami.set_url_base('https://umami.example.com')
        await umami.login_async(username, password)
        stats = await umami.website_stats_async(
            start_at=datetime.datetime.now() - datetime.timedelta(days=7),
            end_at=datetime.datetime.now(),
        )
        print(stats.pageviews, stats.visitors)
        ```
    """
    validate_state(url=True, user=True)

    website_id = website_id or default_website_id

    api_url = _data_url(urls.websites, f'/{website_id}/stats')

    headers = _data_headers()
    params = {
        'startAt': int(start_at.timestamp() * 1000),
        'endAt': int(end_at.timestamp() * 1000),
    }
    optional_params: dict[str, Any] = {
        'path': url,  # API filter renamed 'url' -> 'path' (2025-10-07)
        'referrer': referrer,
        'title': title,
        'query': query,
        'event': event,
        'hostname': host,  # API filter renamed 'host' -> 'hostname' (2025-10-07)
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
    Retrieves the statistics for a specific website over a date range.

    Requires authentication: call login() (self-hosted) or set_cloud_api_key()
    (Umami Cloud) first. start_at and end_at are converted to epoch
    milliseconds for the API.

    Args:
        start_at: Start of the date range as a datetime object.
        end_at: End of the date range as a datetime object.
        website_id: OPTIONAL: The value of your website_id in Umami (overrides
            the set_website_id() value).
        url: OPTIONAL: Filter by URL path.
        referrer: OPTIONAL: Filter by referrer.
        title: OPTIONAL: Filter by page title.
        query: OPTIONAL: Filter by query string.
        event: OPTIONAL: Filter by event name.
        host: OPTIONAL: Filter by hostname.
        os: OPTIONAL: Filter by operating system.
        browser: OPTIONAL: Filter by browser.
        device: OPTIONAL: Filter by device (e.g. 'Mobile').
        country: OPTIONAL: Filter by country.
        region: OPTIONAL: Filter by region/state/province.
        city: OPTIONAL: Filter by city.

    Returns:
        A models.WebsiteStats with the aggregated pageviews, visitors, visits,
        bounces, and totaltime for the range, plus an optional comparison.

    Raises:
        OperationNotAllowedError: If set_url_base() has not been called (and no
            Cloud API key is set), or if no credential is present (neither a
            login token nor a Cloud API key).
        httpx.HTTPStatusError: If the Umami API returns a non-2xx response.

    Example:
        ```python
        import datetime
        import umami

        umami.set_url_base('https://umami.example.com')
        umami.login(username, password)
        stats = umami.website_stats(
            start_at=datetime.datetime.now() - datetime.timedelta(days=7),
            end_at=datetime.datetime.now(),
        )
        print(stats.pageviews, stats.visitors)
        ```
    """
    validate_state(url=True, user=True)

    website_id = website_id or default_website_id

    api_url = _data_url(urls.websites, f'/{website_id}/stats')

    headers = _data_headers()
    params = {
        'startAt': int(start_at.timestamp() * 1000),
        'endAt': int(end_at.timestamp() * 1000),
    }
    optional_params: dict[str, Any] = {
        'path': url,  # API filter renamed 'url' -> 'path' (2025-10-07)
        'referrer': referrer,
        'title': title,
        'query': query,
        'event': event,
        'hostname': host,  # API filter renamed 'host' -> 'hostname' (2025-10-07)
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
    if url and not url_base and not _is_cloud():
        raise OperationNotAllowedError('Set a URL base with set_url_base() or call set_cloud_api_key().')

    if user and not auth_token and not _is_cloud():
        raise OperationNotAllowedError('Call login() or set_cloud_api_key() before proceeding.')
