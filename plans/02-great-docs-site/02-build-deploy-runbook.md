# Unit 2 — Verify the build & write the publish runbook

**Suggested commit:** `docs: add docs build & deploy runbook`
**Branch:** same as Unit 1.
**Files touched (committed):** `dev-docs/docs-site.md` (new); optional `change-log.md` entry.

> Prerequisite: Unit 1 is done and `great-docs build` succeeds locally.

---

## Scope

Prove the built site is correct for **subpath** hosting, then capture the repeatable
build → transfer → serve procedure as a committed runbook Michael runs by hand (deployment is
manual by decision — no CI, no script).

---

## How subpath hosting actually resolves (verified)

This Quarto/Great-Docs version emits **relative** asset/nav links, not root-absolute ones:
`site_libs/…` on the landing page, `../site_libs/…` on nested reference pages. Relative paths are
**inherently subpath-safe** — they resolve correctly at any base, including `/docs/umami-python/`, so
there is nothing to "fix" with a path prefix. `site_url` is still set (it writes `website.site-url`
into `_quarto.yml`, used for the sitemap, canonical links, and `og:` URLs), but the asset wiring does
**not** depend on it here.

Consequence: a plain server that serves `_site` at `/` mostly works too, but to test the **real**
production layout, serve it under the actual path. The reliable check is a faithful serve + asset
status codes (do **not** grep for a `/docs/umami-python/…` prefix — there isn't one; the paths are
relative):

```bash
cd umami && great-docs build
mkdir -p /tmp/docpreview/docs
ln -snf "$(pwd)/great-docs/_site" /tmp/docpreview/docs/umami-python
( cd /tmp/docpreview && python -m http.server 8099 --bind 127.0.0.1 ) &
B=http://127.0.0.1:8099/docs/umami-python
for u in "/" "/reference/" "/reference/new_event.html" "/search.json" "/sitemap.xml"; do
  printf "%-32s " "$u"; curl -s -o /dev/null -w "%{http_code}\n" "$B$u"; done
# also confirm the CSS/JS the landing page links return 200:
for c in $(curl -s "$B/" | grep -oE '(href|src)="(site_libs[^"]+)"' | sed -E 's/.*"(site_libs[^"]+)"/\1/'); do
  printf "%-60s " "$c"; curl -s -o /dev/null -w "%{http_code}\n" "$B/$c"; done
pkill -f "http.server 8099"
```

All page URLs and every linked `site_libs/…` asset should return `200`. (`great-docs preview` is also
fine for fast content iteration.)

> **Build gotcha — inline `Returns:`.** Great Docs renders docstrings via griffe. An inline
> `Returns: <text>` (description on the same line) is parsed as a *trailing text section* and the
> renderer aborts the whole API build with `unexpected text section DocstringSectionKind.text`. Use
> block form (`Returns:` then the description on the next, indented line). This repo was scrubbed of
> inline `Returns:` on 2026-06-08; keep new docstrings in block form.

> **Build gotcha — "source" links (two-tier layout).** Great Docs builds GitHub source links
> relative to the directory holding `pyproject.toml` (`umami/`), but the git root is one level up,
> so links come out as `.../blob/main/umami/impl/__init__.py` (404) instead of
> `.../blob/main/umami/umami/impl/__init__.py`. Fixed by a Quarto `pre_render` hook
> (`scripts/fix_source_links.py`, wired in `great-docs.yml`) that reinserts the missing `umami/`
> segment in the generated `.qmd` before render — automatic on every `build`/`preview`, no manual
> step. `source.path` can't fix this (it collapses every module to its bare filename).

---

## Create `dev-docs/docs-site.md`

Write the runbook below to `dev-docs/docs-site.md`. Fill in the real SSH host/user and confirm the
server path against Michael's nginx layout (`<host>`, `<user>`, and `<docroot>` are placeholders).

````markdown
# Documentation site runbook (Great Docs)

