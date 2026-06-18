# Project Context: The New Current

## What this project is

**The New Current** is a static website publishing energy transition analysis and live UK grid data. It is built and maintained by **Ollie Branston** and lives at [olliebranston.github.io/the-new-current-site](https://olliebranston.github.io/the-new-current-site/).

This file exists to give Claude (both Claude.ai planning sessions and Claude Code implementation sessions) persistent context about the project's purpose, priorities, and direction so that suggestions are always grounded in what this site is actually for.

---

## Owner background

Ollie has worked in the UK energy sector — first at an energy data analytics start-up, now at a consultancy. He has intermediate coding ability: comfortable reading and editing HTML/CSS/JS and Python, but not a professional developer. He is building this site using AI-assisted coding (Claude, previously ChatGPT) and learning by doing. When suggesting code, always explain what it does and why.

---

## Primary goals

1. **Personal brand and professional positioning** — The site should demonstrate Ollie's depth of knowledge in the energy transition and establish him as a credible commentator. The target audience includes energy industry professionals, policy people, and non-specialists genuinely curious about net zero. It is explicitly *not* trying to be neutral: Ollie writes with a point of view.

2. **AI-native credentials** — The site itself should demonstrate that Ollie is comfortable working with AI tools, both in how it is built and potentially in features it exposes to users (e.g. an AI agent trained on site content). This matters for the career outcome below.

3. **Career outcome** — The site is a long-game asset aimed at landing a role at a climate/energy start-up, or positioning Ollie credibly in that space. Recruiters and colleagues are a secondary but real audience — the site should look polished and serious.

---

## Secondary goals

- **Learning** — Building and iterating on this site is how Ollie is developing his coding skills. Explanations matter as much as solutions.
- **Showing range** — The combination of original writing (Thought Pieces, Brain Dumps) and live data dashboards (Data page) is intentional: it demonstrates both analytical thinking and technical capability.
- **Substack growth** — The site should drive newsletter subscriptions. A Substack subscribe button/widget on the Thought Pieces page is a planned addition.

---

## Audience

**Primary:** Energy industry professionals and engaged non-specialists interested in the UK energy transition. Content must be accessible without being dumbed down — the goal is to be insightful to experts and illuminating to newcomers simultaneously.

**Secondary:** Colleagues, recruiters, and potential employers — particularly at climate start-ups. The site should read as evidence of both domain expertise and technical initiative.

---

## Editorial direction

- Thought pieces published roughly **fortnightly**
- Brain dumps published **occasionally** (lower-stakes, more reactive)
- Ollie writes **with a point of view** — this is not a neutral aggregator
- Tone should be: knowledgeable, direct, accessible, occasionally opinionated
- Content topics: UK energy transition, grid data, power markets, domestic bills, policy, clean energy technology

---

## Planned features (not yet built)

These are known future directions — Claude should be aware of them to avoid suggesting architecture that closes them off:

1. **AI agent / chatbot** — An AI assistant trained (or prompted) on the site's content, ideally using the free tier of OpenRouter's API. The intent is for users to ask questions and get answers grounded in Ollie's published analysis.

2. **Expanded data metrics** — Thought pieces reference specific metrics (e.g. carbon intensity, generation mix, price data). The plan is to build these out as live, embedded visualisations tied to the relevant articles or a dedicated metrics section.

3. **GitHub Actions health monitoring** — Some kind of dashboard or routine (possibly a page or a notification mechanism) that surfaces whether the scheduled data-fetch workflows have run successfully. The data pipeline is critical — silent failures are a real risk.

4. **Substack subscribe button** — A call-to-action on the Thought Pieces homepage (`thought-pieces.html`) allowing readers to subscribe to the Substack newsletter directly from the site.

---

## How to work with Ollie

- **Be direct.** If an approach has a flaw, say so upfront — don't bury it.
- **Explain code changes** — what the change does and why, not just what to paste in.
- **Flag downstream consequences** — always note if a change requires running `render_static_layout.py`, or if a GitHub Actions workflow will be affected.
- **Simplest solution first** — no clever abstractions. Minimum viable, then iterate.
- **Step-by-step problem solving** — agree a plan before touching code. Don't try to solve everything at once.
- **Don't be positive for the sake of it** — Ollie prefers candour over reassurance.

---

## Key architectural constraints to keep in mind

- No build step, no framework — pure HTML/CSS/vanilla JS
- All data is static JSON/CSV written to `data/` by Python scripts; the frontend reads it at page load
- Header and footer live in `templates/` and are injected by `scripts/render_static_layout.py` — **never edit injected HTML directly in individual pages**
- `js/main.js` is a single ~1900-line file; CSS is a single `css/styles.css` — keep it that way unless there is a strong reason to split
- GitHub Pages hosting means no server-side logic, no API routes, no environment variables exposed to the frontend
- OpenRouter (free tier) is the intended API for any AI features — not OpenAI directly

---

## File reference

| File / Directory | Purpose |
|---|---|
| `js/main.js` | All frontend JS — Chart.js visualisations, data loading, DOM manipulation |
| `css/styles.css` | All styles |
| `templates/site-header.html` | Shared header (edit here, not in pages) |
| `templates/site-footer.html` | Shared footer (edit here, not in pages) |
| `data/thought-pieces.json` | Article metadata — manually maintained |
| `data/brain-dumps.json` | Brain dump metadata — manually maintained |
| `articles/article-N.html` | Individual article HTML files |
| `scripts/render_static_layout.py` | Injects header/footer and article nav into all pages |
| `scripts/fetch_live_carbon_data.py` | Fetches carbon intensity data |
| `scripts/fetch_green_generation_bills_data.py` | Fetches generation mix + bills data |
| `scripts/fetch_news_radar.py` | Aggregates energy news from RSS feeds |
| `scripts/smoke_test_site.py` | Validates data file structure |
| `docs/data-sources.md` | Documents all external data sources |