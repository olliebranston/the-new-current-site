# Redesign tasks

One per iteration, in this order.

- [x] Tokens: rewrite :root + dark theme tokens per spec; add the font @import; remove body gradient
- [ ] Global type: apply font families and the 8-size scale site-wide
- [ ] Remove all box-shadows, gradients, and non-token radii
- [ ] Header + footer templates (then run render_static_layout.py)
- [ ] Remove floating back-to-top button
- [ ] Homepage: intro copy + lead story layout
- [ ] Homepage: thought pieces grid, brain dumps list, data preview, reporting list, newsletter band
- [ ] Thought pieces page: photo header, underline topic tabs, story grid
- [ ] Article pages: header, byline row, photo, 680px serif body, contents, prev/next
- [ ] Brain dumps page: ruled list, drop "PREVIEW"
- [ ] Data page: flatten chart cards, figure row for live numbers (no chart code changes)
- [ ] Reporting page: ruled newswire list
- [ ] About page
- [ ] Byline and date-format fixes
- [ ] Topic consolidation in thought-pieces.json + check filters still work
- [ ] Article title consistency
- [ ] Dark mode pass across all pages
- [ ] Mobile pass (390px) across all pages
- [ ] Final: all checks pass; write docs/design/CHANGELOG.md summarising every change
