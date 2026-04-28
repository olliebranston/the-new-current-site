from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


BASE_URL = "https://olliebranston.github.io/the-new-current-site/"
REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"


class SiteValidationError(Exception):
    pass


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str, str | None]] = []
        self.canonical: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)

        if tag == "a" and attributes.get("href"):
            self.links.append(("href", attributes["href"] or "", None))
        elif tag in {"img", "script"} and attributes.get("src"):
            self.links.append(("src", attributes["src"] or "", tag))
        elif tag == "link" and attributes.get("href"):
            rel = attributes.get("rel") or ""
            href = attributes["href"] or ""
            self.links.append(("href", href, "link"))

            if rel == "canonical":
                self.canonical = href


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SiteValidationError(f"{path.relative_to(REPO_ROOT)} is invalid JSON: {exc}") from exc


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SiteValidationError(message)


def require_keys(mapping: object, keys: list[str], label: str) -> dict[str, object]:
    require(isinstance(mapping, dict), f"{label} must be an object")
    typed = mapping

    for key in keys:
        require(key in typed, f"{label} missing key: {key}")

    return typed


def require_list(value: object, label: str) -> list[object]:
    require(isinstance(value, list), f"{label} must be a list")
    return value


def require_same_length(labels: object, series: dict[str, object], label: str) -> None:
    labels_list = require_list(labels, f"{label}.labels")

    for key, values in series.items():
        value_list = require_list(values, f"{label}.{key}")
        require(
            len(value_list) == len(labels_list),
            f"{label}.{key} length {len(value_list)} does not match labels length {len(labels_list)}",
        )


def validate_chart_json() -> None:
    for filename in ("carbon-chart-data.json", "power-price-chart-data.json"):
        payload = require_keys(
            load_json(DATA_DIR / filename),
            ["last_updated", "labels", "actual_values", "forecast_values"],
            filename,
        )
        series = {
            "actual_values": payload["actual_values"],
            "forecast_values": payload["forecast_values"],
        }

        if "values" in payload:
            series["values"] = payload["values"]

        require_same_length(payload["labels"], series, filename)

    generation = require_keys(
        load_json(DATA_DIR / "generation-mix-chart-data.json"),
        ["last_updated", "labels", "datasets"],
        "generation-mix-chart-data.json",
    )
    labels = require_list(generation["labels"], "generation-mix-chart-data.json.labels")
    datasets = require_list(generation["datasets"], "generation-mix-chart-data.json.datasets")
    require(len(datasets) > 0, "generation-mix-chart-data.json.datasets must not be empty")

    for index, dataset in enumerate(datasets):
        dataset_mapping = require_keys(dataset, ["key", "label", "values"], f"generation mix dataset {index}")
        values = require_list(dataset_mapping["values"], f"generation mix dataset {index}.values")
        require(len(values) == len(labels), f"generation mix dataset {index} length does not match labels")

    accounting = require_keys(
        load_json(DATA_DIR / "uk-carbon-accounting-chart-data.json"),
        [
            "last_updated",
            "labels",
            "territorial_emissions_mtco2e",
            "consumption_emissions_mtco2e",
            "consumption_per_person_tco2e",
        ],
        "uk-carbon-accounting-chart-data.json",
    )
    require_same_length(
        accounting["labels"],
        {
            "territorial_emissions_mtco2e": accounting["territorial_emissions_mtco2e"],
            "consumption_emissions_mtco2e": accounting["consumption_emissions_mtco2e"],
            "consumption_per_person_tco2e": accounting["consumption_per_person_tco2e"],
        },
        "uk-carbon-accounting-chart-data.json",
    )

    green_bills = require_keys(
        load_json(DATA_DIR / "green-generation-bills-chart-data.json"),
        ["last_updated", "labels", "generation_mix", "domestic_electricity_bill"],
        "green-generation-bills-chart-data.json",
    )
    generation_mix = require_keys(
        green_bills["generation_mix"],
        ["renewable_percentage", "low_carbon_percentage", "zero_carbon_percentage", "fossil_percentage"],
        "green-generation-bills-chart-data.json.generation_mix",
    )
    bill = require_keys(
        green_bills["domestic_electricity_bill"],
        ["bill_gbp_nominal"],
        "green-generation-bills-chart-data.json.domestic_electricity_bill",
    )
    require_same_length(
        green_bills["labels"],
        {
            **generation_mix,
            "bill_gbp_nominal": bill["bill_gbp_nominal"],
        },
        "green-generation-bills-chart-data.json",
    )

    snapshot = require_keys(
        load_json(DATA_DIR / "live-grid-snapshot.json"),
        ["last_updated", "power_price", "carbon_intensity", "demand", "generation", "generation_mix"],
        "live-grid-snapshot.json",
    )

    for metric_name in ("power_price", "carbon_intensity", "demand", "generation"):
        require_keys(snapshot[metric_name], ["value", "unit", "display"], f"live-grid-snapshot.json.{metric_name}")

    mix = require_keys(snapshot["generation_mix"], ["low_carbon_percentage", "segments"], "live-grid-snapshot.json.generation_mix")
    segments = require_list(mix["segments"], "live-grid-snapshot.json.generation_mix.segments")

    for index, segment in enumerate(segments):
        require_keys(segment, ["key", "label", "percentage", "is_low_carbon"], f"live-grid-snapshot segment {index}")


