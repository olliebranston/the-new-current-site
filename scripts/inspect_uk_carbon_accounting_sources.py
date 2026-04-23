import json
from pathlib import Path
from urllib.request import urlopen

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parent.parent
TEMP_DIR = REPO_ROOT / ".tmp-carbon-accounting-sources"
OUTPUT_PATH = REPO_ROOT / "data" / "uk-carbon-accounting-source-inspection.json"

SOURCE_FILES = [
    {
        "key": "production_emissions",
        "label": "ONS production-based emissions",
        "url": "https://download.ons.gov.uk/downloads/datasets/uk-environmental-accounts-atmospheric-emissions-greenhouse-gas-emissions-by-economic-sector-and-gas/editions/current/versions/30.xlsx",
        "filename": "ons_production_emissions.xlsx",
        "kind": "excel",
    },
    {
        "key": "consumption_emissions",
        "label": "Defra UK carbon footprint",
        "url": "https://assets.publishing.service.gov.uk/media/68220f6dd9c9bb76078f7f5f/Defra22_results_UK.ods",
        "filename": "defra_uk_carbon_footprint.ods",
        "kind": "excel",
    },
    {
        "key": "population",
        "label": "ONS population estimates",
        "url": "https://download.ons.gov.uk/downloads/datasets/population-estimates-timeseries-dataset/editions/time-series/versions/70.xlsx",
        "filename": "ons_population_estimates.xlsx",
        "kind": "excel",
    },
]


def ensure_temp_dir():
    TEMP_DIR.mkdir(exist_ok=True)


def download_file(source):
    target_path = TEMP_DIR / source["filename"]

    with urlopen(source["url"]) as response:
        target_path.write_bytes(response.read())

    return target_path


def normalise_cell(value):
    if pd.isna(value):
        return None

    text = str(value).strip()
    return text if text else None


def trim_row(values, limit=10):
    trimmed = [normalise_cell(value) for value in list(values)[:limit]]

    while trimmed and trimmed[-1] is None:
        trimmed.pop()

    return trimmed


def inspect_sheet(file_path, sheet_name, engine):
    raw_preview_df = pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        header=None,
        nrows=8,
        dtype=object,
        engine=engine,
    )
    inferred_header_df = pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        nrows=3,
        dtype=object,
        engine=engine,
    )

    raw_preview = [
        trim_row(row)
        for row in raw_preview_df.itertuples(index=False, name=None)
        if any(cell is not None for cell in trim_row(row))
    ]

    inferred_columns = [
        column_name
        for column_name in [normalise_cell(column) for column in inferred_header_df.columns]
        if column_name is not None
    ]

    return {
        "sheet_name": sheet_name,
        "raw_preview": raw_preview,
        "inferred_columns": inferred_columns[:20],
        "row_count_preview": int(len(raw_preview_df.index)),
        "column_count_preview": int(len(raw_preview_df.columns)),
    }


def inspect_excel_file(file_path):
    engine = "odf" if file_path.suffix.lower() == ".ods" else None
    workbook = pd.ExcelFile(file_path, engine=engine)

    return {
        "sheet_names": workbook.sheet_names,
        "sheet_summaries": [
            inspect_sheet(file_path, sheet_name, engine)
            for sheet_name in workbook.sheet_names
        ],
    }


def build_source_summary(source):
    print(f"Downloading {source['label']}...")
    file_path = download_file(source)
    print(f"Downloaded {file_path.name}")

    if source["kind"] != "excel":
        raise ValueError(f"Unsupported source kind: {source['kind']}")

    inspection = inspect_excel_file(file_path)

    return {
        "key": source["key"],
        "label": source["label"],
        "url": source["url"],
        "downloaded_filename": file_path.name,
        "file_size_bytes": file_path.stat().st_size,
        "inspection": inspection,
    }


def main():
    ensure_temp_dir()

    source_summaries = []

    for source in SOURCE_FILES:
        try:
            source_summaries.append(build_source_summary(source))
        except Exception as error:
            source_summaries.append(
                {
                    "key": source["key"],
                    "label": source["label"],
                    "url": source["url"],
                    "error": str(error),
                }
            )
            print(f"Failed to inspect {source['label']}: {error}")

    inspection_output = {
        "last_updated": pd.Timestamp.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "purpose": (
            "Inspection output for the planned UK production-versus-consumption "
            "carbon accounting charts. This file is meant to help confirm source "
            "workbook structure before building the transformation pipeline."
        ),
        "sources": source_summaries,
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(inspection_output, file, indent=2)

    print(f"Saved {OUTPUT_PATH.name}")


if __name__ == "__main__":
    main()
