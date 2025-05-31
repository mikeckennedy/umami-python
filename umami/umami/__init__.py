from umami import impl
from . import errors  # noqa: F401, E402
from . import models  # noqa: F401, E402
from .impl import active_users, active_users_async  # noqa: F401, E402
from .impl import heartbeat_async, heartbeat  # noqa: F401, E402
from .impl import login_async, login, is_logged_in  # noqa: F401, E402
from .impl import new_event_async, new_event  # noqa: F401, E402
from .impl import new_page_view, new_page_view_async  # noqa: F401, E402
from .impl import set_url_base, set_website_id, set_hostname  # noqa: F401, E402
from .impl import verify_token_async, verify_token  # noqa: F401, E402
from .impl import website_stats, website_stats_async  # noqa: F401, E402
from .impl import websites_async, websites  # noqa: F401, E402
from .impl import enable, disable  # noqa: F401, E402

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
    'new_page_view', 
    'new_page_view_async',
    'website_stats', 
    'website_stats_async',
    'active_users', 
    'active_users_async',
]
# fmt: on
