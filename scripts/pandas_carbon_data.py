import pandas as pd

df = pd.read_csv("data/sample-carbon-intensity.csv")

print("Data loaded successfully")
print()
print("First five rows:")
print(df.head())
print()
print("Column names:")
print(df.columns)
print()
print("Summary statistics:")
print(df["carbon_intensity"].describe())