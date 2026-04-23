import json
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"

TERRITORIAL_CSV_PATH = (
    DATA_DIR
    / "Figure_1__Top_emitting_national_communication_sectors_on_a_territorial_basis__UK_1990_to_2024_(provisional).csv"
)
CONSUMPTION_CSV_PATH = (
    DATA_DIR
    / "Figure_3__UK_consumption_footprint_over_time__UK,_1996_to_2022.csv"
)
POPULATION_CSV_PATH = DATA_DIR / "Historic UK Population.csv"

CLEANED_CSV_PATH = DATA_DIR / "uk-carbon-accounting-data.csv"
CHART_JSON_PATH = DATA_DIR / "uk-carbon-accounting-chart-data.json"

START_YEAR = 1996
END_YEAR = 2022

TERRITORIAL_COMPONENT_COLUMNS = [
    "Electricity supply",
    "Fuel supply",
    "Domestic transport",
    "Buildings and product uses",
    "Industry",
    "Agriculture",
    "Waste",
    "Land use, land use change and forestry",
]

CONSUMPTION_COMPONENT_COLUMNS = [
    "GHG from UK produced goods and services consumed by UK residents",
    "GHG embedded in imported goods and services to UK",
    "UK Households heating emissions arising from the use of fossil fuels",
    "UK Transport emissions generated directly by UK households",
]

POPULATION_COLUMN = "United Kingdom population mid-year estimate"


def load_structured_csv(csv_path, header_row_index):
    return pd.read_csv(csv_path, skiprows=header_row_index)


def load_population_csv(csv_path):
    return pd.read_csv(csv_path, skiprows=range(1, 8))


def normalise_year_column(dataframe):
    dataframe = dataframe.copy()
    dataframe["Year"] = pd.to_numeric(dataframe["Year"], errors="coerce")
    dataframe = dataframe.dropna(subset=["Year"]).copy()
    dataframe["Year"] = dataframe["Year"].astype(int)
    return dataframe


def ensure_numeric_columns(dataframe, columns, dataset_label):
    dataframe = dataframe.copy()

    for column in columns:
        dataframe[column] = pd.to_numeric(dataframe[column], errors="coerce")

        if dataframe[column].isna().any():
            missing_years = dataframe.loc[dataframe[column].isna(), "Year"].astype(str).tolist()
            raise ValueError(
                f"{dataset_label} contains non-numeric values in '{column}' for years: "
                + ", ".join(missing_years)
            )

    return dataframe


def filter_year_range(dataframe):
    return dataframe.loc[
        dataframe["Year"].between(START_YEAR, END_YEAR),
    ].copy()


def validate_expected_years(dataframe, dataset_label):
    expected_years = list(range(START_YEAR, END_YEAR + 1))
    actual_years = dataframe["Year"].tolist()

    if actual_years != expected_years:
        missing_years = sorted(set(expected_years) - set(actual_years))
        extra_years = sorted(set(actual_years) - set(expected_years))
        raise ValueError(
            f"{dataset_label} does not match the expected year range {START_YEAR}-{END_YEAR}. "
            f"Missing years: {missing_years}. Extra years: {extra_years}."
        )


def build_territorial_dataframe():
    territorial_df = load_structured_csv(TERRITORIAL_CSV_PATH, header_row_index=6)
    territorial_df = normalise_year_column(territorial_df)
    territorial_df = ensure_numeric_columns(
        territorial_df,
        TERRITORIAL_COMPONENT_COLUMNS,
        "Territorial emissions dataset",
    )
    territorial_df = filter_year_range(territorial_df)
    territorial_df["territorial_emissions_mtco2e"] = territorial_df[
        TERRITORIAL_COMPONENT_COLUMNS
    ].sum(axis=1)
    validate_expected_years(territorial_df, "Territorial emissions dataset")

    return territorial_df[["Year", "territorial_emissions_mtco2e", *TERRITORIAL_COMPONENT_COLUMNS]]


