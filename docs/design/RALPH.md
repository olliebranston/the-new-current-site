# Ralph loop instructions

You are in an iterative loop. Each iteration:
1. Read docs/design/DESIGN_SPEC.md, docs/design/TASKS.md, docs/design/PROGRESS.md
   (create it if missing), and look at docs/design/reference/*.png if present
   (home.png = homepage, article.png = article page, style-sheet.png = type/colour sheet).
2. Pick the FIRST unticked task. Do only that task.
3. Do not start a server; check_design.py runs its own.
4. Implement the task following the spec and hard rules.
5. Run `python scripts/check_design.py`. Open the screenshots for the pages you
   touched and compare them against the spec and reference PNGs. Fix what's off.
6. A task is done only when: its pages look right in the screenshots at all three
   widths in light and dark, AND every check that applies to completed work passes
   (style checks may still fail for pages not yet reached). The MUST-ALWAYS-PASS checks
   are: i1 console errors, i2 overflow, i3 chart integrity, j smoke test and
   k templates in sync. If any of them fails, fix or revert your change before doing
   anything else.
   i4 (text overlapping a chart) already fails on the pre-redesign baseline: at 768px
   the preview captions on index.html and data.html sit over the chart. It is NOT a
   blocker for earlier tasks, but it MUST pass before the "Data page" task is ticked
   (and must stay passing afterwards).
7. Tick the task in TASKS.md, append 2–3 lines to PROGRESS.md (what changed, any
   compromises), and commit with a descriptive message on `redesign-editorial`.
8. If you are blocked for two iterations on the same task, write the problem in
   PROGRESS.md under "BLOCKED", tick nothing, and move to the next task.
9. When EVERY task is ticked and `python scripts/check_design.py` passes in full,
   output exactly: <promise>TNC_REDESIGN_COMPLETE</promise>
   Never output that phrase otherwise, even to discuss it.

## Rules the loop must not bend

- Stay on branch `redesign-editorial`. Never push, merge, rebase, reset --hard or switch branch.
- Never edit `scripts/check_design.py` (or anything in `scripts/` or `.github/`). If a
  check is hard to pass, fix the site or log it in docs/design/LATER.md. Never weaken a check.
- js/main.js: only card/list HTML strings and date formatting. Never Chart.js config,
  datasets, colours or data loading.
- data/: only `data/thought-pieces.json` and `data/brain-dumps.json`, and only for the
  byline and topic fixes. Every other data file is blocked by permissions.
- To undo a change to a file, use `git restore <file>` (not checkout).

## Notes

- check_design.py takes about 2 minutes (42 page/width/theme renders) and needs
  internet, because Chart.js loads from jsdelivr. Use `--skip-render` for a quick
  style-only pass while iterating, but run the full check before ticking a task.
- The canvas baseline is in `docs/design/chart-baseline.json` (index 3, data 12; this
  includes the doughnut charts that JS creates). Never re-record it.
- Screenshots are saved to `docs/design/screens/<page>-<width>-<theme>.png` (gitignored).
- `smoke_test_site.py` looks for the literal strings `.back-to-top` in styles.css and
  `initBackToTop` in main.js. When removing the back-to-top button, keep both names
  (e.g. hide the button) or check j will fail.
- Chart.js puts an inline `style="display:block"` on every canvas, so a plain CSS rule
  can't hide or resize a chart. Don't fight it with `!important`.

Serve command, for humans only (run from the repo root; all paths are relative):

    python -m http.server 8000      →  http://localhost:8000/index.html
