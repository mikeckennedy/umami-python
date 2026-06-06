# Follow-up: distinct_id polish (post-merge of PR #16)

Apply these changes **after** PR #16 (`FEAT: Added distinct_id to new_page_view and new_event`)
has been merged into `main`. They do two things:

1. **Extend `distinct_id` to the revenue events** — `new_revenue_event` and
   `new_revenue_event_async` currently do *not* accept `distinct_id`, even though the
   `distinct_id` tests landed in `test_revenue.py`. Revenue is arguably the place you most
   want a stable user id, so wire it through.
2. **Relocate the `distinct_id` tests** out of `tests/test_revenue.py` (they test
   `new_event` / `new_page_view`, not revenue) into a dedicated `tests/test_distinct_id.py`,
   and introduce a shared `tests/conftest.py` so the autouse setup fixture is available to
   every test module.

All file paths below are relative to the repo root
(`/Users/michaelkennedy/github/mk/umami-python`). The package source lives under `umami/`.

---

## Coordination with `plans/01-refinements-for-latest-api`

This follow-up and the refinements plan touch some of the same files. Recommended order:
**(1) merge PR #16 → (2) this follow-up → (3) plan Unit 1 → Unit 2 → Unit 3.** Two touchpoints
to keep from crossing wires:

- **Unit 3.1 (unify `new_event` default `url`).** This follow-up deliberately *preserves* the
  existing sync `new_revenue_event` default `url='/event-api-endpoint'` (distinct_id is the only
  concern here — do not change url defaults). Unit 3.1 later unifies all four event/revenue
  functions to `url='/'`; it already lists `new_revenue_event` (sync + async) in its scope, so it
  will supersede this default cleanly. No edit needed in either doc — just land this first.
- **Unit 2 (Cloud auth) + the new `conftest.py`.** The `conftest.py` created in Change 2a resets
  only self-hosted state. Unit 2 adds module-level globals (`api_key`, `cloud_region`); when Unit 2
  lands, **extend this fixture to also reset them** (call `clear_cloud_api_key()` in the fixture)
  so a Cloud test can't leak Cloud mode into later tests. Likewise, the optional dev-deps in
  Section 5 below are where Unit 1's `respx` test dependency should also be declared.

---

## 0. Preconditions (verify before editing)

Run these and confirm the expected results — they prove PR #16 is merged and tell you the
exact state to edit against:

```bash
# Helper + param must exist (proves PR #16 merged):
grep -n "def normalize_distinct_id" umami/umami/impl/__init__.py        # 1 hit
grep -n "distinct_id" umami/umami/impl/__init__.py                       # many hits (event + page_view, sync + async)

# The 7 distinct_id tests should currently live in test_revenue.py:
grep -cE "def test_.*distinct_id" umami/tests/test_revenue.py           # 7 test methods

# Union is already imported by PR #16 (so Change 1 needs no import edit):
grep -n "from typing import" umami/umami/impl/__init__.py                # includes Union
```

If `normalize_distinct_id` is **not** found, stop — PR #16 is not merged yet.

> Note: inside `impl`, the import is `import httpx2 as httpx`, so the test patch targets
> `umami.impl.httpx.post` / `umami.impl.httpx.AsyncClient` resolve to the httpx2 module — they
> are correct and intentional, not a leftover from the old `httpx` dependency.

---

## 1. Add `distinct_id` to the revenue events

File: `umami/umami/impl/__init__.py`

The revenue functions are thin wrappers that delegate to `new_event_async` / `new_event`,
both of which already accept `distinct_id` and run it through `normalize_distinct_id`.
So the wrappers only need to **accept** the param and **forward** it — no validation or
payload code here (validation/normalization happens in the delegate).

### 1a. `new_revenue_event_async`

**Signature** — add `distinct_id` as the last parameter, after `ip_address`:

```python
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
```

**Docstring** — insert this line immediately below the `ip_address:` line (above the blank
line that precedes the `Returns:` entry in the async docstring):

```
        distinct_id: OPTIONAL: The Umami distinct ID for the user as a string or integer. Sent to the API as payload field id.
```

**Delegation call** — add `distinct_id=distinct_id,` to the `await new_event_async(...)` call:

