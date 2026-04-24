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
from openpyxl import load_workbook


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
DESNZ_MAIN_SHEET_NAME = "2.2.1"
DESNZ_PAYMENT_METHODS_SHEET_NAME = "2.2.1 (Payment Methods)"
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
MIN_ANNUAL_ROWS = 8
MIN_OVERLAP_YEARS = 8
EXPECTED_GENERATION_START_YEAR = 2009

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


def get_years(dataframe):
    if dataframe is None or dataframe.empty or "year" not in dataframe.columns:
        return []

    return sorted(
        {
            int(year)
            for year in pd.to_numeric(dataframe["year"], errors="coerce").dropna().tolist()
        }
    )


def format_year_summary(dataframe):
    years = get_years(dataframe)

    if not years:
        return "rows=0, years=none"

    return f"rows={len(dataframe)}, years={years[0]}-{years[-1]}"


def print_year_summary(label, dataframe):
    print(f"{label}: {format_year_summary(dataframe)}")


def normalise_sheet_name(sheet_name):
    return re.sub(r"\s+", " ", str(sheet_name).strip()).lower()


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
        dataframe = fetch_generation_mix_via_csv()
        print("NESO generation source selected: direct CSV")
    except Exception as csv_error:
        print(f"NESO direct CSV failed, falling back to SQL API: {csv_error}")

        try:
            dataframe = fetch_generation_mix_via_sql()
            print("NESO generation source selected: SQL API")
        except Exception as sql_error:
            raise RuntimeError(
                "Could not fetch NESO Historic GB Generation Mix from either source. "
                f"Direct CSV error: {csv_error}. SQL API error: {sql_error}"
            ) from sql_error

    dataframe = dataframe.copy()
    dataframe["year"] = dataframe["year"].astype(int)

    for column in GENERATION_COLUMNS:
        dataframe[column] = pd.to_numeric(dataframe[column], errors="coerce").round(1)

    dataframe["interval_count"] = pd.to_numeric(
        dataframe["interval_count"],
        errors="coerce",
    ).fillna(0).astype(int)

    dataframe = dataframe.sort_values("year").reset_index(drop=True)
    latest_complete_year = datetime.now(timezone.utc).year - 1
    dataframe = dataframe.loc[dataframe["year"] <= latest_complete_year].copy()
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
    excluded_terms = [
        "real terms",
        "unit cost",
        "fixed cost",
        "standing charge",
        "% change",
        "percentage change",
        "financial year",
        "economy 7",
        "fixed consumption",
    ]

    if any(term in normalised for term in excluded_terms):
        return -100

    score = 0

    if "standard electricity" in normalised:
        score += 10

    if "electricity" in normalised:
        score += 4

    if "annual" in normalised or "bill" in normalised:
        score += 2

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

    return score


def find_cash_terms_data_rows(dataframe):
    cash_terms_rows = [
        row_index
        for row_index in range(len(dataframe))
        if row_contains(dataframe, row_index, r"\bcash terms\b|\bcurrent prices?\b")
    ]

    if not cash_terms_rows:
        raise ValueError(
            "Could not find a cash-terms/current-prices section in the DESNZ sheet."
        )

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
        raise ValueError(
            "DESNZ QEP 2.2.1 cash-terms/current-prices section did not contain "
            f"enough annual bill rows. Search rows: {start_search_row}-{end_search_row}."
        )

    return data_rows, year_column


def get_desnz_workbook_sheet_metadata(workbook_bytes):
    workbook = load_workbook(
        BytesIO(workbook_bytes),
        read_only=True,
        data_only=True,
    )
    visible_sheets = []
    hidden_sheets = []

    for worksheet in workbook.worksheets:
        if worksheet.sheet_state == "visible":
            visible_sheets.append(worksheet.title)
        else:
            hidden_sheets.append(worksheet.title)

    workbook.close()
    return visible_sheets, hidden_sheets


