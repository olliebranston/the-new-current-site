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
