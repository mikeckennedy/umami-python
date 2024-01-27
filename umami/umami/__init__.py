from umami import impl

from . import (
    errors,  # noqa: F401, E402
    models,  # noqa: F401, E402
)
from .impl import (  # noqa: F401, E402  # noqa: F401, E402  # noqa: F401, E402  # noqa: F401, E402  # noqa: F401, E402  # noqa: F401, E402
    login,
    login_async,
    new_event,
    new_event_async,
    new_page_view,
    new_page_view_async,
    set_hostname,
    set_url_base,
    set_website_id,
    verify_token,
    verify_token_async,
    websites,
    websites_async,
)

__author__ = 'Michael Kennedy <michael@talkpython.fm>'
__version__ = impl.__version__
user_agent = impl.user_agent

__all__ = [
    models,
    errors,
    set_url_base, set_website_id, set_hostname,
    login_async, login,
    websites_async, websites,
    new_event_async, new_event,
    new_page_view, new_page_view_async,
    verify_token_async, verify_token,
]
