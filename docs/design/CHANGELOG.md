# Editorial redesign — changelog

Branch: `redesign-editorial` (not merged, not pushed). Spec: `DESIGN_SPEC.md`. Per-iteration notes: `PROGRESS.md`. Deferred items: `LATER.md`.

Final state: `python scripts/check_design.py` passes 14/14 (style rules a–f, byline g, dates h, console/overflow/chart integrity/overlap i1–i4, smoke test j, template sync k) across 7 pages × light/dark × 1440/768/390.

## Design system (`css/styles.css`)

- **Tokens.** New `:root` and `[data-theme="dark"]` palettes from the spec (paper, surface, ink, ink-2, ink-muted, ink-faint, rule, accent), plus `--fuel-*` tokens (defined, not yet used by charts), `--band-*` for the newsletter band, `--overlay` for modal scrims, `--focus-ring`, a 4–64px spacing scale, `--page-width` 1200px, `--gutter` 24px and `--article-width` 680px. The old token names (`--bg-*`, `--text-*`, `--brand-blue*`) now alias the new palette.
- **Type.** One Google Fonts `@import` (Newsreader + IBM Plex Sans). Serif for headlines, article and note bodies and the wordmark; sans for UI, navigation, meta and numbers; `tabular-nums` on figures. Exactly 8 sizes (`--fs-12` … `--fs-52`); all 102 old font-size declarations were mapped onto them. Kickers are sans 12/600 caps in `--ink-muted` (no longer blue).
- **Shape.** No box-shadows (focus states use the focus-ring token), no gradients (including the body background), every radius is `var(--radius)` (2px), `0` or `50%` for dots. Separation now comes from 1px rules and space; section headers sit under a 1px ink rule (`.section-header`).
- **Dark mode** follows the tokens throughout; the only dark-specific rules left are the canvas brightness filter and the theme-icon swap. A one-off WCAG AA audit of all rendered text on all 7 pages in both themes found 0 failures.
- **Print** redefines the colour tokens so pages print black on white, including from dark mode.

## Header and footer (`templates/`, then `render_static_layout.py`)

- Header: serif ink wordmark, centred sans nav in sentence case with an accent underline on the active page, plain borderless icon buttons (search, library, theme), and an outlined **Subscribe** → Substack button replacing the blue Contact pill. Below 560px Subscribe moves into the menu. The ⌘K hint is removed and the dark-mode sun icon now renders as a sun.
- Footer: wordmark + one-line description, then Read / Track / Elsewhere columns (Contact, RSS and About kept) and a single "Built by Ollie Branston. © year" line.
- The floating blue back-to-top button is hidden (`.back-to-top { display: none }`). Its JS and selector stay because the smoke test expects them.

## Pages

- **Homepage.** The spec's one-line intro replaces the three "learning project / two halves" paragraphs. Then: the lead story (kicker, 52px serif headline, serif standfirst, byline and date, 3:2 photo); a "Thought pieces" 3-up story grid; Brain dumps as a ruled list beside "From the data" (the three existing gateway charts as ruled rows); Reporting as a newswire list (source · date | headline); "Why this site exists"; and a full-width dark newsletter band.
- **Section pages** (thought pieces, brain dumps, data, reporting, about): the overlaid photo hero is now a full-width photo with the serif title below it.
- **Thought pieces.** Underline topic tabs on a hairline (instead of pills), a flat search box, a ruled newsletter strip, and story cards in a 3/2/1-column grid grouped under Series two / Series one / Archive.
- **Articles.** A CSS-grid layout: header (kicker · topic link, serif 52 H1, italic standfirst, byline, tags) → ruled reading-time/Save/Copy-link row → full-width photo → sticky Contents column beside a 680px serif 20/1.6 body. Previous / Related links sit under an ink rule, followed by a ruled "Stay in the loop" strip.
- **Brain dumps.** A ruled list of notes: date and tag on the left, serif title and full note on the right. The "Brain Dump" and "PREVIEW" labels are gone.
- **Data.** Flat chart rows: kicker, title, description and a new one-line units/source note above each full-width chart. The live big-number tiles are now a compact four-figure row with the generation-mix doughnut below it. The "Three ways in" previews have fixed-height chart boxes, which fixed the pre-redesign text-over-chart overlap (i4).
- **Reporting.** "Editor's picks" are two ruled columns; News radar is a newswire list under R&D / Policy subheadings.
- **About.** Flat editorial layout: intro beside the lightbulb photo (kept here after it left the homepage), the site guide as four ruled columns, plain-text context blocks, an author block with plain LinkedIn/Substack links. "Contact button in the top right" now reads "Contact link at the bottom of every page".
- **Phones.** Tighter vertical rhythm and 40×40 header tap targets.

