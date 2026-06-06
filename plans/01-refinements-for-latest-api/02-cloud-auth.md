# Unit 2 — Umami Cloud API-key authentication

> **Commit:** `feat: Umami Cloud API-key auth (set_cloud_api_key)`
> **Branch:** `feat/cloud-api-key`
> **Files:** `umami/umami/impl/__init__.py`, `umami/umami/urls.py`, `umami/umami/__init__.py`, `README.md` (and tests)
> **Risk:** medium — additive feature; must preserve exact self-hosted behavior.

Add Umami Cloud support via an API key, with **zero breaking changes** to existing self-hosted
(`login()` + token) usage. See `refinements/README.md` for shared context.

**Write the README section first (see "Documentation" below) — it is the spec for this work.**

---

## The problem in two parts

Cloud differs from self-hosted in **two** independent ways:

1. **Auth header.** Self-hosted uses `Authorization: Bearer <token>` from `login()`. Cloud uses a
   custom header `x-umami-api-key: <key>` and has **no** login step.
2. **URL routing.** Self-hosted hits one host with the `/api` prefix for everything. Cloud splits:
   - **Data / management API:** `https://api.umami.is/v1/...` — `/api` becomes `/v1`, with an
     **optional** region segment: `https://api.umami.is/v1/us` or `.../v1/eu`.
   - **Ingestion:** `https://cloud.umami.is/api/send` — keeps `/api`, different host.

A header-only change is not enough; routing must adapt too.

**Key simplifying fact:** API keys are **Cloud-only** (self-hosted authenticates with
username/password). So `set_cloud_api_key(...)` can *imply* Cloud mode and default both Cloud hosts.
When no key is set, every path behaves exactly as today.

---

## Design

Centralize URL building and auth headers behind small helpers, then route every existing call
through them. When `api_key is None`, the helpers reduce to the **exact** current behavior.

### a) New module state + setter (`impl`)

Add next to the existing module-level state (`url_base`, `auth_token`, …):

```python
api_key: Optional[str] = None
cloud_region: Optional[str] = None  # None | 'us' | 'eu'

# Official Umami Cloud hosts
_CLOUD_DATA_BASE = 'https://api.umami.is/v1'    # data/management API (x-umami-api-key)
_CLOUD_SEND_BASE = 'https://cloud.umami.is/api'  # public ingestion (/send, /batch)
```

```python
def set_cloud_api_key(key: str, region: Optional[str] = None) -> None:
    """
    Authenticate against Umami Cloud with an API key instead of login().

    Enables "Cloud mode": data/management calls are routed to
    https://api.umami.is/v1 and authenticated with the `x-umami-api-key`
    header, and events are sent to https://cloud.umami.is/api/send. You do
    NOT need to call set_url_base() or login() in this mode.

    Args:
        key: Your Umami Cloud API key.
        region: Optional 'us' or 'eu' to pin the data region. Defaults to the
                region of the account that owns the key.
    """
    global api_key, cloud_region
    if not key or not key.strip():
        raise ValidationError('API key must not be empty.')
    if region is not None and region not in ('us', 'eu'):
        raise ValidationError("region must be 'us', 'eu', or None.")
    api_key = key.strip()
    cloud_region = region


def clear_cloud_api_key() -> None:
    """Exit Cloud mode and return to token/self-hosted behavior."""
    global api_key, cloud_region
    api_key = None
    cloud_region = None
```

Export both from `umami/umami/__init__.py` and add to `__all__`:

```python
from .impl import set_cloud_api_key, clear_cloud_api_key  # noqa
# ... add 'set_cloud_api_key', 'clear_cloud_api_key' to __all__ under "Configuration/Setup"
```

### b) Routing + auth helpers (`impl`)

