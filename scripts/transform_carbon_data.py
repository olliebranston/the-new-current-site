import pandas as pd
import json

# Load the CSV file into a pandas DataFrame
df = pd.read_csv("data/sample-carbon-intensity.csv")

# Convert timestamp text into real datetime values
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Create helper columns
df["hour"] = df["timestamp"].dt.hour
df["date"] = df["timestamp"].dt.date

print("Transformed data:")
print(df)
print()

# Calculate daily average carbon intensity
daily_average = df.groupby("date")["carbon_intensity"].mean().reset_index()

print("Daily average carbon intensity:")
print(daily_average)

# Save CSV outputs
df.to_csv("data/cleaned-carbon-intensity.csv", index=False)
daily_average.to_csv("data/daily-average-carbon-intensity.csv", index=False)

# Create JSON output for the chart
chart_data = {
    "labels": df["timestamp"].dt.strftime("%H:%M").tolist(),
    "values": df["carbon_intensity"].tolist()
}

with open("data/carbon-chart-data.json", "w") as json_file:
    json.dump(chart_data, json_file, indent=2)

print()
print("Saved cleaned files successfully.")
print("Saved chart JSON successfully.")
