# Learnings

## GitHub's scheduler is late and patchy - set freshness limits from real gaps, per workflow
- Context: site data froze 19 Sep-12 Oct; later the 6h live-grid limit kept failing although nothing was broken.
- Root cause: one stale file failed validate_site.py in every workflow, so none could save; and the 30-min cron actually fires every ~3-10h.
- Next time: when a freshness check fails, first look at real run gaps (`gh run list --workflow ...`); each workflow checks only its own files (`--fresh FILE`), and limits sit above the worst real gap.
- Seen: 2026-10-12 (dc390b82, 3b7834af)

## Many workflows saving at once - always push via scripts/push_with_retry.sh
- Context: a push touching validate_site.py started ~12 workflows; most were rejected when saving ("cannot lock ref", "fetch first").
- Root cause: only one push to main can land at a time; the losers had already rebased and didn't try again.
- Next time: any new workflow that commits ends with `bash scripts/push_with_retry.sh`, never a bare `git push`.
- Seen: 2026-10-12 (d8743393)

## Two workflows writing the same file will clash - one automatic writer per data file
- Context: after the retry fix, comparison charts still failed with a real conflict in data/live-grid-snapshot.json.
- Root cause: four older single-source workflows duplicated comparison charts and ran on the same pushes, writing the same files seconds apart.
- Next time: before adding a push or schedule trigger, check no other automatic workflow writes the same data/ file; extra copies stay manual-only.
- Seen: 2026-10-12 (c63e9d73)

## Python's test server drops connections under a real browser - raise the backlog
- Context: check_design.py failed i1/i3 once ("ERR_CONNECTION_REFUSED", data.html 10 canvases, not 12) with no site change.
- Root cause: socketserver.TCPServer's default request_queue_size is 5; Chromium opens more parallel connections, so a fetch was refused and two charts never drew.
- Next time: when a render check fails on one random page/width with a refused connection, suspect the local server first; any in-process test server sets request_queue_size = 64.
- Seen: 2026-10-20 (7c398e05, scripts/check_design.py)

## Untracking a file on a branch deletes the local copy at merge - back it up first
- Context: the redesign branch stopped tracking .claude/settings.local.json; `gh pr merge --delete-branch` then switched the local copy to main, pulled, and deleted the file.
- Root cause: main's history removes a file it used to track, so git deletes it on pull even though it's now gitignored; `gh pr merge --delete-branch` runs local git checkout/pull itself, outside Claude's git permission rules.
- Next time: before merging a branch that untracks a file, copy it out (e.g. ~/tnc-settings-backup.json) and restore after the pull; use `gh pr merge` without `--delete-branch` if the local branch switch should stay manual.
- Seen: 2026-10-20 (PR #15, 6bda0baf)

## Chart.js writes inline styles on every canvas - change charts through their config, not CSS
- Context: hiding a chart with `#carbonChart { display: none; }` did nothing, so a checker test looked like it had failed.
- Root cause: Chart.js sets `style="display:block; width; height"` on each canvas, which beats stylesheet rules (only !important overrides it).
- Next time: when styling charts (colours, gridlines, size), edit the chart options or the container's size; don't target the canvas in CSS.
- Seen: 2026-10-19 (chart-integrity check test)
