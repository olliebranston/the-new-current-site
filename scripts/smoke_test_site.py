from __future__ import annotations

import argparse
import functools
import http.server
import socketserver
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SMOKE_PATHS = [
    "/",
    "/index.html",
    "/thought-pieces.html",
    "/brain-dumps.html",
    "/data.html",
    "/reporting.html",
    "/about.html",
    "/articles/article-8.html",
    "/css/styles.css",
    "/js/main.js",
    "/sitemap.xml",
    "/robots.txt",
    "/data/thought-pieces.json",
    "/data/news-radar.json",
    "/data/carbon-chart-data.json",
]


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


def run_server() -> tuple[socketserver.TCPServer, str]:
    handler = functools.partial(QuietHandler, directory=str(REPO_ROOT))
    server = socketserver.TCPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    return server, f"http://{host}:{port}"


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "TheNewCurrentSmokeTest/1.0"})

    with urllib.request.urlopen(request, timeout=15) as response:
        if response.status != 200:
            raise RuntimeError(f"{url} returned HTTP {response.status}")

        body = response.read()

    if not body:
        raise RuntimeError(f"{url} returned an empty response")

    return body


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a local static server and smoke-test key site assets.")
    parser.parse_args()
    server, base_url = run_server()
    failures = []

    try:
        for path in SMOKE_PATHS:
            try:
                body = fetch(f"{base_url}{path}")
                print(f"OK {path} ({len(body)} bytes)")
            except (RuntimeError, urllib.error.URLError) as exc:
                failures.append(f"{path}: {exc}")
    finally:
        server.shutdown()
        server.server_close()

    if failures:
        print("Smoke test failures:", file=sys.stderr)

        for failure in failures:
            print(f"- {failure}", file=sys.stderr)

        return 1

    print("Smoke tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
