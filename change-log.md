# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `distinct_id` support in `new_event`, `new_page_view`, and `new_revenue_event` payloads
  (sync and async), sent to Umami as payload field `id`
- Umami Cloud API-key authentication via `set_cloud_api_key(key, region=None)` and
  `clear_cloud_api_key()`. In Cloud mode, data/management calls route to
  `https://api.umami.is/v1[/region]` with an `x-umami-api-key` header, and events are sent to
  `https://cloud.umami.is/api/send` — no `set_url_base()` or `login()` required. Existing
  self-hosted (`login()` + token) usage is byte-for-byte unchanged. Added `urls.me` for Cloud
  key validation in `verify_token`/`verify_token_async`. In Cloud mode, `heartbeat()` /
  `heartbeat_async()` check liveness via the authenticated `/me` endpoint (Cloud has no
  `/api/heartbeat`), and `login()` / `login_async()` raise `OperationNotAllowedError` to fail
  fast (the API key is the credential — there is no username/password login on Cloud).

### Changed
- `validate_state` error messages now mention `set_cloud_api_key()` alongside `set_url_base()` /
  `login()`. Same exception type (`OperationNotAllowedError`) and trigger conditions; text only.
- Response models are more tolerant of variant/partial responses: `WebsiteStats.comparison` and
  `Website.user` are now optional, and `Website` accepts `createUser` (returned by team-website
  listings, where `userId` is null). Successful responses today are unaffected.
- Internal: expanded the unit test suite (now 128 tests) following a suite review — added
  behavioral coverage for `set_url_base` validation, the `validate_state` guards, the
  `login`/`login_async` happy path and response-model deserialization (`LoginResponse`,
  `WebsitesResponse`), `websites`/`websites_async`, the `disable()` no-op (asserting no HTTP
  request is made), `ip_address` payload inclusion/omission, explicit-arg-overrides-defaults
  precedence, `heartbeat_async` self-hosted, and the `verify_token`/`heartbeat` failure branches.
  Added a sync/async parity harness and consolidated the per-file HTTP mock builders into a shared
  `tests/_mocks.py` (net ~210 fewer lines). No production behavior changed.

### Deprecated

### Removed

