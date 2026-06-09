# Documentation site — Great Docs

Stand up a published documentation site for **umami-analytics** using
[Great Docs](https://posit-dev.github.io/great-docs/) (Posit's Quarto-based Python doc generator),
served at **`https://mkennedy.codes/docs/umami-python/`**.

Each document in this folder is a self-contained unit of work that maps to one commit. Hand them to
Claude Code one at a time, in order. As with `plans/01-…`, Michael commits himself — the units give
a **suggested** commit message, the exact changes, and a "done when" checklist; they do **not**
auto-commit, and **no `Co-Authored-By` trailer** is added.

---

## Locked decisions (from Michael, 2026-06-08)

| Decision | Choice | Consequence |
|---|---|---|
| **Where the docs project lives** | **In `umami/`** (idiomatic) | Great Docs runs with project root = `umami/` (where `pyproject.toml` is). Config is `umami/great-docs.yml`; ephemeral build output is `umami/great-docs/_site/`. The string `/docs/umami-python` is **only** a published-URL path, not a repo folder. |
| **Deployment** | **Build locally, Michael transfers** | We configure `site_url` and write a runbook (build + `rsync` + nginx). **No CI, no deploy script** is created. |
| **Narrative depth** | **Minimal** | Landing page comes from `umami/README.md`; everything else is the **auto-generated API reference**. No hand-written guide pages in this batch. |

---

## Why the setup looks the way it does

Three facts about this repo drive every step below. Read them once and the units make sense.

1. **Two-tier layout.** There is **no `pyproject.toml` at the repo root** — it lives at
   `umami/pyproject.toml`, and the importable package is nested again at `umami/umami/`. Great Docs
   discovers the API from the **project root that contains `pyproject.toml`**, and there is no
   config key to point it at an arbitrary package path. **Therefore every `great-docs` command runs
   from `umami/`** (or with `--project-path umami`). This is the whole reason the docs project lives
   in `umami/` and not at the repo top.

2. **Subpath hosting is the one thing that breaks static sites.** The site is served at a path
   (`/docs/umami-python/`), not a domain root. Without help, Quarto emits **root-relative** asset
   paths (`/site_libs/…`, `/reference/…`) that 404 behind a subpath. The fix is a single key —
   **`site_url`** in `great-docs.yml`. Great Docs writes it into the generated `_quarto.yml` as
   `website.site-url` on every build, and Quarto derives the base path (`/docs/umami-python/`) from
   it, so CSS/JS/nav/search all resolve correctly. This is the highest-leverage line in the config;
   if the deployed site looks unstyled, this is the first thing to check.

3. **Dynamic introspection imports the package.** `umami/umami/__init__.py` re-exports everything
   from `.impl`, which imports `httpx2` and `pydantic` at module load. Great Docs' default
   `dynamic: true` mode **imports `umami`** to render the reference, so it must run in an environment
   where `import umami` succeeds. **Install `great-docs` into the existing project venv** (which
   already has `umami` editable-installed + `httpx2` + `pydantic`) — do **not** use isolated
   `uvx great-docs`, whose sandbox can't see `umami`. (If dynamic ever fails, Great Docs auto-retries
   with static `griffe` analysis; you can also pin `dynamic: false`.)

### Environment check (already verified on this machine)

- **Quarto 1.9.38** — installed ✅ (Great Docs renders via Quarto)
- **Python 3.14.5** in the `umami-python` venv — ✅ (Great Docs needs ≥ 3.11)
- **`great-docs`** — added to the `[dev]` extra in `umami/pyproject.toml` (resolves to `0.13.0`,
  verified on 3.14.5); Unit 1 installs it via `uv pip install -e "./umami[dev]"`. It pulls in the
  Jupyter/Quarto execution stack (~95 packages) — heavy, but it's how Quarto runs. (If you'd rather
  not bloat the test install, a separate `docs` extra is a clean alternative; Michael chose `dev`.)
- **Docstring style** — **Google** (`Args:` / `Returns:`), so `parser: google`

---

## Target `great-docs.yml`

`great-docs init` auto-generates a baseline (display name, detected parser, an auto-categorized
`reference:` block). Unit 1 then reshapes it toward the structure below. Treat the `reference:`
section as the **intent**; confirm the exact member-name syntax (especially the `models.*` /
`errors.*` submodule entries) against `great-docs scan --verbose` and adjust if Great Docs expects a
different form.

