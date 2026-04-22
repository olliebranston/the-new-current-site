import csv
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

import pandas as pd


ELEXON_API_BASE = "https://data.elexon.co.uk/bmrs/api/v1"
ELEXON_MARKET_PRICE_URL = f"{ELEXON_API_BASE}/balancing/pricing/market-index"
ELEXON_MARKET_INDEX_PROVIDER = "APXMIDP"

REPO_ROOT = Path(__file__).resolve().parent.parent
LIVE_CSV_PATH = REPO_ROOT / "data" / "live-power-price.csv"
CLEANED_CSV_PATH = REPO_ROOT / "data" / "cleaned-live-power-price.csv"
CHART_JSON_PATH = REPO_ROOT / "data" / "power-price-chart-data.json"


def fetch_json(url):
    with urlopen(url) as response:
        return json.load(response)


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


def build_market_price_url():
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=1)

    query = urlencode(
        {
            "from": start.strftime("%Y-%m-%dT%H:%MZ"),
            "to": now.strftime("%Y-%m-%dT%H:%MZ"),
            "marketIndexDataProvider": ELEXON_MARKET_INDEX_PROVIDER,
            "format": "json",
        }
    )

    return f"{ELEXON_MARKET_PRICE_URL}?{query}"


def main():
    payload = fetch_json(build_market_price_url())
    rows = extract_rows(payload)

    records_by_timestamp = {}

    for row in rows:
        start_time = row.get("startTime")
        price = row.get("price")
        provider = row.get("dataProvider", ELEXON_MARKET_INDEX_PROVIDER)

        if not start_time or price in (None, ""):
            continue

        # The endpoint can still return multiple MID providers, so keep only
        # the one provider we want to chart for a clean single price series.
        if provider != ELEXON_MARKET_INDEX_PROVIDER:
            continue

        try:
            numeric_price = float(price)
        except (TypeError, ValueError):
            continue

        record = {
            "timestamp": start_time,
            "actual_price": numeric_price,
            # Keep the same chart shape as carbon so we can add a real
            # forecast series later without changing the frontend format.
            "forecast_price": None,
            "provider": provider,
            "settlement_date": row.get("settlementDate"),
            "settlement_period": row.get("settlementPeriod"),
            "volume": row.get("volume"),
        }

        # If the API ever returns more than one row for the same timestamp and
        # provider, keep the latest usable version for that half-hour slot.
        existing_record = records_by_timestamp.get(start_time)
        if (
            existing_record is None
            or (record.get("settlement_period") or 0) >= (existing_record.get("settlement_period") or 0)
        ):
            records_by_timestamp[start_time] = record

    records = sorted(records_by_timestamp.values(), key=lambda item: item["timestamp"])

    with open(LIVE_CSV_PATH, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "timestamp",
                "actual_price",
                "forecast_price",
                "provider",
                "settlement_date",
                "settlement_period",
                "volume",
            ],
        )
        writer.writeheader()
        writer.writerows(records)

    df = pd.DataFrame(records)

    if df.empty:
        chart_data = {
            "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "provider": ELEXON_MARKET_INDEX_PROVIDER,
            "labels": [],
            "values": [],
            "actual_values": [],
            "forecast_values": [],
        }
    else:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        df = df.sort_values("timestamp").reset_index(drop=True)
        latest_complete_slot = pd.Timestamp.utcnow().floor("30min") - pd.Timedelta(minutes=30)
        expected_index = pd.date_range(end=latest_complete_slot, periods=48, freq="30min", tz="UTC")

        df = (
            df.drop_duplicates(subset=["timestamp"])
            .set_index("timestamp")
            .reindex(expected_index)
            .reset_index()
            .rename(columns={"index": "timestamp"})
        )
        df["provider"] = df["provider"].fillna(ELEXON_MARKET_INDEX_PROVIDER)
        df["time"] = df["timestamp"].dt.strftime("%H:%M")

        df.to_csv(CLEANED_CSV_PATH, index=False)

        chart_data = {
            "last_updated": pd.Timestamp.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
            "provider": ELEXON_MARKET_INDEX_PROVIDER,
            "labels": df["time"].tolist(),
            "values": [
                None if pd.isna(value) else value for value in df["actual_price"].tolist()
            ],
            "actual_values": [
                None if pd.isna(value) else value for value in df["actual_price"].tolist()
            ],
            "forecast_values": [None for _ in df["actual_price"].tolist()],
        }

    if df.empty:
        pd.DataFrame(
            columns=[
                "timestamp",
                "actual_price",
                "forecast_price",
                "provider",
                "settlement_date",
                "settlement_period",
                "volume",
                "time",
            ]
        ).to_csv(CLEANED_CSV_PATH, index=False)

    with open(CHART_JSON_PATH, "w", encoding="utf-8") as json_file:
        json.dump(chart_data, json_file, indent=2)

    print("Fetched live power price data successfully.")
    print(f"Rows loaded: {len(records)}")
    print(f"Saved {LIVE_CSV_PATH.name}")
    print(f"Saved {CLEANED_CSV_PATH.name}")
    print(f"Saved {CHART_JSON_PATH.name}")


if __name__ == "__main__":
    main()
