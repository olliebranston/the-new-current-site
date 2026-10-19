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
