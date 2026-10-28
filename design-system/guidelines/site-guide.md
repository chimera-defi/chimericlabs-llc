# Using Fable on Chimeric Labs pages

- **Entry:** `<link rel="stylesheet" href="design-system/styles.css">` and `<body class="ds-page">`. No Tailwind, no other CSS framework, no external script. Inter loads from the base file.
- **Page shell:** `.ds-header` containing a Nocturne `.nav` (brand, links, one `.btn-primary`), content in `.ds-wrap` sections, `.ds-footer`.
- **Section pattern:** `.ds-kicker`, then `.ds-title`, then optional `.ds-lede` (max 56ch). Dividers are `.hr` (fade over 48px).
- **Buttons:** outlined. Primary action `.btn .btn-primary`; secondary `.btn .btn-secondary`; quiet `.btn .btn-ghost`. Toggle groups use `.btn .btn-secondary .btn-toggle` with `aria-pressed` (pressed reads as accent outline). Controls are at least 36px tall and keyboard reachable.
- **Recipes:**
  - Listing + sticky panel: `.ds-split`, `.card`, `.card-selected`, `.card-sticky`, `.elev-md`.
  - Readout: `.ds-kv`; the result uses `.ds-final`.
  - Live feed: `.ds-feed`. The newest row carries an accent edge; never fade text for age.
  - Tool mock: `.card-flush`, `.ds-bar-row`, `.ds-seams`, `.ds-suggest`.
  - Flow diagram: `.ds-diagram` with `.ds-node`, `.ds-edge`, `.ds-svg-*` (classes, never fills). Edge labels at most about 10 characters at 12px in an 80px gap; node subtitles at most about 28 characters in a 200px node; measure with `getBBox()`.
  - Steps: `.ds-steps`.
- **Live things:** honour `prefers-reduced-motion`, pause off screen and when the tab is hidden, offer a pause button, keep focus on re-render (restore by a `data-focus` key), do not tear down listeners on `pagehide` (back-forward cache).
- **Concept or demo pages:** a `.ds-notice` at the top, invented numbers marked as placeholders, no wallet, no real trading, no real people or organisations.
- **Existing site pages** (`index.html`, `portfolio.html`, `research.html`) still use the Field Lab v3 tokens in `assets/field-lab/`; they have not been moved to Fable.
