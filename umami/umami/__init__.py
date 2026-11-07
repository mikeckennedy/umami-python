"""
Python client SDK for Umami, the open-source, privacy-preserving web analytics
platform.

This package lets a Python backend send custom events, page views, and revenue
transactions to a self-hosted or Umami Cloud instance, and query basic stats.
It is useful for tracking business-logic events (such as a course purchase)
that have no natural front-end HTML trigger.

The API is a set of module-level functions called as umami.func(...); there is
no client class. Configuration (URL base, website id, hostname, credentials,
and the Cloud API key) is stored as module-global state and set via the set_*,
login, enable, and disable functions.

Two modes are supported:

- Self-hosted: call set_url_base() then login() to obtain a Bearer token.
- Umami Cloud: call set_cloud_api_key() to authenticate with an API key.

Most network operations provide both a synchronous function and an _async twin
with an identical signature (for example new_event and new_event_async).

There is no command-line interface and the package reads no environment
variables; everything is configured at runtime through the functions above.
Input problems raise umami.errors.ValidationError, missing setup raises
umami.errors.OperationNotAllowedError, and non-2xx responses raise
httpx2.HTTPStatusError.

Example:
    ```python
    import umami

    umami.set_url_base('https://umami.example.com')
    umami.login(username, password)
    umami.set_website_id(website_id)
    umami.set_hostname('example.com')

    umami.new_event(
        event_name='checkout-completed',
        title='Checkout',
        url='/checkout',
        custom_data={'plan': 'pro'},
    )
    ```
"""

from . import impl
from . import errors
from . import models
from .impl import active_users, active_users_async
from .impl import heartbeat_async, heartbeat
from .impl import login_async, login, is_logged_in
from .impl import new_event_async, new_event
from .impl import new_revenue_event, new_revenue_event_async
from .impl import new_page_view, new_page_view_async
from .impl import set_url_base, set_website_id, set_hostname
from .impl import set_cloud_api_key, clear_cloud_api_key
from .impl import verify_token_async, verify_token
from .impl import website_stats, website_stats_async
from .impl import websites_async, websites
from .impl import enable, disable

__author__ = 'Michael Kennedy <michael@talkpython.fm>'
__version__ = impl.__version__
user_agent = impl.user_agent

# fmt: off
# ruff: noqa
__all__ = [
    # Core modules
    'models',
    'errors',
    
    # Configuration/Setup
    'set_url_base',
    'set_website_id',
    'set_hostname',
    'set_cloud_api_key',
    'clear_cloud_api_key',
    'enable',
    'disable',
    
    # Authentication
    'login', 
    'login_async', 
    'is_logged_in',
    'verify_token', 
    'verify_token_async',
    
    # Basic operations
    'websites', 
    'websites_async',
    'heartbeat', 
    'heartbeat_async',
    
    # Main features - Events and Analytics
    'new_event',
    'new_event_async',
    'new_revenue_event',
    'new_revenue_event_async',
    'new_page_view',
    'new_page_view_async',
    'website_stats', 
    'website_stats_async',
    'active_users', 
    'active_users_async',
]
# fmt: on
