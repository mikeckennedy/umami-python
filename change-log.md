# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.22] - 2026-02-02

### Fixed
- `new_event_async` crashed with `binascii.Error` due to erroneous `base64.b64decode` / `json.loads` calls on the plain-JSON API response; now returns `resp.json()` directly, matching the other event and page-view methods

### Removed
- Unused `base64` and `json` imports from `umami/impl/__init__.py`

---

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

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
