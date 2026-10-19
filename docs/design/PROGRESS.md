# Progress

## Iteration 1 — Tokens
- Rewrote :root and [data-theme="dark"] with the spec palette, fuel tokens (unused), --font-serif/--font-sans, --radius, --focus-ring, spacing and width tokens; added the single Google Fonts @import; body background is now flat var(--paper) (gradient removed in both themes).
- Legacy token names (--bg-*, --text-*, --border-*, --brand-blue*) now alias the new palette so every page picks it up; shadow/radius legacy tokens left as-is for the "remove shadows/radii" task. --max-width is now 1200px.
- Compromise: spec's light --ink-faint (#6B6F76) on --surface is 4.47:1, just under AA — logged in LATER.md; avoid ink-faint text on surface.

## Iteration 2 — Global type
- Added the 8 --fs- tokens (rem-based: 12/14/16/20/22/28/36/52px) and mapped all 102 font-size declarations onto them (nearest size, with semantic overrides: story card h3 → 22, brain-dump h3 → 20, lead headline → 28, display H1s → 52 desktop / 36 mobile; print pt sizes mapped too). Checks e and f now pass.
- body → var(--font-sans) 16/1.55; h1–h3 → var(--font-serif) 500; h4 stays sans 600; wordmark serif 600; kickers sans 12/600/caps/.06em in --ink-muted (no longer blue); number tiles sans 600 tabular-nums. Fixed .article-content p overriding the article kicker size.
- Compromise: article body is still sans 16px. The serif 20px/680px body is left for the Article pages task.

## Iteration 3 — Shadows, gradients, radii
- All 23 box-shadows → none (focus states → var(--focus-ring)); all 15 gradient backgrounds → var(--paper), decorative glow/sheen pseudo-elements → none; all 70 radii → var(--radius), with status dots → 50% and the nav underline/progress bar → 0. Removed the --shadow-* and --radius-sm/md/lg/xl tokens. Checks b, c, d now pass.
- Compromise: the page-hero photo scrim became a flat var(--scrim) (rgba token) so overlaid titles stay readable until the page-header tasks move titles below photos. Floating panels (cmd palette, history, mobile nav) rely on their existing 1px borders.

## Iteration 4 — Header + footer
- Header template: ink serif wordmark, centred sans nav in sentence case (accent underline on the active page), plain borderless icon buttons (search, library, theme; ⌘K hint removed; sun icon now stroked so it renders in dark mode), outlined "Subscribe" → Substack replaces the blue "Contact" pill. Below 560px the Subscribe button moves into the hamburger menu (fixes 390px overflow).
- Footer template follows the reference: wordmark + one-line description, Read / Track / Elsewhere columns (Contact, RSS feed and About kept under Elsewhere), single "Built by Ollie Branston. © year" line. Removed the dark-mode header/footer overrides (tokens handle it). Re-rendered all pages.
- Not done: the reference's live grid strip under the header needs new data-loading JS → logged in LATER.md.

## Iteration 5 — Back-to-top button
- Replaced the floating blue back-to-top styles with `.back-to-top { display: none; }`. Verified after scrolling at 1440 and 390: JS still adds `.visible`, but the button renders 0×0 and is out of the tab order.
- Compromise: main.js still creates the button (initBackToTop). Removing that call is outside the allowed main.js edits, and the smoke test expects both `initBackToTop` and the `.back-to-top` selector, so the button is hidden rather than deleted. Logged in LATER.md.

## Iteration 6 — Homepage intro + lead story
- index.html: the hero card (eyebrow, "The New Current" H1, three "learning project / two halves" paragraphs, logo image) is replaced by the spec's one-line intro and a lead-story section. The H1 is kept for screen readers (.sr-only). The thought-pieces container moved into the lead section, and its "Thought Pieces / View all" header now comes from the card template.
- main.js (card HTML template only, renderHomepageThoughtPieces): the latest piece renders as kicker "Latest · {topic}", a serif 52px headline, a serif 20px standfirst, a meta line and a 3:2 photo on the right; it stacks below 900px (headline 36px). The two "Recent" cards stay as a temporary 2-up row for the next task. Removed the home-hero/featured-thought CSS and the unused heroSheen animation.
- Compromise: the blue lightbulb photo (content/home-logo.jpg) no longer appears on the homepage, matching the reference. It's still the favicon and the social preview image. The reference's "[Caption: place, year]" isn't shown because there's no caption data.

## Iteration 7 — Homepage sections
- Homepage now follows the reference after the lead story: a "Thought pieces" 3-up story grid (3:2 photo, topic kicker, serif 22 headline, date · co-author), Brain dumps as a ruled list (4 latest, "PREVIEW" label and excerpt dropped) beside "From the data", Reporting as a ruled newswire list (source · date | headline, news first then recommended listen/read), "Why this site exists" as plain text, and a full-width dark ink newsletter band ("A new thought piece every fortnight" → Subscribe on Substack) above the footer. New shared patterns: .section-header (serif title under a 1px ink rule + accent link), .story-grid/.story-card, .ruled-item, .newswire-item.
- "From the data" keeps all three existing gateway charts (same canvases and ids, no chart code touched), restyled as ruled rows with the text on the left and a fixed 180px chart on the right. This also fixes the homepage half of i4. Removed the old compact/preview card CSS, the eyebrow section headings and the dark-mode gateway background.
- Compromises: the band uses --band tokens (dark ink in light mode, near-black surface in dark mode rather than inverting to light). Brain-dump rows link to brain-dumps.html because there are no per-note anchors. The reference's single "carbon intensity, last 24 hours" chart + mix legend would need chart changes → LATER.md.

