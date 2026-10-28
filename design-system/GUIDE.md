# Chimeric Labs design system

Nocturne's structure (kicker, heading, lede; left-aligned; outlined buttons; one accent as line, dot and glow; fading rules; tabular figures) on the site's own Field Lab v3 tokens. Nocturne's blurple and maroon themes are not used.

## Use
```html
<link rel="stylesheet" href="assets/field-lab/tokens.css" />
<link rel="stylesheet" href="assets/field-lab/field-lab.css" />
<link rel="stylesheet" href="design-system/styles.css" />
```
Colours come only from `assets/field-lab/tokens.css` (`var(--bg)`, `--surface`, `--ink`, `--ink-2`, `--line`, `--accent`, `--accent-ink`). Never write a hex. `node scripts/check-tokens.mjs` enforces it. Light and dark follow the tokens.

## Palette taken from the site
Light: bg `--bg`, surface `--surface`, ink `--ink`, muted `--ink-2`, line `--line`, accent orange `--accent`, accent text `--accent-ink`. Dark swaps to the deep-green set in tokens.css. Fonts: Archivo (display), Hanken Grotesk (body), IBM Plex Mono (labels).

## Rules
- Accent is a line, dot, bar fill or glow, never a flood. Accent as text uses `--accent-ink`; paragraphs use `--ink` or `--ink-2`.
- One filled accent action per view (`fl-btn--primary`). Everything else is `ds-btn` (outlined); `ds-btn--primary` adds the accent underline.
- Square plates, 1px `--line` borders, hard stamp shadows only (`ds-card--raised`). No blurred shadows, no gradients except the hero glow.
- Section pattern: `ds-kicker` then `ds-title` then optional `ds-lede` (max 56ch). Max width 1200px, side padding `--ds-pad`.
- Figures that change use `ds-num`. Toggles use `aria-pressed`. Controls are at least 44px tall.
- Motion: respect `prefers-reduced-motion`; pause timers off screen and offer a pause control.

## Components (design-system/styles.css)
`ds-wrap ds-hero ds-section ds-split ds-stack ds-row ds-cols-2`, `ds-kicker ds-title ds-h1 ds-lede ds-muted ds-num`, `ds-rule`, `ds-btn (--primary --ghost --block)`, `ds-tag (--accent)`, `ds-dot`, `ds-field ds-input`, `ds-card (--selected --flash --raised --sticky --flush)`, `ds-avatar ds-listing ds-meta ds-bar`, `ds-kv`, `ds-feed`, `ds-seams ds-suggest ds-bar-row`, `ds-steps`, `ds-diagram` with `ds-node ds-edge ds-arrow ds-svg-*`. Worked example: `breakout.html` + `assets/breakout.js`.

## Themes (variables only)
The shared base is the site palette. A section can opt into a named theme file that redefines the same token names: `<html data-ds-theme="breakout">` plus `design-system/themes/breakout.css` (values from `themes/breakout.json`, the Nocturne v2 maroon export: accent #f65b6f at OKLCH hue 16, contrast table in the JSON). Swapping a theme changes variables only; no class is restyled. Theme-only roles: `--ds-tint`, `--ds-tint-ink`, `--ds-tag`, `--ds-tag-ink`, `--ds-glow`. The site's own pages keep the Field Lab palette.

## No Tailwind on new pages
New pages use `ds-` classes and CSS variables only (no CDN script, no framework). `ds-header` and `ds-footer` replace the Tailwind header and footer. Existing pages keep their Tailwind setup untouched.
