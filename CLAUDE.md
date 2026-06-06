# CLAUDE.md

Guidance for Claude Code (and other AI agents) working in this repository.
`AGENTS.md` and `GEMINI.md` are symlinks to this file — edit **CLAUDE.md only**; the others follow automatically.

---

## 1. What this project is

**umami-analytics** is a Python client SDK for [Umami](https://umami.is), the open-source,
privacy-preserving web analytics platform. It lets Python **backends** send custom events, page
views, and revenue transactions to a self-hosted or Umami Cloud instance, and query basic stats —
useful for tracking deep business-logic events (e.g. a course purchase) that have no natural
front-end HTML trigger.

- **PyPI package:** `umami-analytics` &nbsp;(`pip install umami-analytics` / `uv add umami-analytics`)
- **Import name:** `umami` &nbsp;(i.e. `import umami`)
- **Repo:** https://github.com/mikeckennedy/umami-python
- **License:** MIT © Michael Kennedy <michael@talkpython.fm>
- **Status:** Beta, actively maintained; used in production at Talk Python Training.
- **Python:** 3.10+ (classifiers cover 3.10–3.15).
- **Runtime deps:** `httpx2` (an API-compatible fork of `httpx`), `pydantic`.
- **Scope is intentionally partial:** it wraps the most common Umami endpoints, not the whole API.
  Remaining endpoints are documented at https://umami.is/docs/api.

---

## 2. Repository layout — READ THIS FIRST

This is a **two-tier layout**. The repo root holds docs and tool config; the installable package
lives one level down in `umami/`, and the importable package is nested again at `umami/umami/`.
**Getting the working directory right matters** — see §4.

```
umami-python/                     ← REPO ROOT (docs + lint/type config)
├── CLAUDE.md  AGENTS.md  GEMINI.md   ← this file + two symlinks to it
├── README.md                     top-level docs
├── change-log.md                 Keep a Changelog format (UPDATE THIS for user-facing changes)
├── LICENSE                       MIT
├── ruff.toml                     ★ ruff config lives HERE (repo root)
├── pyrefly.toml                  ★ pyrefly config lives HERE (repo root)
├── .pre-commit-config.yaml       ruff --fix on commit
├── .github/FUNDING.yml           only GitHub file — NO CI workflows exist
├── dev-docs/                     design notes & package reference guides
├── plans/                        in-progress design/refinement plans
├── readme_resources/             README image assets
└── umami/                        ← PACKAGE DIR (build + test config)
    ├── pyproject.toml            ★ package metadata, deps, version, pytest config (hatchling)
    ├── requirements.txt          mirrors runtime deps (httpx2, pydantic)
    ├── tox.ini                   LEGACY / stale (py27–py37) — not the source of truth
    ├── README.md  LICENSE
    ├── umami/                    ← IMPORTABLE PACKAGE ("import umami")
    │   ├── __init__.py           public API re-exports + __all__
    │   ├── impl/__init__.py      ALL implementation + module-global state
    │   ├── models/__init__.py    Pydantic response models
    │   ├── errors/__init__.py    exception classes
    │   ├── urls.py               API endpoint path constants
    │   └── py.typed              PEP 561 marker — package ships type hints
    ├── tests/                    pytest suite (conftest.py + test_*.py)
    └── example_client/           runnable end-to-end demo (client.py + settings)
```

**The gotcha to remember:** `ruff.toml` and `pyrefly.toml` are at the **repo root**, but
`pyproject.toml` and the pytest config are in **`umami/`**. So linting/type-checking run from the
root, while tests run from `umami/`.

---

## 3. Architecture

- **Module-level function API, not a client class.** Everything is called as `umami.some_function(...)`.
- **Global state** lives in `umami/umami/impl/__init__.py` (`url_base`, `auth_token`,
  `default_website_id`, `default_hostname`, `tracking_enabled`, user-agent strings, `__version__`).
  Configuration functions mutate these globals.
- **`__init__.py` is a thin facade:** it re-exports the public functions from `.impl` and exposes the
  `models` and `errors` submodules. The full public surface is the `__all__` list there — keep it in
  sync when adding/removing public functions.
- **Sync + async parity:** nearly every operation has a sync function and an `_async` twin with an
  identical signature and return type (e.g. `new_event` / `new_event_async`). **Preserve this parity** —
  if you change one, change the other.
- **HTTP:** `import httpx2 as httpx`. Sync uses module-level `httpx.post`/`httpx.get`; async uses an
  `httpx.AsyncClient()` context manager. Auth is `Authorization: Bearer <token>`; non-2xx responses
  call `resp.raise_for_status()`.
- **Version** is read at runtime via `importlib.metadata.version('umami-analytics')` (fallback `'0.0.0'`).

### Public API at a glance (`umami.__all__`)

| Group | Functions |
|---|---|
| Config (sync only) | `set_url_base`, `set_website_id`, `set_hostname`, `enable`, `disable` |
| Auth | `login`/`login_async`, `is_logged_in`, `verify_token`/`verify_token_async` |
| Send events | `new_event`/`_async`, `new_revenue_event`/`_async`, `new_page_view`/`_async` |
| Query stats | `websites`/`_async`, `website_stats`/`_async`, `active_users`/`_async` |
| Health | `heartbeat`/`_async` |
| Submodules | `umami.models`, `umami.errors` |

Operational rules baked into the code:
- `set_url_base(...)` is **required before any operation** (it validates the scheme and strips a trailing slash).
- **Login is required** for `websites`, `website_stats`, `active_users`, and `verify_token`.
- **Login is NOT required** to send events/page views (only `url_base` + a `website_id`/`hostname`).
- `disable()` makes the `new_*` functions validate their input and then early-return **without** any
  HTTP call — this is the intended way to silence tracking in dev/test. `enable()` is the default.
- Errors: `errors.ValidationError` (base) and `errors.OperationNotAllowedError` (raised when required
  state like `url_base` or login is missing).

### Typical usage

```python
import umami

umami.set_url_base('https://umami.example.com')
login = umami.login(username, password)

umami.set_website_id(website_id)     # set once, used as the default for later calls
umami.set_hostname('example.com')

umami.new_event(
    event_name='checkout-completed',
    title='Checkout',
    url='/checkout',
    custom_data={'plan': 'pro'},
)

umami.new_revenue_event(revenue=19.99, currency='USD', event_name='checkout-cart', url='/checkout')
```

See `umami/example_client/client.py` for a complete, runnable walkthrough (sync + async).

---

## 4. Dev workflow & commands

Standard toolchain is **uv**. Mind the working directory (see §2).

### First-time setup (from the repo root)
```bash
uv venv
source .venv/bin/activate
uv pip install -e "./umami[dev]"     # installs the package + dev deps (pytest, pytest-asyncio, ruff)
```

### Everyday commands
```bash
# Lint & format — run from the REPO ROOT (configs: ruff.toml at root)
ruff format .
ruff check .

# Tests — run from the PACKAGE DIR (pytest config + tests live under umami/)
cd umami && pytest            # or: pytest -v   |   pytest tests/test_revenue.py

# Type-check (optional; config: pyrefly.toml at root). Pyrefly is NOT a dev dependency:
uvx pyrefly check             # from the repo root
```

### Run the example client
```bash
cd umami/example_client
cp settings-template.json settings.json   # then fill in base_url, username, password
python client.py
```

### Build & release (manual, from the package dir)
```bash
cd umami
# 1. bump `version = "..."` in umami/pyproject.toml
# 2. add a change-log.md entry (see §6)
uv build       # produces wheel + sdist in umami/dist/
uv publish     # uploads to PyPI (needs a token); package name: umami-analytics
```

There is **no CI** (no `.github/workflows`) — the checks below are enforced by you locally /
pre-commit, not by a pipeline. Install the hook with `pre-commit install` if you want auto-formatting on commit.

---

## 5. Definition of done

Before considering a code change complete, run and pass:

1. **`ruff format .` and `ruff check .`** (from repo root) — formatting and lint must be clean.
2. **`pytest`** (from `umami/`) — all tests green. **Add or extend tests** for any new behavior.
3. **`change-log.md`** — add an entry for any user-facing change (see §6).

`pyrefly check` is available and encouraged for type-sensitive changes, but is not a required gate.

When you touch a `new_*`, `*_async`, auth, or query function, also:
- keep the **sync and async twins in lockstep**, and
- update **`__all__`** in `umami/umami/__init__.py` if the public surface changed.

---

## 6. Conventions

**Code style (enforced by ruff — `ruff.toml`):**
- Single quotes (`format.quote-style = "single"`).
- Line length **120**.
- Lint rules `E`, `F`, `I` (errors, pyflakes, isort import ordering); max cyclomatic complexity 10.
- Target version `py313`. Code ships type hints (`py.typed`) — keep new public functions typed.

**Tests (`umami/tests/`):**
- pytest with `pytest-asyncio` (`asyncio_mode = "auto"`, so async tests need no decorator); `testpaths = ["tests"]`.
- **Unit tests only — never contact a real Umami server.** HTTP is mocked with `unittest.mock`
  (`MagicMock`/`AsyncMock`/`patch`), patched at the `umami.impl` import boundary.
- `conftest.py` has an autouse `_setup_umami` fixture seeding `url_base`, hostname, website_id and
  enabling tracking for every test.
- Organize tests in classes (`TestX` / `TestXAsync`), use `@pytest.mark.parametrize`, and assert on
  the request payload that would be sent.

**Changelog & versioning:**
- `change-log.md` follows [Keep a Changelog](https://keepachangelog.com): group entries under
  Added / Changed / Deprecated / Removed / Fixed / Security, with an `Unreleased` section at the top.
- SemVer 2.0. The single source of version truth is `version = "..."` in `umami/pyproject.toml`.

**Git / PR flow:**
- Work lands on `main`; external PRs are welcome but **open an issue first** to confirm a feature fits
  the library's direction (the SDK is deliberately a partial wrapper).
- Commit messages: short, imperative; reference issues with `closes #N`.
- **Do not add a `Co-Authored-By` trailer** to commits or PR bodies in this repo.

---

## 7. References

- Umami API docs: https://umami.is/docs/api
- httpx2 / Umami package guides: `dev-docs/package-guides/`
- In-flight design plans: `plans/`
- Developer notes: `dev-docs/`