## Iteration 8 — Thought pieces page
- Page header (shared .page-hero on thought pieces, brain dumps, data, reporting and about): the overlaid white title with its dark tint is now a full-width 2px-radius photo (clamp 220–400px) with the serif title set below it. Removed the --scrim token. The thought-pieces H1 is now sentence case.
- Topic filters (shared .tp-filter-chip, so brain dumps too) are underline tabs on a hairline: ink underline on the active tab, wrapping on desktop and side-scrolling below 700px. The search box is flat with a 1px rule. The newsletter prompt is a ruled strip with an ink "Subscribe on Substack" button instead of the orange button on a blue box.
- main.js card/section templates: each piece is a .story-card in a 3/2/1-column .story-grid (photo 3:2, "Featured · topic" kicker with bookmark and read badge, serif headline, 3-line summary, date · co-author), under section headers ("Series two", "Series one", "Archive"). Checked that topic filter, search and bookmarking still work.
- Found a pre-existing bug: the "Saved" tab always shows "No saved articles" because the topic match fails while Saved is on. It's filter logic, so I haven't touched it; logged in LATER.md.

## Iteration 9 — Article pages
- CSS only (no article HTML or JS changes). .article-content is now a grid: header (kicker · accent topic link, serif 52 H1, italic serif standfirst, sans meta) → ruled byline/actions row (reading time | Save, Copy link as plain text buttons) → full-width 2:1 photo (3:2 on mobile) → a sticky "Contents" column (220px, ruled list, active item bold) beside a 680px serif 20/1.6 body. Grid `order` moves the photo below the header because the HTML has it first. Opening paragraph is serif 22, roman not italic; h2 serif 28, h3 sans 16/600; links underlined; bios italic 16 under a hairline; pull quote and footnotes restyled.
- Prev/next and related links sit under a 1px ink rule (caps labels, underlined serif titles); "Stay in the loop" is a ruled strip with an ink button, aligned to the body column. Below 1000px it's one column (max 680px) with the contents list inline after the opening.
- Compromise: the reference byline row reads "Ollie Branston with X · date · min read". Article pages don't have the author in their HTML, so the row shows reading time + actions, and month + tags stay in the meta line. Adding the byline text is part of the byline task.

## Iteration 10 — Brain dumps page
- Notes are a ruled list instead of bordered cards: a 220px left column with the date and a small-caps tag, then the serif 28 title and the full note in serif 20/1.6 at 680px. There's a 1px ink rule at the top of the list and hairlines between notes; below 900px the date and tag sit inline above the title. The redundant "Brain Dump" kicker is gone (the homepage "PREVIEW" label was already dropped in iteration 7). H1 is now sentence case.
- main.js: only the two note templates changed (initBrainDumpsPage, plus the unused renderBrainDumps). Checked that tag tabs (5 → Gas 1) and search still filter. The copy button (only in the unused renderer) is restyled as a plain text button.

