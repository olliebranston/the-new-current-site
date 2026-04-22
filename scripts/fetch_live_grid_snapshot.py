import json
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import quote
from urllib.request import urlopen


CARBON_INTENSITY_URL = "https://api.carbonintensity.org.uk/intensity"
GENERATION_MIX_URL = "https://api.carbonintensity.org.uk/generation"

# NESO open data resources used for the snapshot.
NESO_SQL_API = "https://api.neso.energy/api/3/action/datastore_search_sql?sql="
NESO_GENERATION_RESOURCE_ID = "f93d1835-75bc-43e5-84ad-12472b180a98"
NESO_DEMAND_RESOURCE_ID = "177f6fa4-ae49-4182-81ea-0c6b35f26ca6"

LOW_CARBON_FUELS = {"wind", "solar", "hydro", "nuclear", "biomass"}
SEGMENT_COLOURS = {
    "wind": "#2457ff",
    "solar": "#f5b700",
    "hydro": "#0ea5e9",
    "nuclear": "#16a34a",
    "biomass": "#8b5cf6",
    "gas": "#f97316",
    "coal": "#475569",
    "imports": "#ec4899",
    "other": "#94a3b8",
    "storage": "#14b8a6",
}

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = REPO_ROOT / "data" / "live-grid-snapshot.json"


def fetch_json(url):
    with urlopen(url) as response:
        return json.load(response)


def fetch_neso_latest_record(resource_id, order_by_fields):
    sql = f'SELECT * FROM "{resource_id}" ORDER BY {order_by_fields} LIMIT 1'
    url = NESO_SQL_API + quote(sql, safe="")
    payload = fetch_json(url)
    records = payload["result"]["records"]
    return records[0] if records else None


def fetch_carbon_intensity():
    payload = fetch_json(CARBON_INTENSITY_URL)
    row = payload["data"][0]
    intensity = row["intensity"]
    value = intensity.get("actual")

    # Keep the snapshot honest: if the API has no actual value yet, leave it blank.
    if value is None:
        return {"value": None, "unit": "gCO2/kWh", "display": "Awaiting actual"}

    return {
        "value": value,
        "unit": "gCO2/kWh",
        "display": f"{round(value)} gCO2/kWh",
    }


def fetch_generation_mix():
    carbon_mix_payload = fetch_json(GENERATION_MIX_URL)
    mix_row = carbon_mix_payload["data"][0]
    mix_items = mix_row.get("generationmix", [])

    segments = []
    low_carbon_total = 0

    for item in mix_items:
        fuel = item.get("fuel", "").lower()
        percentage = float(item.get("perc", 0))

        if percentage <= 0:
            continue

        if fuel in LOW_CARBON_FUELS:
            low_carbon_total += percentage

        segments.append(
            {
                "key": fuel,
                "label": fuel.replace("_", " ").title(),
                "percentage": round(percentage, 1),
                "color": SEGMENT_COLOURS.get(fuel, "#94a3b8"),
                "is_low_carbon": fuel in LOW_CARBON_FUELS,
            }
        )

    return {
        "low_carbon_percentage": round(low_carbon_total),
        "segments": segments,
    }


def fetch_generation_total():
    record = fetch_neso_latest_record(
        NESO_GENERATION_RESOURCE_ID,
        '"DATETIME" DESC'
    )

    if not record:
        return {"value": None, "unit": "MW", "display": "Unavailable"}

    value = record.get("GENERATION")
    if value is None:
        return {"value": None, "unit": "MW", "display": "Unavailable"}

    return {
        "value": round(float(value)),
        "unit": "MW",
        "display": f"{round(float(value)):,} MW",
    }


def fetch_demand():
    record = fetch_neso_latest_record(
        NESO_DEMAND_RESOURCE_ID,
        '"SETTLEMENT_DATE" DESC, "SETTLEMENT_PERIOD" DESC'
    )

    if not record:
        return {"value": None, "unit": "MW", "display": "Unavailable"}

    value = record.get("ND")
    if value is None:
        return {"value": None, "unit": "MW", "display": "Unavailable"}

    return {
        "value": round(float(value)),
        "unit": "MW",
        "display": f"{round(float(value)):,} MW",
    }


def build_snapshot():
    # Power price is left as a clear placeholder for Phase 1 until a stable
    # public source is chosen and added to the pipeline.
    snapshot = {
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "power_price": {
            "value": None,
            "unit": "GBP/MWh",
            "display": "Coming soon",
        },
        "carbon_intensity": fetch_carbon_intensity(),
        "demand": fetch_demand(),
        "generation": fetch_generation_total(),
        "generation_mix": fetch_generation_mix(),
    }

    return snapshot


def main():
    snapshot = build_snapshot()

    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(snapshot, file, indent=2)

    print(f"Saved {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
