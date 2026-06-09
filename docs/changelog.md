# Changelog

This changelog is generated automatically from [GitHub Releases](https://github.com/mikeckennedy/umami-python/releases).


# v0.6.25

*2026-06-07* · [GitHub](https://github.com/mikeckennedy/umami-python/releases/tag/v0.6.25)


## \[0.6.25\] - 2026-06-07


### Added

- `distinct_id` support in [new_event](reference/new_event.html#umami.new_event), [new_page_view](reference/new_page_view.html#umami.new_page_view), and [new_revenue_event](reference/new_revenue_event.html#umami.new_revenue_event) payloads (sync and async), sent to Umami as payload field `id`
- Umami Cloud API-key authentication via `set_cloud_api_key(key, region=None)` and [clear_cloud_api_key()](reference/clear_cloud_api_key.html#umami.clear_cloud_api_key). In Cloud mode, data/management calls route to `https://api.umami.is/v1[/region]` with an `x-umami-api-key` header, and events are sent to `https://cloud.umami.is/api/send` -- no [set_url_base()](reference/set_url_base.html#umami.set_url_base) or [login()](reference/login.html#umami.login) required. Existing self-hosted ([login()](reference/login.html#umami.login) + token) usage is byte-for-byte unchanged. Added `urls.me` for Cloud key validation in [verify_token](reference/verify_token.html#umami.verify_token)/[verify_token_async](reference/verify_token_async.html#umami.verify_token_async). In Cloud mode, [heartbeat()](reference/heartbeat.html#umami.heartbeat) / [heartbeat_async()](reference/heartbeat_async.html#umami.heartbeat_async) check liveness via the authenticated `/me` endpoint (Cloud has no `/api/heartbeat`), and [login()](reference/login.html#umami.login) / [login_async()](reference/login_async.html#umami.login_async) raise [OperationNotAllowedError](reference/errors.OperationNotAllowedError.html#umami.errors.OperationNotAllowedError) to fail fast (the API key is the credential -- there is no username/password login on Cloud).


### Changed

- `validate_state` error messages now mention [set_cloud_api_key()](reference/set_cloud_api_key.html#umami.set_cloud_api_key) alongside [set_url_base()](reference/set_url_base.html#umami.set_url_base) / [login()](reference/login.html#umami.login). Same exception type ([OperationNotAllowedError](reference/errors.OperationNotAllowedError.html#umami.errors.OperationNotAllowedError)) and trigger conditions; text only.
- Response models are more tolerant of variant/partial responses: `WebsiteStats.comparison` and `Website.user` are now optional, and [Website](reference/models.Website.html#umami.models.Website) accepts `createUser` (returned by team-website listings, where `userId` is null). Successful responses today are unaffected.
- Internal: expanded the unit test suite (now 128 tests) following a suite review -- added behavioral coverage for [set_url_base](reference/set_url_base.html#umami.set_url_base) validation, the `validate_state` guards, the [login](reference/login.html#umami.login)/[login_async](reference/login_async.html#umami.login_async) happy path and response-model deserialization ([LoginResponse](reference/models.LoginResponse.html#umami.models.LoginResponse), [WebsitesResponse](reference/models.WebsitesResponse.html#umami.models.WebsitesResponse)), [websites](reference/websites.html#umami.websites)/[websites_async](reference/websites_async.html#umami.websites_async), the [disable()](reference/disable.html#umami.disable) no-op (asserting no HTTP request is made), `ip_address` payload inclusion/omission, explicit-arg-overrides-defaults precedence, [heartbeat_async](reference/heartbeat_async.html#umami.heartbeat_async) self-hosted, and the [verify_token](reference/verify_token.html#umami.verify_token)/[heartbeat](reference/heartbeat.html#umami.heartbeat) failure branches. Added a sync/async parity harness and consolidated the per-file HTTP mock builders into a shared `tests/_mocks.py` (net ~210 fewer lines). No production behavior changed.


### Fixed

- [website_stats_async()](reference/website_stats_async.html#umami.website_stats_async) sent its date range as snake_case `start_at`/`end_at` query params, which the Umami API ignores -- it silently returned all-time stats regardless of the requested window. Now sends camelCase `startAt`/`endAt`, matching the sync [website_stats()](reference/website_stats.html#umami.website_stats). ([\#18](https://github.com/mikeckennedy/umami-python/issues/18))
- [active_users()](reference/active_users.html#umami.active_users) and [active_users_async()](reference/active_users_async.html#umami.active_users_async) read the active-visitor count from a non-existent `x` key, so they always returned `0`. They now read Umami's current `visitors` key (falling back to the legacy `x` key for compatibility). ([\#19](https://github.com/mikeckennedy/umami-python/issues/19))
- [website_stats()](reference/website_stats.html#umami.website_stats) / [website_stats_async()](reference/website_stats_async.html#umami.website_stats_async) sent their `url` and `host` filters under the old query-param names, which Umami renamed on 2025-10-07 (`url` → `path`, `host` → `hostname`) -- so filtering stats by URL or hostname was a silent no-op. The public `url`/`host` keyword arguments are unchanged; they now map to the current `path`/`hostname` wire names. ([\#20](https://github.com/mikeckennedy/umami-python/issues/20))
- [heartbeat()](reference/heartbeat.html#umami.heartbeat) / [heartbeat_async()](reference/heartbeat_async.html#umami.heartbeat_async) issued a `POST` to `/api/heartbeat`, which current Umami answers with `405 Method Not Allowed`; the broad exception handler swallowed the error so the call always returned `False` even against a healthy server. They now issue a `GET` (the endpoint returns `{"ok": true}`).
- [new_event()](reference/new_event.html#umami.new_event) and [new_revenue_event()](reference/new_revenue_event.html#umami.new_revenue_event) (sync) defaulted `url` to `'/event-api-endpoint'` while their async twins used `'/'`. All four now default to `'/'`, so the sync/async twins agree and no placeholder path appears in dashboards.


# v0.5.24

*2026-06-04* · [GitHub](https://github.com/mikeckennedy/umami-python/releases/tag/v0.5.24)


## \[0.5.24\] - 2026-06-04


### Changed

- Migrated HTTP backend from `httpx` to `httpx2`, imported as `import httpx2 as httpx` so all call sites remain unchanged
- Files: `umami/umami/impl/__init__.py`, `umami/requirements.txt`, `umami/pyproject.toml`, `pyrefly.toml`, `README.md`, `umami/README.md`


# v0.4.23

*2026-03-13* · [GitHub](https://github.com/mikeckennedy/umami-python/releases/tag/v0.4.23)


## \[0.4.23\]


### Added

- [new_revenue_event()](reference/new_revenue_event.html#umami.new_revenue_event) and [new_revenue_event_async()](reference/new_revenue_event_async.html#umami.new_revenue_event_async) for tracking revenue with Umami's new revenue feature
- Revenue events automatically inject `revenue` (float) and `currency` (ISO 4217 string) into event custom data
- Input validation: revenue must be a number \>= 0, currency must be a non-empty string
- Defaults to `event_name='revenue'` and `currency='USD'` for simple usage
- 15 new tests covering sync/async revenue events, validation, and edge cases


# v0.3.22

*2026-02-03* · [GitHub](https://github.com/mikeckennedy/umami-python/releases/tag/v0.3.22)


## \[0.3.22\] - 2026-02-02


### Fixed

- [new_event_async](reference/new_event_async.html#umami.new_event_async) crashed with `binascii.Error` due to erroneous `base64.b64decode` / `json.loads` calls on the plain-JSON API response; now returns `resp.json()` directly, matching the other event and page-view methods


# v0.3.21

*2025-12-12* · [GitHub](https://github.com/mikeckennedy/umami-python/releases/tag/v0.3.21)


### Added

- Change-log preservation section for tracking historical release details
- Pyrefly configuration file treating `umami/umami` package as type-resolution root


### Changed

- Centralized all version information into a single location for easier maintenance
- Updated Python requirement to 3.10+ (dropped support for Python 3.8 and 3.9)
- Refactored [WebsiteStats](reference/models.WebsiteStats.html#umami.models.WebsiteStats) to use plain integers instead of custom `Metric` type - Thanks [<span class="citation" cites="rubitcat">@rubitcat</span>](https://github.com/rubitcat) ([\#15](https://github.com/mikeckennedy/umami-python/issues/15))
- Updated `ruff.toml` to enforce consistent import ordering


### Fixed

- Suppressed and cleaned up unnecessary type-checking warnings


# v0.2.20

*2025-05-31* · [GitHub](https://github.com/mikeckennedy/umami-python/releases/tag/v0.2.20)

Umami-Python Release Notes

**Since 5fa35183 (7 commits)**


## 🚀 New Features

- **Development and Testing Tracking**: Added options to disable tracking for development and testing environments. This allows users to control data collection based on their needs.

When tracking is disabled: - ✅ **No HTTP requests** are made to your Umami server - ✅ **API calls still validate** parameters (helps catch configuration issues) - ✅ **All other functions work normally** (login, websites, stats, etc.) - ✅ **Functions return appropriate values** for compatibility


## 📚 Documentation

- Documented the heartbeat check feature for monitoring system health.
- Added documentation for new methods in the Umami API: `get_heartbeat` and `enabled/disable`.


## 🧹 Maintenance

- Sorted some imports in various files to improve code organization and readability.
- Fixed a minor typo in the documentation, ensuring consistency across the project.


# v0.2.19

*2025-05-31* · [GitHub](https://github.com/mikeckennedy/umami-python/releases/tag/v0.2.19)

Umami-Python Release Notes

**Since 1d17c014 (16 commits)**


## 🚀 New Features

- **Heartbeat Functions**: Added asynchronous ([heartbeat_async](reference/heartbeat_async.html#umami.heartbeat_async)) and synchronous ([heartbeat](reference/heartbeat.html#umami.heartbeat)) versions of the existing heartbeat function for improved import flexibility.
- Added website stats and active users functions ([website_stats](reference/website_stats.html#umami.website_stats), [active_users](reference/active_users.html#umami.active_users)) Thanks [<span class="citation" cites="orangethewell">@orangethewell</span>](https://github.com/orangethewell)


## 🐛 Bug Fixes

- **Login Fix**: Corrected the API data handling from `data` to `json` in the login process. Originally, this was not a problem with the server, but it has started failing. If you have encountered login errors, this may fix it.


## ⚡ Performance

- **Heartbeat Function Optimization**: Improved the performance of the heartbeat function by optimizing its execution flow.


# v0.2.18

*2025-05-31* · [GitHub](https://github.com/mikeckennedy/umami-python/releases/tag/v0.2.18)

Umami-Python Release Notes

**Since 3a08f77a (2 commits)**


## 🚀 New Features

- **Python Version Update**: Upgraded to Python 3.13 and 3.14, providing better support for modern applications.


## 🐛 Bug Fixes

- **API Call Method Fix**: Corrected the use of `data` instead of `json` in login API calls, ensuring proper data transmission.

Originally, this was not a problem with the server, but it has started failing. If you have encountered login errors, this may fix it.


# v0.2.17

*2024-04-19* · [GitHub](https://github.com/mikeckennedy/umami-python/releases/tag/v0.2.17)

Adds `is_logged_in() -> bool` method to check whether login has been called and was successful.


# v0.2.15

*2024-03-01* · [GitHub](https://github.com/mikeckennedy/umami-python/releases/tag/v0.2.15)

- Fixes schema change from Umami 2.9 to 2.10 on websites response
- Includes new heartbeat function from 0.1.14 release


# v0.1.14

*2024-03-01* · [GitHub](https://github.com/mikeckennedy/umami-python/releases/tag/v0.1.14)

Add heartbeat API endpoint.


# v0.1.13

*2024-02-13* · [GitHub](https://github.com/mikeckennedy/umami-python/releases/tag/v0.1.13)

Support IP address in new_event and new_page_view payloads, see issue [\#2](https://github.com/mikeckennedy/umami-python/issues/2).

It looks like Umami added the IP data field in the payload (see https://github.com/umami-software/umami/pull/2479 ). It's not clear when the feature will be released in a new build ( https://github.com/umami-software/umami/releases ). But in preparation, I added the id_address parameter to both new_event and new_page_view as well as their async twins.

This is out in version 0.1.13 and on PyPI at https://pypi.org/project/umami-analytics/0.1.13/ Thanks for the idea [<span class="citation" cites="ddxv">@ddxv</span>](https://github.com/ddxv)


# v0.1.12

*2024-01-27* · [GitHub](https://github.com/mikeckennedy/umami-python/releases/tag/v0.1.12)

Add ability to pass alternative user agent to events (but be careful, umami blocks what it perceives as bots).


# v0.1.11

*2024-01-24* · [GitHub](https://github.com/mikeckennedy/umami-python/releases/tag/v0.1.11)

- Added method: [new_page_view()](reference/new_page_view.html#umami.new_page_view) and [new_page_view_async()](reference/new_page_view_async.html#umami.new_page_view_async).
- Dropped auth requirement for new event, it's not needed (see [\#1](https://github.com/mikeckennedy/umami-python/issues/1) )


# v0.1.10

*2024-01-22* · [GitHub](https://github.com/mikeckennedy/umami-python/releases/tag/v0.1.10)

- Added platform type (e.g. Windows) to user agent.
- Added doc strings to most methods.
- Bump the version for next release.
- Added better validation for some functions.
- Added custom error types for validation.


# v0.1.9

*2024-01-21* · [GitHub](https://github.com/mikeckennedy/umami-python/releases/tag/v0.1.9)

First real release outside our own apps. Enjoy!
