from umami import impl
from . import errors  # noqa: F401, E402
from . import models  # noqa: F401, E402
from .impl import login_async, login, is_logged_in, heartbeat  # noqa: F401, E402
from .impl import new_event_async, new_event  # noqa: F401, E402
from .impl import new_page_view, new_page_view_async  # noqa: F401, E402
from .impl import set_url_base, set_website_id, set_hostname  # noqa: F401, E402
from .impl import verify_token_async, verify_token  # noqa: F401, E402
from .impl import websites_async, websites  # noqa: F401, E402

__author__ = 'Michael Kennedy <michael@talkpython.fm>'
__version__ = impl.__version__
user_agent = impl.user_agent

__all__ = [
    models,
    errors,
    set_url_base, set_website_id, set_hostname,
    login_async, login, is_logged_in,
    websites_async, websites,
    new_event_async, new_event,
    new_page_view, new_page_view_async,
    verify_token_async, verify_token,
    heartbeat,
]
