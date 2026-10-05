---
name: tnc-site-health
description: Use when Ollie asks whether The New Current site is healthy, after a push, or on a weekly check-in - checks failing GitHub Actions, stale data files, broken links/validation, oversized images, and the live site responding. Produces a short RAG status with exact fixes.
metadata:
  origin: adapted from ECC canary-watch + seo (MIT), tailored to this repo's scripts and workflows
---

# TNC Site Health

Goal: a 1-minute answer to "is anything broken or quietly rotting?" Report problems first, and don't pad with green items.

## Checks (run all, in this order)

1. **Sync:** `git pull --rebase` so local data matches what the bots committed.
2. **CI:** `gh run list --limit 30 --json name,conclusion,createdAt,headBranch` (needs the `gh` CLI. If it's missing, say so and ask Ollie to check the Actions tab). Flag any workflow whose **latest** run failed, and any scheduled workflow with no run in > 2× its cadence (comparison charts ~30 min, news radar 12h, bills monthly).
3. **Validation:** `python scripts/validate_site.py`. This covers chart JSON shape, data freshness, internal links/assets, sitemap vs canonicals and layout markers.
4. **Smoke:** `python scripts/smoke_test_site.py`.
5. **Images:** `python scripts/image_size_report.py`. List anything over 500 KB with its size. These slow the article pages, especially on mobile.
6. **Live site:** fetch `https://olliebranston.github.io/the-new-current-site/` plus the newest article URL from `data/thought-pieces.json`. Expect HTTP 200 and the article title present.
7. **SEO basics (only on request or monthly):** every page has a unique `<title>`, meta description and canonical; `robots.txt` references `sitemap.xml`; new articles appear in `sitemap.xml` and `feed.xml`.

## Output

```
TNC HEALTH - <date>
RED   <issue> - <evidence> - <fix>
AMBER <issue> - <evidence> - <fix>
GREEN <one line: everything else checked and fine>
Not checked: <anything skipped and why>
```

If something is RED, offer to fix it using `systematic-debugging`. Don't start fixing unprompted.
