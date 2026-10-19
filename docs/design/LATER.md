# Later

Open items after the editorial redesign, roughly in priority order. Each has a minimum viable version.

## Open — design

1. **Chart.js styling.** Chart lines, legends and grids still use the pre-redesign blue (#2457ff-ish), boxed legends and default grid colours; the generation-mix doughnut uses its own palette (its near-black gas segment almost vanishes in dark mode). MVP: in each chart config, set the primary line to `--accent`, gridlines to `--rule`, legend boxes off, and map doughnut segments to the `--fuel-*` tokens.
2. **Homepage 24-hour carbon chart.** The reference shows one 24-hour carbon-intensity chart with a latest-value label and a fuel-mix legend, in place of the three gateway previews. MVP: a smaller instance of the Data page's carbon chart with the fuel tokens as its legend.
3. **Section hero photos.** Now 2:1 on desktop with a focal point per photo; phones are unchanged. Revisit whether to show each photo whole (e.g. 3:2 beside the title) instead of cropping.
4. **Brain-dump deep links.** Notes have no per-note anchors, so homepage rows all link to brain-dumps.html. MVP: add an `id` per note in the page template and link to `brain-dumps.html#note-id`.

## Open — clean-up

- **Back-to-top:** hidden with CSS, but main.js still builds it (`initBackToTop`). Remove the function and the two back-to-top lines in `scripts/smoke_test_site.py` CONTENT_CHECKS together.
- **Data page source lines** (`.data-chart-source`, `.data-gateway-source`) are hand-written from data/*.json metadata and docs/data-sources.md. If a fetch script changes source, update the line, or render it from each JSON's metadata.
- **Archive titles** in thought-pieces.json end in "… Thought Piece" (e.g. "UN Gender Bond Thought Piece"). Trim in the JSON and the article pages together, then re-run render_static_layout.py.
- **Contrast:** light `--ink-faint` (#6B6F76) on `--surface` is 4.47:1 (AA needs 4.5). It isn't used that way today; either darken ink-faint slightly or keep it off surface.
- **Ticker freshness:** the homepage ticker shows `live-grid-snapshot.json`, which GitHub's scheduler updates every ~3–10 hours, not live. Consider a "data is X hours old" note when it's stale.

## Done (resolved after the loop, Oct 2026)

- "Saved" tab always empty — fixed in `filterArticles` (topic match no longer fails while Saved is on).
- JSON-LD `alternateName: "Oliver Branston"` restored; check g allows exactly that field inside JSON-LD.
- RSS: `generate_rss.py` defaults to "Ollie Branston" and gives archive items the category "Archive"; feed.xml regenerated.
- Agentic-AI series titles: "(Part 1)" / "(Part 2)" now in the JSON and the pages.
- Live grid ticker under the homepage header (built from live-grid-snapshot.json, fuel-mix bar uses the `--fuel-*` tokens).
- Accent matched to the lightbulb brand mark (#0053BD light, #5AA9F7 dark).
