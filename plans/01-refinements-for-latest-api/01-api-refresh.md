# Unit 1 — API refresh (correctness fixes)

> **Commit:** `fix: refresh wrapped endpoints for current Umami API`
> **Branch:** `fix/api-refresh`
> **File:** `umami/umami/impl/__init__.py` (and tests)
> **Risk:** low — three localized fixes, no signature changes.

Three correctness/staleness fixes that bring the already-wrapped endpoints back in line with the
current Umami API. See `refinements/README.md` for shared context. No public API changes.

---

## 1.1 — `website_stats_async` sends snake_case date params

In `website_stats_async`, the `params` dict uses snake_case:

```python
params = {
    'start_at': int(start_at.timestamp() * 1000),
    'end_at': int(end_at.timestamp() * 1000),
}
```

The sync `website_stats` already does it correctly (`startAt` / `endAt`).

**Why it's wrong:** `GET /api/websites/:id/stats` reads `startAt` / `endAt` (camelCase). Unknown
query params are ignored, so the async path silently returns **all-time** stats regardless of the
date range.

**Fix:** change the async dict to match the sync one:

```python
params = {
    'startAt': int(start_at.timestamp() * 1000),
    'endAt': int(end_at.timestamp() * 1000),
}
```

---

## 1.2 — `active_users()` reads the wrong response field

At the end of both `active_users` and `active_users_async`:

```python
return int(resp.json().get('x', 0))
```

**Why it's wrong:** `GET /api/websites/:id/active` returns `{"visitors": 5}` in current Umami, not
`{"x": N}`. As written, the function always returns `0`.

**Fix (defensive — prefers the current key, tolerates an old one):** apply to both variants:

```python
data = resp.json()
return int(data.get('visitors', data.get('x', 0)))
```

---

## 1.3 — stats filters use renamed query params (`url` → `path`, `host` → `hostname`)

In the `optional_params` dict in **both** `website_stats` and `website_stats_async`:

```python
optional_params: dict[str, Any] = {
    'url': url,
    ...
    'host': host,
    ...
}
```

**Why it's wrong:** the 2025-10-07 API change renamed the **filter** keys `url → path` and
`host → hostname` (other keys unchanged). Filtering by URL or hostname is currently a silent no-op.

**Fix (keep the function signature — zero breaking for callers):** keep the `url` / `host` keyword
arguments, but map them to the correct wire names:

```python
optional_params: dict[str, Any] = {
    'path': url,          # API filter renamed 'url' -> 'path' (2025-10-07)
    'referrer': referrer,
    'title': title,
    'query': query,
    'event': event,
    'hostname': host,     # API filter renamed 'host' -> 'hostname' (2025-10-07)
    'os': os,
    'browser': browser,
    'device': device,
    'country': country,
    'region': region,
    'city': city,
}
```

*Optional follow-up (still non-breaking):* add `path` / `hostname` parameters as the preferred names,
keep `url` / `host` as deprecated aliases (`path = path or url`) with a `DeprecationWarning`. Adding
the other supported filters (`language`, `tag`, `distinctId`, `utm*`, `segment`, `cohort`) is left to
the backlog.

---

## Tests to add

Use `unittest.mock` (the existing house style), **not `respx`** — see the testing note in the
shared-context README. Patch the HTTP entry point and assert on the captured `params=` kwarg:
the sync stats/active calls use `httpx.get` directly (`patch('umami.impl.httpx.get')`); the async
ones use `httpx.AsyncClient(...).get` (`patch('umami.impl.httpx.AsyncClient', return_value=mock_client)`
where `mock_client.get` is an `AsyncMock`).

- **Async stats dates:** call `website_stats_async`, then assert `mock_client.get.call_args.kwargs['params']`
  contains `'startAt'` and `'endAt'` (and **not** `'start_at'`).
- **active_users field:** `mock_resp.json.return_value = {'visitors': 5}`; assert `active_users()` and
  `active_users_async()` both return `5`.
- **Filter names:** call `website_stats(url='/pricing', host='example.com', ...)`; assert the captured
  `params` has `params['path'] == '/pricing'` and `params['hostname'] == 'example.com'`.

> The stats tests build `models.WebsiteStats(**resp.json())`, so `mock_resp.json()` must return a
> **valid** stats shape (including `comparison`) or construction raises. Either supply a minimal
> stats fixture, or land Unit 3.2 (`comparison` optional) first so the fixture can be tiny.

## Done when

- [ ] Async `website_stats_async` sends `startAt`/`endAt`.
- [ ] Both `active_users` variants read `visitors`.
- [ ] Both `website_stats` variants send `path`/`hostname` for the `url`/`host` kwargs.
- [ ] New tests pass; existing tests unchanged.
