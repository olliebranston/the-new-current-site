from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
THOUGHT_PIECES_PATH = REPO_ROOT / "data" / "thought-pieces.json"
OUTPUT_PATH = REPO_ROOT / "feed.xml"
SITE_BASE = "https://olliebranston.github.io/the-new-current-site"


def format_rss_date(date_str: str) -> str:
    dt = datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
    return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")


def build_feed(articles: list[dict]) -> str:
    sorted_articles = sorted(
        articles,
        key=lambda a: a.get("date", ""),
        reverse=True,
    )

    rss = ET.Element("rss", version="2.0")
    rss.set("xmlns:atom", "http://www.w3.org/2005/Atom")
    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = "The New Current"
    ET.SubElement(channel, "link").text = f"{SITE_BASE}/"
    ET.SubElement(channel, "description").text = (
        "Energy transition writing and analysis by Ollie Branston — "
        "markets, policy, technology, and system change."
    )
    ET.SubElement(channel, "language").text = "en-gb"
    ET.SubElement(channel, "lastBuildDate").text = format_rss_date(
        sorted_articles[0]["date"] if sorted_articles else "2025-01-01"
    )

    atom_link = ET.SubElement(channel, "atom:link")
    atom_link.set("href", f"{SITE_BASE}/feed.xml")
    atom_link.set("rel", "self")
    atom_link.set("type", "application/rss+xml")

    for article in sorted_articles:
        link = article.get("link", "")
        if not link.startswith("articles/"):
            continue
        full_url = f"{SITE_BASE}/{link}"

        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = article.get("title", "Untitled")
        ET.SubElement(item, "link").text = full_url
        ET.SubElement(item, "guid", isPermaLink="true").text = full_url
        ET.SubElement(item, "description").text = article.get("summary", "")
        ET.SubElement(item, "author").text = article.get("author", "Oliver Branston")
        ET.SubElement(item, "category").text = article.get("topic", "Energy")

        date_str = article.get("date")
        if date_str:
            ET.SubElement(item, "pubDate").text = format_rss_date(date_str)

    ET.indent(rss, space="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(rss, encoding="unicode")


def main() -> None:
    payload = json.loads(THOUGHT_PIECES_PATH.read_text(encoding="utf-8"))
    articles = payload.get("articles", [])
    feed_xml = build_feed(articles)
    OUTPUT_PATH.write_text(feed_xml, encoding="utf-8")
    print(f"Generated {OUTPUT_PATH.relative_to(REPO_ROOT)} ({len(articles)} articles)")


if __name__ == "__main__":
    main()
