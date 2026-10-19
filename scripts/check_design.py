"""Design-system and rendering checks for the editorial redesign.

Usage:
    python scripts/check_design.py                    # run every check
    python scripts/check_design.py --record-baseline  # (re)write docs/design/chart-baseline.json
    python scripts/check_design.py --skip-render      # style/byline/smoke/sync checks only

Prints one PASS/FAIL line per check and exits 1 if any check fails.
Screenshots of every page/width/theme are saved to docs/design/screens/ (gitignored).
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import http.server
import json
import re
import socketserver
import subprocess
import sys
import threading
from dataclasses import dataclass, field
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CSS_PATH = REPO_ROOT / "css" / "styles.css"
DESIGN_DIR = REPO_ROOT / "docs" / "design"
SCREENS_DIR = DESIGN_DIR / "screens"
BASELINE_PATH = DESIGN_DIR / "chart-baseline.json"

PAGES = [
    "index.html",
    "thought-pieces.html",
    "articles/article-8.html",
    "brain-dumps.html",
    "data.html",
    "reporting.html",
    "about.html",
]
WIDTHS = [1440, 768, 390]
THEMES = ["light", "dark"]
VIEWPORT_HEIGHT = 900
MAX_DETAIL_LINES = 12

# Selectors made only of :root / html / data-theme parts are token blocks.
TOKEN_SELECTOR_RE = re.compile(
    r"^(?::root|html|\[data-theme=[\"']?(?:dark|light)[\"']?\]"
    r"|:not\(\[data-theme=[\"']?(?:dark|light)[\"']?\]\))+$"
)
COLOUR_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b|\b(?:rgba?|hsla?)\s*\(", re.IGNORECASE)
GRADIENT_RE = re.compile(r"(?:repeating-)?(?:linear|radial|conic)-gradient\s*\(", re.IGNORECASE)
ISO_DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")


@dataclass
class Result:
    key: str
    name: str
    passed: bool
    details: list[str] = field(default_factory=list)


@dataclass
class Declaration:
    prop: str
    value: str
    line: int
    selector: str
    in_token_block: bool


# ─── CSS parsing ────────────────────────────────────────────────────


def strip_comments(css: str) -> str:
    # Replace comments with same-length whitespace so line numbers stay correct.
    return re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group(0)), css, flags=re.DOTALL)


def parse_declarations(css: str) -> list[Declaration]:
    """Walk the stylesheet tracking the innermost selector for every declaration."""
    css = strip_comments(css)
    declarations: list[Declaration] = []
    stack: list[str] = []
    buffer_start = 0
    i = 0

    def line_of(pos: int) -> int:
        return css.count("\n", 0, pos) + 1

    def flush_declarations(chunk: str, chunk_start: int) -> None:
        if not stack or stack[-1].startswith("@"):
            return
        selector = stack[-1]
        compact = re.sub(r"\s+", "", selector)
        in_token = all(TOKEN_SELECTOR_RE.match(part) for part in compact.split(",") if part)
        offset = 0
        for piece in chunk.split(";"):
            if ":" in piece and piece.strip():
                prop, value = piece.split(":", 1)
                prop_pos = chunk_start + offset + (len(piece) - len(piece.lstrip()))
                declarations.append(
                    Declaration(prop.strip().lower(), value.strip(), line_of(prop_pos), selector, in_token)
                )
            offset += len(piece) + 1

    while i < len(css):
        ch = css[i]
        if ch in "\"'":
            end = css.find(ch, i + 1)
            i = len(css) if end == -1 else end + 1
            continue
        if ch == "(":
            # Skip parenthesised content (url(), data URIs) wholesale.
            depth = 1
            j = i + 1
            while j < len(css) and depth:
                depth += {"(": 1, ")": -1}.get(css[j], 0)
                j += 1
            i = j
            continue
        if ch == "{":
            head = css[buffer_start:i]
            # Anything before the last ';' in the head is a declaration (or @import).
            if ";" in head:
                cut = head.rfind(";") + 1
                flush_declarations(head[:cut], buffer_start)
                head = head[cut:]
            stack.append(head.strip())
            buffer_start = i + 1
        elif ch == "}":
            flush_declarations(css[buffer_start:i], buffer_start)
            if stack:
                stack.pop()
            buffer_start = i + 1
        i += 1

    return declarations


def fmt_decl(d: Declaration) -> str:
    selector = re.sub(r"\s+", " ", d.selector)
    return f"line {d.line}: {selector[:60]} {{ {d.prop}: {d.value[:70]} }}"


def summarise(failures: list[str]) -> list[str]:
    shown = failures[:MAX_DETAIL_LINES]
    if len(failures) > MAX_DETAIL_LINES:
        shown.append(f"... and {len(failures) - MAX_DETAIL_LINES} more")
    return shown


def style_checks() -> list[Result]:
    decls = parse_declarations(CSS_PATH.read_text(encoding="utf-8"))
    results = []

    bad = [fmt_decl(d) for d in decls if not d.in_token_block and COLOUR_RE.search(d.value)]
    results.append(Result("a", "No literal colours outside token blocks", not bad, [f"{len(bad)} violations"] + summarise(bad) if bad else []))

    bad = [
        fmt_decl(d)
        for d in decls
        if d.prop == "box-shadow" and not re.fullmatch(r"none|var\(--focus-ring[\w-]*\)", d.value.replace(" !important", "").strip())
    ]
    results.append(Result("b", "box-shadow only none or focus-ring token", not bad, [f"{len(bad)} violations"] + summarise(bad) if bad else []))

    bad = [fmt_decl(d) for d in decls if GRADIENT_RE.search(d.value)]
    results.append(Result("c", "No gradients", not bad, [f"{len(bad)} violations"] + summarise(bad) if bad else []))

    allowed_radius = {"var(--radius)", "0", "0px", "50%"}
    bad = []
    for d in decls:
        if re.fullmatch(r"border(-[a-z]+)*-radius", d.prop):
            parts = [p for p in re.split(r"[\s/]+", d.value.replace("!important", "")) if p]
            if not parts or any(p not in allowed_radius for p in parts):
                bad.append(fmt_decl(d))
    results.append(Result("d", "border-radius only var(--radius), 0 or 50%", not bad, [f"{len(bad)} violations"] + summarise(bad) if bad else []))

    fs_tokens = sorted({d.prop for d in decls if d.prop.startswith("--fs-")})
    bad = [
        fmt_decl(d)
        for d in decls
        if (d.prop == "font-size" and not re.fullmatch(r"var\(--fs-[\w-]+\)|inherit", d.value.replace(" !important", "").strip()))
        or (d.prop == "font" and d.value.strip() != "inherit")
    ]
    details = [f"{len(fs_tokens)} --fs- tokens defined: {', '.join(fs_tokens) or 'none'}"]
    if bad:
        details.append(f"{len(bad)} font-size violations")
        details += summarise(bad)
    results.append(Result("e", "font-size via var(--fs-…) and at most 8 size tokens", not bad and len(fs_tokens) <= 8, details))

    bad = [
        fmt_decl(d)
        for d in decls
        if d.prop == "font-family"
        and not d.in_token_block
        and not re.fullmatch(r"var\(--font-(serif|sans)\)|inherit", d.value.replace(" !important", "").strip())
    ]
    results.append(Result("f", "font-family only var(--font-serif) / var(--font-sans)", not bad, [f"{len(bad)} violations"] + summarise(bad) if bad else []))

    return results


# ─── Content checks ─────────────────────────────────────────────────


def html_files() -> list[Path]:
    return sorted(p for p in REPO_ROOT.rglob("*.html") if ".git" not in p.parts and "node_modules" not in p.parts)


# The one permitted use: the Person "alternateName" inside JSON-LD structured data,
# which tells search engines both names belong to the same person.
ALLOWED_ALTERNATE_NAME_RE = re.compile(r'^\s*"alternateName":\s*"Oliver Branston",?\s*$')


def byline_check() -> Result:
    bad = []
    for path in sorted((REPO_ROOT / "data").glob("*.json")) + html_files():
        in_json_ld = False
        for n, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if '<script type="application/ld+json">' in line:
                in_json_ld = True
            if "Oliver Branston" in line and not (
                path.suffix == ".html" and in_json_ld and ALLOWED_ALTERNATE_NAME_RE.match(line)
            ):
                bad.append(f"{path.relative_to(REPO_ROOT).as_posix()}:{n}")
            if "</script>" in line:
                in_json_ld = False
    return Result("g", 'No "Oliver Branston" byline in data/*.json or .html', not bad, [f"{len(bad)} occurrences"] + summarise(bad) if bad else [])


def run_script(key: str, name: str, script: str) -> tuple[Result, str]:
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / script)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    output = (proc.stdout + proc.stderr).strip()
    return Result(key, name, proc.returncode == 0, [] if proc.returncode == 0 else output.splitlines()[-MAX_DETAIL_LINES:]), output


def smoke_check() -> Result:
    return run_script("j", "smoke_test_site.py passes", "smoke_test_site.py")[0]


def layout_sync_check() -> Result:
    def snapshot() -> dict[str, str]:
        return {p.relative_to(REPO_ROOT).as_posix(): hashlib.sha1(p.read_bytes()).hexdigest() for p in html_files()}

    before = snapshot()
    result, output = run_script("k", "render_static_layout.py produces no diff", "render_static_layout.py")
    after = snapshot()
    changed = sorted(path for path in after if before.get(path) != after[path])
    if not result.passed:
        return result
    if changed:
        return Result("k", result.name, False, ["Pages were out of sync with templates (now re-rendered):"] + summarise(changed))
    return result


# ─── Rendering checks (Playwright) ──────────────────────────────────


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


class ThreadingServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    request_queue_size = 64  # Chromium opens many parallel connections; the default backlog of 5 drops some


def start_server() -> tuple[socketserver.TCPServer, str]:
    handler = functools.partial(QuietHandler, directory=str(REPO_ROOT))
    server = ThreadingServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    host, port = server.server_address
    return server, f"http://{host}:{port}"


PAGE_PROBE_JS = r"""
() => {
  const canvases = [...document.querySelectorAll('canvas')];
  const canvasInfo = canvases.map((c) => {
    const r = c.getBoundingClientRect();
    let blank = true;
    let error = null;
    if (c.width > 0 && c.height > 0) {
      try {
        const data = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
        const step = Math.max(4, Math.floor(data.length / 4 / 20000) * 4);
        for (let i = 3; i < data.length; i += step) { if (data[i] !== 0) { blank = false; break; } }
      } catch (e) { error = String(e); }
    }
    return {
      id: c.id || c.className || '(anonymous)',
      cssW: r.width, cssH: r.height, w: c.width, h: c.height, blank, error,
      rect: { left: r.left + scrollX, top: r.top + scrollY, right: r.right + scrollX, bottom: r.bottom + scrollY },
    };
  });

  // Text vs canvas overlap: measure actual text runs, ignore text inside the canvas's own wrapper.
  const overlaps = [];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
    acceptNode: (n) => (n.nodeValue.trim() ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT),
  });
  const textNodes = [];
  while (walker.nextNode()) textNodes.push(walker.currentNode);
  canvases.forEach((c, idx) => {
    const cr = c.getBoundingClientRect();
    if (!cr.width || !cr.height) return;
    const wrapper = c.parentElement;
    for (const node of textNodes) {
      const el = node.parentElement;
      if (!el || (wrapper && wrapper.contains(el))) continue;
      if (el.closest('script,style,noscript,template,[hidden],[aria-hidden="true"]')) continue;
      const cs = getComputedStyle(el);
      if (cs.visibility === 'hidden' || parseFloat(cs.opacity) === 0) continue;
      const range = document.createRange();
      range.selectNodeContents(node);
      for (const tr of range.getClientRects()) {
        const w = Math.min(tr.right, cr.right) - Math.max(tr.left, cr.left);
        const h = Math.min(tr.bottom, cr.bottom) - Math.max(tr.top, cr.top);
        if (w > 2 && h > 2) {
          overlaps.push(`${canvasInfo[idx].id} <- "${node.nodeValue.trim().slice(0, 40)}" (${el.tagName.toLowerCase()}${el.className ? '.' + String(el.className).split(' ')[0] : ''})`);
          break;
        }
      }
    }
  });

  return {
    canvases: canvasInfo,
    overlaps,
    scrollWidth: document.documentElement.scrollWidth,
    innerWidth: window.innerWidth,
    text: document.body.innerText,
  };
}
"""


def render_checks(record_baseline: bool) -> list[Result]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return [Result("i", "Rendering checks", False, ["playwright not installed: pip install -r requirements-dev.txt && python -m playwright install chromium"])]

    SCREENS_DIR.mkdir(parents=True, exist_ok=True)
    baseline = {} if record_baseline or not BASELINE_PATH.exists() else json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    if not record_baseline and not baseline:
        return [Result("i", "Rendering checks", False, [f"{BASELINE_PATH.relative_to(REPO_ROOT)} missing; run with --record-baseline first"])]

    console_fail: list[str] = []
    overflow_fail: list[str] = []
    chart_fail: list[str] = []
    overlap_fail: list[str] = []
    date_fail: list[str] = []
    recorded: dict[str, int] = {}

    server, base_url = start_server()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            for page_path in PAGES:
                for theme in THEMES:
                    for width in WIDTHS:
                        label = f"{page_path} {width}px {theme}"
                        context = browser.new_context(
                            viewport={"width": width, "height": VIEWPORT_HEIGHT},
                            reduced_motion="reduce",  # disables scroll fade-ins so screenshots show everything
                        )
                        context.add_init_script(f"try {{ localStorage.setItem('theme', '{theme}'); }} catch (e) {{}}")
                        page = context.new_page()
                        errors: list[str] = []
                        page.on("console", lambda msg, errors=errors: errors.append(msg.text) if msg.type == "error" else None)
                        page.on("pageerror", lambda exc, errors=errors: errors.append(f"pageerror: {exc}"))
                        page.on(
                            "response",
                            lambda resp, errors=errors: errors.append(f"HTTP {resp.status} {resp.url}")
                            if resp.status >= 400 and resp.url.startswith(base_url)
                            else None,
                        )
                        try:
                            page.goto(f"{base_url}/{page_path}", wait_until="networkidle", timeout=45000)
                        except Exception as exc:  # noqa: BLE001 - report navigation problems as failures
                            errors.append(f"navigation: {exc}")
                        page.wait_for_timeout(1200)  # let Chart.js finish its animations

                        probe = page.evaluate(PAGE_PROBE_JS)
                        safe = page_path.replace("/", "_").replace(".html", "")
                        page.screenshot(path=str(SCREENS_DIR / f"{safe}-{width}-{theme}.png"), full_page=True)
                        context.close()

                        if errors:
                            console_fail += [f"{label}: {e[:160]}" for e in errors]
                        if probe["scrollWidth"] > probe["innerWidth"]:
                            overflow_fail.append(f"{label}: scrollWidth {probe['scrollWidth']} > innerWidth {probe['innerWidth']}")

                        count = len(probe["canvases"])
                        if record_baseline:
                            if page_path in recorded and recorded[page_path] != count:
                                chart_fail.append(f"{label}: canvas count {count} differs from {recorded[page_path]} at another width/theme")
                            recorded.setdefault(page_path, count)
                        elif count != baseline.get(page_path):
                            chart_fail.append(f"{label}: {count} canvases, baseline {baseline.get(page_path)}")
                        for c in probe["canvases"]:
                            if c["cssW"] <= 0 or c["cssH"] <= 0 or c["w"] <= 0 or c["h"] <= 0:
                                chart_fail.append(f"{label}: canvas {c['id']} has zero size")
                            elif c["error"]:
                                chart_fail.append(f"{label}: canvas {c['id']} unreadable ({c['error'][:80]})")
                            elif c["blank"]:
                                chart_fail.append(f"{label}: canvas {c['id']} is blank")
                        overlap_fail += [f"{label}: {o}" for o in probe["overlaps"]]

                        if theme == "light" and width == WIDTHS[0]:
                            dates = sorted(set(ISO_DATE_RE.findall(probe["text"])))
                            if dates:
                                date_fail.append(f"{page_path}: {len(dates)} ISO dates e.g. {', '.join(dates[:4])}")
            browser.close()
    finally:
        server.shutdown()

    if record_baseline:
        BASELINE_PATH.write_text(json.dumps(recorded, indent=2) + "\n", encoding="utf-8")
        print(f"Recorded canvas baseline to {BASELINE_PATH.relative_to(REPO_ROOT).as_posix()}: {recorded}")

    combos = len(PAGES) * len(WIDTHS) * len(THEMES)
    return [
        Result("h", "No raw ISO dates in rendered text", not date_fail, summarise(date_fail)),
        Result("i1", f"No console errors ({combos} page/width/theme combos)", not console_fail, [f"{len(console_fail)} errors"] + summarise(console_fail) if console_fail else []),
        Result("i2", "No horizontal overflow", not overflow_fail, summarise(overflow_fail)),
        Result("i3", "Chart integrity (canvas count vs baseline, non-zero, not blank)", not chart_fail, [f"{len(chart_fail)} problems"] + summarise(chart_fail) if chart_fail else []),
        Result("i4", "No text overlapping a canvas", not overlap_fail, [f"{len(overlap_fail)} overlaps"] + summarise(overlap_fail) if overlap_fail else []),
    ]


# ─── Main ───────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the editorial redesign rules and rendering integrity.")
    parser.add_argument("--record-baseline", action="store_true", help="write docs/design/chart-baseline.json from the current site")
    parser.add_argument("--skip-render", action="store_true", help="skip the Playwright checks (h, i)")
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    results = style_checks()
    results.append(byline_check())
    if not args.skip_render:
        results += render_checks(args.record_baseline)
    results.append(smoke_check())
    results.append(layout_sync_check())

    for r in results:
        print(f"{'PASS' if r.passed else 'FAIL'} [{r.key}] {r.name}")
        for line in r.details:
            print(f"       {line}")

    failed = [r.key for r in results if not r.passed]
    print()
    print(f"SUMMARY: {len(results) - len(failed)}/{len(results)} checks passed" + (f"; failed: {', '.join(failed)}" if failed else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
