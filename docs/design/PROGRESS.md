# Progress

## Iteration 1 — Tokens
- Rewrote :root and [data-theme="dark"] with the spec palette, fuel tokens (unused), --font-serif/--font-sans, --radius, --focus-ring, spacing and width tokens; added the single Google Fonts @import; body background is now flat var(--paper) (gradient removed in both themes).
- Legacy token names (--bg-*, --text-*, --border-*, --brand-blue*) now alias the new palette so every page picks it up; shadow/radius legacy tokens left as-is for the "remove shadows/radii" task. --max-width is now 1200px.
- Compromise: spec's light --ink-faint (#6B6F76) on --surface is 4.47:1, just under AA — logged in LATER.md; avoid ink-faint text on surface.

## Iteration 2 — Global type
- Added the 8 --fs- tokens (rem-based: 12/14/16/20/22/28/36/52px) and mapped all 102 font-size declarations onto them (nearest size, with semantic overrides: story card h3 → 22, brain-dump h3 → 20, lead headline → 28, display H1s → 52 desktop / 36 mobile; print pt sizes mapped too). Checks e and f now pass.
- body → var(--font-sans) 16/1.55; h1–h3 → var(--font-serif) 500; h4 stays sans 600; wordmark serif 600; kickers sans 12/600/caps/.06em in --ink-muted (no longer blue); number tiles sans 600 tabular-nums. Fixed .article-content p overriding the article kicker size.
- Compromise: article body is still sans 16px. The serif 20px/680px body is left for the Article pages task.
