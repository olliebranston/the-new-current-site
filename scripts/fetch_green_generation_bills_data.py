import csv
import html
import json
import re
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"

NESO_RESOURCE_ID = "f93d1835-75bc-43e5-84ad-12472b180a98"
NESO_DATASET_PAGE_URL = (
    "https://www.neso.energy/data-portal/historic-generation-mix/"
    "historic_gb_generation_mix"
)
NESO_DIRECT_CSV_URL = (
    "https://api.neso.energy/dataset/88313ae5-94e4-4ddc-a790-593554d8c6b9/"
    "resource/f93d1835-75bc-43e5-84ad-12472b180a98/download/df_fuel_ckan.csv"
)
NESO_SQL_API_URL = "https://api.neso.energy/api/3/action/datastore_search_sql"

DESNZ_ANNUAL_BILLS_PAGE_URL = (
    "https://www.gov.uk/government/statistical-data-sets/"
    "annual-domestic-energy-price-statistics"
)
DESNZ_QEP_221_FALLBACK_URL = (
    "https://assets.publishing.service.gov.uk/media/69ca3804b66ff902f45443ce/"
    "table_221.xlsx"
)
OFGEM_DATA_PORTAL_URL = "https://www.ofgem.gov.uk/news-and-insight/data/data-portal"

GENERATION_MIX_CSV_PATH = DATA_DIR / "gb-generation-mix-annual-data.csv"
ELECTRICITY_BILLS_CSV_PATH = DATA_DIR / "uk-domestic-electricity-bills-annual-data.csv"
CHART_JSON_PATH = DATA_DIR / "green-generation-bills-chart-data.json"

GENERATION_COLUMNS = [
    "renewable_percentage",
    "low_carbon_percentage",
    "zero_carbon_percentage",
    "fossil_percentage",
]

USER_AGENT = "The New Current data updater (https://olliebranston.github.io/the-new-current-site/)"


def fetch_bytes(url):
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=90) as response:
        return response.read()


def fetch_text(url):
    return fetch_bytes(url).decode("utf-8", errors="replace")


def fetch_json(url):
    return json.loads(fetch_text(url))


def build_neso_sql_url(sql):
    return f"{NESO_SQL_API_URL}?{urlencode({'sql': sql})}"


def normalise_number(value):
    if value is None or pd.isna(value):
        return None

    cleaned = re.sub(r"[^0-9.\-]", "", str(value))

    if cleaned in {"", "-", "."}:
        return None

    try:
        return float(cleaned)
    except ValueError:
        return None


def normalise_year(value):
    if value is None or pd.isna(value):
        return None

    match = re.search(r"\b(19|20)\d{2}\b", str(value))

    if not match:
        return None

    year = int(match.group(0))
    current_year = datetime.now(timezone.utc).year

    if year < 1990 or year > current_year + 1:
        return None

    return year


def fetch_generation_mix_via_sql():
    sql = f"""
        SELECT
          date_part('year', "DATETIME") AS year,
          avg("RENEWABLE_perc") AS renewable_percentage,
          avg("LOW_CARBON_perc") AS low_carbon_percentage,
          avg("ZERO_CARBON_perc") AS zero_carbon_percentage,
          avg("FOSSIL_perc") AS fossil_percentage,
          count(*) AS interval_count
        FROM "{NESO_RESOURCE_ID}"
        WHERE
          "DATETIME" IS NOT NULL
          AND "RENEWABLE_perc" IS NOT NULL
          AND "LOW_CARBON_perc" IS NOT NULL
          AND "FOSSIL_perc" IS NOT NULL
        GROUP BY 1
        ORDER BY 1
    """
    payload = fetch_json(build_neso_sql_url(sql))

    if not payload.get("success"):
        raise RuntimeError(f"NESO SQL API returned an unsuccessful response: {payload}")

    records = payload.get("result", {}).get("records", [])

    if not records:
        raise RuntimeError("NESO SQL API returned no generation mix records.")

    dataframe = pd.DataFrame(records)
    dataframe["year"] = dataframe["year"].apply(normalise_year)

    for column in GENERATION_COLUMNS:
        dataframe[column] = pd.to_numeric(dataframe[column], errors="coerce")

    dataframe["interval_count"] = pd.to_numeric(dataframe["interval_count"], errors="coerce")

    return dataframe.dropna(subset=["year", *GENERATION_COLUMNS]).copy()