def build_desnz_candidate_sheet_names(visible_sheets):
    candidates = []
    normalised_lookup = {
        normalise_sheet_name(sheet_name): sheet_name
        for sheet_name in visible_sheets
    }

    for preferred_sheet_name in [
        DESNZ_MAIN_SHEET_NAME,
        DESNZ_PAYMENT_METHODS_SHEET_NAME,
    ]:
        matched_sheet_name = normalised_lookup.get(normalise_sheet_name(preferred_sheet_name))

        if matched_sheet_name:
            candidates.append(matched_sheet_name)

    if not candidates:
        qep_221_sheets = [
            sheet_name
            for sheet_name in visible_sheets
            if "2.2.1" in normalise_sheet_name(sheet_name)
        ]
        raise ValueError(
            "Could not find the exact visible DESNZ QEP 2.2.1 sheet names. "
            f"Expected '{DESNZ_MAIN_SHEET_NAME}' or '{DESNZ_PAYMENT_METHODS_SHEET_NAME}'. "
            f"Visible QEP 2.2.1-like sheets: {qep_221_sheets}. "
            f"All visible sheets: {visible_sheets}"
        )

    return candidates


def parse_electricity_bill_workbook(workbook_bytes):
    visible_sheets, hidden_sheets = get_desnz_workbook_sheet_metadata(workbook_bytes)
    candidate_sheet_names = build_desnz_candidate_sheet_names(visible_sheets)
    parse_errors = []

    print(f"DESNZ visible QEP 2.2.1 candidate sheets: {candidate_sheet_names}")
    hidden_qep_sheets = [
        sheet_name
        for sheet_name in hidden_sheets
        if "2.2.1" in normalise_sheet_name(sheet_name)
    ]

    if hidden_qep_sheets:
        print(f"DESNZ hidden QEP 2.2.1 sheets ignored: {hidden_qep_sheets}")

    for sheet_name in candidate_sheet_names:
        try:
            dataframe = pd.read_excel(
                BytesIO(workbook_bytes),
                sheet_name=sheet_name,
                header=None,
                engine="openpyxl",
            )
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

            eligible_bill_columns = [
                column
                for column in bill_columns
                if column["score"] > 0
            ]

            if not eligible_bill_columns:
                labels = "; ".join(item["label"] for item in bill_columns[:8])
                raise ValueError(
                    "Could not identify a representative nominal GBP electricity bill column. "
                    f"Candidate headers: {labels}"
                )

            selected_column = max(eligible_bill_columns, key=lambda item: item["score"])
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

            parse_metadata = {
                "sheet_name": str(sheet_name),
                "selected_column_header": selected_column["label"],
                "selected_column_score": selected_column["score"],
                "year_column": str(year_column),
                "selection_note": (
                    "Selected the highest-scoring eligible column from the visible QEP 2.2.1 "
                    "cash-terms/current-prices section, preferring overall/all-consumer "
                    "UK nominal standard electricity bills."
                ),
            }

            print(f"DESNZ selected sheet: {parse_metadata['sheet_name']}")
            print(f"DESNZ selected column/header: {parse_metadata['selected_column_header']}")
            print(f"DESNZ selected column score: {parse_metadata['selected_column_score']}")

            return bills_df, parse_metadata
        except Exception as error:
            parse_errors.append(f"{sheet_name}: {error}")

    raise ValueError(
        "Could not parse the preferred DESNZ QEP 2.2.1 electricity bill sheets. "
        + " | ".join(parse_errors)
    )


def build_electricity_bill_dataframe():
    page_html = fetch_text(DESNZ_ANNUAL_BILLS_PAGE_URL)
    workbook_url = find_desnz_qep_221_workbook_url(page_html)
    print(f"DESNZ QEP 2.2.1 workbook URL: {workbook_url}")
    workbook_bytes = fetch_bytes(workbook_url)
    bills_df, parse_metadata = parse_electricity_bill_workbook(workbook_bytes)

    return bills_df, workbook_url, parse_metadata


