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
