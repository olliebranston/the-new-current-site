---
name: verify-before-done
description: Use before saying any work is done, fixed, passing or ready to commit/push in this repo - runs the repo's real checks fresh and reports evidence, not assumptions. Also use when Ollie asks "is it working?" or before any git commit.
metadata:
  origin: merges obra/superpowers verification-before-completion (MIT) with ECC verification-loop (MIT), tailored for Ollie
---

# Verify Before Done

**Iron law: no completion claim without fresh evidence from this message.** "Should work", "looks right", "tests passed earlier" are not evidence. Ollie values accuracy over reassurance - an honest "2 checks fail" beats a confident "done".

## The gate

Before claiming any status:
1. **Identify** which command proves the claim.
2. **Run** it in full, now.
3. **Read** the output and exit code; count failures.
4. **Report** the actual state with the evidence, including anything skipped.

## This repo's checks

Run from the repo root. Pick the rows that match what changed; when unsure, run all of them.

| Changed | Command | Pass looks like |
|---|---|---|
| Anything | `python scripts/validate_site.py` | `Site validation passed.` |
| Anything | `python scripts/smoke_test_site.py` | exit 0 |
| Any HTML, `templates/`, `data/thought-pieces.json` | `python scripts/render_static_layout.py` then `git diff --stat` | only the expected pages change |
| `js/main.js` | `node --check js/main.js` | no output, exit 0 |
| Images in `content/` | `python scripts/image_size_report.py` | new images under the 500 KB threshold |
| Python scripts in `scripts/` | run the script once locally | runs clean and writes the expected file in `data/` |

Notes:
- `validate_site.py` includes **data-freshness** checks (live grid data must be < 6h old). Locally that fails if you haven't pulled the bot's latest data commits. Run `git pull` first. If freshness is the *only* failure, report it as "stale local data, not a code problem", but say so explicitly.
- After a push, check CI rather than assuming: `gh run list --limit 8` (if the `gh` CLI is installed) or ask Ollie to glance at the Actions tab. `site-quality`, `render-static-layout`, `update-sitemap` and `generate-rss` all trigger on content pushes.
- Visual check: for layout/CSS/JS changes, run `python -m http.server` and ask Ollie to eyeball the affected page (light and dark theme). Say that this check was manual.

## Diff review (always)

```
git status
git diff --stat
git diff
```
Check every changed file for: unintended edits, debug prints left behind, secrets or tokens (`.env`, API keys, bot tokens), files outside the agreed plan.

## Report format

```
VERIFICATION
Checks:   <command> -> PASS/FAIL (detail)
          ...
Diff:     <n> files changed - all within plan? yes/no
Not verified: <anything you could not check, and why>
Status:   READY / NOT READY
```

## Red flags

- Using "should", "probably", "seems to" about the result
- Saying "Done!" before running checks
- Trusting a subagent's success report without checking the diff
- Treating lint-pass as proof that behaviour works