```python
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
        return f'{_CLOUD_DATA_BASE}{region}{rel}{suffix}'                       # .../v1[/region]/x
    return f'{url_base}{path_const}{suffix}'                                    # unchanged self-hosted


def _send_url() -> str:
    """Full URL for the ingestion endpoint (/api/send) in the active mode."""
    if _is_cloud():
        return f'{_CLOUD_SEND_BASE}/send'   # https://cloud.umami.is/api/send
    return f'{url_base}{urls.events}'        # unchanged self-hosted (or cloud-events via set_url_base)


def _data_headers(extra: Optional[dict] = None) -> dict:
    """Auth headers for data/management calls in the active mode."""
    headers = {'User-Agent': user_agent}
    if extra:
        headers.update(extra)
    if _is_cloud():
        headers['x-umami-api-key'] = api_key
    else:
        headers['Authorization'] = f'Bearer {auth_token}'  # identical to today
    return headers


def _send_headers(ua: str = event_user_agent) -> dict:
    """Headers for ingestion calls. Self-hosted unchanged; Cloud send is unauthenticated."""
    headers = {'User-Agent': ua}
    if not _is_cloud():
        headers['Authorization'] = f'Bearer {auth_token}'  # identical to today (may be 'Bearer None')
    return headers
```

> `_send_headers` reproduces today's self-hosted behavior exactly (it always set
> `Authorization: Bearer {auth_token}`, even unauthenticated → literal `Bearer None`). Cloud
> ingestion is public, so no auth is sent. If you want to drop the `Bearer None` artifact, do it as a
> separate, clearly-noted change — not here.

### c) `urls.py` — add the `me` endpoint (for Cloud `verify_token`)

```python
login = '/api/auth/login'
websites = '/api/websites'
events = '/api/send'
verify = '/api/auth/verify'
heartbeat = '/api/heartbeat'
me = '/api/me'          # add this
```

### d) Route existing functions through the helpers

Mechanical replacements (no behavior change when `api_key is None`):

| Function | Before | After |
|---|---|---|
| `login` / `login_async` | `url = f'{url_base}{urls.login}'` | `url = _data_url(urls.login)` |
| `websites` / `_async` | `url = f'{url_base}{urls.websites}'` + inline headers | `url = _data_url(urls.websites)`; `headers = _data_headers()` |
| `active_users` / `_async` | `url = f'{url_base}{urls.websites}/{website_id}/active'` + inline headers | `url = _data_url(urls.websites, f'/{website_id}/active')`; `headers = _data_headers()` |
| `website_stats` / `_async` | `api_url = f'{url_base}{urls.websites}/{website_id}/stats'` + inline headers | `api_url = _data_url(urls.websites, f'/{website_id}/stats')`; `headers = _data_headers()` |
| `new_event` / `_async` | `api_url = f'{url_base}{urls.events}'` + inline headers | `api_url = _send_url()`; `headers = _send_headers()` |
| `new_page_view` / `_async` | `api_url = f'{url_base}{urls.events}'` + inline headers (uses `ua`) | `api_url = _send_url()`; `headers = _send_headers(ua=ua)` |
| `new_revenue_event` / `_async` | (delegates to `new_event`) | no change — inherits the fix |

> Coordinate with Unit 1: `website_stats` / `active_users` are touched in both units. Land Unit 1
> first; this unit then only swaps their URL/header construction for the helpers.

### e) `validate_state` — accept an API key

```python
def validate_state(url: bool = False, user: bool = False):
    if url and not url_base and not _is_cloud():
        raise OperationNotAllowedError('Set a URL base with set_url_base() or call set_cloud_api_key().')
    if user and not auth_token and not _is_cloud():
        raise OperationNotAllowedError('Call login() or set_cloud_api_key() before proceeding.')
```

### f) `is_logged_in` and `verify_token` — recognize Cloud

```python
def is_logged_in() -> bool:
    return auth_token is not None or api_key is not None
```

For `verify_token` / `verify_token_async`, branch for Cloud (no token to verify — validate the key
via `/me` when `check_server`):

```python
def verify_token(check_server: bool = True) -> bool:
    try:
        validate_state(url=True, user=True)
        if not check_server:
            return is_logged_in()
        if _is_cloud():
            url = _data_url(urls.me)                      # GET https://api.umami.is/v1/me
            resp = httpx.get(url, headers=_data_headers(), follow_redirects=True)
            resp.raise_for_status()
            body = resp.json()
            return 'user' in body or 'username' in body
        # self-hosted: unchanged
        url = f'{url_base}{urls.verify}'
        headers = {'User-Agent': event_user_agent, 'Authorization': f'Bearer {auth_token}'}
        resp = httpx.post(url, headers=headers, follow_redirects=True)
        resp.raise_for_status()
        return 'username' in resp.json()
    except Exception:
        return False
```