def fetch_generation_mix_via_csv():
    csv_bytes = fetch_bytes(NESO_DIRECT_CSV_URL)
    dataframe = pd.read_csv(
        BytesIO(csv_bytes),
        usecols=[
            "DATETIME",
            "RENEWABLE_perc",
            "LOW_CARBON_perc",
            "ZERO_CARBON_perc",
            "FOSSIL_perc",
        ],
    )
    dataframe["timestamp"] = pd.to_datetime(dataframe["DATETIME"], utc=True, errors="coerce")
    dataframe = dataframe.dropna(subset=["timestamp"]).copy()
    dataframe["year"] = dataframe["timestamp"].dt.year

    renamed = dataframe.rename(
        columns={
            "RENEWABLE_perc": "renewable_percentage",
            "LOW_CARBON_perc": "low_carbon_percentage",
            "ZERO_CARBON_perc": "zero_carbon_percentage",
            "FOSSIL_perc": "fossil_percentage",
        }
    )

    annual = (
        renamed.groupby("year", as_index=False)
        .agg(
            renewable_percentage=("renewable_percentage", "mean"),
            low_carbon_percentage=("low_carbon_percentage", "mean"),
            zero_carbon_percentage=("zero_carbon_percentage", "mean"),
            fossil_percentage=("fossil_percentage", "mean"),
            interval_count=("DATETIME", "count"),
        )
    )

    return annual


def build_generation_mix_dataframe():
    try:
        dataframe = fetch_generation_mix_via_sql()
    except Exception as error:
        print(f"NESO SQL aggregation failed, falling back to direct CSV: {error}")
        dataframe = fetch_generation_mix_via_csv()

    dataframe = dataframe.copy()
    dataframe["year"] = dataframe["year"].astype(int)

    for column in GENERATION_COLUMNS:
        dataframe[column] = pd.to_numeric(dataframe[column], errors="coerce").round(1)

    dataframe["interval_count"] = pd.to_numeric(
        dataframe["interval_count"],
        errors="coerce",
    ).fillna(0).astype(int)

    dataframe = dataframe.sort_values("year").reset_index(drop=True)
    validate_generation_mix(dataframe)

    return dataframe[["year", *GENERATION_COLUMNS, "interval_count"]]


def find_desnz_qep_221_workbook_url(page_html):
    anchor_pattern = re.compile(
        r"<a\b(?P<attrs>[^>]*)>(?P<body>.*?)</a>",
        flags=re.IGNORECASE | re.DOTALL,
    )
    href_pattern = re.compile(r'href=["\'](?P<href>[^"\']+)["\']', flags=re.IGNORECASE)

    candidates = []

    for match in anchor_pattern.finditer(page_html):
        attrs = match.group("attrs")
        body = html.unescape(re.sub(r"<[^>]+>", " ", match.group("body")))
        href_match = href_pattern.search(attrs)

        if not href_match:
            continue

        href = html.unescape(href_match.group("href"))
        context_start = max(0, match.start() - 500)
        context_end = min(len(page_html), match.end() + 500)
        context = html.unescape(
            re.sub(r"<[^>]+>", " ", page_html[context_start:context_end])
        )
        searchable_text = f"{body} {context} {href}".lower()

        if not (href.lower().endswith((".xlsx", ".xls")) or "xlsx" in href.lower()):
            continue

        if "qep 2.2.1" in searchable_text or "table_221" in searchable_text:
            candidates.append(urljoin(DESNZ_ANNUAL_BILLS_PAGE_URL, href))

    if candidates:
        return candidates[0]

    direct_asset_links = re.findall(
        r"https?://assets\.publishing\.service\.gov\.uk[^\"'<>\s]+\.xlsx",
        page_html,
        flags=re.IGNORECASE,
    )

    for href in direct_asset_links:
        if "table_221" in href.lower():
            return html.unescape(href)

    all_workbook_links = re.findall(
        r'href=["\']([^"\']+\.xlsx[^"\']*)["\']',
        page_html,
        flags=re.IGNORECASE,
    )

    for href in all_workbook_links:
        if "table_221" in href.lower():
            return urljoin(DESNZ_ANNUAL_BILLS_PAGE_URL, html.unescape(href))

    print("Could not discover QEP 2.2.1 workbook link from GOV.UK page; using fallback URL.")
    return DESNZ_QEP_221_FALLBACK_URL