def build_consumption_dataframe():
    consumption_df = load_structured_csv(CONSUMPTION_CSV_PATH, header_row_index=6)
    consumption_df = normalise_year_column(consumption_df)
    consumption_df = ensure_numeric_columns(
        consumption_df,
        CONSUMPTION_COMPONENT_COLUMNS,
        "Consumption emissions dataset",
    )
    consumption_df = filter_year_range(consumption_df)
    consumption_df["consumption_emissions_mtco2e"] = consumption_df[
        CONSUMPTION_COMPONENT_COLUMNS
    ].sum(axis=1)
    validate_expected_years(consumption_df, "Consumption emissions dataset")

    return consumption_df[["Year", "consumption_emissions_mtco2e", *CONSUMPTION_COMPONENT_COLUMNS]]


def build_population_dataframe():
    population_df = load_population_csv(POPULATION_CSV_PATH)
    population_df = population_df.rename(columns={"Title": "Year"})
    population_df = normalise_year_column(population_df)
    population_df = ensure_numeric_columns(
        population_df,
        [POPULATION_COLUMN],
        "Population dataset",
    )
    population_df = filter_year_range(population_df)
    validate_expected_years(population_df, "Population dataset")

    return population_df[["Year", POPULATION_COLUMN]].rename(
        columns={POPULATION_COLUMN: "population"}
    )


def build_combined_dataframe():
    territorial_df = build_territorial_dataframe()
    consumption_df = build_consumption_dataframe()
    population_df = build_population_dataframe()

    combined_df = territorial_df.merge(consumption_df, on="Year", how="inner").merge(
        population_df,
        on="Year",
        how="inner",
    )

    validate_expected_years(combined_df, "Combined UK carbon accounting dataset")

    combined_df["consumption_per_person_tco2e"] = (
        combined_df["consumption_emissions_mtco2e"] * 1_000_000
    ) / combined_df["population"]

    combined_df["label"] = combined_df["Year"].astype(str)

    return combined_df


def build_chart_json(combined_df):
    return {
        "last_updated": pd.Timestamp.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "labels": combined_df["label"].tolist(),
        "territorial_emissions_mtco2e": combined_df["territorial_emissions_mtco2e"]
        .round(1)
        .tolist(),
        "consumption_emissions_mtco2e": combined_df["consumption_emissions_mtco2e"]
        .round(1)
        .tolist(),
        "consumption_per_person_tco2e": combined_df["consumption_per_person_tco2e"]
        .round(2)
        .tolist(),
        "metadata": {
            "start_year": START_YEAR,
            "end_year": END_YEAR,
            "units": {
                "territorial_emissions_mtco2e": "MtCO2e",
                "consumption_emissions_mtco2e": "MtCO2e",
                "consumption_per_person_tco2e": "tCO2e per person",
            },
            "definitions": {
                "territorial_emissions_mtco2e": (
                    "Annual UK territorial greenhouse gas emissions total, calculated "
                    "by summing the sector columns in the DESNZ territorial emissions source."
                ),
                "consumption_emissions_mtco2e": (
                    "Annual UK consumption-based greenhouse gas emissions total, "
                    "calculated by summing the four published components in the Defra source."
                ),
                "consumption_per_person_tco2e": (
                    "Consumption-based emissions divided by the UK mid-year population estimate."
                ),
            },
            "sources": {
                "territorial": TERRITORIAL_CSV_PATH.name,
                "consumption": CONSUMPTION_CSV_PATH.name,
                "population": POPULATION_CSV_PATH.name,
            },
        },
    }


def main():
    combined_df = build_combined_dataframe()
    combined_df.to_csv(CLEANED_CSV_PATH, index=False)

    chart_json = build_chart_json(combined_df)
    with open(CHART_JSON_PATH, "w", encoding="utf-8") as json_file:
        json.dump(chart_json, json_file, indent=2)

    print("Built UK carbon accounting data successfully.")
    print(f"Rows loaded: {len(combined_df)}")
    print(f"Saved {CLEANED_CSV_PATH.name}")
    print(f"Saved {CHART_JSON_PATH.name}")


if __name__ == "__main__":
    main()
