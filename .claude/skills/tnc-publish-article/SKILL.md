---
name: tnc-publish-article
description: Use when Ollie wants to add a new interview article or thought piece to The New Current site (pastes article text, mentions "article 14", "upload the Dan Gill piece", etc.). Covers the article HTML, lead image, thought-pieces.json entry, layout render, sitemap/RSS and validation, ending in a ready-to-commit diff.
metadata:
  origin: new - encodes Ollie's existing article upload workflow (see commit b4fee64e for a reference run)
---

# Publish a New Current Article

The reference run is commit `b4fee64e` (articles 12-13). A correct publish touches roughly: `articles/article-N.html` (new), the previous article (nav only, via script), `content/article-N.jpg`, `data/thought-pieces.json`, `sitemap.xml`, `feed.xml`.

## 0. Gather inputs (ask once for anything missing, in one message)

- Article text (Ollie usually pastes it)
- Interviewee full name, and their bio paragraph
- Title, subheading, one-sentence summary (≤ 200 chars, used for meta description, OG and card)
- Topic (one, e.g. "Data centres") and 3-4 extra tags for the meta line
- Publish date (default today, Europe/London)
- Lead image file path, plus alt text
- Section: default is the current series (`series-two`). If Ollie says it starts a new series, see step 5.
- Whether a disclaimer bio line is needed (e.g. interviewee's employer requires one, as with EY)

Don't draft missing title/summary copy silently. Propose options and let Ollie choose.

## 1. Work out N

`N = highest existing articles/article-N.html + 1` (ignore `archive-article-*`). Confirm with Ollie: "This will be article-N in series-two, OK?"

## 2. Build the HTML from the latest article in the same section

Copy the most recent `articles/article-*.html` in that section as the template. **Don't hand-write the page from scratch.** Then replace, and only replace:

- `<title>`, meta description, canonical URL, all `og:*` and `twitter:*` tags (title, description, URL, image → `content/article-N.jpg`)
- JSON-LD: `headline`, `description`, `image`, `datePublished`, `dateModified`
- `data-topic` on `<article>`, lead `<img>` src and alt
- Header: kicker, `<h1>`, `.article-subheading`, `.article-meta` (`Mon YYYY · Topic · tag · tag · tag`)
- Body: intro paragraphs as `<p class="article-opening"><em>…</em></p>`; interview questions as `<h3>`, answers as `<p>`; bios as `<p class="article-bio"><em>…</em></p>`. Escape `&` as `&amp;`.

Leave the header/footer injected blocks and the `<!-- article-navigation:start -->` block alone. The render script regenerates them.

**Text fidelity:** keep the interviewee's words as given. Fix obvious typos only, and list every change you made for Ollie. If you spot a statistic or factual claim that looks wrong or unsourced, flag it (the account-level `energy-fact-check` skill can run a full check) but don't change it silently.

## 3. Lead image

- Save as `content/article-N.jpg`, **lowercase `.jpg`** (GitHub Pages is case-sensitive, and `.JPEG` broke the about page once).
- Images on this site have been 1.5-4.7 MB, against the repo's own 500 KB threshold. Resize before committing:

```python
from PIL import Image
im = Image.open(SRC).convert("RGB")
im.thumbnail((1600, 1600))
im.save("content/article-N.jpg", "JPEG", quality=82, optimize=True, progressive=True)
```
Then run `python scripts/image_size_report.py` and confirm it's under threshold.

## 4. thought-pieces.json entry

Append to `articles` in `data/thought-pieces.json`, matching existing fields exactly:

```json
{
  "title": "<Interviewee> on <subject>",
  "author": "Oliver Branston with <Interviewee>",
  "date": "YYYY-MM-DD",
  "topic": "<Topic>",
  "summary": "<summary>",
  "link": "articles/article-N.html",
  "image": "content/article-N.jpg",
  "section": "series-two",
  "featured": false
}
```

`featured` only adds a "Featured" badge on the card. The hero slot is always the newest article. Ask Ollie whether this one gets the badge.

## 5. New series only

If this is the first article of a new section, add it to `CROSS_SECTION_PREVIOUS` in `scripts/render_static_layout.py` (`"articles/article-N.html": "articles/article-<last of previous section>.html"`) and make sure the section key is handled wherever sections are listed on `thought-pieces.html` / `js/main.js`. This is the article-9 CI failure. Don't repeat it.

## 6. Regenerate

```
python scripts/render_static_layout.py
python scripts/generate_sitemap.py
python scripts/generate_rss.py
```

`git diff --stat` should show the new article, a small nav change on the previous article, the JSON, sitemap, feed and the image. Anything else needs an explanation.

## 7. Verify and hand over

Run `verify-before-done`. Then give Ollie:
- the diff summary
- a proposed commit message: `Add article-N: <Interviewee> on <subject>`
- the live URL it will have: `https://olliebranston.github.io/the-new-current-site/articles/article-N.html`

Don't commit or push unless Ollie asks. After he pushes, check the Actions runs (`gh run list --limit 8`) and that the live URL returns 200 after a few minutes.

## 8. Distribution prompt

End by reminding Ollie he can run `linkedin-repurpose` in Cowork/claude.ai on the published URL to draft LinkedIn and Substack posts.