def cell_text(value):
    if value is None or pd.isna(value):
        return ""

    text = str(value).strip()

    if text.lower() == "nan":
        return ""

    return re.sub(r"\s+", " ", text)


def row_contains(dataframe, row_index, pattern):
    regex = re.compile(pattern, flags=re.IGNORECASE)

    for value in dataframe.iloc[row_index].tolist():
        if regex.search(cell_text(value)):
            return True

    return False


def choose_year_column(dataframe, row_indices):
    best_column = None
    best_count = 0

    for column in dataframe.columns:
        count = sum(normalise_year(dataframe.at[row_index, column]) is not None for row_index in row_indices)

        if count > best_count:
            best_column = column
            best_count = count

    if best_column is None or best_count < 5:
        raise ValueError("Could not identify a year column in DESNZ QEP 2.2.1 workbook.")

    return best_column


def header_label_for_column(dataframe, column, data_start_row):
    context_start = max(0, data_start_row - 12)
    context = dataframe.iloc[context_start:data_start_row, :].map(cell_text)
    context = context.replace("", pd.NA).ffill(axis=1).fillna("")
    labels = []

    for value in context[column].tolist():
        if value and value not in labels:
            labels.append(value)

    return " ".join(labels)


def score_bill_column(label):
    normalised = label.lower().replace("-", " ")
    score = 0

    if "overall" in normalised:
        score += 12

    if "all consumers" in normalised or "all consumer" in normalised:
        score += 8

    if "uk" in normalised or "united kingdom" in normalised:
        score += 3

    if "cash terms" in normalised or "current price" in normalised:
        score += 2

    if "direct debit" in normalised:
        score += 1

    if "credit" in normalised or "prepayment" in normalised:
        score -= 3

    if (
        "real terms" in normalised
        or "unit cost" in normalised
        or "fixed cost" in normalised
        or "standing charge" in normalised
        or "% change" in normalised
    ):
        score -= 20

    return score


def find_cash_terms_data_rows(dataframe):
    cash_terms_rows = [
        row_index
        for row_index in range(len(dataframe))
        if row_contains(dataframe, row_index, r"\bcash terms\b|\bcurrent prices?\b")
    ]
    real_terms_rows = [
        row_index
        for row_index in range(len(dataframe))
        if row_contains(dataframe, row_index, r"\breal terms\b")
    ]

    start_search_row = cash_terms_rows[0] + 1 if cash_terms_rows else 0
    following_real_terms = [row for row in real_terms_rows if row > start_search_row]
    end_search_row = following_real_terms[0] if following_real_terms else len(dataframe)
    candidate_rows = list(range(start_search_row, end_search_row))
    year_column = choose_year_column(dataframe, candidate_rows)
    data_rows = [
        row_index
        for row_index in candidate_rows
        if normalise_year(dataframe.at[row_index, year_column]) is not None
    ]

    if len(data_rows) < 5:
        all_rows = list(range(len(dataframe)))
        year_column = choose_year_column(dataframe, all_rows)
        data_rows = [
            row_index
            for row_index in all_rows
            if normalise_year(dataframe.at[row_index, year_column]) is not None
        ]

    if len(data_rows) < 5:
        raise ValueError("DESNZ QEP 2.2.1 workbook did not contain enough annual bill rows.")

    return data_rows, year_column


