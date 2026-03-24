import json
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

ARPA_E_URL = "https://arpa-e.energy.gov/news-and-events/news-and-insights"
EU_RI_NEWS_URL = "https://research-and-innovation.ec.europa.eu/news_en"
EIC_URL = "https://www.ukeic.com/"

DG_ENERGY_NEWS_URL = "https://energy.ec.europa.eu/news_en"
DESNZ_NEWS_URL = "https://www.gov.uk/government/organisations/department-for-energy-security-and-net-zero"
EC_ENERGY_URL = "https://energy.ec.europa.eu/index_en"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; TheNewCurrentBot/1.0)"
}


def fetch_arpa_e_r_and_d():
    response = requests.get(ARPA_E_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    items = []
    seen_links = set()

    keywords = [
        "technology",
        "technologies",
        "innovation",
        "innovators",
        "battery",
        "storage",
        "hydrogen",
        "grid",
        "carbon",
        "clean energy",
        "solar",
        "wind",
        "nuclear",
        "research",
        "funding",
    ]

    for link in soup.find_all("a", href=True):
        href = link["href"]
        text = " ".join(link.stripped_strings).strip()

        if not text:
            continue

        if "/news-and-events/news-and-insights/" not in href:
            continue

        if href.startswith("http"):
            full_link = href
        else:
            full_link = f"https://arpa-e.energy.gov{href}"

        if full_link in seen_links:
            continue

        text_lower = text.lower()

        if not any(keyword in text_lower for keyword in keywords):
            continue

        seen_links.add(full_link)

        items.append(
            {
                "headline": text,
                "source": "ARPA-E",
                "link": full_link,
                "summary": "Recent ARPA-E item selected for energy innovation relevance."
            }
        )

        if len(items) >= 4:
            break

    return items


def fetch_eu_research_r_and_d():
    response = requests.get(EU_RI_NEWS_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    items = []
    seen_links = set()

    keywords = [
        "energy",
        "battery",
        "hydrogen",
        "grid",
        "renewable",
        "clean energy",
        "solar",
        "wind",
        "innovation",
        "research",
        "technology",
        "technologies",
    ]

    for link in soup.find_all("a", href=True):
        href = link["href"]
        text = " ".join(link.stripped_strings).strip()

        if not text:
            continue

        if "/news/" not in href and "/all-research-and-innovation-news/" not in href:
            continue

        if href.startswith("http"):
            full_link = href
        else:
            full_link = f"https://research-and-innovation.ec.europa.eu{href}"

        if full_link in seen_links:
            continue

        text_lower = text.lower()

        if not any(keyword in text_lower for keyword in keywords):
            continue

        seen_links.add(full_link)

        items.append(
            {
                "headline": text,
                "source": "EU Research & Innovation",
                "link": full_link,
                "summary": "Recent EU research and innovation item selected for energy relevance."
            }
        )

        if len(items) >= 4:
            break

    return items


def fetch_eic_r_and_d():
    response = requests.get(EIC_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    items = []
    seen_links = set()

    keywords = [
        "innovation",
        "innovator",
        "battery",
        "hydrogen",
        "grid",
        "storage",
        "electricity",
        "network",
        "solar",
        "wind",
        "net zero",
        "technology",
    ]

    for link in soup.find_all("a", href=True):
        href = link["href"]
        text = " ".join(link.stripped_strings).strip()

        if not text:
            continue

        if href.startswith("http"):
            full_link = href
        else:
            full_link = f"https://www.ukeic.com{href}"

        if full_link in seen_links:
            continue

        text_lower = text.lower()

        if not any(keyword in text_lower for keyword in keywords):
            continue

        seen_links.add(full_link)

        items.append(
            {
                "headline": text,
                "source": "Energy Innovation Centre",
                "link": full_link,
                "summary": "Recent innovation-related item from the Energy Innovation Centre."
            }
        )

        if len(items) >= 4:
            break

    return items


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


def fetch_ec_energy_policy():
    response = requests.get(EC_ENERGY_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    items = []
    seen_links = set()

    keywords = [
        "energy",
        "electricity",
        "renewables",
        "grid",
        "infrastructure",
        "bills",
        "policy",
        "guidance",
        "commission",
    ]

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

        text_lower = text.lower()

        if not any(keyword in text_lower for keyword in keywords):
            continue

        seen_links.add(full_link)

        items.append(
            {
                "headline": text,
                "source": "European Commission Energy",
                "link": full_link,
                "summary": "Recent European Commission energy-policy item."
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
    "r_and_d": (
        safe_fetch(fetch_arpa_e_r_and_d, "ARPA-E R&D")
        + safe_fetch(fetch_eu_research_r_and_d, "EU Research & Innovation R&D")
        + safe_fetch(fetch_eic_r_and_d, "EIC R&D")
    ),
    "policy": (
        safe_fetch(fetch_dg_energy_policy, "DG Energy Policy")
        + safe_fetch(fetch_desnz_policy, "DESNZ Policy")
        + safe_fetch(fetch_ec_energy_policy, "EC Energy Policy")
    )
}

with open("data/news-radar.json", "w", encoding="utf-8") as file:
    json.dump(news_radar, file, indent=2)

print("Saved automated news-radar.json successfully.")
print(f"R&D items: {len(news_radar['r_and_d'])}")
print(f"Policy items: {len(news_radar['policy'])}")