### Fixed
- `website_stats_async()` sent its date range as snake_case `start_at`/`end_at` query
  params, which the Umami API ignores — it silently returned all-time stats regardless
  of the requested window. Now sends camelCase `startAt`/`endAt`, matching the sync
  `website_stats()`. (#18)
- `active_users()` and `active_users_async()` read the active-visitor count from a
  non-existent `x` key, so they always returned `0`. They now read Umami's current
  `visitors` key (falling back to the legacy `x` key for compatibility). (#19)
- `website_stats()` / `website_stats_async()` sent their `url` and `host` filters under
  the old query-param names, which Umami renamed on 2025-10-07 (`url` → `path`,
  `host` → `hostname`) — so filtering stats by URL or hostname was a silent no-op. The
  public `url`/`host` keyword arguments are unchanged; they now map to the current
  `path`/`hostname` wire names. (#20)
- `heartbeat()` / `heartbeat_async()` issued a `POST` to `/api/heartbeat`, which current Umami
  answers with `405 Method Not Allowed`; the broad exception handler swallowed the error so the
  call always returned `False` even against a healthy server. They now issue a `GET` (the endpoint
  returns `{"ok": true}`).
- `new_event()` and `new_revenue_event()` (sync) defaulted `url` to `'/event-api-endpoint'` while
  their async twins used `'/'`. All four now default to `'/'`, so the sync/async twins agree and no
  placeholder path appears in dashboards.

### Security

---

## [0.5.24] - 2026-06-04

### Changed
- Migrated HTTP backend from `httpx` to `httpx2`, imported as `import httpx2 as httpx` so all call sites remain unchanged
- Files: `umami/umami/impl/__init__.py`, `umami/requirements.txt`, `umami/pyproject.toml`, `pyrefly.toml`, `README.md`, `umami/README.md`

### Notes
- Motivated by supply-chain/maintainer-governance concerns around `httpx` (stalled releases, locked-down issues/discussions). Confirm `httpx2` is the intended, API-compatible fork before publishing this release.

---

## [0.4.23] - 2026-03-12

### Added
- `new_revenue_event()` and `new_revenue_event_async()` for tracking revenue with Umami's new revenue feature
- Revenue events automatically inject `revenue` (float) and `currency` (ISO 4217 string) into event custom data
- Input validation: revenue must be a number >= 0, currency must be a non-empty string
- Defaults to `event_name='revenue'` and `currency='USD'` for simple usage
- 15 new tests covering sync/async revenue events, validation, and edge cases

---

## [0.3.22] - 2026-02-02

### Fixed
- `new_event_async` crashed with `binascii.Error` due to erroneous `base64.b64decode` / `json.loads` calls on the plain-JSON API response; now returns `resp.json()` directly, matching the other event and page-view methods

### Removed
- Unused `base64` and `json` imports from `umami/impl/__init__.py`

---

## [0.3.21] - 2025-12-12

### Added
- Change-log preservation section for tracking historical release details
- Pyrefly configuration file treating `umami/umami` package as type-resolution root

### Changed
- Centralized all version information into a single location for easier maintenance
- Updated Python requirement to 3.10+ (dropped support for Python 3.8 and 3.9)
- Refactored `WebsiteStats` to use plain integers instead of custom `Metric` type - Thanks @rubitcat (#15)
- Updated `ruff.toml` to enforce consistent import ordering

### Fixed
- Suppressed and cleaned up unnecessary type-checking warnings

---

## [0.2.20] - 2025-05-30

### Added
- Development and testing tracking options to disable tracking for dev/test environments
- When tracking is disabled: no HTTP requests are made, API calls still validate parameters, all other functions work normally, functions return appropriate values for compatibility
- Documentation for heartbeat check feature and new methods (`get_heartbeat`, `enable/disable`)

### Changed
- Sorted imports in various files to improve code organization and readability
- Fixed minor typo in documentation

---

## [0.2.19] - 2025-05-30

### Added
- Asynchronous (`heartbeat_async`) and synchronous (`heartbeat`) versions of the heartbeat function for improved import flexibility
- Website stats and active users functions (`website_stats`, `active_users`) - Thanks @orangethewell

### Fixed
- Login API data handling corrected from `data` to `json` parameter

### Changed
- Optimized heartbeat function execution flow for improved performance

---

## [0.2.18] - 2025-05-30

### Added
- Python 3.13 and 3.14 support

### Fixed
- API call method fix: corrected the use of `data` instead of `json` in login API calls

---

## [0.2.17] - 2024-04-18

### Added
- `is_logged_in() -> bool` method to check whether login has been called and was successful

---

## [0.2.15] - 2024-02-29

### Added
- Heartbeat function (from 0.1.14 release)

### Fixed
- Schema change compatibility from Umami 2.9 to 2.10 on websites response

---

## [0.1.14] - 2024-02-29

### Added
- Heartbeat API endpoint

---

## [0.1.13] - 2024-02-13

### Added
- IP address support in `new_event` and `new_page_view` payloads (and async variants)
- Prepares for Umami IP data field feature (see umami-software/umami#2479)

---

## [0.1.12] - 2024-01-27

### Added
- Ability to pass alternative user agent to events (note: Umami blocks what it perceives as bots)

---

## [0.1.11] - 2024-01-24

### Added
- `new_page_view()` and `new_page_view_async()` methods

### Changed
- Dropped auth requirement for new event (not needed, see #1)

---

## [0.1.10] - 2024-01-22

### Added
- Platform type (e.g. Windows) to user agent
- Doc strings to most methods
- Better validation for some functions
- Custom error types for validation

---

## Template for Future Entries

<!--
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features or capabilities
- Files: `path/to/new/file.ext`, `another/file.ext`

### Changed
- Modifications to existing functionality
- Files: `path/to/modified/file.ext` (summary if many files)

### Deprecated
- Features that will be removed in future versions
- Files affected: `path/to/deprecated/file.ext`

### Removed
- Features or files that were deleted
- Files: `path/to/removed/file.ext`

### Fixed
- Bug fixes and corrections
- Files: `path/to/fixed/file.ext`

### Security
- Security patches or vulnerability fixes
- Files: `path/to/security/file.ext`

### Notes
- Additional context or important information
- Major dependencies updated
- Breaking changes explanation
-->
