import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

import pandas as pd


GENERATION_MIX_URL_TEMPLATE = "https://api.carbonintensity.org.uk/generation/{from_time}/pt24h"
REPO_ROOT = Path(__file__).resolve().parent.parent
LIVE_CSV_PATH = REPO_ROOT / "data" / "live-generation-mix.csv"
CLEANED_CSV_PATH = REPO_ROOT / "data" / "cleaned-live-generation-mix.csv"
CHART_JSON_PATH = REPO_ROOT / "data" / "generation-mix-chart-data.json"

FUEL_ORDER = [
    "wind",
    "solar",
    "hydro",
    "nuclear",
    "biomass",
    "storage",
    "gas",
    "imports",
    "coal",
    "other",
]

FUEL_LABELS = {
    "wind": "Wind",
    "solar": "Solar",
    "hydro": "Hydro",
    "nuclear": "Nuclear",
    "biomass": "Biomass",
    "storage": "Storage",
    "gas": "Gas",
    "imports": "Imports",
    "coal": "Coal",
    "other": "Other",
}


def fetch_json(url):
    with urlopen(url) as response:
        return json.load(response)


def build_generation_mix_url():
    now = datetime.now(timezone.utc)
    from_time = now.strftime("%Y-%m-%dT%H:%MZ")
    return GENERATION_MIX_URL_TEMPLATE.format(from_time=from_time)


def main():
    payload = fetch_json(build_generation_mix_url())
    rows = payload.get("data", [])

    records = []

    for row in rows:
        timestamp = row.get("from")
        mix_items = row.get("generationmix", [])

        if not timestamp or not isinstance(mix_items, list):
            continue

        for item in mix_items:
            fuel = str(item.get("fuel", "")).lower()
            percentage = item.get("perc")

            if fuel not in FUEL_ORDER or percentage in (None, ""):
                continue

            try:
                numeric_percentage = float(percentage)
            except (TypeError, ValueError):
                continue

            records.append(
                {
                    "timestamp": timestamp,
                    "fuel": fuel,
                    "percentage": numeric_percentage,
                }
            )

    with open(LIVE_CSV_PATH, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=["timestamp", "fuel", "percentage"],
        )
        writer.writeheader()
        writer.writerows(records)

    df = pd.DataFrame(records)

    if df.empty:
        cleaned_df = pd.DataFrame(columns=["timestamp", "time", *FUEL_ORDER])
        chart_data = {
            "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "labels": [],
            "datasets": [
                {
                    "key": fuel,
                    "label": FUEL_LABELS[fuel],
                    "values": [],
                }
                for fuel in FUEL_ORDER
            ],
        }
    else:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        pivot_df = (
            df.pivot_table(
                index="timestamp",
                columns="fuel",
                values="percentage",
                aggfunc="first",
            )
            .reindex(columns=FUEL_ORDER, fill_value=0)
            .fillna(0)
            .sort_values("timestamp")
        )
        latest_complete_slot = pd.Timestamp.utcnow().floor("30min") - pd.Timedelta(minutes=60)
        expected_index = pd.date_range(end=latest_complete_slot, periods=48, freq="30min", tz="UTC")
        pivot_df = (
            pivot_df.reindex(expected_index)
            .fillna(0)
            .reset_index()
            .rename(columns={"index": "timestamp"})
        )
        pivot_df["time"] = pivot_df["timestamp"].dt.strftime("%H:%M")
        cleaned_df = pivot_df[["timestamp", "time", *FUEL_ORDER]]

        chart_data = {
            "last_updated": pd.Timestamp.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
            "labels": cleaned_df["time"].tolist(),
            "datasets": [
                {
                    "key": fuel,
                    "label": FUEL_LABELS[fuel],
                    "values": [
                        None if pd.isna(value) else float(value)
                        for value in cleaned_df[fuel].tolist()
                    ],
                }
                for fuel in FUEL_ORDER
            ],
        }

    cleaned_df.to_csv(CLEANED_CSV_PATH, index=False)

    with open(CHART_JSON_PATH, "w", encoding="utf-8") as json_file:
        json.dump(chart_data, json_file, indent=2)

    print("Fetched generation mix over time successfully.")
    print(f"Rows loaded: {len(records)}")
    print(f"Saved {LIVE_CSV_PATH.name}")
    print(f"Saved {CLEANED_CSV_PATH.name}")
    print(f"Saved {CHART_JSON_PATH.name}")


if __name__ == "__main__":
    main()
