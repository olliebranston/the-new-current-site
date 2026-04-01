import json
import re
import urllib3
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import requests
from bs4 import BeautifulSoup

# ----------------
# SOURCE URLS
# ----------------

# R&D
EU_RI_RESEARCH_RSS_URL = "https://research-and-innovation.ec.europa.eu/node/2/rss_en"
DOE_H2_RSS_URL = "https://www.energy.gov/rss/eere-fuelcells/904691"
HYDROGEN_PROGRAM_NEWS_URL = "https://www.energy.gov/eere/fuelcells/listings/hydrogen-and-fuel-cell-news"
JRC_SES_NEWS_URL = "https://ses.jrc.ec.europa.eu/news-events"
CORDIS_ENERGY_URL = "https://cordis.europa.eu/domain-of-application/energy"

# Policy
DG_ENERGY_RSS_URL = "https://energy.ec.europa.eu/node/2/rss_en"
DESNZ_NEWS_URL = "https://www.gov.uk/government/organisations/department-for-energy-security-and-net-zero"
OFGEM_RSS_URL = "https://www.ofgem.gov.uk/rss.xml"
ACER_NEWS_URL = "https://acer.europa.eu/news-and-events/news"
NESO_NEWS_URL = "https://www.neso.energy/news-and-events"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; TheNewCurrentBot/1.0)"
}

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ----------------
# HTTP HELPERS
# ----------------

