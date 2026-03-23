import pandas as pd

# Load the CSV file into a pandas DataFrame
df = pd.read_csv("data/sample-carbon-intensity.csv")

# Convert the timestamp column from text into a real datetime format
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Create a new column showing just the hour
df["hour"] = df["timestamp"].dt.hour

# Create a new column showing just the date
df["date"] = df["timestamp"].dt.date

print("Transformed data:")
print(df)
print()

# Calculate the average carbon intensity by date
daily_average = df.groupby("date")["carbon_intensity"].mean().reset_index()

print("Daily average carbon intensity:")
print(daily_average)

# Save the transformed full dataset
df.to_csv("data/cleaned-carbon-intensity.csv", index=False)

# Save the daily averages
daily_average.to_csv("data/daily-average-carbon-intensity.csv", index=False)

print()
print("Saved cleaned files successfully.")
