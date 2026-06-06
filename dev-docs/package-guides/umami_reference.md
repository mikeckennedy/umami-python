# Umami Analytics API — Comprehensive Reference

> Umami is a privacy-focused, open-source web analytics platform (a Google Analytics alternative). Everything you can do in the Umami dashboard is available over a JSON HTTP API: managing websites, users, and teams; pulling stats, metrics, sessions, and event data; running attribution/funnel/journey/retention/revenue reports; and ingesting page views and custom events from any backend. This guide documents the full HTTP surface so you can build a client against it in any language. The official clients are JavaScript/TypeScript (`@umami/api-client`, `@umami/node`); for Python, the community `umami-analytics` package wraps the most common calls, and this guide documents the full REST surface so you can reach everything beyond that.

> Verified against the official Umami API documentation (`api.umami.is`), API changelog through **2026-05-28**. Applies to self-hosted Umami **v2.x / v3.x** and **Umami Cloud**. All data is returned as JSON.

---

## Table of contents

- [Installation & scope](#installation--scope)
- [Base URLs](#base-urls)
- [Authentication](#authentication)
  - [Self-hosted: token login](#self-hosted-token-login)
  - [Umami Cloud: API key](#umami-cloud-api-key)
  - [Rate limits & restricted routes (Cloud)](#rate-limits--restricted-routes-cloud)
- [API conventions](#api-conventions)
  - [Response shapes](#response-shapes)
  - [Pagination & search](#pagination--search)
  - [Two date conventions (read this)](#two-date-conventions-read-this)
  - [Filters](#filters)
  - [Time unit buckets](#time-unit-buckets)
  - [Enums & magic numbers](#enums--magic-numbers)
- [Quick start (Python)](#quick-start-python)
- [Python client: umami-analytics](#python-client-umami-analytics)
- [Endpoint reference](#endpoint-reference)
  - [Authentication endpoints](#authentication-endpoints)
  - [Me](#me)
  - [Users (admin)](#users-admin)
  - [Teams](#teams)
  - [Websites](#websites)
  - [Website statistics](#website-statistics)
  - [Events & event data](#events--event-data)
  - [Sessions & session data](#sessions--session-data)
  - [Realtime](#realtime)
  - [Reports (CRUD)](#reports-crud)
  - [Reports (dynamic / run)](#reports-dynamic--run)
  - [Revenue](#revenue)
  - [Links](#links)
  - [Pixels](#pixels)
  - [Share pages](#share-pages)
  - [Admin](#admin)
  - [Sending stats (ingestion)](#sending-stats-ingestion)
- [Common patterns](#common-patterns)
- [Official clients (JS/TS)](#official-clients-jsts)
- [Appendix: API changelog highlights](#appendix-api-changelog-highlights)

---

## Installation & scope

There is **nothing to install** for the HTTP API itself — it's a REST API you call over HTTPS. For Python, the examples here use [`requests`](https://requests.readthedocs.io/) (sync) or [`httpx`](https://www.python-httpx.org/) (sync/async):

```bash
pip install requests        # or: pip install httpx
```

The API splits cleanly into two surfaces:

| Surface | Purpose | Auth |
| --- | --- | --- |
| **Data / management API** (`/api/...`) | Query stats, manage websites/users/teams, run reports | Bearer token (self-hosted) or API key (Cloud) |
| **Ingestion API** (`/api/send`, `/api/batch`) | Send page views and custom events from a server/app | **No token** — but a valid `User-Agent` header is required |

---

## Base URLs

The base URL depends on whether you self-host or use Umami Cloud.

| Deployment | Data / management API base | Ingestion endpoint |
| --- | --- | --- |
| **Self-hosted** | `http://<your-instance>/api` | `http://<your-instance>/api/send` |
| **Umami Cloud** | `https://api.umami.is/v1` | `https://cloud.umami.is/api/send` |

Notes:

- On Cloud the data API lives under the **`/v1`** prefix (`https://api.umami.is/v1`). Self-hosted has no version prefix — endpoints sit directly under `/api`.
- **Cloud region pinning** is optional. The region defaults to the region of the account that owns the API key. To force a region, append it directly after the `/v1` base as the next path segment: `https://api.umami.is/v1/us` or `https://api.umami.is/v1/eu`.
- Throughout this reference, endpoint paths are written in the self-hosted form (`/api/websites`, …). On Cloud, replace the `/api` base with `https://api.umami.is/v1` (so `/api/websites` → `https://api.umami.is/v1/websites`).
- Path parameters are shown as `:websiteId`, `:userId`, etc.

---

## Authentication

### Self-hosted: token login

Self-hosted instances use a username/password login that returns a **JWT bearer token**.

**`POST /api/auth/login`** — exchange credentials for a token.

Request body:

```json
{
  "username": "your-username",
  "password": "your-password"
}
```

Response:

```json
{
  "token": "eyTMjU2IiwiY...4Q0JDLUhWxnIjoiUE_A",
  "user": {
    "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "username": "admin",
    "role": "admin",
    "createdAt": "2000-00-00T00:00:00.000Z",
    "isAdmin": true
  }
}
```

Send the token on every subsequent request via an `Authorization` header:

```http
Authorization: Bearer eyTMjU2IiwiY...4Q0JDLUhWxnIjoiUE_A
```

```shell
curl https://your-umami.example.com/api/websites \
  -H "Accept: application/json" \
  -H "Authorization: Bearer <token>"
```

**`POST /api/auth/verify`** — check whether a token is still valid. Returns the current user (including `teams`):

```json
{
  "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "username": "admin",
  "role": "admin",
  "createdAt": "2000-00-00T00:00:00.000Z",
  "isAdmin": true,
  "teams": []
}
```

### Umami Cloud: API key

Umami Cloud does **not** use the login flow. Generate an API key in the dashboard (Settings → API keys) and pass it in a custom header on every request:

```http
x-umami-api-key: <api-key>
```

```shell
curl https://api.umami.is/v1/websites \
  -H "Accept: application/json" \
  -H "x-umami-api-key: <api-key>"
```

Every route in this reference is available on Cloud via the API key, **except** the restricted routes below.

### Rate limits & restricted routes (Cloud)

- **Rate limit:** each API key is limited to **50 calls every 15 seconds**. Build ret/backoff into batch jobs (see [Common patterns](#common-patterns)).
- **Restricted routes** (not available with a Cloud API key):

  ```text
  /me/password
  /users
  /users/*
  ```

  User management and password changes are self-hosted/admin-only.

---

## API conventions

### Response shapes

A few shapes recur across the whole API:

- **Single object** — `GET`/`POST` of one entity returns that entity directly (e.g. a website object).
- **Paginated list** — list endpoints return an envelope:

  ```json
  { "data": [ /* items */ ], "count": 923, "page": 1, "pageSize": 20 }
  ```

  Some admin list endpoints also include `"orderBy"`.
- **Delete** — delete endpoints return `{ "ok": true }`.
- **Time series** — series endpoints return arrays of `{ "x": ..., "y": ... }` or `{ "t": ..., "y": ... }` points (`x`/`t` = label or timestamp, `y` = count).

### Pagination & search

List endpoints accept these query parameters:

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `page` | number | `1` | Page number (1-based). |
| `pageSize` | number | `20` | Results per page. (Some endpoints document no fixed default beyond the server's; treat `20` as typical.) |
| `search` | string | — | Free-text search (where supported). |

The response echoes `page` and `pageSize` and includes `count` (total matching rows) so you can compute how many pages remain.

### Two date conventions (read this)

This is the single most common source of client bugs. **Umami uses two different date formats depending on the endpoint family:**

| Endpoint family | Parameter names | Format | Where |
| --- | --- | --- | --- |
| `GET /api/websites/:id/*` stats, events, sessions, realtime, revenue | `startAt`, `endAt` | **Unix milliseconds** (integer) | query string |
| `POST /api/reports/*` (attribution, breakdown, funnel, goal, journey, performance, retention, revenue, utm) | `startDate`, `endDate` | **ISO 8601 strings** | inside the `parameters` object of the JSON body |

Examples:

```text
GET  /api/websites/abc/stats?startAt=1739577600000&endAt=1739664000000
POST /api/reports/funnel    body: { ..., "parameters": { "startDate": "2025-07-23T07:00:00.000Z", "endDate": "2025-10-22T06:59:59.999Z", ... } }
```

In Python, convert a `datetime` to the millisecond form with `int(dt.timestamp() * 1000)` and to the ISO form with `dt.isoformat()`.

### Filters

Most query/stat/report endpoints support a shared set of **filters**. Where this reference notes "supports filters", you may add any of:

| Filter | Type | Description |
| --- | --- | --- |
| `path` | string | URL path. (Formerly `url` — renamed 2025-10-07.) |
| `referrer` | string | Referrer. |
| `title` | string | Page title. |
| `query` | string | Query-parameter value. |
| `browser` | string | Browser. |
| `os` | string | Operating system. |
| `device` | string | Device type (e.g. `mobile`, `desktop`, `laptop`). |
| `country` | string | Country code. |
| `region` | string | Region/state/province. |
| `city` | string | City. |
| `language` | string | Browser language (e.g. `en-US`). |
| `hostname` | string | Hostname. (Formerly `host` — renamed 2025-10-07.) |
| `tag` | string | Tag. |
| `event` | string | Event name. |
| `distinctId` | string | Distinct (logged-in user) ID. |
| `utmSource` | string | UTM source. |
| `utmMedium` | string | UTM medium. |
| `utmCampaign` | string | UTM campaign. |
| `utmContent` | string | UTM content. |
| `utmTerm` | string | UTM term. |
| `segment` | uuid | Saved segment ID (v3.0.0+). |
| `cohort` | uuid | Saved cohort ID (v3.0.0+). |

**How filters are passed depends on the HTTP method:**

- **`GET` endpoints** (stats, events, sessions, metrics, …): pass each filter as its **own query-string parameter**, e.g. `?startAt=...&endAt=...&os=Mac OS&country=US`.
- **`POST /api/reports/*` endpoints**: pass them as a single **`filters` object** at the top level of the JSON body, e.g. `{ "websiteId": "...", "type": "funnel", "filters": { "os": "Mac OS", "device": "desktop" }, "parameters": { ... } }`.

Segments and cohorts are saved filter sets created in the dashboard; reference them by UUID via the `segment` / `cohort` filters.

### Time unit buckets

Endpoints that return time series accept a `unit` parameter that controls bucket size. Umami auto-promotes to the next-largest unit if the range exceeds the maximum:

| `unit` | Maximum range before promotion |
| --- | --- |
| `minute` | up to 60 minutes |
| `hour` | up to 30 days |
| `day` | up to 6 months |
| `month` | no limit |
| `year` | no limit |

Series endpoints also typically accept a `timezone` (e.g. `America/Los_Angeles`).

### Enums & magic numbers

Several fields use integer or string enums:

| Concept | Values |
| --- | --- |
| **Event `type`** (ingestion `/api/send`) | `event`, `identify`, `performance` |
| **`eventType`** (in event/activity responses) | `1` = pageview, `2` = custom event |
| **Event-data `dataType`** | `1` = string, `2` = number, `3` = date, `4` = boolean |
| **User `role`** | `admin`, `user`, `view-only` |
| **Team member `role`** | `team-owner` (creator), `team-manager`, `team-member`, `team-view-only` |
| **Share `shareType`** | `1` = website, `2` = link, `3` = pixel, `4` = board |
| **Report `type`** (saved reports) | `attribution`, `breakdown`, `funnel`, `goal`, `journey`, `retention`, `revenue`, `utm` |
| **`compare`** (period comparison) | `prev` (previous period), `yoy` (year-over-year) |

---

## Quick start (Python)

Self-hosted (token auth), pull summarized stats for the last 24 hours:

```python
import time
import requests

BASE = "https://your-umami.example.com/api"
WEBSITE_ID = "your-website-id"

# 1. Log in for a bearer token.
token = requests.post(
    f"{BASE}/auth/login",
    json={"username": "admin", "password": "your-password"},
).json()["token"]

headers = {"Authorization": f"Bearer {token}"}

# 2. Query stats. startAt/endAt are Unix milliseconds.
now_ms = int(time.time() * 1000)
day_ago_ms = now_ms - 24 * 60 * 60 * 1000

stats = requests.get(
    f"{BASE}/websites/{WEBSITE_ID}/stats",
    headers=headers,
    params={"startAt": day_ago_ms, "endAt": now_ms},
).json()

print(stats["pageviews"], stats["visitors"], stats["visits"])
```

Umami Cloud (API key) — same calls, different base and header, no login:

```python
import requests

BASE = "https://api.umami.is/v1"
headers = {"x-umami-api-key": "your-api-key"}

websites = requests.get(f"{BASE}/websites", headers=headers).json()
print(websites["data"])
```

---

## Python client: `umami-analytics`

For Python, the community **[`umami-analytics`](https://github.com/mikeckennedy/umami-python)** package (by Michael Kennedy) is the most direct way in. It's built on `httpx` and `pydantic`, ships **sync and async** variants of every networked call (`func()` and `func_async()`), and deliberately wraps the **subset most apps need** — sending events/page views/revenue, listing websites, summarized stats, active users, and auth. Configuration and the auth token are held at module level, so most calls take no boilerplate.

```bash
pip install umami-analytics
```

```python
import umami

umami.set_url_base("https://your-umami.example.com")   # base WITHOUT the trailing /api
login = umami.login("admin", "your-password")           # not required just to send events
umami.set_website_id("your-website-id")                 # default for subsequent calls
umami.set_hostname("example.com")                       # default hostname

# Send a custom event (no login required). distinct_id maps to the payload `id`.
umami.new_event(
    event_name="purchase-course",
    url="/checkout/complete",
    custom_data={"course": "python-101"},
    distinct_id="user-123",
)

# Track revenue — wraps new_event() and adds revenue/currency to the event data.
umami.new_revenue_event(revenue=19.99, currency="USD", event_name="checkout", url="/checkout")

# Record a page view.
umami.new_page_view(page_title="Dashboard", url="/dashboard", distinct_id="user-123")

# Pull summarized stats: datetimes in, a typed pydantic model out.
from datetime import datetime, timedelta
end = datetime.now()
stats = umami.website_stats(start_at=end - timedelta(days=7), end_at=end)
print(stats.pageviews, stats.visitors, stats.bounces)

print(umami.active_users())   # -> int
print(umami.websites())       # -> list[Website] (pydantic models)
```

Coverage map (every networked call also has an `_async` twin, e.g. `new_event_async`):

| Function | Endpoint | Notes |
| --- | --- | --- |
| `set_url_base` / `set_website_id` / `set_hostname` | — | Module-level config and defaults. |
| `enable()` / `disable()` | — | Toggle tracking; when disabled, `new_*` calls no-op (still validate). |
| `login(username, password)` | `POST /api/auth/login` | Caches the bearer token; returns a `LoginResponse` with `.token`. |
| `verify_token(check_server=True)` | `POST /api/auth/verify` | Returns `bool`. |
| `is_logged_in()` | — | Whether a token is cached. |
| `websites()` | `GET /api/websites` | Returns `list[Website]`. |
| `website_stats(start_at, end_at, ...)` | `GET /api/websites/:id/stats` | `datetime` args; returns a `WebsiteStats` model. Optional filter kwargs. |
| `active_users()` | `GET /api/websites/:id/active` | Returns `int`. |
| `new_event(event_name, url, ...)` | `POST /api/send` (`type=event`) | Custom event; no auth needed. `distinct_id` → payload `id`. |
| `new_page_view(page_title, url, ...)` | `POST /api/send` | Page view (no event name). |
| `new_revenue_event(revenue, currency, ...)` | `POST /api/send` | Adds `revenue`/`currency` to the event data. |
| `heartbeat()` | `POST /api/heartbeat` | Server-reachability check. |

**Beyond the wrapped subset** — reports, sessions, event data, metrics/pageview series, realtime, teams, users, links, pixels, and share pages — call the HTTP API directly. After `umami.login(...)` you already have a token; a thin helper plus the two date converters (for the [ms-vs-ISO split](#two-date-conventions-read-this)) is all you need:

```python
import httpx
from datetime import datetime, timezone

BASE = "https://your-umami.example.com/api"          # or https://api.umami.is/v1 on Cloud
HEADERS = {"Authorization": f"Bearer {login.token}"}  # from umami.login(...) above
# On Umami Cloud instead: HEADERS = {"x-umami-api-key": "your-api-key"}

def to_ms(dt: datetime) -> int:
    """GET stats/sessions/events/revenue endpoints want Unix milliseconds."""
    return int(dt.timestamp() * 1000)

def to_iso(dt: datetime) -> str:
    """POST /reports/* endpoints want ISO strings inside `parameters`."""
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

def api_get(path: str, **params):
    r = httpx.get(f"{BASE}{path}", headers=HEADERS, params=params, follow_redirects=True)
    r.raise_for_status()
    return r.json()

def api_post(path: str, body):
    r = httpx.post(f"{BASE}{path}", headers=HEADERS, json=body, follow_redirects=True)
    r.raise_for_status()
    return r.json()
```

---

## Endpoint reference

Below, every endpoint is listed with its method, path, parameters, request body (for writes), and a representative response. Large response payloads are trimmed to show structure. Unless noted, data/management endpoints require auth (bearer token or API key).

### Authentication endpoints

```text
POST /api/auth/login     # → { token, user }
POST /api/auth/verify    # → current user (+ teams)
```

See [Authentication](#authentication) above for bodies and responses. `auth/login` is the only endpoint that does not require an existing credential on self-hosted.

---

### Me

Information about the currently authenticated principal.

```text
GET /api/me              # account/session info for your token/key
GET /api/me/teams        # your teams (paginated)
GET /api/me/websites     # your websites (paginated)
```

**`GET /api/me`**

```json
{
  "token": "xxxxxxxxxxxxxxx",
  "authKey": "auth:xxxxxxxxxxxxxxx",
  "shareToken": null,
  "user": {
    "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "username": "member",
    "role": "user",
    "createdAt": "2025-10-08T18:03:19.823Z",
    "isAdmin": false
  }
}
```

**`GET /api/me/websites`**

| Parameter | Type | Description |
| --- | --- | --- |
| `includeTeams` | boolean | Include websites where you are the team owner. |

Returns a paginated list of website objects (same shape as [Websites](#websites)).

**`GET /api/me/teams`** — paginated list of teams you belong to, each with `members` and a `_count` of `{ websites, members }`.

---

### Users (admin)

Self-hosted, admin-only. **Not available on Umami Cloud** (`/users` and `/users/*` are restricted).

```text
POST   /api/users                    # create a user
GET    /api/users/:userId            # get a user
POST   /api/users/:userId            # update a user
DELETE /api/users/:userId            # delete a user
GET    /api/users/:userId/websites   # websites owned by the user (paginated)
GET    /api/users/:userId/teams      # teams the user belongs to (paginated)
```

**`POST /api/users`** — create a user.

| Parameter | Type | Description |
| --- | --- | --- |
| `username` | string | The user's username. |
| `password` | string | The user's password. |
| `role` | string | One of `admin`, `user`, `view-only`. |
| `id` | string | (optional) Force a specific UUID. |

Request / response:

```json
// body
{ "username": "member", "password": "umami", "role": "user" }
// response
{ "id": "xxxxxxxx-...", "username": "member", "role": "user" }
```

**`POST /api/users/:userId`** — update. All fields optional: `username`, `password`, `role`.

**`GET /api/users/:userId`** → `{ id, username, role, createdAt }`.

**`DELETE /api/users/:userId`** → `{ "ok": true }`.

**`GET /api/users/:userId/websites`** — params: `includeTeams`, `search`, `page`, `pageSize`. Paginated website list.

**`GET /api/users/:userId/teams`** — params: `page`, `pageSize`. Paginated team list.

---

### Teams

```text
GET    /api/teams                          # all teams (paginated)
POST   /api/teams                          # create a team
POST   /api/teams/join                     # join a team via access code
GET    /api/teams/:teamId                  # get a team (+ members)
POST   /api/teams/:teamId                  # update a team
DELETE /api/teams/:teamId                  # delete a team
GET    /api/teams/:teamId/users            # team members (paginated)
POST   /api/teams/:teamId/users            # add a user to the team
GET    /api/teams/:teamId/users/:userId    # get one member
POST   /api/teams/:teamId/users/:userId    # update a member's role
DELETE /api/teams/:teamId/users/:userId    # remove a member
GET    /api/teams/:teamId/websites         # team websites (paginated)
```

**`GET /api/teams`** — params: `page`, `pageSize`. Each team includes `accessCode`, `members[]` (with nested `user`), and `_count: { websites, members }`.

**`POST /api/teams`** — body `{ "name": "marketing" }`. Returns an array `[team, ownerMembership]` (the new team plus the creator's `team-owner` membership).

**`POST /api/teams/join`** — body `{ "accessCode": "..." }`. Returns the new `team-member` membership record.

**`POST /api/teams/:teamId`** — update. Optional: `name`, `accessCode` (regenerate the join code).

**`POST /api/teams/:teamId/users`** — add a member.

| Parameter | Type | Description |
| --- | --- | --- |
| `userId` | string | ID of the user to add. |
| `role` | string | `team-member`, `team-view-only`, or `team-manager`. |

**`POST /api/teams/:teamId/users/:userId`** — update a member's `role` (same enum as above).

**`DELETE`** endpoints return `{ "ok": true }`.

---

### Websites

```text
GET    /api/websites                       # all your websites (paginated)
POST   /api/websites                       # create a website
GET    /api/websites/:websiteId            # get a website
POST   /api/websites/:websiteId            # update a website
DELETE /api/websites/:websiteId            # delete a website
POST   /api/websites/:websiteId/reset      # delete all collected data
GET    /api/websites/:websiteId/recorder   # recorder config (PUBLIC, no auth)
```

**`GET /api/websites`**

| Parameter | Type | Description |
| --- | --- | --- |
| `includeTeams` | boolean | Include websites where you are the team owner. |
| `search` | string | (optional) Search text. |
| `page` | number | (optional, default 1) Page. |
| `pageSize` | number | (optional) Page size. |

A website object:

```json
{
  "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "name": "Example",
  "domain": "example.com",
  "shareId": null,
  "resetAt": null,
  "userId": "xxxxxxxx-...",
  "teamId": null,
  "createdBy": "xxxxxxxx-...",
  "createdAt": "2025-10-10T22:01:06.201Z",
  "updatedAt": "2025-10-10T22:02:02.220Z",
  "deletedAt": null
}
```

**`POST /api/websites`** — create.

| Parameter | Type | Description |
| --- | --- | --- |
| `name` | string | Display name in Umami. |
| `domain` | string | The full domain being tracked. |
| `shareId` | string | (optional) Unique string to enable a public share URL; set `null` to unshare. |
| `teamId` | string | (optional) Create under a team. |
| `id` | string | (optional) Force a specific UUID. |

**`POST /api/websites/:websiteId`** — update. Accepts `name`, `domain`, `shareId`, and a nested **`replayConfig`** object (session replay + heatmaps):

| `replayConfig` field | Type | Description |
| --- | --- | --- |
| `replayEnabled` | boolean | Enable/disable session replay recording. |
| `heatmapEnabled` | boolean | Enable/disable heatmap collection. |
| `sampleRate` | number | Fraction of sessions to record for replay (0–1). |
| `heatmapSampleRate` | number | Fraction of sessions to record for heatmaps (0–1). |
| `maskLevel` | string | PII masking: `strict` or `moderate`. |
| `maxDuration` | number | Max recording duration (seconds). |
| `blockSelector` | string | CSS selector for elements to exclude. |

The response is the updated website object and additionally carries a top-level `recorderEnabled` (boolean) alongside the nested `replayConfig`.

> Changelog note (2026-05-28): `replayConfig` is now a nested object; the old top-level `replayEnabled` moved inside it.

**`DELETE /api/websites/:websiteId`** and **`POST /api/websites/:websiteId/reset`** both return `{ "ok": true }`. `reset` wipes all collected data for the site but keeps the site.

**`GET /api/websites/:websiteId/recorder`** — **public, no auth**. Used by the browser tracker to initialize replay/heatmaps. Returns `{ "enabled": false }` if the site is missing or recording is off, otherwise the resolved recorder config (`enabled`, `replayEnabled`, `heatmapEnabled`, `sampleRate`, `heatmapSampleRate`, `maskLevel`, `maxDuration`, `blockSelector`).

---

### Website statistics

All support [filters](#filters) as query params.

```text
GET /api/websites/:websiteId/active             # active visitors (last 5 min)
GET /api/websites/:websiteId/daterange          # earliest/latest data dates
GET /api/websites/:websiteId/events/series      # event counts over time
GET /api/websites/:websiteId/metrics            # top values by dimension
GET /api/websites/:websiteId/metrics/expanded   # dimension rows with full metrics
GET /api/websites/:websiteId/pageviews          # pageviews/sessions time series
GET /api/websites/:websiteId/stats              # summarized totals (+ comparison)
```

**`GET /api/websites/:websiteId/active`** → `{ "visitors": 5 }` (unique visitors in the last 5 minutes).

**`GET /api/websites/:websiteId/daterange`** → `{ "startDate": "...", "endDate": "..." }` (range of available data).

**`GET /api/websites/:websiteId/stats`** — summarized totals for a range.

| Parameter | Type | Description |
| --- | --- | --- |
| `startAt` | number | Start timestamp (ms). |
| `endAt` | number | End timestamp (ms). |
| `filters` | — | Any [filter](#filters) as query params. |

```json
{
  "pageviews": 15171,
  "visitors": 4415,
  "visits": 5680,
  "bounces": 3567,
  "totaltime": 809968,
  "comparison": {
    "pageviews": 38675, "visitors": 10568, "visits": 14595,
    "bounces": 9364, "totaltime": 2182387
  }
}
```

Field meanings: `pageviews` (page hits), `visitors` (unique visitors), `visits` (unique visits), `bounces` (single-page visits), `totaltime` (seconds on site). `comparison` is the prior period.

**`GET /api/websites/:websiteId/pageviews`** — pageviews + sessions as parallel time series.

| Parameter | Type | Description |
| --- | --- | --- |
| `startAt` / `endAt` | number | Range (ms). |
| `unit` | string | `year` \| `month` \| `day` \| `hour` \| `minute`. |
| `timezone` | string | e.g. `America/Los_Angeles`. |
| `compare` | string | (optional) `prev` \| `yoy`. |
| `filters` | — | Query-param filters. |

```json
{
  "pageviews": [ { "x": "2025-10-19T07:00:00Z", "y": 4129 } ],
  "sessions":  [ { "x": "2025-10-19T07:00:00Z", "y": 1397 } ]
}
```

**`GET /api/websites/:websiteId/metrics`** — top values for one dimension.

| Parameter | Type | Description |
| --- | --- | --- |
| `startAt` / `endAt` | number | Range (ms). |
| `type` | string | Dimension (see list below). |
| `limit` | number | (optional, default `500`) Rows returned. |
| `offset` | number | (optional, default `0`) Rows skipped. |
| `filters` | — | Query-param filters. |

**`type` values:** `path` · `entry` · `exit` · `title` · `query` · `referrer` · `channel` · `domain` · `country` · `region` · `city` · `browser` · `os` · `device` · `language` · `screen` · `event` · `hostname` · `tag` · `distinctId`.

Returns `[{ "x": "Mac OS", "y": 1918 }, ...]` where `x` is the value and `y` is the visitor count.

**`GET /api/websites/:websiteId/metrics/expanded`** — same parameters and `type` values, but each row carries full metrics:

```json
[ { "name": "Mac OS", "pageviews": 74020, "visitors": 16982, "visits": 24770, "bounces": 15033, "totaltime": 149156302 } ]
```

**`GET /api/websites/:websiteId/events/series`** — event counts bucketed over time.

| Parameter | Type | Description |
| --- | --- | --- |
| `startAt` / `endAt` | number | Range (ms). |
| `unit` | string | Bucket size. |
| `timezone` | string | Timezone. |
| `filters` | — | Query-param filters. |

Returns `[{ "x": "<event name>", "t": "<timestamp>", "y": <count> }, ...]`.

---

### Events & event data

Operations around individual events and the custom data attached to them. All support [filters](#filters).

```text
GET /api/websites/:websiteId/events                       # raw event/pageview rows
GET /api/websites/:websiteId/events/stats                 # aggregate event stats (+compare)
GET /api/websites/:websiteId/event-data                   # event data grouped by event
GET /api/websites/:websiteId/event-data/:eventId          # event data for one event
GET /api/websites/:websiteId/event-data/events            # event/property names + counts
GET /api/websites/:websiteId/event-data/fields            # property/value counts
GET /api/websites/:websiteId/event-data/properties        # event+property counts
GET /api/websites/:websiteId/event-data/values            # value counts for a property
GET /api/websites/:websiteId/event-data/stats             # totals (events/properties/records)
GET /api/websites/:websiteId/event-data-pivot             # pivoted rows (parallel arrays)
```

**`GET /api/websites/:websiteId/events`** — raw event rows in a range.

| Parameter | Type | Description |
| --- | --- | --- |
| `startAt` / `endAt` | number | Range (ms). |
| `search` | string | (optional) Search text. |
| `page` / `pageSize` | number | Pagination (default 1 / 20). |
| `filters` | — | Query-param filters. |

Each row includes `urlPath`, `referrerDomain`, `country`, `city`, `device`, `os`, `browser`, `pageTitle`, `eventType` (`1`=pageview, `2`=custom event), `eventName`, `hasData`, and IDs. Paginated envelope.

**`GET /api/websites/:websiteId/events/stats`** — aggregate counts with optional comparison.

| Parameter | Type | Description |
| --- | --- | --- |
| `startAt` / `endAt` | number | Range (ms). |
| `compare` | string | (optional) `prev` \| `yoy`. |
| `filters` | — | Query-param filters. |

```json
{ "data": { "events": 753, "visitors": 607, "visits": 687, "uniqueEvents": 8, "comparison": { "events": 1809, "visitors": 1374, "visits": 1655, "uniqueEvents": 10 } } }
```

**`GET /api/websites/:websiteId/event-data`** — event data grouped by event, with each event's `eventProperties[]` (`dataKey`, `stringValue`, `numberValue`, `dateValue`, `dataType`, `createdAt`). Params: `startAt`, `endAt`, `page`, `pageSize`, `filters`.

**`GET /api/websites/:websiteId/event-data/:eventId`** — flat array of property rows for a single event instance.

**`GET /api/websites/:websiteId/event-data/events`** — distinct event/property pairs with counts. Params: `startAt`, `endAt`, optional `event` (name filter), `filters`. Returns `[{ "eventName", "propertyName", "dataType", "total" }]`.

**`GET /api/websites/:websiteId/event-data/fields`** — property/value distribution. Params: `startAt`, `endAt`, `filters`. Returns `[{ "propertyName", "dataType", "value", "total" }]`.

**`GET /api/websites/:websiteId/event-data/properties`** — event/property counts. Params: `startAt`, `endAt`, `filters`. Returns `[{ "eventName", "propertyName", "total" }]`.

**`GET /api/websites/:websiteId/event-data/values`** — value counts for one event + property. Params: `startAt`, `endAt`, **required** `event` (name), **required** `propertyName`, `filters`. Returns `[{ "value", "total" }]`.

> Changelog note (2025-10-07): on `event-data/values`, the old `eventName` query param was renamed to `event`.

**`GET /api/websites/:websiteId/event-data/stats`** — `[{ "events": 16, "properties": 13, "records": 26 }]`.

**`GET /api/websites/:websiteId/event-data-pivot`** — pivoted rows where properties are parallel arrays (`propertyKeys` / `propertyValues`). Params: `startAt`, `endAt`, `eventName` (to pivot on), `page`, `pageSize`, `filters`.

```json
{ "data": [ { "eventId": "...", "sessionId": "...", "eventName": "signup", "urlPath": "/register", "createdAt": "...", "propertyKeys": ["plan", "source"], "propertyValues": ["pro", "organic"] } ], "count": 100, "page": 1, "pageSize": 20 }
```

---

### Sessions & session data

A session represents a visitor; session data is the custom/identify properties attached to it. All support [filters](#filters).

```text
GET /api/websites/:websiteId/sessions                       # session rows (paginated)
GET /api/websites/:websiteId/sessions/stats                 # summarized session stats
GET /api/websites/:websiteId/sessions/weekly                # counts by weekday/hour grid
GET /api/websites/:websiteId/sessions/:sessionId            # one session
GET /api/websites/:websiteId/sessions/:sessionId/activity   # session activity log
GET /api/websites/:websiteId/sessions/:sessionId/properties # session properties
GET /api/websites/:websiteId/session-data/properties        # property counts
GET /api/websites/:websiteId/session-data/values            # value counts for a property
GET /api/websites/:websiteId/session-data-pivot             # pivoted session data
GET /api/websites/:websiteId/session-data/stats             # activity grouped by property value
```

**`GET /api/websites/:websiteId/sessions`** — params `startAt`, `endAt`, `search`, `page`, `pageSize`, `filters`. Each row: `id`, `hostname`, `browser`, `os`, `device`, `screen`, `language`, `country`, `region`, `city`, `firstAt`, `lastAt`, `visits`, `views`, `createdAt`.

**`GET /api/websites/:websiteId/sessions/stats`** — summarized counts:

```json
{ "pageviews": { "value": 2924 }, "visitors": { "value": 905 }, "visits": { "value": 1050 }, "countries": { "value": 84 }, "events": { "value": 517 } }
```

**`GET /api/websites/:websiteId/sessions/weekly`** — params `startAt`, `endAt`, `timezone`, `filters`. Returns a 7-row array (one per weekday), each a 24-element array of hourly counts.

**`GET /api/websites/:websiteId/sessions/:sessionId`** — single session with `distinctId`, `events`, `totaltime`, plus the row fields above.

**`GET /api/websites/:websiteId/sessions/:sessionId/activity`** — params `startAt`, `endAt`. Chronological activity: `[{ "createdAt", "urlPath", "urlQuery", "referrerDomain", "eventId", "eventType", "eventName", "visitId", "hasData" }]`.

**`GET /api/websites/:websiteId/sessions/:sessionId/properties`** — property rows for one session (`dataKey`, `dataType`, `stringValue`, `numberValue`, `dateValue`, `createdAt`).

**`GET /api/websites/:websiteId/session-data/properties`** — counts by property name. Params: `startAt`, `endAt`, optional `propertyName` (filter to one), `filters`. Returns `[{ "propertyName", "total" }]`.

**`GET /api/websites/:websiteId/session-data/values`** — value counts for a property. Params: `startAt`, `endAt`, **required** `propertyName`, optional `dataType` (`1`=string, `2`=number, `3`=date, `4`=boolean), `filters`. Returns `[{ "value", "total" }]`.

**`GET /api/websites/:websiteId/session-data-pivot`** — pivoted by `propertyName`, parallel `propertyKeys`/`propertyValues` per session. Params: `startAt`, `endAt`, **required** `propertyName` (to pivot on), optional `page`, `pageSize`, `filters`. Paginated.

**`GET /api/websites/:websiteId/session-data/stats`** — activity grouped by a property value. Params: `startAt`, `endAt`, `propertyName`, `filters`. Returns `[{ "label", "activity", "sessions", "visits", "views", "events" }]`, ordered by `activity` desc, **max 100 rows**.

---

### Realtime

```text
GET /api/realtime/:websiteId    # last 30 minutes, always UTC
```

Returns aggregate maps and arrays for the trailing 30 minutes: `countries`, `urls`, `referrers` (objects of `value → count`), `events[]` (recent rows), `series.views` / `series.visitors` (per-minute time series), `totals` (`views`, `visitors`, `events`, `countries`), and a `timestamp`.

> Changelog note (2025-11-13): the `timezone` parameter was removed; realtime always returns UTC.

---

### Reports (CRUD)

Saved report definitions. The dynamic "run" endpoints (next section) compute results; these manage the saved configs.

```text
GET    /api/reports               # list saved reports for a website
POST   /api/reports               # create a saved report
GET    /api/reports/:reportId     # get a saved report
POST   /api/reports/:reportId     # update a saved report
DELETE /api/reports/:reportId     # delete a saved report
```

**`GET /api/reports`** — params: `websiteId` (required), `type` (one of the saved report types), `page`, `pageSize`. Returns a paginated list of report objects.

**`POST /api/reports`** — create.

| Parameter | Type | Description |
| --- | --- | --- |
| `websiteId` | string | Target website. |
| `type` | string | `attribution` \| `breakdown` \| `funnel` \| `goal` \| `journey` \| `retention` \| `revenue` \| `utm`. |
| `name` | string | Report name. |
| `description` | string | (optional) Description. |
| `parameters` | object | Type-specific parameters (see run endpoints). |

```json
{ "id": "...", "userId": "...", "websiteId": "...", "type": "goal", "name": "Triggered Login-button", "description": "", "parameters": { "type": "event", "value": "login-button-header" }, "createdAt": "...", "updatedAt": "..." }
```

**`POST /api/reports/:reportId`** updates with the same fields; **`DELETE`** returns `{ "ok": true }`.

---

### Reports (dynamic / run)

These compute and return analytics directly. Each takes a JSON body of the shape:

```json
{
  "websiteId": "xxxxxxxx-...",
  "type": "<report type>",
  "filters": { /* optional: any filter keys */ },
  "parameters": { /* report-specific; uses startDate/endDate ISO strings */ }
}
```

Remember: report endpoints use **`startDate`/`endDate` ISO strings inside `parameters`** (not `startAt`/`endAt` ms). See [Two date conventions](#two-date-conventions-read-this).

```text
POST /api/reports/attribution    # marketing attribution
POST /api/reports/breakdown      # multi-dimension breakdown
POST /api/reports/funnel         # funnel conversion/drop-off
POST /api/reports/goal           # goal completion counts
POST /api/reports/journey        # navigation paths
POST /api/reports/performance    # Core Web Vitals
POST /api/reports/retention      # return-visitor retention
POST /api/reports/revenue        # revenue (see Revenue section)
POST /api/reports/utm            # UTM campaign breakdown
```

**`POST /api/reports/attribution`** — `parameters`: `startDate`, `endDate`, `model` (`first-click` \| `last-click`), `type` (`path` \| `event`), `step` (conversion step). Response groups conversions by `referrer`, `paidAds`, `utm_source`/`utm_medium`/`utm_campaign`/`utm_content`/`utm_term`, plus `total` (`pageviews`, `visitors`, `visits`).

**`POST /api/reports/breakdown`** — `parameters`: `startDate`, `endDate`, `fields` (array of dimensions). **Fields:** `path`, `title`, `query`, `referrer`, `browser`, `os`, `device`, `country`, `region`, `city`, `hostname`, `tag`, `event`, `distinctId`, `utmSource`, `utmMedium`, `utmCampaign`, `utmContent`, `utmTerm`. Returns rows of metrics plus the requested field columns:

```json
[ { "views": 37856, "visitors": 9229, "visits": 13145, "bounces": 8105, "totaltime": 12985151, "os": "Mac OS", "country": "US" } ]
```

**`POST /api/reports/funnel`** — `parameters`: `startDate`, `endDate`, `steps` (array, **min 2**; each `{ "type": "path"|"event", "value": "..." }`), `window` (days allowed between steps). Returns per-step `visitors`, `previous`, `dropped`, `dropoff`, `remaining`.

**`POST /api/reports/goal`** — `parameters`: `startDate`, `endDate`, `type` (`path` \| `event`), `value`. Returns `{ "num": 11935, "total": 50602 }` (conversions / eligible).

**`POST /api/reports/journey`** — `parameters`: `startDate`, `endDate`, `steps` (number, **3–7**), `startStep`, optional `endStep`. Returns `[{ "items": ["/", "/pricing", null, ...], "count": 6433 }]`.

**`POST /api/reports/performance`** — Core Web Vitals. `parameters`: `startDate`, `endDate`, optional `unit` (`year` \| `month` \| `hour` \| `day` — note: no `minute` here), `timezone`, `metric` (`lcp` \| `inp` \| `cls` \| `fcp` \| `ttfb`). Response has `chart` (percentile time series), `summary` (per-metric `p50`/`p75`/`p95` + `count`), and `pages`/`pageTitles`/`devices`/`browsers` breakdowns. (Note: `performance` is a run-only type; it is not one of the saved-report `type` values.)

**`POST /api/reports/retention`** — `parameters`: `startDate`, `endDate`, `timezone`. Returns daily cohort rows `[{ "date", "day", "visitors", "returnVisitors", "percentage" }]`.

**`POST /api/reports/utm`** — `parameters`: `startDate`, `endDate`. Returns objects of `utm_source` / `utm_medium` / `utm_campaign` / `utm_term` / `utm_content`, each an array of `{ "utm", "views" }`.

---

### Revenue

Revenue has both a dynamic report (`POST /api/reports/revenue`) and dedicated GET endpoints. The GET endpoints use **`startAt`/`endAt` ms** (query); the report uses **`startDate`/`endDate` ISO** (body).

```text
POST /api/reports/revenue                       # full revenue report (chart/total/breakdowns)
GET  /api/websites/:websiteId/revenue/chart     # revenue time series
GET  /api/websites/:websiteId/revenue/stats     # revenue totals (+ comparison)
GET  /api/websites/:websiteId/revenue/metrics   # revenue by dimension
GET  /api/websites/:websiteId/revenue/sessions  # sessions with revenue (paginated)
```

**`POST /api/reports/revenue`** — `parameters`: `startDate`, `endDate`, `timezone`, `currency` (ISO 4217), optional `compare`. Response: `chart[]`, `total` (`sum`, `count`, `unique_count`, `total_sessions`, `average`, `arpu`, plus `comparison`), and `country`/`region`/`referrer`/`channel` breakdown arrays.

**`GET .../revenue/chart`** — params `startAt`, `endAt`, `timezone`, `currency`, optional `compare`. Returns `[{ "x": "<event>", "t": "<ts>", "y": <amount>, "count": <n> }]`.

**`GET .../revenue/stats`** — same params; returns the `total`-shaped object (`sum`, `count`, `unique_count`, `total_sessions`, `average`, `arpu`, `comparison`).

**`GET .../revenue/metrics`** — params `startAt`, `endAt`, `timezone`, `type` (`country` \| `region` \| `referrer` \| `channel`), `currency`. Returns `[{ "name", "value" }]`.

**`GET .../revenue/sessions`** — params `startAt`, `endAt`, `timezone`, `currency`, optional `page`, `pageSize`, `search`. Paginated session list with revenue.

> Currency comes from the `currency` and `revenue` properties on tracked events (see [Sending stats](#sending-stats-ingestion)).

---

### Links

Short links (URL shortener). All return the link object or a paginated list.

```text
GET    /api/links            # list (paginated)
POST   /api/links            # create
GET    /api/links/:linkId    # get
POST   /api/links/:linkId    # update
DELETE /api/links/:linkId    # delete → { ok: true }
```

**`POST /api/links`**

| Parameter | Type | Description |
| --- | --- | --- |
| `name` | string | Link name. |
| `url` | string | Destination URL. |
| `slug` | string | URL slug (**min 8 characters**). |
| `teamId` | string | (optional) Create under a team. |

Update accepts the same fields (all optional). A link object: `{ id, name, url, slug, userId, teamId, createdAt, updatedAt, deletedAt }`. List params: `search`, `page`, `pageSize`.

---

### Pixels

Tracking pixels. Same shape as Links minus the `url`.

```text
GET    /api/pixels             # list (paginated)
POST   /api/pixels             # create
GET    /api/pixels/:pixelId    # get
POST   /api/pixels/:pixelId    # update
DELETE /api/pixels/:pixelId    # delete → { ok: true }
```

**`POST /api/pixels`** — `name`, `slug` (**min 8 chars**), optional `teamId`. A pixel object: `{ id, name, slug, userId, teamId, createdAt, updatedAt, deletedAt }`.

---

### Share pages

Public share pages expose dashboards/links/pixels/boards read-only.

```text
POST   /api/share                          # create a share page
GET    /api/share/id/:shareId              # get by share ID
POST   /api/share/id/:shareId              # update
DELETE /api/share/id/:shareId              # delete → { ok: true }
GET    /api/websites/:websiteId/shares     # list a website's shares (paginated)
POST   /api/websites/:websiteId/shares     # create a share for a website
```

**`POST /api/share`**

| Parameter | Type | Description |
| --- | --- | --- |
| `entityId` | string | ID of the shared entity (website/link/pixel/board). |
| `shareType` | number | `1`=website, `2`=link, `3`=pixel, `4`=board. |
| `name` | string | Share page name. |
| `slug` | string | Share page slug. |
| `parameters` | object | Which panels are visible (e.g. `{ "overview": true, "events": true }`). |

`parameters` toggles dashboard panels; the full set includes `overview`, `events`, `sessions`, `goals`, `funnels`, `journeys`, `retention`, `attribution`, `breakdown`, `revenue`, `realtime`, `compare`, `utm` (booleans). **`POST /api/websites/:websiteId/shares`** is a convenience that creates a website share from just `name` + `parameters`.

---

### Admin

Self-hosted, admin-only. **Not available on Umami Cloud.** All paginated with `search`, `page` (default 1), `pageSize` (default 20).

```text
GET /api/admin/users        # all users across the instance
GET /api/admin/websites     # all websites across the instance
GET /api/admin/teams        # all teams across the instance
```

`admin/users` rows include `_count.websites`; `admin/teams` rows include `members[]` and `_count`; `admin/websites` rows include nested `user` and `team`. The `admin/users` response also includes an `orderBy` field (`createdAt`).

---

### Sending stats (ingestion)

This is how you record page views and custom events from a backend, mobile app, or webhook. **These endpoints require no auth token**, but you **must send a valid `User-Agent` header** or the request is rejected. On Cloud, post to `https://cloud.umami.is/api/send`.

```text
POST /api/send     # record one event
POST /api/batch    # record many events (JSON array)
```

**Required headers:** send `Content-Type: application/json` and a non-empty, realistic `User-Agent`. Requests **without a valid `User-Agent` are silently dropped** (not registered, but you may still get a 200). No `Authorization`/`x-umami-api-key` header is used on these endpoints.

**`POST /api/send`** — body has a `payload` object and a `type`.

| Field | Type | Description |
| --- | --- | --- |
| `payload.website` | string | Website ID (**required**). |
| `payload.hostname` | string | Host name. |
| `payload.url` | string | Page URL/path. |
| `payload.title` | string | Page title. |
| `payload.referrer` | string | Referrer URL. |
| `payload.screen` | string | Screen resolution (e.g. `1920x1080`). |
| `payload.language` | string | Visitor language (e.g. `en-US`). |
| `payload.tag` | string | Additional tag. |
| `payload.id` | string | Session identifier. |
| `payload.name` | string | Event name (for custom events). |
| `payload.data` | object | (optional) Custom event/session data. |
| `type` | string | `event`, `identify`, or `performance`. |

The three `type` values:

- **`event`** — a page view (no `name`) or a custom event (with `name`, optional `data`).
- **`identify`** — attach session data / a logged-in user's **distinct ID** to the current session. Put `id` and any properties in `payload.data` (the distinct ID can be any string up to **50 characters** — use an internal user ID or a hash, not raw PII).
- **`performance`** — Core Web Vitals measurements.

Sample request and response:

```json
// body
{
  "payload": {
    "hostname": "example.com",
    "language": "en-US",
    "referrer": "",
    "screen": "1920x1080",
    "title": "dashboard",
    "url": "/",
    "website": "your-website-id",
    "name": "event-name",
    "data": { "foo": "bar" }
  },
  "type": "event"
}
// response
{ "cache": "xxxxxxxxxxxxxxx", "sessionId": "xxxxxxxx-...", "visitId": "xxxxxxxx-..." }
```

> The `cache` token returned can be sent back on subsequent calls (as a `cache` field) to skip session re-resolution; the browser tracker does this automatically.

**`POST /api/batch`** — send an **array** of `/api/send`-shaped objects in one request. Same auth/User-Agent rules. Each item is forwarded to `/api/send`, so all `type` values and payload fields apply.

```json
// response
{ "size": 2, "processed": 2, "errors": 0, "details": [], "cache": "xxxxxxxxxxxxxxx" }
```

If items fail, `errors` is the failure count and `details[]` lists each failure with its `index` in the submitted array.

Python — record a server-side custom event with revenue:

```python
import requests

requests.post(
    "https://your-umami.example.com/api/send",
    json={
        "payload": {
            "hostname": "example.com",
            "language": "en-US",
            "url": "/checkout",
            "website": "your-website-id",
            "name": "payment-received",
            "data": {"revenue": 49.99, "currency": "USD", "plan": "pro"},
        },
        "type": "event",
    },
    headers={"User-Agent": "MyApp/1.0"},  # required
)
```

---

## Common patterns

These build on the `umami-analytics` setup and the `api_get` / `api_post` helpers from [Python client](#python-client-umami-analytics).

**Daily traffic summary** — the library returns a typed model.

```python
from datetime import datetime, timedelta

end = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
start = end - timedelta(days=1)

stats = umami.website_stats(start_at=start, end_at=end)
bounce_rate = stats.bounces / stats.visits * 100 if stats.visits else 0
print(f"{start:%Y-%m-%d}: {stats.visitors} visitors, "
      f"{stats.pageviews} views, {bounce_rate:.1f}% bounce")
```

**Top 10 pages** — `metrics` isn't wrapped, so call it directly.

```python
metrics = api_get("/websites/your-website-id/metrics",
                  startAt=to_ms(start), endAt=to_ms(end), type="path", limit=10)
for i, row in enumerate(metrics, 1):
    print(f"{i:2}. {row['x']} — {row['y']} views")
```

**Run a funnel report** — reports use ISO dates inside `parameters` and put filters in a `filters` object.

```python
funnel = api_post("/reports/funnel", {
    "websiteId": "your-website-id",
    "type": "funnel",
    "filters": {"country": "US"},
    "parameters": {
        "startDate": to_iso(start),
        "endDate": to_iso(end),
        "steps": [
            {"type": "path", "value": "/"},
            {"type": "event", "value": "signup"},
        ],
        "window": 60,
    },
})
for step in funnel:
    print(step["value"], step["visitors"], f"{(step['dropoff'] or 0) * 100:.1f}% drop")
```

**Page through a large result set.**

```python
def iter_sessions(website_id, start, end, page_size=100):
    page = 1
    while True:
        resp = api_get(f"/websites/{website_id}/sessions",
                       startAt=to_ms(start), endAt=to_ms(end),
                       page=page, pageSize=page_size)
        yield from resp["data"]
        if page * resp["pageSize"] >= resp["count"]:
            break
        page += 1
```

**Batch-ingest events with rate-limit awareness (Cloud).** Stay under 50 calls / 15s. (For one-off events, `umami.new_event(...)` is simpler; `/api/batch` is unauthenticated but needs a `User-Agent`.)

```python
import time, httpx

def send_batches(events, chunk=100, url="https://cloud.umami.is/api/batch"):
    for i in range(0, len(events), chunk):
        httpx.post(url, json=events[i:i + chunk], headers={"User-Agent": "MyApp/1.0"})
        time.sleep(0.3)  # one batch call per chunk; pace below the limit
```

**Compare this period vs. previous.** Either request `compare=prev` on endpoints that support it (`pageviews`, `stats` returns a `comparison` block already, `events/stats`, revenue), or make two ranged calls and diff `visitors`/`pageviews` yourself.

---

## Official clients (JS/TS)

For Python, use [`umami-analytics`](#python-client-umami-analytics) (above). Umami's own official clients are JavaScript/TypeScript — worth knowing for parity and for the function→endpoint mapping, which is a useful index of the full endpoint set even from Python.

**`@umami/api-client`** — typed client covering every data/management endpoint (Node 18.18+).

```js
import { getClient } from '@umami/api-client';
const client = getClient();
const { ok, data, status, error } = await client.getWebsites();
```

Every call returns `{ ok: boolean, status: number, data?: T, error?: any }`. Configure via env vars:

```dotenv
# Self-hosted
UMAMI_API_CLIENT_USER_ID=<user uuid>      # user performing the calls
UMAMI_API_CLIENT_SECRET=<APP_SECRET>      # must match the app's APP_SECRET
UMAMI_API_CLIENT_ENDPOINT=https://your-server/api/

# Umami Cloud
UMAMI_API_KEY=<api key>
UMAMI_API_CLIENT_ENDPOINT=https://api.umami.is/v1
```

Function → endpoint mapping (selected): `getMe() → GET /me`, `getMyWebsites() → GET /me/websites`, `getWebsites() → GET /websites`, `createWebsite(data) → POST /websites`, `getWebsiteStats(id, data) → GET /websites/{id}/stats`, `getWebsiteMetrics(id, data) → GET /websites/{id}/metrics`, `getWebsitePageviews(id, data) → GET /websites/{id}/pageviews`, `getWebsiteEvents(id, data) → GET /websites/{id}/events`, `resetWebsite(id) → POST /websites/{id}/reset`, `getUsers() → GET /users`, `createUser(data) → POST /users`, `getTeams() → GET /teams`, `joinTeam(data) → POST /teams/join`, `getEventDataEvents/Fields/Stats(...) → GET /event-data/*`.

**`@umami/node`** — server-side ingestion helper (a thin wrapper over `/api/send`).

```js
import umami from '@umami/node';
umami.init({ websiteId: '...', hostUrl: 'https://umami.mywebsite.com' });
umami.track({ url: '/home' });
umami.track({ name: 'signup', data: { plan: 'pro' } });
umami.identify({ id: user.id, plan: user.plan });  // distinct ID + session data
```

`track()` accepts `hostname`, `language`, `referrer`, `screen`, `title`, `url`, `name`, `data`.

---

## Appendix: API changelog highlights

Notable changes to `api.umami.is` that affect clients (most recent first):

- **2026-05-28** — Added revenue GET endpoints (`/revenue/chart`, `/revenue/stats`, `/revenue/metrics`, `/revenue/sessions`) and `GET /websites/:id/recorder`. `replayConfig` became a nested object on `POST /websites/:id` (the old top-level `replayEnabled` moved inside it).
- **2026-05-04** — Added `event-data-pivot`, `session-data-pivot`, `session-data/stats`; added `propertyName` to `session-data/properties` and `dataType` to `session-data/values`.
- **2026-03-11** — Added `GET /websites/:id/daterange`, `GET /websites/:id/events/stats`, `POST /links`, `POST /pixels`, and `POST /reports/performance`. `POST /reports/goals` renamed to `POST /reports/goal` (singular). Revenue report gained `compare`, `arpu`, `comparison`, and region/referrer/channel breakdowns.
- **2026-03-02** — Added `GET /websites/:id/event-data`.
- **2026-02-04** — Added the Share API.
- **2025-11-13** — `GET /realtime/:id` dropped `timezone`; always returns UTC.
- **2025-10-07** — Renamed filter `url` → `path` and `host` → `hostname`; the `metrics` `type` value `url` → `path`; `event-data/values` query param `eventName` → `event`; `stats` response gained the `comparison` block; the `insights` report type was renamed to `breakdown`.
- **2024-05-23 / 2024-03-27** — `stats` renamed `change` → `prev`, `uniques` → `visitors`, and added `visits`.

If your training data predates these, double-check filter names (`path`/`hostname`), the `goal` (singular) report path, and the nested `replayConfig`.
