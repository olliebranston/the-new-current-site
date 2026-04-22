import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
from urllib.parse import quote, urlencode
from urllib.request import urlopen


CARBON_INTENSITY_URL = "https://api.carbonintensity.org.uk/intensity"
GENERATION_MIX_URL = "https://api.carbonintensity.org.uk/generation"
ELEXON_API_BASE = "https://data.elexon.co.uk/bmrs/api/v1"
ELEXON_MARKET_PRICE_URL = f"{ELEXON_API_BASE}/balancing/pricing/market-index"
ELEXON_DEMAND_URL = f"{ELEXON_API_BASE}/demand/actual/total"
ELEXON_MARKET_INDEX_PROVIDER = "APXMIDP"

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


def extract_rows(payload):
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]

    if isinstance(payload, dict):
        data = payload.get("data")
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]

        records = payload.get("records")
        if isinstance(records, list):
            return [item for item in records if isinstance(item, dict)]

        if isinstance(data, dict):
            nested_rows = extract_rows(data)
            if nested_rows:
                return nested_rows

    return []


def build_elexon_range_params():
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=2)

    return urlencode(
        {
            "from": start.strftime("%Y-%m-%dT%H:%MZ"),
            "to": now.strftime("%Y-%m-%dT%H:%MZ"),
            "format": "json",
        }
    )


def latest_settlement_first(row):
    settlement_date = str(
        row.get("settlementDate")
        or row.get("settlement_date")
        or row.get("date")
        or ""
    )
    settlement_period = int(
        row.get("settlementPeriod")
        or row.get("settlement_period")
        or row.get("settlementPeriodNumber")
        or 0
    )
    publish_time = str(
        row.get("publishTime")
        or row.get("publishDatetime")
        or row.get("publishDateTime")
        or row.get("startTime")
        or row.get("start_time")
        or ""
    )

    return (settlement_date, settlement_period, publish_time)


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


def fetch_power_price():
    try:
        # This endpoint appears to behave like a time-series query, so request
        # a recent range for one provider and then inspect the returned rows.
        market_price_params = {
            "from": (datetime.now(timezone.utc) - timedelta(days=2)).strftime("%Y-%m-%dT%H:%MZ"),
            "to": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
            "marketIndexDataProvider": ELEXON_MARKET_INDEX_PROVIDER,
            "format": "json",
        }
        url = f"{ELEXON_MARKET_PRICE_URL}?{urlencode(market_price_params)}"
        payload = fetch_json(url)
        rows = extract_rows(payload)
    except Exception as error:
        print(f"Power price fetch failed: {error}")
        return {"value": None, "unit": "GBP/MWh", "display": "Price unavailable"}

    top_level_keys = list(payload.keys()) if isinstance(payload, dict) else []
    print(f"Power price response keys: {top_level_keys}")
    print(f"Power price rows found: {len(rows)}")

    if rows:
        print(f"Power price first row keys: {list(rows[0].keys())}")

    # Use the most recent market price row with a usable marketIndexPrice value.
    for row in sorted(rows, key=latest_settlement_first, reverse=True):
        raw_value = row.get("marketIndexPrice")

        if raw_value in (None, ""):
            continue

        try:
            numeric_value = float(raw_value)
        except (TypeError, ValueError):
            continue

        rounded_value = round(numeric_value)

        return {
            "value": numeric_value,
            "unit": "GBP/MWh",
            "display": f"{rounded_value} GBP/MWh",
        }

    print(
        "Power price unavailable: no usable marketIndexPrice found "
        f"for provider {ELEXON_MARKET_INDEX_PROVIDER} in the requested time range"
    )
    return {"value": None, "unit": "GBP/MWh", "display": "Price unavailable"}


def fetch_demand():
    try:
        url = f"{ELEXON_DEMAND_URL}?{build_elexon_range_params()}"
        payload = fetch_json(url)
        rows = extract_rows(payload)
    except Exception:
        return {"value": None, "unit": "MW", "display": "Demand unavailable"}

    # Read the documented actual total load rows and take the latest usable
    # quantity value, rather than guessing between several field names.
    for row in sorted(rows, key=latest_settlement_first, reverse=True):
        raw_value = row.get("quantity")

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
        "power_price": fetch_power_price(),
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
