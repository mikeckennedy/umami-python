# Code issues surfaced by the docstring review (for GitHub triage)

These were found while doing a code-verified docstring pass (2026-06-09). They are **code**
issues, not documentation ones — the docstrings were written to describe *current* behavior, so
the published docs are accurate today. Each item below is a candidate GitHub issue. File:
`umami/umami/impl/__init__.py` unless noted.

Because these are behavior/contract changes, they should land separately from the docstring work
(their own commit/PR, with tests and a changelog entry). After fixing #1 and #2, the corresponding
`Returns:` / `Raises:` docstring sections should be updated to match.

---

## 1. Sync/async send functions return inconsistent types

**Severity:** medium · **Affects twin parity** (CLAUDE.md §3)

`new_event_async` (line 482) is annotated `-> dict` and returns `resp.json()` (or `{}` when
tracking is disabled). Its sync twin `new_event` (line 596) has **no return annotation**, uses a
bare `return` on the disabled path, and has no trailing `return`, so it returns `None` on every
path. The same asymmetry exists for `new_revenue_event` (line 810, returns `new_event(...)` →
`None`) vs `new_revenue_event_async` (line 707, returns the dict). The page-view twins both return
`None`, which is at least consistent.

This looks unintended and breaks the sync/async parity the project otherwise maintains.

**Proposed fix:** have sync `new_event` `return resp.json()` (and `return {}` on the disabled
path), add a `-> dict` annotation, and let `new_revenue_event` return that result. Then update the
sync `Returns:` docstrings (currently "None. The async twin … returns the parsed JSON response dict
instead.") to match the async ones.

---

## 2. `validate_event_data` raises a bare `Exception` instead of `errors.ValidationError`

**Severity:** medium · **Public error contract**

`validate_event_data` (line 1116) raises a plain `Exception` for missing hostname / website_id /
event_name, inconsistent with the rest of the SDK, which uses `errors.ValidationError` /
`OperationNotAllowedError`. Because `new_event`, `new_page_view`, and `new_revenue_event` delegate
to it, a generic `Exception` genuinely propagates — which is why those functions' new `Raises:`
sections honestly list `Exception`.

**Proposed fix:** raise `errors.ValidationError` instead. Then change those functions' `Raises:`
entries from `Exception` to `ValidationError`. Add/adjust a test asserting the exception type.

---

## 3. Dead and crash-prone guard in `validate_event_data`

**Severity:** low (latent) · `umami/umami/impl/__init__.py:1124`

```python
if not event_name and not event_name.strip():
```

This is logically dead: it can only be reached when `event_name` is truthy, so `not event_name` is
already `False` and the branch never fires. It would also raise `AttributeError` if `event_name`
were ever `None`. The page-view callers pass the literal `'NOT NEEDED'`, so it is never exercised
there either.

**Proposed fix:** the `and` should almost certainly be `or` to be a real empty-string check
(`if not event_name or not event_name.strip():`). Pairs naturally with #2.

---

## 4. `Website` model fields `shareId` / `resetAt` / `deletedAt` are required `typing.Any`

**Severity:** low–medium · `umami/umami/models/__init__.py:97,98,102`

These three fields are typed `typing.Any` with **no default**, so the Umami API must always return
those keys or model construction raises `pydantic.ValidationError` inside `websites()` /
`websites_async()`. `tests/test_model_optionality.py` has to pass them explicitly for this reason.
If the API ever omits them, callers get a hard error.

**Proposed fix:** give them `Optional[...] = None` defaults to harden against missing keys. The new
docstring already describes them as "or null" on the assumption the API returns them as `null`.

---

## Design notes (no change required — flagged for awareness)

- **`heartbeat` / `verify_token` can't distinguish "misconfigured" from "server down".** Both call
  `validate_state()` *inside* a `try/except Exception` that returns `False`, so a missing
  `url_base` / Cloud key surfaces as `False` rather than the `OperationNotAllowedError` every other
  function raises for the same condition. This is the intended liveness/validity design; noted only
  in case finer-grained reporting is ever wanted.
- **Optional polish:** adding `pydantic.Field(description=...)` to response-model fields would let
  Great Docs surface per-attribute descriptions beyond the class-level `Attributes:` prose. Also
  worth confirming whether `WebsitesResponse` (never returned to callers) should stay in the
  published "Response models" section.