```yaml
# umami/great-docs.yml — Umami Analytics documentation site
display_name: Umami Analytics       # package import name is `umami`; PyPI is `umami-analytics`
parser: google                      # docstrings use Google-style Args:/Returns:
dynamic: true                       # import-based introspection (accurate for .impl re-exports)

# Published at a subpath — drives Quarto's base path so CSS/JS/nav/search resolve. (See "Why" #2.)
site_url: "https://mkennedy.codes/docs/umami-python/"

# GitHub integration (also auto-detectable from pyproject [project.urls] Source/Homepage)
repo: https://github.com/mikeckennedy/umami-python
github_style: widget
source:
  enabled: true
  branch: main
  placement: usage

pypi: true                          # -> https://pypi.org/project/umami-analytics/

sidebar_filter:
  enabled: true
  min_items: 20

# Landing page is umami/README.md automatically — no `homepage`/`user_guide` needed (minimal scope).

reference:
  title: "API Reference"
  desc: "The public umami-analytics surface: configuration, auth, sending events, and querying stats."
  sections:
    - title: Configuration
      desc: One-time setup. set_url_base is required before any operation.
      contents: [set_url_base, set_website_id, set_hostname, set_cloud_api_key, clear_cloud_api_key, enable, disable]
    - title: Authentication
      desc: Required for the query endpoints and verify_token.
      contents: [login, login_async, is_logged_in, verify_token, verify_token_async]
    - title: Sending events
      desc: Custom events, revenue, and page views. No login required.
      contents: [new_event, new_event_async, new_revenue_event, new_revenue_event_async, new_page_view, new_page_view_async]
    - title: Querying stats
      desc: Read analytics back out. Requires login.
      contents: [websites, websites_async, website_stats, website_stats_async, active_users, active_users_async]
    - title: Health
      contents: [heartbeat, heartbeat_async]
    - title: Response models
      desc: Pydantic models returned by the query functions.
      contents: [models.WebsitesResponse, models.Website, models.WebsiteStats, models.WebsiteStatsCmp, models.LoginResponse, models.User, models.WebsiteUser]
    - title: Errors
      desc: Exception hierarchy (ValidationError is the base).
      contents: [errors.ValidationError, errors.OperationNotAllowedError]
```

> The public surface mirrors `__all__` in `umami/umami/__init__.py`. Note it now includes
> `set_cloud_api_key` / `clear_cloud_api_key` (Umami Cloud API-key auth) — the table in `CLAUDE.md`
> §3 predates those and is slightly stale; the structure above is authoritative.

---

## Units of work (do in this order)

| Order | Document | Suggested commit | What |
|---|---|---|---|
| 1 | [`01-scaffold-config.md`](01-scaffold-config.md) | `docs: add Great Docs config for the documentation site` | Install `great-docs` into the venv; `great-docs init` from `umami/`; reshape `umami/great-docs.yml` to the target above; ignore the build dir; add a `Documentation` URL to `pyproject.toml`. |
| 2 | [`02-build-deploy-runbook.md`](02-build-deploy-runbook.md) | `docs: add docs build & deploy runbook` | First clean build + local preview to verify subpath assets; add `dev-docs/docs-site.md` runbook (install → build → `rsync` transfer → nginx location block); optional `change-log.md` note. |

Unit 1 is the substance. Unit 2 is verification + the repeatable runbook Michael will use to publish.

---

## What gets committed vs. ignored

- ✅ **Commit:** `umami/great-docs.yml`, the `umami/.gitignore` update, the `pyproject.toml`
  `Documentation` URL, and `dev-docs/docs-site.md`.
- ❌ **Never commit:** `umami/great-docs/` — the ephemeral Quarto build directory (contains
  `_site/`, `.quarto/`, generated `_quarto.yml`, `llms.txt`, etc.). Unit 1 gitignores it.

---

## Future work (explicitly out of scope here)

Deferred by the "minimal / build-locally" decisions; pick up later if wanted:

- **Fuller narrative guides** (the "Full guide set" we set aside): getting started, self-hosted vs
  Umami Cloud auth, sending events, querying stats, sync-vs-async patterns, error handling, and an
  example-client walkthrough — authored as `.qmd` files under `umami/<user_guide>/` and wired with
  `user_guide:` in `great-docs.yml`.
- **CI auto-deploy** — a GitHub Actions workflow that builds and `rsync`/SSH-deploys to the server on
  push to `main` (needs repo secrets: SSH key, host, target path). `great-docs setup-github-pages`
  exists but targets GitHub Pages, not Michael's nginx box, so it would be adapted, not used as-is.
- **Versioned docs** (`great-docs build --versions …`) with a version selector. Great Docs
  auto-appends the version prefix to `site-url`, so subpath hosting keeps working.
- **Changelog page** from GitHub Releases (`changelog.enabled`) — requires published Releases on the
  repo (tags alone aren't enough). The repo's `change-log.md` stays the source of truth meanwhile.
- **Quality gates before publish** — `great-docs check-links`, `proofread`, `lint`, plus a social-card
  image. `llms.txt` / `llms-full.txt` are generated automatically on every build (free).

---

## References

- Great Docs user guide: https://posit-dev.github.io/great-docs/
- Great Docs full LLM reference: https://posit-dev.github.io/great-docs/llms-full.txt
  (Deployment → "Subdirectory Deployments" and Configuration → "Site URL" are the relevant sections)
- Umami HTTP API: https://umami.is/docs/api
- Public surface: `umami/umami/__init__.py` (`__all__`); models: `umami/umami/models/__init__.py`;
  errors: `umami/umami/errors/__init__.py`
