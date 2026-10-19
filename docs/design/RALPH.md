# Ralph loop instructions

You are in an iterative loop. Each iteration:
1. Read docs/design/DESIGN_SPEC.md, docs/design/TASKS.md, docs/design/PROGRESS.md
   (create it if missing), and look at docs/design/reference/*.png if present.
2. Pick the FIRST unticked task. Do only that task.
3. Start the local server (command recorded below) if it isn't running.
4. Implement the task following the spec and hard rules.
5. Run `python scripts/check_design.py`. Open the screenshots for the pages you
   touched and compare them against the spec and reference PNGs. Fix what's off.
6. A task is done only when: its pages look right in the screenshots at all three
   widths in light and dark, AND every check that applies to completed work passes
   (style checks may still fail for pages not yet reached). Chart integrity, smoke
   test, console errors and overflow must ALWAYS pass — if they fail, fix or revert
   your change before doing anything else.
7. Tick the task in TASKS.md, append 2–3 lines to PROGRESS.md (what changed, any
   compromises), and commit with a descriptive message on `redesign-editorial`.
8. If you are blocked for two iterations on the same task, write the problem in
   PROGRESS.md under "BLOCKED", tick nothing, and move to the next task.
9. When EVERY task is ticked and `python scripts/check_design.py` passes in full,
   output exactly: <promise>TNC_REDESIGN_COMPLETE</promise>
   Never output that phrase otherwise, even to discuss it.

Serve command (run from the repo root; all page, CSS, image and data paths are relative, so the repo root is the site root):

    python -m http.server 8000

Then open http://localhost:8000/index.html.

## Notes for the loop

- `scripts/check_design.py` starts its own throwaway server on a random port, so it does not need the one above. It takes about 2.5 minutes (42 page/width/theme renders) and needs internet because Chart.js loads from jsdelivr. Use `--skip-render` for a quick style-only pass while iterating, but run the full check before ticking a task.
- The canvas baseline is in `docs/design/chart-baseline.json` (index 3, data 12; this includes the doughnut charts that JS creates). Never re-record it during the redesign.
- Reference mock-ups (Homepage, Article page, Style sheet) are gitignored. If `docs/design/reference/` is empty, unzip `docs/The New Current redesign-png.zip` into it.
- Screenshots are saved as `docs/design/screens/<page>-<width>-<theme>.png`.
- `smoke_test_site.py` looks for the literal strings `.back-to-top` in styles.css and `initBackToTop` in main.js. When removing the back-to-top button, don't delete those names or the smoke check (j) will fail.
- Baseline already fails check i4: at 768px the preview captions on index and data overlap the chart. This needs fixing in the homepage or data task.