## Iteration 11 — Data page (i4 now passes)
- Chart cards lost their borders, backgrounds, hover lift and dashed inner boxes. Each chart sits on paper under its kicker, a serif 22 title, the description and a new one-line units/source line (.data-chart-source, written from the data files' metadata and the axis titles in data.html). Charts run full width at 360px (300px below 900px), with hairlines between rows. Section headings sit under a 1px ink rule; "Last updated" is plain meta text instead of a pill.
- "Three ways into the data" gateway: flat 3-up previews with fixed 200px chart boxes. This fixes i4: the old fixed grid rows let the chart's margins push into the caption. Live GB dashboard: the four big-number tiles are a compact figure row (label, 36px tabular value, unit) with hairline dividers, 2×2 below 900px; the generation-mix doughnut sits full width below. No Chart.js config, dataset, colour or data-loading code was touched; canvas counts unchanged (i3).
- Removed the old data-page, card and pill CSS plus the unused .data-preview-*/.data-future-grid rules. Also fixed the CSS clean-up helper, which had silently skipped selectors matched with a `^` anchor.
- Compromise: the source lines are hand-written into data.html, so they won't change automatically if a data source changes (see LATER.md).

## Iteration 12 — Reporting page
- News radar items reuse the homepage newswire row: "source · date" on the left, sans 16/500 headline on the right, hairline between rows, stacked below 900px. In main.js only buildRadarArticle's markup changed (meta first, newswire classes; the radar-item class is kept). R&D and Policy are serif 22 subheadings over a hairline; "Show N more" is a plain accent text button.
- reporting.html: "Editor's picks" and "News radar" are serif section headers under the 1px ink rule (News radar has "Last updated" as meta text on the right). The two recommendations are flat ruled columns: kicker, serif 22 title, source, description (one column below 900px). Removed the old reporting/recommendation/radar card CSS and the 16px grid gap between radar rows.

## Iteration 13 — About page
- Flattened every card. The intro is a 7/5 grid (kicker, serif 36 statement, serif 20 body | the lightbulb photo at 3:2, which keeps that photo on the site). "What you will find here" and "Project context" sit under 1px ink rules; the site guide is four ruled columns (2 below 900px, 1 below 560px) with serif 22 titles; the context blocks and "About me" are plain serif 20/1.6 text at 680px with hairlines between them. The author photo is 220px at 4:5, and LinkedIn/Substack are plain accent links instead of brand-coloured pills (removes two literal colours).
- Copy fix: "contact button in the top right" → "Contact link at the bottom of every page", since the header Contact button became Subscribe in iteration 4.

## Iteration 14 — Byline and date format (checks g and h now pass)
- Byline: the 17 `author` values in data/thought-pieces.json now read "Ollie Branston…" (byte-level replace, nothing else changed). The JS fallbacks and co-author regex are updated. Every article header gets a byline line from the JSON ("**Ollie Branston** with X · <time>22 September 2026</time>"), and the abbreviated "Sep 2026 ·" is dropped from the tag meta line. Removed `"alternateName": "Oliver Branston"` from the JSON-LD on index.html and about.html (see LATER.md).
- Dates: a new formatDisplayDate() renders "22 September 2026" everywhere. Date-only ISO strings are read in UTC so they can't shift a day; timestamps use Europe/London. It covers story cards, the lead story, brain dumps (homepage and page), radar and homepage newswire rows (from published_at, so "8 October" not "08 October"), the command palette and history panel, and both "Last updated" stamps ("12 October 2026, 20:46 UTC"). The ISO dates in the JSON are unchanged.

## Iteration 15 — Topic consolidation
- data/thought-pieces.json `topic` values mapped per the spec (byte-level, topic lines only): Markets and policy 5, Grids and operations 4, Technology 3, Demand 2. The 3 archive pieces now have `"topic": ""`, so they stay in the Archive section (`section: "archive"`) but no longer produce an "Archive" tab, because the tab builder skips empty topics. The topic tabs now fit on one row: All · Saved · Demand · Grids and operations · Markets and policy · Technology.
- Article pages: updated each `data-topic` to match, and removed it on archive pages (render_static_layout only adds the attribute when it's missing, so it would otherwise go stale). Ran render_static_layout.py: related links on 13 articles changed because they rank by same topic, and those changes are committed so check k passes.
- Verified in a browser: each tab filters correctly (5/4/3/2), "All" shows 17 in Series two / Series one / Archive, the article topic chip links to the new topic URL and opens with that tab active, and archive articles show no chip.

## Iteration 16 — Article title consistency
- Compared every article's H1 and <title> with thought-pieces.json: 15 of 17 already matched. Two H1s carried series numbering not in the JSON: article-8 ("…grid operators 1: The governed data core") and article-14 ("…grid operators 2: Achieving growth"). Both H1s now use the JSON title; <title>/og:title already matched. All 17 now match, and render_static_layout reports no changes.
- Compromise: the JSON title wins because the loop may only edit the JSON byline and topic fields, and the reference mock-up uses the JSON wording. The "Part 1/2" series cue is lost from those two headlines → LATER.md.

## Iteration 17 — Dark mode pass (all 14 checks pass)
- Removed the last 8 literal colours, so check a passes: table header → var(--surface); skip link → ink on paper; the cmd-palette and history-panel overlays use a new --overlay token (lighter scrim in light mode, darker in dark). The print stylesheet now redefines the colour tokens under `@media print` (also over `:root[data-theme="dark"]`), so printing from dark mode gives black on white. The only dark-mode overrides left are the canvas brightness filter and the theme-icon swap; everything else follows the tokens.
- Ran a one-off WCAG AA audit of every visible text node against its composited background (7 pages × light/dark at 1440): 0 failures. A deliberately low-contrast probe was flagged (2.23:1), so the audit itself works. Visual sweep of all dark pages: consistent, no leftover light panels.
- Known gap (Chart.js, out of scope): chart lines use the old darker blue, which is weaker on the dark paper. Already in LATER.md.

## Iteration 18 — Mobile pass (390px)
- Reviewed all 7 pages at 390 in light and dark (tops and lower sections). Layouts already collapse cleanly from earlier iterations: lead story stacks, story grid is one column, brain dumps/data/about are single columns, the figure row is 2×2, newswire rows stack, and the footer uses three short columns.
- Fixed vertical rhythm: the global `section` margin and main's 80px bottom padding stacked on top of the flex gaps (about 110–200px of blank space around homepage sections and the newsletter band). Homepage sections no longer add their own margin; main padding is now 32/64 (24/48 on phones), the band has no extra top margin, and the section gap is 48px on the homepage and 32px on section pages. Header icon buttons are 40×40 on phones (36 on desktop) for easier tapping, and the header still fits at 390. All 14 checks pass.
