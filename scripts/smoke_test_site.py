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


CONTENT_CHECKS: list[tuple[str, bytes, str]] = [
    ("/index.html", b"themeToggle", "theme toggle button"),
    ("/index.html", b"data-theme", "anti-FOUC theme loader script"),
    ("/thought-pieces.html", b"themeToggle", "theme toggle button"),
    ("/thought-pieces.html", b"data-theme", "anti-FOUC theme loader script"),
    ("/articles/article-8.html", b"themeToggle", "theme toggle button"),
    ("/articles/article-8.html", b"data-theme", "anti-FOUC theme loader script"),
    ("/css/styles.css", b'[data-theme="dark"]', "dark mode CSS"),
    ("/css/styles.css", b".theme-toggle", "theme toggle CSS"),
    ("/css/styles.css", b".tp-search-bar", "thought pieces search CSS"),
    ("/css/styles.css", b".reading-progress", "reading progress bar CSS"),
    ("/css/styles.css", b".back-to-top", "back-to-top button CSS"),
    ("/js/main.js", b"initThemeToggle", "theme toggle JS"),
    ("/js/main.js", b"initReadingProgress", "reading progress JS"),
    ("/js/main.js", b"initBackToTop", "back-to-top JS"),
    ("/js/main.js", b"initThoughtPiecesPage", "thought pieces search JS"),
    # Iteration 3
    ("/index.html", b"skip-link", "skip-to-content link"),
    ("/index.html", b"application/rss+xml", "RSS autodiscovery link"),
    ("/index.html", b"feed.xml", "RSS feed link in head"),
    ("/css/styles.css", b"@media print", "print styles"),
    ("/css/styles.css", b".skip-link", "skip link CSS"),
    ("/js/main.js", b"initBrainDumpsPage", "brain dumps search JS"),
    ("/js/main.js", b"initKeyboardShortcuts", "keyboard shortcuts JS"),
    ("/js/main.js", b"initArticlePageFeatures", "article page features JS"),
    ("/js/main.js", b"article-toc", "table of contents JS"),
    ("/js/main.js", b"article-share-btn", "share button JS"),
    ("/js/main.js", b"BOOKMARKS_KEY", "bookmarks JS"),
    # Iteration 8
    ("/js/main.js", b"radar-show-more", "radar show-more button JS"),
    ("/js/main.js", b"heading-anchor", "article H2 deep link anchor JS"),
    ("/js/main.js", b"footer-year", "dynamic footer year JS"),
    ("/js/main.js", b"refreshLiveSnapshot", "auto-refresh live snapshot JS"),
    ("/css/styles.css", b".radar-show-more", "radar show-more CSS"),
    ("/css/styles.css", b".heading-anchor", "heading anchor CSS"),
    # Iteration 9
    ("/js/main.js", b"highlightMatch", "command palette search highlighting JS"),
    ("/js/main.js", b"toc-active", "ToC active section tracking JS"),
    ("/js/main.js", b"article-newsletter-cta", "newsletter CTA JS"),
    ("/css/styles.css", b".cmd-highlight", "command palette highlight CSS"),
    ("/css/styles.css", b".article-newsletter-cta", "newsletter CTA CSS"),
    ("/css/styles.css", b".toc-active", "ToC active section CSS"),
    # Iteration 10
    ("/js/main.js", b"trapFocus", "focus trap utility JS"),
    ("/js/main.js", b"QUICK_ACTIONS", "command palette quick actions JS"),
    ("/js/main.js", b"toggle-theme", "dark mode quick action JS"),
    ("/js/main.js", b"showShortcuts", "keyboard shortcuts help JS"),
    ("/css/styles.css", b".shortcuts-panel", "keyboard shortcuts panel CSS"),
    ("/css/styles.css", b".shortcut-row", "shortcut row CSS"),
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a local static server and smoke-test key site assets.")
    parser.parse_args()
    server, base_url = run_server()
    failures = []
    body_cache: dict[str, bytes] = {}

    try:
        for path in SMOKE_PATHS:
            try:
                body = fetch(f"{base_url}{path}")
                body_cache[path] = body
                print(f"OK {path} ({len(body)} bytes)")
            except (RuntimeError, urllib.error.URLError) as exc:
                failures.append(f"{path}: {exc}")

        for path, needle, description in CONTENT_CHECKS:
            body = body_cache.get(path)
            if body is None:
                failures.append(f"{path}: content check skipped (fetch failed)")
                continue
            if needle not in body:
                failures.append(f"{path}: missing {description} ({needle.decode()!r})")
            else:
                print(f"OK {path} contains {description}")
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
