from __future__ import annotations

import datetime as dt
import re
import subprocess
from pathlib import Path
from xml.etree import ElementTree as ET


BASE_URL = "https://olliebranston.github.io/the-new-current-site/"
REPO_ROOT = Path(__file__).resolve().parents[1]
SITEMAP_PATH = REPO_ROOT / "sitemap.xml"
ROOT_PAGE_ORDER = [
    "index.html",
    "thought-pieces.html",
    "brain-dumps.html",
    "data.html",
    "reporting.html",
    "about.html",
]


def git_last_modified(path: Path) -> str:
    relative_path = path.relative_to(REPO_ROOT).as_posix()
    result = subprocess.run(
        ["git", "log", "-1", "--format=%cs", "--", relative_path],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    last_modified = result.stdout.strip()
    if last_modified:
        return last_modified

    return dt.date.today().isoformat()


def page_url(path: Path) -> str:
    relative_path = path.relative_to(REPO_ROOT).as_posix()
    if relative_path == "index.html":
        return BASE_URL

    return f"{BASE_URL}{relative_path}"


def discover_pages() -> list[Path]:
    ordered_root_pages = [
        REPO_ROOT / filename
        for filename in ROOT_PAGE_ORDER
        if (REPO_ROOT / filename).is_file()
    ]
    ordered_root_names = {path.name for path in ordered_root_pages}
    extra_root_pages = sorted(
        path
        for path in REPO_ROOT.glob("*.html")
        if path.name not in ordered_root_names
    )
    article_pages = sorted((REPO_ROOT / "articles").glob("*.html"), key=article_sort_key)

    return [*ordered_root_pages, *extra_root_pages, *article_pages]


def article_sort_key(path: Path) -> tuple[bool, list[int | str]]:
    natural_name = [
        int(part) if part.isdigit() else part
        for part in re.findall(r"\d+|\D+", path.name)
    ]
    return (path.name.startswith("archive-"), natural_name)


def build_sitemap(pages: list[Path]) -> ET.ElementTree:
    ET.register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
    urlset = ET.Element("{http://www.sitemaps.org/schemas/sitemap/0.9}urlset")

    for page in pages:
        url = ET.SubElement(urlset, "{http://www.sitemaps.org/schemas/sitemap/0.9}url")
        loc = ET.SubElement(url, "{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        loc.text = page_url(page)
        lastmod = ET.SubElement(url, "{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod")
        lastmod.text = git_last_modified(page)

    tree = ET.ElementTree(urlset)
    ET.indent(tree, space="  ")
    return tree


def main() -> None:
    tree = build_sitemap(discover_pages())
    tree.write(SITEMAP_PATH, encoding="utf-8", xml_declaration=True)
    SITEMAP_PATH.write_text(f"{SITEMAP_PATH.read_text(encoding='utf-8')}\n", encoding="utf-8")


if __name__ == "__main__":
    main()
