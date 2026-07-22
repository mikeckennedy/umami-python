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

# The canonical install command. Great Docs derives the generated skill's install
# line from the IMPORTABLE module name (`umami`), producing `pip install umami` —
# which installs an unrelated PyPI package. The distribution is `umami-analytics`.
CANONICAL_INSTALL = 'uv pip install umami-analytics'


def _replace_in_file(path: Path, old: str, new: str) -> int:
    """Replace exact substring `old` with `new` in `path`. Idempotent and non-fatal.

    Returns the number of occurrences replaced. Missing files or absent patterns are
    warned about (not errors) so a future Great Docs change can't break publishing.
    """
    if not path.is_file():
        print(f'  note: {path.relative_to(SITE)} not found; skipping', file=sys.stderr)
        return 0
    text = path.read_text(encoding='utf-8')
    count = text.count(old)
    if count == 0:
        return 0  # already correct (idempotent) or the generator changed its output
    path.write_text(text.replace(old, new), encoding='utf-8')
    return count


def fix_skill_install(site: Path) -> int:
    """Rewrite the generated skill's `pip install umami` to the real distribution name.

    Great Docs has no config knob for the install/distribution name (it reuses the
    importable module name), so we patch the generated artifacts after the build. Each
    replacement is an exact, anchored substring, so it never touches `umami-analytics`,
    `import umami`, or the intentional "# NOT pip install umami" note from extra_body.
    """
    edits = 0
    # Markdown skill files: top-level skill.md plus the two .well-known copies. Anchor
    # on the ```bash fenced block so the backtick-quoted warning line is left alone.
    md_old = '```bash\npip install umami\n```'
    md_new = f'```bash\n{CANONICAL_INSTALL}\n```'
    for md in [site / 'skill.md', *sorted(site.glob('.well-known/**/SKILL.md'))]:
        edits += _replace_in_file(md, md_old, md_new)
    # Search index: same fence, but newlines are JSON-escaped (literal backslash-n).
    edits += _replace_in_file(
        site / 'search.json',
        '```bash\\npip install umami\\n```',
        f'```bash\\n{CANONICAL_INSTALL}\\n```',
    )
    # Human-facing skills page: the command is syntax-highlighted, so `pip` sits in its
    # own span. Rewrite the whole highlighted fragment.
    edits += _replace_in_file(
        site / 'skills.html',
        '<span class="ex">pip</span> install umami</span>',
        '<span class="ex">uv pip</span> install umami-analytics</span>',
    )
    return edits


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

    # Post-build: correct the generated skill's install command before mirroring.
    n_install = fix_skill_install(SITE)
    print(f'Patched skill install command in {n_install} place(s) -> "{CANONICAL_INSTALL}"')

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
