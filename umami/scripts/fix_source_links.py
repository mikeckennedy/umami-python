#!/usr/bin/env python3
"""Quarto pre-render hook: repair GitHub "source" links for this two-tier repo.

Great Docs builds source links relative to the directory that holds `pyproject.toml`
(`umami/`), but the git repository root is one level above that (`umami-python/`). So
every generated link is missing the leading `umami/` package-dir segment:

    .../blob/main/umami/impl/__init__.py        <- what Great Docs writes (404)
    .../blob/main/umami/umami/impl/__init__.py   <- the real file on GitHub

Wired via `pre_render` in great-docs.yml, Quarto runs this after the reference `.qmd`
files are generated and before they're rendered to HTML, so patching the `.qmd` source
here produces correct links in the built site (and in `great-docs preview`).

Stdlib only — Quarto runs it with whatever `python3` is on PATH. Idempotent.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

REPO = 'mikeckennedy/umami-python'

# `.../blob/<branch>/umami/<x>`  ->  `.../blob/<branch>/umami/umami/<x>`
# The negative lookahead keeps it idempotent (won't double an already-fixed path).
_PATTERN = re.compile(rf'(github\.com/{re.escape(REPO)}/blob/[^/]+/)umami/(?!umami/)')
_REPLACEMENT = r'\1umami/umami/'

# Quarto sets QUARTO_PROJECT_DIR; during pre-render the CWD is the project dir too.
_PROJECT_DIR = Path(os.environ.get('QUARTO_PROJECT_DIR', '.')).resolve()


def _fix_file(path: Path) -> bool:
    text = path.read_text(encoding='utf-8')
    fixed = _PATTERN.sub(_REPLACEMENT, text)
    if fixed != text:
        path.write_text(fixed, encoding='utf-8')
        return True
    return False


def main() -> None:
    targets = list(_PROJECT_DIR.rglob('*.qmd'))
    targets += [p for name in ('llms.txt', 'llms-full.txt') if (p := _PROJECT_DIR / name).exists()]
    changed = sum(_fix_file(p) for p in targets)
    print(f"[fix_source_links] inserted missing 'umami/' segment in {changed} file(s)")


if __name__ == '__main__':
    main()
