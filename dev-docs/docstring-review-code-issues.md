# Code issues surfaced by the docstring review — RESOLVED 2026-06-09

These were found while doing a code-verified docstring pass and have now been **fixed** (Michael
approved all four plus the model-field polish). This file is kept as a record of what changed and
why. File references are `umami/umami/impl/__init__.py` unless noted.

All changes are covered by tests and recorded in `change-log.md` under `[Unreleased]`. The suite is
138 tests, green; `ruff format`/`ruff check` clean.

---

## 1. Sync/async send functions returned inconsistent types — FIXED

The sync send functions returned `None` while their async twins returned the response `dict`. They
now return the parsed JSON response (and `{}` when tracking is disabled), matching the async twins:

- `new_event` — added `-> dict`, returns `resp.json()` (and `{}` on the disabled path).
- `new_revenue_event` — added `-> dict`; it returns the result of `new_event(...)`, now a dict.
- `new_page_view` and `new_page_view_async` — added `-> dict` and a `return resp.json()` (both
  previously returned `None`); `{}` on the disabled path.

Docstrings (`Returns:`, the disabled-path note) updated to match. Tests:
`tests/test_sync_async_parity.py::TestSendReturnParity` (return-value parity across all three pairs)
and the updated disabled-path assertions in `tests/test_tracking_toggle.py` / `tests/test_revenue.py`
(now assert `{}`).

## 2. `validate_event_data` raised a bare `Exception` — FIXED

It now raises `errors.ValidationError` for missing hostname / website_id / event_name, so callers
can catch it alongside the SDK's other validation errors. The send functions' `Raises:` sections
were updated (the `Exception` entry merged into the `ValidationError` entry). Test:
`tests/test_validate_event_data.py`.

## 3. Dead/crash-prone guard in `validate_event_data` — FIXED

`if not event_name and not event_name.strip():` → `if not event_name or not event_name.strip():`.
Whitespace-only event names are now rejected (previously slipped through), and `None` no longer risks
`AttributeError` (short-circuit). Test: the parametrized blank/whitespace cases in
`tests/test_validate_event_data.py`.

## 4. `Website.shareId` / `resetAt` / `deletedAt` were required `typing.Any` — FIXED

They now default to `None`, so a websites response that omits those keys constructs instead of raising
`pydantic.ValidationError`. Test:
`tests/test_model_optionality.py::TestWebsiteNullableFieldsOptional`.

## Polish: `pydantic.Field(description=...)` on response-model fields — DONE (with a caveat)

Every response-model field now carries a `Field(description=...)`, and `griffe-pydantic` was added as
a dev dependency (`umami/pyproject.toml [dev]`, guarded `python_version >= '3.11'` like great-docs).

**Caveat — verified empirically:** the installed Great Docs (0.13.0) constructs its griffe
`GriffeLoader` **without** an `extensions=` argument and exposes no config knob for it, so it does not
load `griffe-pydantic`. A sentinel test (a `Field` description differing from the docstring text)
confirmed the rendered reference shows the **docstring `Attributes:`** text, not the `Field`
description. So:

- The docstring `Attributes:` sections were **kept** — they are what actually render on the docs site.
- The `Field` descriptions add value today for IDEs / `model_json_schema()` / other tooling, and will
  surface on the docs site once the generator loads the griffe-pydantic extension.
- No regression: rebuilt the site and confirmed the model pages render cleanly (no `FieldInfo` repr
  leaks, no duplicated field docs).

**Open follow-up (Michael's call):** to actually render the `Field` metadata on the docs site, Great
Docs needs to load griffe extensions (e.g. a newer version with extension support, a config option,
or a request upstream). Until then the `Attributes:` sections and `Field` descriptions are maintained
in parallel — a small duplication to be aware of.

---

## Design notes (still no change required)

- **`heartbeat` / `verify_token` can't distinguish "misconfigured" from "server down".** Both call
  `validate_state()` inside a `try/except Exception` that returns `False`. This is the intended
  liveness/validity design; flagged only in case finer-grained reporting is ever wanted.
- **`WebsitesResponse`** is never returned to callers (the SDK unwraps it to the `websites` list) but
  is still listed in the published "Response models" section. Left as-is; worth a glance if trimming
  the reference surface.