def parse_electricity_bill_workbook(workbook_bytes):
    sheets = pd.read_excel(BytesIO(workbook_bytes), sheet_name=None, header=None, engine="openpyxl")
    candidate_sheets = []

    for sheet_name, dataframe in sheets.items():
        sheet_text = " ".join(dataframe.fillna("").astype(str).head(30).values.flatten()).lower()

        if "2.2.1" in str(sheet_name).lower() or "2.2.1" in sheet_text:
            candidate_sheets.insert(0, (sheet_name, dataframe))
        else:
            candidate_sheets.append((sheet_name, dataframe))

    parse_errors = []

    for sheet_name, dataframe in candidate_sheets:
        try:
            data_rows, year_column = find_cash_terms_data_rows(dataframe)
            data_start_row = min(data_rows)
            bill_columns = []

            for column in dataframe.columns:
                if column == year_column:
                    continue

                values = [normalise_number(dataframe.at[row_index, column]) for row_index in data_rows]
                usable_values = [value for value in values if value is not None]

                if len(usable_values) < 5:
                    continue

                label = header_label_for_column(dataframe, column, data_start_row)
                bill_columns.append(
                    {
                        "column": column,
                        "label": label,
                        "score": score_bill_column(label),
                        "values": values,
                    }
                )

            if not bill_columns:
                raise ValueError("No numeric bill columns found.")

            selected_column = max(bill_columns, key=lambda item: item["score"])

            if selected_column["score"] <= 0:
                labels = "; ".join(item["label"] for item in bill_columns[:8])
                raise ValueError(
                    "Could not identify the representative all-payment-types bill column. "
                    f"Candidate headers: {labels}"
                )

            records = []

            for row_index, bill_value in zip(data_rows, selected_column["values"]):
                year = normalise_year(dataframe.at[row_index, year_column])

                if year is None or bill_value is None:
                    continue

                records.append(
                    {
                        "year": int(year),
                        "bill_gbp_nominal": round(float(bill_value), 1),
                    }
                )

            bills_df = pd.DataFrame(records).drop_duplicates(subset=["year"])
            bills_df = bills_df.sort_values("year").reset_index(drop=True)
            validate_bills(bills_df)

            return bills_df, {
                "sheet_name": str(sheet_name),
                "selected_column_header": selected_column["label"],
                "selection_note": (
                    "Selected the highest-scoring representative column from QEP 2.2.1, "
                    "preferring Overall / all-consumer UK cash-terms bills."
                ),
            }
        except Exception as error:
            parse_errors.append(f"{sheet_name}: {error}")

    raise ValueError(
        "Could not parse DESNZ QEP 2.2.1 electricity bill workbook. "
        + " | ".join(parse_errors)
    )


def build_electricity_bill_dataframe():
    page_html = fetch_text(DESNZ_ANNUAL_BILLS_PAGE_URL)
    workbook_url = find_desnz_qep_221_workbook_url(page_html)
    workbook_bytes = fetch_bytes(workbook_url)
    bills_df, parse_metadata = parse_electricity_bill_workbook(workbook_bytes)

    return bills_df, workbook_url, parse_metadata


def validate_generation_mix(dataframe):
    missing_columns = [column for column in ["year", *GENERATION_COLUMNS] if column not in dataframe.columns]

    if missing_columns:
        raise ValueError(f"Generation mix data is missing columns: {missing_columns}")

    if len(dataframe) < 8:
        raise ValueError("Generation mix data has too few annual rows to chart.")

    for column in GENERATION_COLUMNS:
        if dataframe[column].isna().any():
            raise ValueError(f"Generation mix column contains missing values: {column}")

        invalid_values = dataframe.loc[
            (dataframe[column] < 0) | (dataframe[column] > 100),
            ["year", column],
        ]

        if not invalid_values.empty:
            raise ValueError(
                f"Generation mix column contains values outside 0-100: {invalid_values.to_dict('records')}"
            )


def validate_bills(dataframe):
    if "year" not in dataframe.columns or "bill_gbp_nominal" not in dataframe.columns:
        raise ValueError("Electricity bill data must contain year and bill_gbp_nominal columns.")

    if len(dataframe) < 8:
        raise ValueError("Electricity bill data has too few annual rows to chart.")

    if dataframe["bill_gbp_nominal"].isna().any():
        raise ValueError("Electricity bill data contains missing bill values.")

    if (dataframe["bill_gbp_nominal"] <= 0).any():
        raise ValueError("Electricity bill data contains non-positive bill values.")


