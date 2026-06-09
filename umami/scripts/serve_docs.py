#!/usr/bin/env python3
"""Serve the built docs under the production subpath for a faithful local check.

`great-docs preview` serves at the server root (http://localhost:3000/), which works
because the site uses relative asset paths. This helper instead mounts the built
`great-docs/_site/` under the *real* deployed subpath, so what you see locally matches
production exactly:

    http://127.0.0.1:8099/docs/umami-python/   ==   https://mkennedy.codes/docs/umami-python/

Run the "Build Docs" config (or `great-docs build`) first to produce `great-docs/_site/`.
"""

from __future__ import annotations

import functools
import http.server
import socketserver
from pathlib import Path

PREFIX = '/docs/umami-python'
PORT = 8099
ROOT = Path(__file__).resolve().parent.parent / 'great-docs' / '_site'


class SubpathHandler(http.server.SimpleHTTPRequestHandler):
    """Serve files from ROOT, but only under PREFIX (mirrors an nginx `alias`)."""

    def translate_path(self, path: str) -> str:
        clean = path.split('?', 1)[0].split('#', 1)[0]
        if clean.startswith(PREFIX):
            path = clean[len(PREFIX) :] or '/'
        return super().translate_path(path)

    def send_head(self):  # redirect bare root / prefix-without-slash to PREFIX/
        if self.path in ('/', PREFIX):
            self.send_response(302)
            self.send_header('Location', PREFIX + '/')
            self.end_headers()
            return None
        return super().send_head()


class Server(socketserver.TCPServer):
    allow_reuse_address = True


def main() -> None:
    if not ROOT.is_dir():
        raise SystemExit(f"Build output not found: {ROOT}\nRun the 'Build Docs' config (great-docs build) first.")
    handler = functools.partial(SubpathHandler, directory=str(ROOT))
    with Server(('127.0.0.1', PORT), handler) as httpd:
        print(f'Serving {ROOT}')
        print(f'  -> http://127.0.0.1:{PORT}{PREFIX}/   (Ctrl+C to stop)')
        httpd.serve_forever()


if __name__ == '__main__':
    main()
