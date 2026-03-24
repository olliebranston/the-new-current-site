import json
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

DG_ENERGY_NEWS_URL = "https://energy.ec.europa.eu/news_en"
DESNZ_NEWS_URL = "https://www.gov.uk/government/organisations/department-for-energy-security-and-net-zero"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; TheNewCurrentBot/1.0)"
}


def fetch_dg_energy_policy():
    response = requests.get(DG_ENERGY_NEWS_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    items = []
    seen_links = set()

    for link in soup.find_all("a", href=True):
        href = link["href"]
        text = " ".join(link.stripped_strings).strip()

        if not text:
            continue

        if "/news/" not in href:
            continue

        if href.startswith("http"):
            full_link = href
        else:
            full_link = f"https://energy.ec.europa.eu{href}"

        if full_link in seen_links:
            continue

        seen_links.add(full_link)

        items.append(
            {
                "headline": text,
                "source": "DG Energy",
                "link": full_link,
                "summary": "Recent European Commission energy-policy item."
            }
        )

        if len(items) >= 4:
            break

    return items


def fetch_desnz_policy():
    response = requests.get(DESNZ_NEWS_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    items = []
    seen_links = set()

    keywords = [
        "energy",
        "net zero",
        "electricity",
        "wind",
        "solar",
        "grid",
        "clean power",
        "nuclear",
        "hydrogen",
        "offshore",
        "emissions",
    ]

    for link in soup.find_all("a", href=True):
        href = link["href"]
        text = " ".join(link.stripped_strings).strip()

        if not text:
            continue

        if not href.startswith("/government/news/"):
            continue

        full_link = f"https://www.gov.uk{href}"

        if full_link in seen_links:
            continue

        text_lower = text.lower()

        if not any(keyword in text_lower for keyword in keywords):
            continue

        seen_links.add(full_link)

        items.append(
            {
                "headline": text,
                "source": "DESNZ",
                "link": full_link,
                "summary": "Recent UK government energy-policy item."
            }
        )

        if len(items) >= 4:
            break

    return items


def safe_fetch(fetch_function, label):
    try:
        items = fetch_function()
        print(f"{label}: fetched {len(items)} items")
        return items
    except Exception as error:
        print(f"{label}: failed with error: {error}")
        return []


news_radar = {
    "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    "r_and_d": [],
    "policy": (
        safe_fetch(fetch_dg_energy_policy, "DG Energy Policy")
        + safe_fetch(fetch_desnz_policy, "DESNZ Policy")
    )
}

with open("data/news-radar.json", "w", encoding="utf-8") as file:
    json.dump(news_radar, file, indent=2)

print("Saved automated news-radar.json successfully.")
print(f"R&D items: {len(news_radar['r_and_d'])}")
print(f"Policy items: {len(news_radar['policy'])}")