(Apply the equivalent branch to `verify_token_async`.)

---

## Zero-breaking guarantee

When `api_key is None` (every existing user):

- `_is_cloud()` is `False`.
- `_data_url(c, s)` returns `f'{url_base}{c}{s}'` — identical to the current f-strings.
- `_send_url()` returns `f'{url_base}{urls.events}'` — identical.
- `_data_headers()` returns `{'User-Agent': user_agent, 'Authorization': f'Bearer {auth_token}'}` —
  identical to the inline dicts in the data calls.
- `_send_headers(ua)` returns `{'User-Agent': ua, 'Authorization': f'Bearer {auth_token}'}` —
  identical to the tracking calls (including the `Bearer None` case).
- `validate_state` / `is_logged_in` add `or _is_cloud()` clauses that are always `False`.
- `urls.py` only **gains** `me`; existing constants are untouched.

No public signature changes; new symbols are purely additive.

---

## Documentation — write the project README first (it's the spec)

**Do this before the code.** Add a clearly-labeled **"Umami Cloud"** usage section to `README.md`
(and mirror in `umami/README.md` if that copy is published). The README example is the acceptance
spec — the code is correct when it makes that example work verbatim. It should show:

- `pip install umami-analytics`
- `umami.set_cloud_api_key("your-cloud-api-key", region="eu")` — `region` optional.
- That **no `set_url_base()` and no `login()`** are needed in Cloud mode.
- A data call (`website_stats(...)` / `active_users()`) **and** an event call, noting events go to
  `cloud.umami.is` automatically while data goes to `api.umami.is/v1`.
- A one-line note that the existing **self-hosted (`login()`) usage is unchanged** — keep the current
  self-hosted example as the primary path; present Cloud as a labeled alternative.
- Where to create the key (Umami Cloud → Settings → API keys) and the rate limit (**50 calls / 15s**).
- `umami.clear_cloud_api_key()` to return to self-hosted/token behavior.

Add a Core Features bullet, e.g. `☁️ Authenticate against Umami Cloud with an API key (set_cloud_api_key).`

---

## Cloud usage (the target behavior)

```python
import umami

umami.set_cloud_api_key("your-cloud-api-key", region="eu")  # region optional
umami.set_website_id("your-website-id")

# Data API -> https://api.umami.is/v1/eu/... with x-umami-api-key
print(umami.active_users())
from datetime import datetime, timedelta
end = datetime.now()
print(umami.website_stats(start_at=end - timedelta(days=7), end_at=end).visitors)

# Events -> https://cloud.umami.is/api/send (unauthenticated)
umami.new_event(event_name="purchase", url="/checkout", hostname="example.com")
```

---

## Tests to add

- `set_cloud_api_key()` then `websites()` → request to `https://api.umami.is/v1/websites` with an
  `x-umami-api-key` header and **no** `Authorization` header.
- With `region="eu"`, the path is `.../v1/eu/websites`.
- In Cloud mode, `new_event(...)` posts to `https://cloud.umami.is/api/send` with no auth header.
- `clear_cloud_api_key()` restores self-hosted routing/headers.
- **Regression:** with no API key, a self-hosted `website_stats(...)` request is byte-identical to
  current behavior (URL + headers).

## Done when

- [ ] README "Umami Cloud" section written (the spec) + Core Features bullet.
- [ ] `set_cloud_api_key` / `clear_cloud_api_key` added and exported in `__all__`.
- [ ] `urls.me` added.
- [ ] Routing/auth helpers added; all listed functions routed through them.
- [ ] `validate_state`, `is_logged_in`, `verify_token` (+ async) recognize Cloud mode.
- [ ] Cloud + regression tests pass; existing self-hosted tests unchanged.
