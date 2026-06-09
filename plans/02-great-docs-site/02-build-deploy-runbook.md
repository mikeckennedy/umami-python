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
  gitignored) is mirrored into the committed repo-root **`docs/`** by `scripts/build_docs.py`.
  Landing page: `umami/README.md`. API reference: auto-generated from `umami.__all__`.
- Deployment is **git-based**: commit `docs/`, push, and `git pull` on the server; nginx serves `docs/`.

## Prerequisites (once)

```bash
# from repo root, in a Python >= 3.11 venv
uv pip install -e "./umami[dev]"   # installs umami (editable) + great-docs + test/lint tools
quarto --version                    # Great Docs renders via Quarto (>= 1.5)
```

`great-docs` is in the `[dev]` extra. `dynamic: true` introspection imports `umami`, so it must run
in a venv where `import umami` works (the editable install above).

## Build

The "Build Docs" VSCode task (or the script directly) builds **and** mirrors the site into the
committed `docs/` folder:

```bash
python umami/scripts/build_docs.py    # great-docs build -> umami/great-docs/_site -> docs/
```

## Verify (subpath-aware)

Asset links are **relative** (subpath-safe). Use the "Preview Docs (subpath)" config, or:

```bash
python umami/scripts/serve_docs.py    # serves committed docs/ at http://127.0.0.1:8099/docs/umami-python/
```

All page URLs and linked `site_libs/…` assets should return `200`.

## Publish (commit, push, pull on the server)

The build mirrors the site into the committed repo-root `docs/`, so publishing is a normal git push
— no file transfer:

```bash
git add docs && git commit -m "docs: rebuild site" && git push
```

On the server, pull the repo (or a deploy checkout) on each release:

```bash
git -C <repo-on-server> pull --ff-only
```

## nginx (serve the committed docs/ at the subpath)

```nginx
# inside the mkennedy.codes `server { }` block
location = /docs/umami-python {
    return 301 /docs/umami-python/;        # enforce trailing slash so base paths resolve
}
location /docs/umami-python/ {
    alias <repo-on-server>/docs/;          # the committed docs/ folder (mirror of _site)
    index index.html;
    try_files $uri $uri/ $uri.html =404;   # Quarto clean URLs + directory indexes
}
```

`alias` strips the `/docs/umami-python/` URL prefix and serves from `docs/`, so the relative asset
links resolve correctly under the subpath.

## Re-publishing after changes

```bash
python umami/scripts/build_docs.py    # rebuild + refresh docs/
git add docs && git commit -m "docs: rebuild site" && git push
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
