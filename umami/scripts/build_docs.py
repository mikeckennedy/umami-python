#!/usr/bin/env python3
"""Build the docs and mirror the static site into the committed `docs/` folder.

`great-docs build` writes to `umami/great-docs/_site/`, which is ephemeral and gitignored
(Great Docs regenerates that directory on every build). This wrapper runs the build and then
mirrors `_site/` into the repo-root **`docs/`** directory, which IS committed to git. Publishing
is then just: commit `docs/`, push, and `git pull` on the server (nginx serves `docs/` statically).

Run via the VSCode "Build Docs" task/launch, or directly:  python umami/scripts/build_docs.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
UMAMI_DIR = _SCRIPT_DIR.parent  # umami/  (Great Docs project root, holds pyproject.toml)
REPO_ROOT = UMAMI_DIR.parent  # repo root
SITE = UMAMI_DIR / 'great-docs' / '_site'  # build output (ephemeral, gitignored)
DEST = REPO_ROOT / 'docs'  # committed, served statically by the web server


def main() -> int:
    # Use the great-docs from the same venv as this interpreter.
    great_docs = Path(sys.executable).with_name('great-docs')
    cmd = [str(great_docs) if great_docs.exists() else 'great-docs', 'build']
    print(f'$ {" ".join(cmd)}  (cwd={UMAMI_DIR})')
    result = subprocess.run(cmd, cwd=UMAMI_DIR)
    if result.returncode != 0:
        return result.returncode

    if not SITE.is_dir():
        print(f'error: build output missing: {SITE}', file=sys.stderr)
        return 1

    # Mirror _site/ -> docs/ as a full replace, so pages deleted between builds don't linger.
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(SITE, DEST)

    n_files = sum(1 for p in DEST.rglob('*') if p.is_file())
    print(f'\nMirrored {SITE.relative_to(REPO_ROOT)} -> {DEST.relative_to(REPO_ROOT)}/ ({n_files} files)')
    print('Publish with:  git add docs && git commit -m "docs: rebuild site" && git push')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