def validate_content_json() -> None:
    thought_pieces = require_keys(load_json(DATA_DIR / "thought-pieces.json"), ["articles"], "thought-pieces.json")
    articles = require_list(thought_pieces["articles"], "thought-pieces.json.articles")
    seen_links: set[str] = set()

    for index, article in enumerate(articles):
        mapping = require_keys(
            article,
            ["title", "author", "date", "topic", "summary", "link", "image", "section", "featured"],
            f"thought-pieces article {index}",
        )
        date.fromisoformat(str(mapping["date"]))
        link = str(mapping["link"])
        require(link not in seen_links, f"Duplicate thought piece link: {link}")
        seen_links.add(link)
        require((REPO_ROOT / link).is_file(), f"Thought piece link does not exist: {link}")

        image = mapping.get("image")
        if image:
            require((REPO_ROOT / str(image)).is_file(), f"Thought piece image does not exist: {image}")

    brain_dumps = require_keys(load_json(DATA_DIR / "brain-dumps.json"), ["notes"], "brain-dumps.json")
    notes = require_list(brain_dumps["notes"], "brain-dumps.json.notes")

    for index, note in enumerate(notes):
        mapping = require_keys(note, ["title", "date", "tag", "content"], f"brain dump note {index}")
        date.fromisoformat(str(mapping["date"]))
        content = mapping["content"]
        require(isinstance(content, str) or isinstance(content, list), f"brain dump note {index}.content must be text or list")

    recommendations = require_keys(
        load_json(DATA_DIR / "recommendations.json"),
        ["recommended_read", "recommended_listen"],
        "recommendations.json",
    )

    for key in ("recommended_read", "recommended_listen"):
        require_keys(recommendations[key], ["title", "source", "link", "description"], f"recommendations.json.{key}")

    radar = require_keys(load_json(DATA_DIR / "news-radar.json"), ["last_updated", "r_and_d", "policy"], "news-radar.json")

    for group_name in ("r_and_d", "policy"):
        group = require_list(radar[group_name], f"news-radar.json.{group_name}")

        for index, item in enumerate(group):
            require_keys(item, ["headline", "source", "link", "published_at", "display_date"], f"news radar {group_name} item {index}")


def is_external_or_special(url: str) -> bool:
    return (
        not url
        or url.startswith("#")
        or url.startswith("mailto:")
        or url.startswith("tel:")
        or url.startswith("http://")
        or url.startswith("https://")
        or url.startswith("data:")
    )


def resolve_internal_url(page: Path, url: str) -> Path:
    url_without_fragment = url.split("#", 1)[0]
    parsed = urlparse(url_without_fragment)
    path = parsed.path
    return (page.parent / path).resolve()


def validate_internal_links_and_assets() -> dict[Path, str]:
    canonicals: dict[Path, str] = {}

    for page in sorted(REPO_ROOT.glob("*.html")) + sorted((REPO_ROOT / "articles").glob("*.html")):
        parser = LinkParser()
        parser.feed(page.read_text(encoding="utf-8"))

        if parser.canonical:
            canonicals[page] = parser.canonical

        for attribute, url, tag in parser.links:
            if is_external_or_special(url):
                continue

            target = resolve_internal_url(page, url)
            require(
                target.is_file(),
                f"{page.relative_to(REPO_ROOT)} has missing {attribute} target: {url}",
            )

            if tag == "img":
                require(target.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"}, f"Image target has unexpected suffix: {url}")

    return canonicals


def sitemap_loc_for_page(page: Path) -> str:
    relative = page.relative_to(REPO_ROOT).as_posix()

    if relative == "index.html":
        return BASE_URL

    return f"{BASE_URL}{relative}"


def validate_sitemap_and_canonicals(canonicals: dict[Path, str]) -> None:
    sitemap_path = REPO_ROOT / "sitemap.xml"
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    tree = ET.parse(sitemap_path)
    locations = {
        element.text
        for element in tree.findall(".//sm:loc", namespace)
        if element.text
    }

    pages = sorted(REPO_ROOT.glob("*.html")) + sorted((REPO_ROOT / "articles").glob("*.html"))
    expected_locations = {sitemap_loc_for_page(page) for page in pages}

    require(locations == expected_locations, "sitemap.xml locations do not match discovered HTML pages")

    for page in pages:
        expected = sitemap_loc_for_page(page)
        canonical = canonicals.get(page)
        require(canonical == expected, f"{page.relative_to(REPO_ROOT)} canonical mismatch: expected {expected}, found {canonical}")


def validate_layout_markers() -> None:
    articles = require_list(require_keys(load_json(DATA_DIR / "thought-pieces.json"), ["articles"], "thought-pieces.json")["articles"], "thought-pieces.json.articles")
    listed_article_paths = {
        REPO_ROOT / str(article["link"])
        for article in articles
        if isinstance(article, dict) and str(article.get("link", "")).startswith("articles/")
    }

    for page in sorted(REPO_ROOT.glob("*.html")) + sorted((REPO_ROOT / "articles").glob("*.html")):
        text = page.read_text(encoding="utf-8")
        require("<!-- site-header:start -->" in text, f"{page.relative_to(REPO_ROOT)} missing generated header marker")
        require("<!-- site-footer:start -->" in text, f"{page.relative_to(REPO_ROOT)} missing generated footer marker")

        if page in listed_article_paths:
            require("<!-- article-navigation:start -->" in text, f"{page.relative_to(REPO_ROOT)} missing generated article navigation")


def validate() -> None:
    validate_chart_json()
    validate_content_json()
    canonicals = validate_internal_links_and_assets()
    validate_sitemap_and_canonicals(canonicals)
    validate_layout_markers()


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate static site data, links, sitemap, and generated layout markers.")
    parser.parse_args()

    try:
        validate()
    except SiteValidationError as exc:
        print(f"Site validation failed: {exc}", file=sys.stderr)
        return 1

    print("Site validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