```python
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
```

### 1b. `new_revenue_event` (sync)

Make the same three edits to the sync function. **Do not copy the 1a signature block** — the
sync function has a different `url` default (`'/event-api-endpoint'` vs the async `'/'`). The
post-edit signature is:

```python
def new_revenue_event(
    revenue: float,
    currency: str = 'USD',
    event_name: str = 'revenue',
    hostname: Optional[str] = None,
    url: str = '/event-api-endpoint',
    website_id: Optional[str] = None,
    title: Optional[str] = None,
    custom_data: Optional[Dict[str, Any]] = None,
    referrer: str = '',
    language: str = 'en-US',
    screen: str = '1920x1080',
    ip_address: Optional[str] = None,
    distinct_id: Optional[Union[str, int]] = None,
):
```

**Docstring** — the sync docstring's `ip_address:` line is its *last* line (there is no
`Returns:` entry). Append the same `distinct_id:` line right after it.

**Delegation call** — add `distinct_id=distinct_id,` to the `return new_event(...)` call.

> Note: `Union` and `Optional` are already imported (PR #16 added `Union`). No import change needed.
> No change to `umami/umami/__init__.py` is needed either — `new_revenue_event` /
> `new_revenue_event_async` are already re-exported and listed in `__all__`; adding a parameter
> does not affect the public exports.

---

## 2. Relocate the distinct_id tests + shared fixture

### 2a. Create `umami/tests/conftest.py`

Move the autouse setup fixture into a `conftest.py` so it applies to **all** test modules
(pytest auto-discovers `conftest.py`; test files do not import it). This is required because
the autouse fixture currently lives in `test_revenue.py` and would otherwise not run for the
new test module — the new tests would fail with "url_base not set" style errors.

Create the file with exactly this content:

```python
import pytest

import umami


@pytest.fixture(autouse=True)
def _setup_umami():
    """Set up default umami state for all tests."""
    umami.set_url_base('https://example.com')
    umami.set_hostname('test.com')
    umami.set_website_id('test-website-id')
    umami.enable()
    yield
```

### 2b. Remove the now-duplicated fixture from `umami/tests/test_revenue.py`

Delete the `_setup_umami` fixture definition (the `@pytest.fixture(autouse=True)` block near
the top, including its decorator and the `def _setup_umami(): ... yield` body). Leave the
`import` lines intact — `test_revenue.py` still uses `pytest`, `umami`, the mock helpers, and
`ValidationError`.

Do **not** leave a copy in both places: if `test_revenue.py` keeps its own `_setup_umami`,
it shadows the conftest one for that module (harmless but confusing). Remove it.

### 2c. Remove the 7 distinct_id tests from `umami/tests/test_revenue.py`

Delete these methods (they move to the new file):

In `class TestNewRevenueEvent`:
- `test_new_event_includes_distinct_id`
- `test_new_event_normalizes_integer_distinct_id`
- `test_new_event_rejects_invalid_distinct_id_type`
- `test_new_page_view_includes_distinct_id`

In `class TestNewRevenueEventAsync`:
- `test_new_event_async_includes_distinct_id`
- `test_new_page_view_async_includes_distinct_id`
- `test_new_page_view_async_normalizes_integer_distinct_id`

The four `TestNewRevenueEvent` methods above are the first methods in that class (they sit
directly below the fixture removed in 2b and above `test_default_revenue_event`), so 2b + the
four sync deletions can be done as one contiguous removal down to `test_default_revenue_event`.

After this, `test_revenue.py` should contain only genuine revenue tests — **15 total
(11 sync + 4 async)** — and the `test_revenue_currency_override_custom_data` reformat from
PR #16 can stay as-is.

### 2d. Create `umami/tests/test_distinct_id.py`

This holds the 7 relocated tests **plus** 3 new tests covering revenue `distinct_id`
forwarding (added in Change 1) — **10 total: 6 sync + 4 async**. Create with exactly this
content:

```python
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from umami.errors import ValidationError

import umami


def _mock_post():
    """A MagicMock standing in for httpx.post with a JSON-returning response."""
    mock_resp = MagicMock()
    mock_resp.json.return_value = {}
    mock_resp.raise_for_status = MagicMock()
    mock_post = MagicMock(return_value=mock_resp)
    return mock_post


def _mock_async_client():
    """An AsyncMock standing in for httpx.AsyncClient (async context manager)."""
    mock_resp = MagicMock()
    mock_resp.json.return_value = {}
    mock_resp.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.post = AsyncMock(return_value=mock_resp)
    return mock_client


class TestDistinctIdSync:
    """distinct_id handling for the sync event / page_view / revenue functions."""

    def test_new_event_includes_distinct_id(self):
        with patch('umami.impl.httpx.post', _mock_post()) as mock_post:
            umami.new_event(event_name='signup', distinct_id='user-123')
        payload = mock_post.call_args.kwargs['json']['payload']
        assert payload['id'] == 'user-123'

    def test_new_event_normalizes_integer_distinct_id(self):
        with patch('umami.impl.httpx.post', _mock_post()) as mock_post:
            umami.new_event(event_name='signup', distinct_id=12345)
        payload = mock_post.call_args.kwargs['json']['payload']
        assert payload['id'] == '12345'

    def test_new_event_rejects_invalid_distinct_id_type(self):
        with pytest.raises(ValidationError, match='string or integer'):
            umami.new_event(event_name='signup', distinct_id=['bad-type'])  # type: ignore[arg-type]

    def test_new_page_view_includes_distinct_id(self):
        with patch('umami.impl.httpx.post', _mock_post()) as mock_post:
            umami.new_page_view(page_title='Account', url='/account', distinct_id='user-456')
        payload = mock_post.call_args.kwargs['json']['payload']
        assert payload['id'] == 'user-456'

    def test_new_revenue_event_includes_distinct_id(self):
        with patch('umami.impl.httpx.post', _mock_post()) as mock_post:
            umami.new_revenue_event(revenue=19.99, distinct_id='user-789')
        payload = mock_post.call_args.kwargs['json']['payload']
        assert payload['id'] == 'user-789'

    def test_new_revenue_event_normalizes_integer_distinct_id(self):
        with patch('umami.impl.httpx.post', _mock_post()) as mock_post:
            umami.new_revenue_event(revenue=19.99, distinct_id=42)
        payload = mock_post.call_args.kwargs['json']['payload']
        assert payload['id'] == '42'


class TestDistinctIdAsync:
    """distinct_id handling for the async event / page_view / revenue functions."""

    @pytest.mark.asyncio
    async def test_new_event_async_includes_distinct_id(self):
        mock_client = _mock_async_client()
        with patch('umami.impl.httpx.AsyncClient', return_value=mock_client):
            await umami.new_event_async(event_name='signup', distinct_id='user-123')
        payload = mock_client.post.call_args.kwargs['json']['payload']
        assert payload['id'] == 'user-123'

    @pytest.mark.asyncio
    async def test_new_page_view_async_includes_distinct_id(self):
        mock_client = _mock_async_client()
        with patch('umami.impl.httpx.AsyncClient', return_value=mock_client):
            await umami.new_page_view_async(page_title='Account', url='/account', distinct_id='user-456')
        payload = mock_client.post.call_args.kwargs['json']['payload']
        assert payload['id'] == 'user-456'

    @pytest.mark.asyncio
    async def test_new_page_view_async_normalizes_integer_distinct_id(self):
        mock_client = _mock_async_client()
        with patch('umami.impl.httpx.AsyncClient', return_value=mock_client):
            await umami.new_page_view_async(page_title='Account', url='/account', distinct_id=67890)
        payload = mock_client.post.call_args.kwargs['json']['payload']
        assert payload['id'] == '67890'

    @pytest.mark.asyncio
    async def test_new_revenue_event_async_includes_distinct_id(self):
        mock_client = _mock_async_client()
        with patch('umami.impl.httpx.AsyncClient', return_value=mock_client):
            await umami.new_revenue_event_async(revenue=19.99, distinct_id='user-789')
        payload = mock_client.post.call_args.kwargs['json']['payload']
        assert payload['id'] == 'user-789'
```

> The original PR tests were written with `@patch(...)` decorators that inject a `mock_post`
> argument. The version above uses small `_mock_post()` / `_mock_async_client()` helpers with
> `with patch(...)` to cut the per-test boilerplate. Either style works; if you prefer to keep
> the exact original test bodies, just move them verbatim and add the three revenue tests in the
> same decorator style. The assertions (`payload['id'] == ...`) are what matter.

---

## 3. Docs & changelog consistency

### 3a. README revenue example (both copies)

Add a `distinct_id` line to the `new_revenue_event(...)` example in **both**
`README.md` and `umami/README.md` (the repo keeps the root and package READMEs byte-identical
in this region — apply the *exact same* edit to both files). Find the block:

```python
# Track revenue for a transaction
revenue_resp = umami.new_revenue_event(
    revenue=19.99,  # Monetary amount (required)
    currency='USD',  # ISO 4217 currency code, defaults to 'USD'
    event_name='checkout-cart',  # Defaults to 'revenue' if omitted
    url='/checkout',
    custom_data={'product': 'widget', 'quantity': 2})
```

and add `distinct_id='user-123',` (e.g. before `custom_data=...`):

```python
    url='/checkout',
    distinct_id='user-123',  # OPTIONAL: stable per-user id, sent as payload id
    custom_data={'product': 'widget', 'quantity': 2})
```

### 3b. Changelog

In `change-log.md`, under `## [Unreleased]` → `### Added`, broaden the PR #16 entry so it
covers revenue events too. Replace the existing distinct_id line with:

```
- `distinct_id` support in `new_event`, `new_page_view`, and `new_revenue_event` payloads
  (sync and async), sent to Umami as payload field `id`
```

### 3c. Example client (intentionally skipped)

`umami/example_client/client.py` is a demo, not a tested contract, and currently shows neither
`new_revenue_event` nor `distinct_id`. It is intentionally left unchanged here. Add a
`distinct_id` / revenue showcase there only if you want — it is out of scope for this change.

---

## 4. Verify

From the `umami/` directory:

```bash
cd umami

# Tests — expect 25 passing total:
#   test_revenue.py     = 15 (11 sync + 4 async)
#   test_distinct_id.py = 10 (6 sync + 4 async)
uv run --with pytest --with pytest-asyncio --with pydantic --with httpx2 python -m pytest tests/ -q

# Formatting / lint (repo uses ruff; config is the repo-root ruff.toml, single-quote style)
uv run --with ruff ruff format .
uv run --with ruff ruff check .
```

Expected: `25 passed`, and `test_distinct_id.py` is collected as its own module.
Sanity-check the relocation worked (paths are relative to `umami/`, i.e. after `cd umami`):

```bash
grep -cE "def test_.*distinct_id" tests/test_revenue.py   # 0   (all distinct_id tests moved out)
grep -cE "def test_" tests/test_distinct_id.py            # 10  (6 sync + 4 async)
```

> **The async tests depend on `pytest-asyncio` being installed.** The repo configures no
> `asyncio_mode` (pytest runs in strict mode), so the explicit `@pytest.mark.asyncio` markers
> are what make the async tests run — and removing a marker would silently *skip* a test. The
> `--with pytest-asyncio` flag above supplies the plugin for this command; a bare `pytest`
> without it fails the 4 async tests with `Unknown pytest.mark.asyncio`. See the optional
> step 5 to fix this permanently.
>
> `uv run` may also create/refresh an untracked `umami/uv.lock` as a side effect — that's not an
> intended change from this doc; ignore or `rm` it.

---

## 5. (Optional) Persist the async test config

This is a **pre-existing repo gap, not specific to distinct_id**: `umami/pyproject.toml`
declares no test dependencies and no pytest config, so the async tests (the new ones *and* the
existing ones in `test_revenue.py`) only pass when `pytest-asyncio` happens to be on the path.
To make a plain `pytest` work out of the box, add to `umami/pyproject.toml` (or use your
preferred dev-dependency convention):

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"

[dependency-groups]
dev = ["pytest", "pytest-asyncio"]
```

With `asyncio_mode = "auto"` the `@pytest.mark.asyncio` decorators become optional (existing
markers still work). This touches test infrastructure repo-wide, so decide on it separately
from the distinct_id change — it is not required for the tests above to pass under the given
`uv run` command.
