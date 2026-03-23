import json
import csv
from urllib.request import urlopen

import pandas as pd

API_URL = "https://api.carbonintensity.org.uk/intensity/date"

with urlopen(API_URL) as response:
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

with open("data/live-carbon-intensity.csv", "w", newline="", encoding="utf-8") as csv_file:
    writer = csv.DictWriter(
        csv_file,
        fieldnames=["timestamp", "forecast", "actual", "index", "chart_value"],
    )
    writer.writeheader()
    writer.writerows(records)

df = pd.DataFrame(records)

df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
df["time"] = df["timestamp"].dt.strftime("%H:%M")
df["date"] = df["timestamp"].dt.strftime("%Y-%m-%d")

daily_average = df.groupby("date")["chart_value"].mean().reset_index()

df.to_csv("data/cleaned-live-carbon-intensity.csv", index=False)
daily_average.to_csv("data/daily-average-live-carbon-intensity.csv", index=False)

chart_data = {
    "last_updated": pd.Timestamp.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
    "labels": df["time"].tolist(),
    "values": df["chart_value"].tolist(),
    "actual_values": [
        None if pd.isna(value) else value for value in df["actual"].tolist()
    ],
    "forecast_values": [
        None if pd.isna(value) else value for value in df["forecast"].tolist()
    ],
}

with open("data/carbon-chart-data.json", "w", encoding="utf-8") as json_file:
    json.dump(chart_data, json_file, indent=2)

print("Fetched live data successfully.")
print(f"Rows loaded: {len(df)}")
print("Saved live-carbon-intensity.csv")
print("Saved cleaned-live-carbon-intensity.csv")
print("Saved daily-average-live-carbon-intensity.csv")
print("Saved carbon-chart-data.json")