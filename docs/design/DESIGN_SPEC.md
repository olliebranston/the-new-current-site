# The New Current — Editorial Redesign Spec

Direction: editorial — closer to the FT / BloombergNEF than to a SaaS template.
Typography, hairline rules and whitespace do the work; boxes and shadows don't.
Keep every existing page, section, feature, photo and chart.

## Fonts

Fonts (Google Fonts, loaded with ONE @import at the top of styles.css):
- --font-serif: 'Newsreader', Georgia, serif — headlines, article body, wordmark
- --font-sans: 'IBM Plex Sans', system-ui, sans-serif — UI, navigation, meta, numbers
- Use font-variant-numeric: tabular-nums wherever numbers sit in rows/tiles.

## Type scale

Type scale (the only 8 sizes allowed):
--fs-12 kicker/caption · --fs-14 meta/nav · --fs-16 UI body · --fs-20 article body &
list titles · --fs-22 story headline · --fs-28 section heading · --fs-36 mobile
display · --fs-52 display/article H1.
Article body: serif 20px, line-height 1.6, max-width 680px.
Display: serif 500 weight, letter-spacing -0.02em, line-height 1.05.
Kicker: sans 12px, 600, uppercase, letter-spacing .06em, colour --ink-muted (NOT blue).

## Colour tokens

Colour tokens (light):
--paper #FBFAF7 · --surface #F3F1EC · --ink #16181D · --ink-2 #4A4E55 ·
--ink-muted #5C6068 · --ink-faint #6B6F76 · --rule #E4E1DA · --accent #1F45D1
Dark theme: derive equivalents (paper ~#111215, ink ~#ECEAE4, rule ~#2A2C31,
accent ~#7C9BFF); every pair must meet WCAG AA contrast.
Accent is used ONLY for links, the primary data line and active states — never for
kickers, headings or decoration.
The blue lightbulb image is the brand mark. Keep it, and keep the blue accent that ties to it.

Fuel palette (define as tokens for later; do not wire into charts in this loop):
gas #8C8F96 · wind #2E6BD9 · nuclear #7B5CC4 · biomass #4E9A63 · solar #E2B33C ·
imports #C9C4BA

## Shape and space

Shape: --radius 2px (images, buttons). No box-shadows. No gradients (including the
body background). Separation comes from 1px --rule hairlines and space; section
headers sit under a 1px --ink rule. Spacing scale 4/8/12/16/24/32/48/64.
Content width 1200px with 24px side gutters.

## Patterns

Patterns:
- Header: serif wordmark left, sans nav centre/right, "Subscribe" outlined button,
  search icon. Bookmark and theme toggle may stay but as plain icon buttons, no
  circles. Remove the floating blue back-to-top button.
- Homepage: one-line intro, then lead story (big serif headline + photo), then
  "Thought pieces" 3-up grid (photo 3:2, kicker, serif headline, date), then
  Brain dumps as a ruled list beside "From the data", then Reporting as a ruled
  newswire list (source · date | headline), then a dark ink newsletter band.
- Brain dumps & Reporting: ruled lists, NOT one card per item. Drop the "PREVIEW" label.
- Photos: keep all. Square-ish corners (2px), consistent 3:2 crop in grids,
  object-fit: cover. Page-header photo heroes become a full-width photo with the
  page title set in serif BELOW it, not overlaid.
- Topic filters: underline tabs on a hairline, not pills.
- Data page: chart cards lose shadows/gradient/dashed inner boxes; a chart sits
  on paper under a title + one-line source/units line. Big-number tiles become a
  compact row of figures with label, value and units.
- Cards, where kept (data previews): flat --paper or --surface, 1px --rule border
  or none, 2px radius, no shadow.

## Content fixes (in scope)

Content fixes (in scope):
- Homepage intro: replace the three "learning project / two halves" paragraphs with:
  "Analysis of the UK energy transition — power markets, grids and policy —
  alongside live data from the GB electricity system. By Ollie Branston."
- Byline: "Ollie Branston" everywhere (data/*.json author fields and article HTML).
- Dates displayed as "22 September 2026" everywhere. Keep ISO dates in the JSON;
  change only how they are displayed.
- Article titles: the title on each article page must match thought-pieces.json.
- Topic consolidation — update `topic` values in data/thought-pieces.json:
    Power and gas, Energy market regulation, Carbon pricing and trade, Power systems
        → "Markets and policy"
    Grid and system operation, AI and grid operations, Energy resilience
        → "Grids and operations"
    Batteries, Nuclear, CCUS → "Technology"
    Data centres, Behind-the-meter energy → "Demand"
    Archive → keep as the archive SECTION, not a topic filter
  (Brain dump tags unchanged.)

## Hard rules

Hard rules:
- js/main.js: you may ONLY edit (a) the HTML strings/templates that build cards and
  lists, and (b) date formatting. Do NOT edit any Chart.js configuration, dataset,
  colour, data-loading or fetch code. If a design change seems to need a chart
  edit, skip it and log it in docs/design/LATER.md.
- Do not edit anything in scripts/ except scripts/check_design.py, and nothing in
  .github/. Do not edit data/*.json except the byline and topic fixes above.
- Header/footer: edit templates/, then run scripts/render_static_layout.py.
- Out of scope (log ideas in LATER.md, don't do them): RSS/news feed filtering,
  image compression, Chart.js styling, new features.
