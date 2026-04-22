import json
import csv
from pathlib import Path
from urllib.request import urlopen

import pandas as pd

API_URL_TEMPLATE = "https://api.carbonintensity.org.uk/intensity/{from_time}/pt24h"
REPO_ROOT = Path(__file__).resolve().parent.parent
LIVE_CSV_PATH = REPO_ROOT / "data" / "live-carbon-intensity.csv"
CLEANED_CSV_PATH = REPO_ROOT / "data" / "cleaned-live-carbon-intensity.csv"
DAILY_AVERAGE_CSV_PATH = REPO_ROOT / "data" / "daily-average-live-carbon-intensity.csv"
CHART_JSON_PATH = REPO_ROOT / "data" / "carbon-chart-data.json"

from_time = pd.Timestamp.now("UTC").strftime("%Y-%m-%dT%H:%MZ")
api_url = API_URL_TEMPLATE.format(from_time=from_time)

with urlopen(api_url) as response:
    api_data = json.load(response)

rows = api_data["data"]

records = []

for row in rows:
    timestamp = row["from"]
    forecast = row["intensity"]["forecast"]
    actual = row["intensity"]["actual"]
    index_value = row["intensity"]["index"]

    chart_value = actual if actual is not None else forecast

    records.append(
        {
            "timestamp": timestamp,
            "forecast": forecast,
            "actual": actual,
            "index": index_value,
            "chart_value": chart_value,
        }
    )

with open(LIVE_CSV_PATH, "w", newline="", encoding="utf-8") as csv_file:
    writer = csv.DictWriter(
        csv_file,
        fieldnames=["timestamp", "forecast", "actual", "index", "chart_value"],
    )
    writer.writeheader()
    writer.writerows(records)

df = pd.DataFrame(records)
df = df[df["actual"].notna()].reset_index(drop=True)

df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
df = df.dropna(subset=["timestamp"]).copy()

latest_complete_slot = pd.Timestamp.now("UTC").floor("30min") - pd.Timedelta(minutes=30)
expected_index = pd.date_range(
    end=latest_complete_slot,
    periods=48,
    freq="30min",
    tz="UTC",
)

df = (
    df.drop_duplicates(subset=["timestamp"])
    .set_index("timestamp")
    .reindex(expected_index)
    .reset_index()
    .rename(columns={"index": "timestamp"})
)

df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
df["time"] = df["timestamp"].dt.strftime("%H:%M")
df["date"] = df["timestamp"].dt.strftime("%Y-%m-%d")

daily_average = df.groupby("date", dropna=True)["chart_value"].mean().reset_index()

df.to_csv(CLEANED_CSV_PATH, index=False)
daily_average.to_csv(DAILY_AVERAGE_CSV_PATH, index=False)

chart_data = {
    "last_updated": pd.Timestamp.now("UTC").strftime("%Y-%m-%d %H:%M UTC"),
    "labels": df["time"].tolist(),
    "values": [
        None if pd.isna(value) else value for value in df["chart_value"].tolist()
    ],
    "actual_values": [
        None if pd.isna(value) else value for value in df["actual"].tolist()
    ],
    "forecast_values": [None for _ in df["actual"].tolist()],
    "daily_average": daily_average.to_dict(orient="records"),
}

with open(CHART_JSON_PATH, "w", encoding="utf-8") as json_file:
    json.dump(chart_data, json_file, indent=2)

print("Fetched live data successfully.")
print(f"Rows loaded: {len(df)}")
print("Saved live-carbon-intensity.csv")
print("Saved cleaned-live-carbon-intensity.csv")
print("Saved daily-average-live-carbon-intensity.csv")
print("Saved carbon-chart-data.json")