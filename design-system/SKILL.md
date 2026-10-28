---
name: chimeric-design-system
description: Build or restyle Chimeric Labs pages (listing plus sticky panel, forms, tool mocks, diagrams) in the site's Field Lab v3 look using design-system/styles.css. Use for new pages in chimericlabs-llc.
---

# Chimeric Labs pages

1. Read `design-system/GUIDE.md`, then copy the head and header from `breakout.html` (tokens.css, field-lab.css, site.css, design-system/styles.css, Tailwind config).
2. Colours, spacing and fonts come from tokens only; no hex anywhere but `assets/field-lab/tokens.css`. Run `node scripts/check-tokens.mjs` before committing.
3. Compose with `ds-*` classes; use `fl-*` for the one primary action, notices and pills. Do not fight Tailwind utilities with overrides: swap the class.
4. Layout recipes: listing + sticky panel (`ds-split`, `ds-card--sticky`), form card, tool mock (`ds-seams`), flow diagram (`ds-diagram`, classes not fills), 5-step list (`ds-steps`).
5. Concept or demo pages: label them at the top (`fl-notice`) and mark every invented number as a placeholder. No wallets, no live trading, no third-party embeds.
6. JS: native module, no build step, `const`, arrow functions, `AbortController`; tickers honour reduced motion, pause off screen and have a pause button.
7. Check light and dark at 1440 and 390 for horizontal scroll and console errors.
