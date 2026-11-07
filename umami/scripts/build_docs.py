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

# Files the site must contain for AI agents. Great Docs reports success even when
# llms-full.txt is skipped (it prints "Could not import <package>" and moves on), so the
# only reliable check is the output itself.
REQUIRED_OUTPUTS = [
    'llms.txt',
    'llms-full.txt',
    'skill.md',
    '.well-known/agent-skills/index.json',
    '.well-known/agent-skills/umami-analytics/SKILL.md',
    '.well-known/skills/default/SKILL.md',
    'user-guide/index.html',
    'reference/index.html',
    'sitemap.xml',
    'robots.txt',
    'search.json',
]
USER_GUIDE_DIR = UMAMI_DIR / 'user_guide'
SKILL_FILE = UMAMI_DIR / 'skills' / 'umami-analytics' / 'SKILL.md'


def _guide_titles() -> list[str]:
    """Titles from the user guide frontmatter, in sidebar order."""
    titles = []
    for qmd in sorted(USER_GUIDE_DIR.glob('*.qmd')):
        for line in qmd.read_text(encoding='utf-8').splitlines()[1:12]:
            if line.startswith('title:'):
                titles.append(line.split(':', 1)[1].strip().strip('"'))
                break
    return titles


def verify_site(site: Path) -> list[str]:
    """Return a list of problems with the built site. Empty means it is publishable."""
    problems = [f'missing {rel}' for rel in REQUIRED_OUTPUTS if not (site / rel).is_file()]
    if problems:
        return problems

    full = (site / 'llms-full.txt').read_text(encoding='utf-8')
    if 'This is the User Guide documentation' not in full:
        problems.append('llms-full.txt has no User Guide section (user_guide/ not picked up)')
    for title in _guide_titles():
        if f'### {title}\n' not in full:  # Great Docs adds this heading for pages that open with prose
            problems.append(f'llms-full.txt is missing the guide page "{title}"')

    skill_src = SKILL_FILE.read_text(encoding='utf-8')
    for rel in ('skill.md', '.well-known/agent-skills/umami-analytics/SKILL.md', '.well-known/skills/default/SKILL.md'):
        if (site / rel).read_text(encoding='utf-8') != skill_src:
            problems.append(f'{rel} is not the hand-written skill from {SKILL_FILE.relative_to(UMAMI_DIR)}')

    robots = (site / 'robots.txt').read_text(encoding='utf-8')
    for name in ('llms.txt', 'llms-full.txt'):
        if f'Llms-txt: https://mkennedy.codes/docs/umami-python/{name}' not in robots:
            problems.append(f'robots.txt does not list {name}')
    return problems


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

    # Refuse to publish a site that is missing its agent-facing files or guide pages.
    problems = verify_site(SITE)
    if problems:
        print('error: built site failed verification:', file=sys.stderr)
        for p in problems:
            print(f'  - {p}', file=sys.stderr)
        return 1
    print(f'Verified {len(REQUIRED_OUTPUTS)} required outputs, the skill copies, and the user guide in llms-full.txt')

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
