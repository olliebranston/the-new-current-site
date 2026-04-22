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
    actual_value = intensity.get("actual")
    forecast_value = intensity.get("forecast")

    # Prefer the actual reading, but fall back to the forecast if the API
    # has not published an actual value for the current time window yet.
    if actual_value is not None:
        rounded_value = round(actual_value)
        return {
            "value": actual_value,
            "unit": "gCO2/kWh",
            "display": f"{rounded_value} gCO2/kWh (actual)",
        }

    if forecast_value is not None:
        rounded_value = round(forecast_value)
        return {
            "value": forecast_value,
            "unit": "gCO2/kWh",
            "display": f"{rounded_value} gCO2/kWh (forecast)",
        }

    return {"value": None, "unit": "gCO2/kWh", "display": "Carbon intensity unavailable"}


def fetch_generation_mix():
    carbon_mix_payload = fetch_json(GENERATION_MIX_URL)

    # The live API returns "data" as a single object here, not a list.
    # This fallback handling keeps the script from crashing if that shape changes.
    data = carbon_mix_payload.get("data")

    if isinstance(data, list):
        mix_row = data[0] if data else {}
    elif isinstance(data, dict):
        mix_row = data
    else:
        return {
            "low_carbon_percentage": 0,
            "segments": [],
        }

    mix_items = mix_row.get("generationmix", [])

    if not isinstance(mix_items, list):
        return {
            "low_carbon_percentage": 0,
            "segments": [],
        }

    segments = []
    low_carbon_total = 0

    for item in mix_items:
        if not isinstance(item, dict):
            continue

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
        return {"value": None, "unit": "MW", "display": "Demand unavailable"}

    # NESO demand datasets can vary a little in field names, so try a few
    # sensible options and ignore blank or zero-like values that would mislead.
    possible_fields = ["ND", "DEMAND", "demand", "national_demand"]

    for field_name in possible_fields:
        raw_value = record.get(field_name)

        if raw_value in (None, ""):
            continue

        try:
            numeric_value = float(raw_value)
        except (TypeError, ValueError):
            continue

        if numeric_value <= 0:
            continue

        rounded_value = round(numeric_value)

        return {
            "value": rounded_value,
            "unit": "MW",
            "display": f"{rounded_value:,} MW",
        }

    return {"value": None, "unit": "MW", "display": "Demand unavailable"}


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
