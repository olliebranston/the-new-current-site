# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

**The New Current** is a static website (GitHub Pages) publishing energy transition analysis. It has no build step for the frontend — pages are pre-rendered HTML with vanilla JS + Chart.js. Data is fetched by Python scripts run on schedule via GitHub Actions and committed back to the repo as JSON/CSV files that the frontend reads directly.

## Running scripts locally

Python 3.12 is required. Install dependencies once:

```
pip install -r requirements.txt
```

Key scripts and when to run them:

| Script | Purpose |
|---|---|
| `python scripts/render_static_layout.py` | Re-inject header/footer templates into all HTML pages |
| `python scripts/fetch_live_carbon_data.py` | Pull latest carbon intensity from the Carbon Intensity API |
| `python scripts/fetch_green_generation_bills_data.py` | Fetch generation mix + domestic bills data |
| `python scripts/fetch_news_radar.py` | Scrape/aggregate energy news from RSS feeds |
| `python scripts/smoke_test_site.py` | Validate data file structure and integrity |

There is no dev server — open HTML files directly in a browser or use a local static server (`python -m http.server`).

## Architecture

### Data pipeline

GitHub Actions workflows run Python scripts on a schedule (every 30 mins for live grid data, daily for news). Each script fetches from an external API or RSS feed, transforms with pandas, and writes JSON/CSV to `data/`. The workflow then commits these files back to the repo. The frontend reads those static files at page load — there are no API routes.

Live sources: Carbon Intensity API, Elexon BMRS (prices), NESO (historic generation mix), DESNZ data portal (domestic bills). News sources: ~9 RSS feeds. All sources are documented in `docs/data-sources.md`.

### Template injection

`templates/site-header.html` and `templates/site-footer.html` are injected into every HTML page by `render_static_layout.py`. When editing the header or footer, edit the template file and re-run the script — do not edit the injected HTML in individual pages directly. The script also computes Previous/Next/Related article links and injects them into article pages based on `data/thought-pieces.json`.

### Frontend

Single JS file: `js/main.js` (~1900 lines). It loads JSON data files and renders Chart.js visualisations for carbon intensity, generation mix, power prices, and domestic bills. No framework, no state management — data is fetched at load and DOM elements are populated directly by ID.

Single CSS file: `css/styles.css`.

### Content data files

- `data/thought-pieces.json` — article metadata (title, date, author, topic, section, featured flag). Manually maintained. Used by both the template system and the frontend.
- `data/brain-dumps.json` — quick notes. Manually maintained.
- `articles/article-N.html` — individual article HTML files.

### Routing

File-based: `index.html`, `thought-pieces.html`, `data.html`, `reporting.html`, `brain-dumps.html`, `about.html`, and `articles/article-N.html`. No server-side routing.
