# Later

- Contrast: light --ink-faint #6B6F76 on --surface #F3F1EC is 4.47:1 (AA needs 4.5). On --paper it is 4.84:1. Either darken ink-faint slightly or never use it on surface.
- Live grid strip under the header (reference home.png: "GB grid, 17:47 UTC · Low-carbon 51% [fuel bar] · Carbon intensity · Price · Demand · Live data →"). Needs a new fetch of data/live-grid-snapshot.json on every page, which is a main.js data-loading change and a new feature, so it's out of scope for this loop.
- Back-to-top: the button is hidden with CSS but main.js still builds it (initBackToTop). To delete it properly, remove initBackToTop() from main.js and the two back-to-top lines from scripts/smoke_test_site.py CONTENT_CHECKS together.