## Content and data

- **Byline:** "Ollie Branston" everywhere. Changed the 17 `author` values in `data/thought-pieces.json`; every article header now has a byline ("**Ollie Branston** with X · 22 September 2026"); removed the JSON-LD `alternateName: "Oliver Branston"`.
- **Dates** display as "22 September 2026" via `formatDisplayDate()` in `main.js` (cards, lists, radar, palette, history, and "Last updated" stamps such as "12 October 2026, 20:46 UTC"). ISO dates in the JSON are unchanged.
- **Topics** consolidated in `thought-pieces.json`: Markets and policy (5), Grids and operations (4), Technology (3), Demand (2). The 3 archive pieces have an empty topic and live only in the Archive section. Article `data-topic` attributes were updated to match, and related links re-rendered.
- **Titles:** article-8 and article-14 H1s now match the JSON (they had "1:/2:" series numbering).

## Review round (after the loop)

- Accent changed to match the lightbulb brand mark: #0053BD (light), #5AA9F7 (dark), with matching hover and tints. The lightbulb is recorded as the brand mark in CLAUDE.md and DESIGN_SPEC.md and now sits beside the newsletter band text on the homepage.
- Homepage: the intro line is removed; a single ink rule runs above the lead headline and its 4:3 photo; brain dumps (two-column list) and "From the data" (3-up with source lines) are full-width sections; "Why this site exists" runs in two columns; a live grid ticker sits under the header (live-grid-snapshot.json).
- Section heroes are 2:1 on desktop with a focal point per photo; in-page links stop below the sticky header; article topic links scroll to the filtered list; nav is 16px ink; article byline and actions read as one ruled band; topic tabs wrap on phones; subscribe buttons and Substack links turn Substack orange on hover.
- Fixes: the "Saved" tab now works; RSS author and archive category; JSON-LD alternateName restored (with a narrow check g exception); "(Part 1)/(Part 2)" series titles; check_design.py's local server backlog raised to stop flaky page loads.
- Reference PNGs removed from the branch (kept locally in ~/tnc-design-reference/) so they don't enter main's history; merge with a squash.

## What did not change (hard rules)

- No Chart.js configuration, dataset, colour, data-loading or fetch code in `js/main.js`. Only card/list HTML templates and date formatting changed. Canvas counts match the pre-redesign baseline (`chart-baseline.json`).
- Nothing in `scripts/` except the new `check_design.py`, which was not edited during the loop. Nothing in `.github/`. Only `data/thought-pieces.json` was edited (byline + topic lines).

## Open items (see LATER.md for detail)

- Chart.js styling still uses the old blue and default legend and grid colours; the fuel tokens aren't wired in yet.
- Pre-existing bug: the "Saved" tab on Thought pieces always shows nothing. It's a one-line filter-logic fix, which this loop wasn't allowed to make.
- Reference items that need new features or data wiring: the live grid strip under the header, and a single 24-hour carbon-intensity chart with a fuel legend on the homepage.
- Decisions for Ollie: whether to restore the JSON-LD `alternateName`; the series numbering on the two agentic-AI headlines; the "… Thought Piece" suffix on archive titles; and whether the reference PNGs in `docs/design/reference/` should be removed before merging (they'd be published by GitHub Pages).
- RSS: `feed.xml` and `generate_rss.py` still default to "Oliver Branston", and archive items will get an empty `<category>`.
- Contrast: light `--ink-faint` on `--surface` is 4.47:1. It isn't currently used that way, but it shouldn't be.