The docs site for `umami-analytics` is built with [Great Docs](https://posit-dev.github.io/great-docs/)
and published at **https://mkennedy.codes/docs/umami-python/**.

- Config: `umami/great-docs.yml` (committed). Build output: `umami/great-docs/_site/` (ephemeral,
  gitignored). Landing page: `umami/README.md`. API reference: auto-generated from `umami.__all__`.
- Deployment is **manual**: build locally, `rsync` the `_site/` to the server, nginx serves it.

## Prerequisites (once)

```bash
# from repo root, in a Python >= 3.11 venv
uv pip install -e "./umami[dev]"   # installs umami (editable) + great-docs + test/lint tools
quarto --version                    # Great Docs renders via Quarto (>= 1.5)
```

`great-docs` is in the `[dev]` extra. `dynamic: true` introspection imports `umami`, so it must run
in a venv where `import umami` works (the editable install above).

## Build

```bash
cd umami
great-docs build          # -> umami/great-docs/_site/
```

## Verify (subpath-aware)

Asset links are **relative** (subpath-safe), so serve under the real path and check status codes —
don't grep for a path prefix:

```bash
mkdir -p /tmp/docpreview/docs && ln -snf "$(pwd)/great-docs/_site" /tmp/docpreview/docs/umami-python
( cd /tmp/docpreview && python -m http.server 8099 --bind 127.0.0.1 ) &
B=http://127.0.0.1:8099/docs/umami-python
for u in "/" "/reference/" "/reference/new_event.html" "/search.json"; do
  printf "%-30s " "$u"; curl -s -o /dev/null -w "%{http_code}\n" "$B$u"; done   # all 200
pkill -f "http.server 8099"
# open http://localhost:8099/docs/umami-python/ in a browser for a visual check
```

## Publish (transfer to the server)

```bash
# trailing slash on the SOURCE copies the contents of _site/ into the target dir
rsync -avz --delete umami/great-docs/_site/ <user>@<host>:<docroot>/docs/umami-python/
```

`--delete` keeps the server in exact sync (removes files dropped from the build). Drop it if other
content lives under that directory.

## nginx (serve the static site at the subpath)

```nginx
# inside the mkennedy.codes `server { }` block
location = /docs/umami-python {
    return 301 /docs/umami-python/;        # enforce trailing slash so base paths resolve
}
location /docs/umami-python/ {
    alias <docroot>/docs/umami-python/;    # dir holding the _site contents
    index index.html;
    try_files $uri $uri/ $uri.html =404;   # Quarto clean URLs + directory indexes
}
```

`alias` strips the `/docs/umami-python/` URL prefix and serves from the target dir, so the
prefixed asset links (`/docs/umami-python/site_libs/…`) resolve to `<docroot>/docs/umami-python/site_libs/…`.

## Re-publishing after changes

```bash
cd umami && great-docs build && \
rsync -avz --delete great-docs/_site/ <user>@<host>:<docroot>/docs/umami-python/
```
````

---

## Optional: changelog note

The `Documentation` URL added to `pyproject.toml` (Unit 1) is user-facing on PyPI, so a `change-log.md`
entry is reasonable. Under the `Unreleased` → `Added` group:

```markdown
### Added
- Documentation site published at https://mkennedy.codes/docs/umami-python/ (built with Great Docs),
  and a `Documentation` project URL on PyPI.
```

---

## Done when

- [ ] `grep` shows `/docs/umami-python/site_libs/…` in the built `index.html` (base path correct).
- [ ] The faithful local preview at `http://localhost:8099/docs/umami-python/` renders **styled**,
      with working navigation and a loading API **Reference** section.
- [ ] `dev-docs/docs-site.md` exists with the build/verify/transfer/nginx steps and real host details
      (or clearly-marked placeholders) — committed.
- [ ] (Optional) `change-log.md` has the `Added` note.
- [ ] No `umami/great-docs/` artifacts are staged (still gitignored from Unit 1).