def validate_generation_mix(dataframe):
    missing_columns = [column for column in ["year", *GENERATION_COLUMNS] if column not in dataframe.columns]

    if missing_columns:
        raise ValueError(f"Generation mix data is missing columns: {missing_columns}")

    if len(dataframe) < MIN_ANNUAL_ROWS:
        raise ValueError("Generation mix data has too few annual rows to chart.")

    generation_years = get_years(dataframe)

    if generation_years and generation_years[0] > EXPECTED_GENERATION_START_YEAR + 1:
        raise ValueError(
            "Generation mix data starts later than expected for NESO Historic GB Generation Mix. "
            f"Expected coverage around {EXPECTED_GENERATION_START_YEAR}; "
            f"found {generation_years[0]}-{generation_years[-1]}."
        )

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

    if len(dataframe) < MIN_ANNUAL_ROWS:
        raise ValueError("Electricity bill data has too few annual rows to chart.")

    if dataframe["bill_gbp_nominal"].isna().any():
        raise ValueError("Electricity bill data contains missing bill values.")

    if (dataframe["bill_gbp_nominal"] <= 0).any():
        raise ValueError("Electricity bill data contains non-positive bill values.")


def build_aligned_chart_data(generation_df, bills_df, source_metadata):
    generation_years = get_years(generation_df)
    bill_years = get_years(bills_df)
    overlap_years = sorted(set(generation_years) & set(bill_years))
    bill_source_metadata = source_metadata.get("domestic_electricity_bills", {})

    print_year_summary("Generation dataframe", generation_df)
    print_year_summary("Electricity bills dataframe", bills_df)

    if overlap_years:
        print(
            "Overlap years: "
            f"rows={len(overlap_years)}, years={overlap_years[0]}-{overlap_years[-1]}, "
            f"values={overlap_years}"
        )
    else:
        print("Overlap years: rows=0, years=none, values=[]")

    merged = generation_df.merge(bills_df, on="year", how="inner").sort_values("year")

    if len(merged) < MIN_OVERLAP_YEARS:
        raise ValueError(
            "Overlapping generation mix and electricity bill period has too few years to chart. "
            f"Required at least {MIN_OVERLAP_YEARS}; found {len(merged)}. "
            f"Generation years: {generation_years[0] if generation_years else 'none'}-"
            f"{generation_years[-1] if generation_years else 'none'}. "
            f"Bill years: {bill_years[0] if bill_years else 'none'}-"
            f"{bill_years[-1] if bill_years else 'none'}. "
            f"Overlapping years found: {overlap_years}. "
            f"DESNZ selected sheet: {bill_source_metadata.get('sheet_name', 'unknown')}. "
            "DESNZ selected column/header: "
            f"{bill_source_metadata.get('selected_column_header', 'unknown')}."
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
                "RENEWABLE_perc, LOW_CARBON_perc, ZERO_CARBON_perc, and FOSSIL_perc. "
                "Only completed calendar years are included."
            ),
            "bill_transform": (
                "Nominal GBP annual domestic standard electricity bill from DESNZ QEP 2.2.1, "
                "based on fixed consumption of 3,400 kWh/year. The parser prefers the "
                "Overall / all-consumer UK cash-terms series."
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
    print_year_summary("Generation dataframe before alignment", generation_df)
    print_year_summary("Electricity bills dataframe before alignment", bills_df)

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

    write_csv(GENERATION_MIX_CSV_PATH, generation_df)
    write_csv(ELECTRICITY_BILLS_CSV_PATH, bills_df)
    print(f"Saved {GENERATION_MIX_CSV_PATH.name}")
    print(f"Saved {ELECTRICITY_BILLS_CSV_PATH.name}")

    chart_data = build_aligned_chart_data(generation_df, bills_df, source_metadata)

    with open(CHART_JSON_PATH, "w", encoding="utf-8") as json_file:
        json.dump(chart_data, json_file, indent=2)

    print("Built green generation and domestic electricity bill data successfully.")
    print(f"Generation rows: {len(generation_df)}")
    print(f"Bill rows: {len(bills_df)}")
    print(
        "Aligned range: "
        f"{chart_data['year_range']['start']}-{chart_data['year_range']['end']}"
    )
    print(f"Saved {CHART_JSON_PATH.name}")


if __name__ == "__main__":
    main()
