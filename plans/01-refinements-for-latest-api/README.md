# `umami-analytics` — refinements

Each document in this folder is a **self-contained unit of work that maps to one commit**. Hand them
to Claude Code one at a time, in order; each lists its own scope, suggested commit message, branch,
the exact code changes, tests to add, and a "done when" checklist.

## Shared context (applies to every unit)

- **Package source root:** `umami/umami/`. The module changed most is
  `umami/umami/impl/__init__.py` (called `impl` below), plus `umami/umami/urls.py` and
  `umami/umami/models/__init__.py`.
- **Companion API reference:** the full Umami HTTP API (paths, params, request/response shapes, the
  two date conventions, filter semantics, enums) is documented in
  `package-guides/umami_reference.md` in the *python-package-guides-for-agents* repo. Use it to verify
  any endpoint detail.
- **Verified against:** the source in this clone and the official Umami API docs (v2.x/v3.x,
  `api.umami.is` changelog through 2026-05-28).
- **Guiding principle:** additive and **zero-breaking**. Existing self-hosted (`login()` + token)
  code must behave identically; new behavior is opt-in.
- **Testing convention:** the package now uses `httpx2` (imported as `import httpx2 as httpx`), a
  hard fork in its own namespace. Tests mock with `unittest.mock` by patching `umami.impl.httpx.*`
  (e.g. `patch('umami.impl.httpx.get')`, or `patch('umami.impl.httpx.AsyncClient')` with an
  `AsyncMock`), which is namespace-agnostic. **Do not use `respx`** — it patches the `httpx`
  namespace and silently fails to intercept `httpx2`, so requests fall through to the real network
  while the test still appears to pass.

## Units of work (commit in this order)

| Order | Document | Commit | What |
|------|----------|--------|------|
| 1 | [`01-api-refresh.md`](01-api-refresh.md) | `fix: refresh wrapped endpoints for current Umami API` | Correctness fixes: async stats date params, `active_users` response field, renamed stat filter keys. |
| 2 | [`02-cloud-auth.md`](02-cloud-auth.md) | `feat: Umami Cloud API-key auth (set_cloud_api_key)` | New `set_cloud_api_key()` + Cloud URL routing & header. Docs-first. Zero breaking changes. |
| 3 | [`03-polish.md`](03-polish.md) | `chore: model optionality + unify event url default` | Optional resilience: make response-model fields optional; unify `new_event` default `url`. |

Units 1 and 2 are the substance. Unit 3 is optional polish — land it only if wanted.

## Future work / backlog (not in this batch)

The library intentionally wraps a subset of the API. High-value additions, roughly prioritized,
for separate future PRs:

- **Reports (run):** `POST /api/reports/{funnel,goal,breakdown,attribution,journey,retention,utm,revenue,performance}`.
  Note: reports use `startDate`/`endDate` **ISO strings** inside a `parameters` object, and filters go
  in a top-level `filters` object — different from the GET stats convention.
- **Sessions & session-data:** `GET /api/websites/:id/sessions[...]`, `session-data/*`.
- **Event data:** `GET /api/websites/:id/event-data[...]`, `events`, `events/stats`.
- **Metrics & series:** `metrics`, `metrics/expanded`, `pageviews`, `events/series`, `active`, `daterange`.
- **Realtime:** `GET /api/realtime/:id`.
- **Batch ingestion:** `POST /api/batch` (array of `/api/send` bodies) for high-volume sending.
- **`identify` / `performance` send types** on `/api/send` (today only `type='event'` is sent).
- **Management:** websites CRUD, teams, users, links, pixels, share pages.

When wrapping these, also add the filters the current API supports that `website_stats` doesn't yet
expose: `language`, `tag`, `distinctId`, `utmSource/Medium/Campaign/Content/Term`, `segment`, `cohort`.
