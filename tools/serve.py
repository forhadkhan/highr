#!/usr/bin/env python3
"""Local static server that mirrors GitHub Pages URLs: /privacy serves privacy.html, / serves index.html.

    python3 tools/serve.py [port]      # default 8000, serves the project root
"""
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        resolved = Path(super().translate_path(path))
        if not resolved.exists() and resolved.with_name(resolved.name + ".html").is_file():
            return str(resolved.with_name(resolved.name + ".html"))
        return str(resolved)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"http://localhost:{port}/")
    ThreadingHTTPServer(("127.0.0.1", port), partial(Handler, directory=str(ROOT))).serve_forever()