def get_response(url, timeout=30):
    """
    First try normal SSL verification.
    If that fails, retry with verify=False so local certificate issues
    do not automatically eliminate otherwise-usable public sources.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout, verify=True)
        response.raise_for_status()
        return response
    except requests.exceptions.SSLError:
        response = requests.get(url, headers=HEADERS, timeout=timeout, verify=False)
        response.raise_for_status()
        return response


def fetch_page(url):
    response = get_response(url)
    return BeautifulSoup(response.text, "html.parser")


def fetch_text(url):
    response = get_response(url)
    return response.text


# ----------------
# TEXT / DATE HELPERS
# ----------------

def clean_text(text):
    return re.sub(r"\s+", " ", text or "").strip()


def parse_iso_date(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def extract_date_from_string(text):
    if not text:
        return None

    patterns = [
        r"(\d{4}-\d{2}-\d{2})",
        r"(\d{4}/\d{2}/\d{2})",
        r"(\d{1,2}\s+[A-Z][a-z]+\s+\d{4})",
        r"([A-Z][a-z]+\s+\d{1,2},\s+\d{4})",
        r"(\d{1,2}\.[0-9]{1,2}\.[0-9]{4})",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if not match:
            continue

        raw = match.group(1)

        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d %B %Y", "%B %d, %Y", "%d.%m.%Y"):
            try:
                parsed = datetime.strptime(raw, fmt)
                return parsed.replace(tzinfo=timezone.utc)
            except ValueError:
                continue

    return None


# ----------------
# ITEM HELPERS
# ----------------

def build_item(headline, source, link, published_date=None):
    headline = clean_text(headline)
    link = clean_text(link)

    if not headline or not link:
        return None

    published_at = None
    display_date = None

    if published_date:
        published_date = published_date.astimezone(timezone.utc)
        published_at = published_date.isoformat().replace("+00:00", "Z")
        display_date = published_date.strftime("%d %B %Y")

    return {
        "headline": headline,
        "source": source,
        "link": link,
        "published_at": published_at,
        "display_date": display_date,
    }


def deduplicate_items(items):
    deduplicated = []
    seen_links = set()

    for item in items:
        if not item:
            continue

        link = item.get("link")
        if not link or link in seen_links:
            continue

        seen_links.add(link)
        deduplicated.append(item)

    return deduplicated


def sort_items_by_date(items):
    return sorted(
        items,
        key=lambda item: parse_iso_date(item.get("published_at")) or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )


def combine_sort_deduplicate_limit(*source_lists, limit=5, per_source_limit=2):
    combined = []

    for source_list in source_lists:
        combined.extend(source_list)

    deduplicated = deduplicate_items(combined)
    sorted_items = sort_items_by_date(deduplicated)

    selected_items = []
    source_counts = {}

    for item in sorted_items:
        source = item.get("source", "Unknown")
        current_count = source_counts.get(source, 0)

        if current_count >= per_source_limit:
            continue

        selected_items.append(item)
        source_counts[source] = current_count + 1

        if len(selected_items) >= limit:
            break

    return selected_items


def safe_fetch(fetch_function, label):
    try:
        items = fetch_function()
        print(f"{label}: fetched {len(items)} items")
        return items
    except Exception as error:
        print(f"{label}: failed with error: {error}")
        return []


# ----------------
# RSS FETCHER
# ----------------

def fetch_rss_items(feed_url, source_name, keywords=None):
    rss_text = fetch_text(feed_url)
    root = ET.fromstring(rss_text)

    items = []

    for item in root.findall(".//item"):
        title = clean_text(item.findtext("title", default=""))
        link = clean_text(item.findtext("link", default=""))
        pub_date_raw = clean_text(item.findtext("pubDate", default=""))
        description = clean_text(item.findtext("description", default=""))

        if not title or not link:
            continue

        combined_text = f"{title} {description}".lower()

        if keywords and not any(keyword in combined_text for keyword in keywords):
            continue

        published_date = None

        if pub_date_raw:
            try:
                published_date = parsedate_to_datetime(pub_date_raw)
                if published_date.tzinfo is None:
                    published_date = published_date.replace(tzinfo=timezone.utc)
                else:
                    published_date = published_date.astimezone(timezone.utc)
            except Exception:
                published_date = None

        if not published_date:
            published_date = extract_date_from_string(link)

        built = build_item(
            headline=title,
            source=source_name,
            link=link,
            published_date=published_date,
        )

        if built:
            items.append(built)

    return items


# ----------------
# PAGE FETCHERS
# ----------------

def fetch_article_list_with_dates(url, source_name, keywords=None, link_prefix=None):
    soup = fetch_page(url)
    items = []
    seen_links = set()

    candidate_blocks = soup.find_all(["article", "li", "div"])

    for block in candidate_blocks:
        block_text = clean_text(block.get_text(" ", strip=True))
        if len(block_text) < 20:
            continue

        links = block.find_all("a", href=True)
        if not links:
            continue

        date = extract_date_from_string(block_text)

        for link in links:
            href = clean_text(link.get("href", ""))
            headline = clean_text(link.get_text(" ", strip=True))

            if not href or not headline or len(headline) < 8:
                continue

            full_link = href if href.startswith("http") else f"{link_prefix or url.rstrip('/')}{href}"

            if full_link in seen_links:
                continue

            combined_text = headline.lower()
            if keywords and not any(keyword in combined_text for keyword in keywords):
                continue

            seen_links.add(full_link)

            published_date = date or extract_date_from_string(full_link)

            built = build_item(
                headline=headline,
                source=source_name,
                link=full_link,
                published_date=published_date,
            )

            if built:
                items.append(built)

    return deduplicate_items(items)


# ----------------
# R&D SOURCES
# ----------------

def fetch_eu_research_r_and_d_rss():
    keywords = [
        "energy", "battery", "hydrogen", "grid", "renewable", "clean energy",
        "solar", "wind", "innovation", "research", "technology", "technologies",
        "fusion", "storage", "decarbonisation", "decarbonization"
    ]
    return fetch_rss_items(EU_RI_RESEARCH_RSS_URL, "EU Research & Innovation", keywords)


def fetch_doe_hydrogen_r_and_d_rss():
    keywords = [
        "hydrogen", "fuel cell", "electrolyser", "electrolyzer", "clean hydrogen",
        "storage", "innovation", "research", "technology", "technologies"
    ]
    return fetch_rss_items(DOE_H2_RSS_URL, "DOE Hydrogen & Fuel Cells", keywords)


def fetch_hydrogen_program_news_page():
    keywords = [
        "hydrogen", "fuel cell", "electrolyser", "electrolyzer",
        "storage", "technology", "research", "innovation"
    ]
    return fetch_article_list_with_dates(
        HYDROGEN_PROGRAM_NEWS_URL,
        "Hydrogen Program",
        keywords=keywords,
        link_prefix="https://www.energy.gov"
    )


def fetch_jrc_ses_news_page():
    keywords = [
        "energy", "renewable", "grid", "appliance", "solar", "wind",
        "storage", "hydrogen", "innovation", "research", "technology"
    ]
    return fetch_article_list_with_dates(
        JRC_SES_NEWS_URL,
        "JRC SES",
        keywords=keywords,
        link_prefix="https://ses.jrc.ec.europa.eu"
    )


def fetch_cordis_energy_page():
    keywords = [
        "energy", "renewable", "solar", "wind", "battery", "storage",
        "hydrogen", "innovation", "research", "technology"
    ]
    return fetch_article_list_with_dates(
        CORDIS_ENERGY_URL,
        "CORDIS Energy",
        keywords=keywords,
        link_prefix="https://cordis.europa.eu"
    )


# ----------------
# POLICY SOURCES
# ----------------

def fetch_dg_energy_policy_rss():
    keywords = [
        "energy", "security", "electricity", "gas", "renewable", "renewables",
        "hydrogen", "nuclear", "grid", "infrastructure", "oil", "efficiency",
        "market", "supply"
    ]
    return fetch_rss_items(DG_ENERGY_RSS_URL, "DG Energy", keywords)


def fetch_desnz_policy():
    soup = fetch_page(DESNZ_NEWS_URL)
    items = []
    seen_links = set()

    keywords = [
        "energy", "net zero", "electricity", "wind", "solar", "grid",
        "clean power", "nuclear", "hydrogen", "offshore", "emissions",
        "bill", "storage", "network", "market"
    ]

    for link in soup.find_all("a", href=True):
        href = clean_text(link.get("href", ""))
        headline = clean_text(link.get_text(" ", strip=True))

        if not headline or not href.startswith("/government/news/"):
            continue

        full_link = f"https://www.gov.uk{href}"

        if full_link in seen_links:
            continue

        if not any(keyword in headline.lower() for keyword in keywords):
            continue

        seen_links.add(full_link)
        published_date = extract_date_from_string(full_link)

        built = build_item(
            headline=headline,
            source="DESNZ",
            link=full_link,
            published_date=published_date,
        )

        if built:
            items.append(built)

    return items


def fetch_ofgem_policy_rss():
    keywords = [
        "energy", "electricity", "gas", "grid", "network", "supplier",
        "price cap", "flexibility", "consumer", "market", "offshore"
    ]
    return fetch_rss_items(OFGEM_RSS_URL, "Ofgem", keywords)


def fetch_acer_policy_page():
    keywords = [
        "electricity", "gas", "energy market", "flexibility", "hydrogen",
        "capacity", "market integration", "network code", "remit", "energy"
    ]
    return fetch_article_list_with_dates(
        ACER_NEWS_URL,
        "ACER",
        keywords=keywords,
        link_prefix="https://acer.europa.eu"
    )


def fetch_neso_policy_page():
    keywords = [
        "grid", "connections", "system", "electricity", "network",
        "clean power", "energy", "flexibility", "markets", "transmission"
    ]
    return fetch_article_list_with_dates(
        NESO_NEWS_URL,
        "NESO",
        keywords=keywords,
        link_prefix="https://www.neso.energy"
    )


# ----------------
# RUN PIPELINE
# ----------------

r_and_d_items = combine_sort_deduplicate_limit(
    safe_fetch(fetch_eu_research_r_and_d_rss, "EU Research & Innovation R&D RSS"),
    safe_fetch(fetch_doe_hydrogen_r_and_d_rss, "DOE Hydrogen & Fuel Cells R&D RSS"),
    safe_fetch(fetch_hydrogen_program_news_page, "Hydrogen Program R&D page"),
    safe_fetch(fetch_jrc_ses_news_page, "JRC SES R&D page"),
    safe_fetch(fetch_cordis_energy_page, "CORDIS Energy R&D page"),
    limit=5,
    per_source_limit=2,
)

policy_items = combine_sort_deduplicate_limit(
    safe_fetch(fetch_dg_energy_policy_rss, "DG Energy Policy RSS"),
    safe_fetch(fetch_desnz_policy, "DESNZ Policy"),
    safe_fetch(fetch_ofgem_policy_rss, "Ofgem Policy RSS"),
    safe_fetch(fetch_acer_policy_page, "ACER Policy page"),
    safe_fetch(fetch_neso_policy_page, "NESO Policy page"),
    limit=5,
    per_source_limit=2,
)

news_radar = {
    "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    "r_and_d": r_and_d_items,
    "policy": policy_items,
}

with open("data/news-radar.json", "w", encoding="utf-8") as file:
    json.dump(news_radar, file, indent=2)

print("Saved automated news-radar.json successfully.")
print(f"R&D items: {len(news_radar['r_and_d'])}")
print(f"Policy items: {len(news_radar['policy'])}")