import csv

with open("data/sample-carbon-intensity.csv", newline="") as file:
    reader = csv.DictReader(file)
    rows = list(reader)

print("Rows loaded:", len(rows))
print("First row:", rows[0])
print("Last row:", rows[-1])