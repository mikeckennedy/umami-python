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

## The subpath gotcha (read first)

Because `site_url` ends in `/docs/umami-python/`, Quarto emits asset/nav links **prefixed** with that
path (e.g. `/docs/umami-python/site_libs/…`). That's exactly right for production — **and** it means
a naïve local server that serves `_site` at `/` will 404 every asset and the page will look
unstyled. **That is not a broken build.** Verify the right way (below) before concluding anything is
wrong.

### Verify correctness two ways

1. **Confirm the prefix is baked in** (fast, proves production-correctness):

   ```bash
   cd umami
   grep -o '/docs/umami-python/site_libs[^"]*' great-docs/_site/index.html | head
   ```

   Seeing `/docs/umami-python/site_libs/…` means the base path is wired correctly. (Empty output ⇒
   `site_url` is wrong/missing — fix Unit 1 before going further.)

2. **Preview under the real path** (faithful end-to-end, mirrors nginx `alias`):

   ```bash
   cd umami
   mkdir -p /tmp/docpreview/docs
   ln -snf "$(pwd)/great-docs/_site" /tmp/docpreview/docs/umami-python
   ( cd /tmp/docpreview && python -m http.server 8099 )
   # open http://localhost:8099/docs/umami-python/  → styled, nav works, reference loads
   ```

`great-docs preview` is still fine for fast content iteration, but it may show the unstyled look for
the reason above — trust check #2 for "does it work deployed."

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

```bash
grep -o '/docs/umami-python/site_libs[^"]*' great-docs/_site/index.html | head   # prefix present?
# faithful local preview at the real path:
mkdir -p /tmp/docpreview/docs && ln -snf "$(pwd)/great-docs/_site" /tmp/docpreview/docs/umami-python
( cd /tmp/docpreview && python -m http.server 8099 )   # http://localhost:8099/docs/umami-python/
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
