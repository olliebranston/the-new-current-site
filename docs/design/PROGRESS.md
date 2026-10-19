# Progress

## Iteration 1 — Tokens
- Rewrote :root and [data-theme="dark"] with the spec palette, fuel tokens (unused), --font-serif/--font-sans, --radius, --focus-ring, spacing and width tokens; added the single Google Fonts @import; body background is now flat var(--paper) (gradient removed in both themes).
- Legacy token names (--bg-*, --text-*, --border-*, --brand-blue*) now alias the new palette so every page picks it up; shadow/radius legacy tokens left as-is for the "remove shadows/radii" task. --max-width is now 1200px.
- Compromise: spec's light --ink-faint (#6B6F76) on --surface is 4.47:1, just under AA — logged in LATER.md; avoid ink-faint text on surface.