def build_aligned_chart_data(generation_df, bills_df, source_metadata):
    merged = generation_df.merge(bills_df, on="year", how="inner").sort_values("year")

    if len(merged) < 8:
        raise ValueError(
            "Overlapping generation mix and electricity bill period has too few years to chart."
        )

    expected_years = list(range(int(merged["year"].min()), int(merged["year"].max()) + 1))
    actual_years = merged["year"].astype(int).tolist()

    if actual_years != expected_years:
        missing_years = sorted(set(expected_years) - set(actual_years))
        raise ValueError(
            "Aligned chart data has gaps in the final year range. "
            f"Missing years: {missing_years}"
        )

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return {
        "last_updated": generated_at,
        "labels": merged["year"].astype(str).tolist(),
        "year_range": {
            "start": int(merged["year"].min()),
            "end": int(merged["year"].max()),
        },
        "generation_mix": {
            "renewable_percentage": merged["renewable_percentage"].round(1).tolist(),
            "low_carbon_percentage": merged["low_carbon_percentage"].round(1).tolist(),
            "zero_carbon_percentage": merged["zero_carbon_percentage"].round(1).tolist(),
            "fossil_percentage": merged["fossil_percentage"].round(1).tolist(),
        },
        "domestic_electricity_bill": {
            "bill_gbp_nominal": merged["bill_gbp_nominal"].round(1).tolist(),
        },
        "metadata": {
            "generated_at": generated_at,
            "x_axis": (
                "Both charts use the same overlapping annual year range and the same "
                "year labels."
            ),
            "generation_transform": (
                "Annual mean percentages from NESO Historic GB Generation Mix fields "
                "RENEWABLE_perc, LOW_CARBON_perc, ZERO_CARBON_perc, and FOSSIL_perc."
            ),
            "bill_transform": (
                "Nominal GBP annual domestic standard electricity bill from DESNZ QEP 2.2.1. "
                "The parser prefers the Overall / all-consumer UK cash-terms series."
            ),
            "inflation_adjustment": "None. Values are nominal GBP.",
            "sources": source_metadata,
            "ofgem_bill_breakdown_future_hook": {
                "status": "not implemented",
                "source": "Ofgem Data Portal",
                "url": OFGEM_DATA_PORTAL_URL,
            },
        },
    }


def write_csv(path, dataframe):
    dataframe.to_csv(path, index=False, quoting=csv.QUOTE_MINIMAL)


def main():
    generation_df = build_generation_mix_dataframe()
    bills_df, desnz_workbook_url, bill_parse_metadata = build_electricity_bill_dataframe()

    source_metadata = {
        "generation_mix": {
            "name": "NESO Data Portal - Historic GB Generation Mix",
            "page_url": NESO_DATASET_PAGE_URL,
            "direct_csv_url": NESO_DIRECT_CSV_URL,
            "resource_id": NESO_RESOURCE_ID,
            "date_accessed": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        },
        "domestic_electricity_bills": {
            "name": "DESNZ/GOV.UK - Annual domestic energy bills, QEP 2.2.1",
            "page_url": DESNZ_ANNUAL_BILLS_PAGE_URL,
            "workbook_url": desnz_workbook_url,
            "date_accessed": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            **bill_parse_metadata,
        },
    }

    chart_data = build_aligned_chart_data(generation_df, bills_df, source_metadata)

    write_csv(GENERATION_MIX_CSV_PATH, generation_df)
    write_csv(ELECTRICITY_BILLS_CSV_PATH, bills_df)

    with open(CHART_JSON_PATH, "w", encoding="utf-8") as json_file:
        json.dump(chart_data, json_file, indent=2)

    print("Built green generation and domestic electricity bill data successfully.")
    print(f"Generation rows: {len(generation_df)}")
    print(f"Bill rows: {len(bills_df)}")
    print(
        "Aligned range: "
        f"{chart_data['year_range']['start']}-{chart_data['year_range']['end']}"
    )
    print(f"Saved {GENERATION_MIX_CSV_PATH.name}")
    print(f"Saved {ELECTRICITY_BILLS_CSV_PATH.name}")
    print(f"Saved {CHART_JSON_PATH.name}")


if __name__ == "__main__":
    main()
