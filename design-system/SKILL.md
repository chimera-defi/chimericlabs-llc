---
name: fable-design
description: Use this skill to build well-branded Chimeric Labs interfaces, mocks and pages in the Fable design system (Nocturne dark base, maroon accent, data colours, page patterns). Covers tokens, component classes, layout recipes and the colour-literal check. Use for new site pages, product mocks and benchmark pages, in Claude Design or Claude Code.
user-invocable: true
---

Read `readme.md`, then `guidelines/nocturne-guide.md`, `guidelines/site-guide.md` and `theme.json`.

1. Link `styles.css` from every page (it imports tokens/ and components/patterns.css). Use Nocturne's classes (`.btn .tag .card .field .input .seg .nav .table .dialog .hr`) and the `ds-*` page patterns in `components/patterns.css`. Override variables only, never classes.
2. Every colour, font, space, radius and shadow is a `var(--*)`. Colours live only in `tokens/*.css`. Charts use `--data-*`; the accent means "best / selected".
3. No Tailwind, framework or third-party script on pages built with this system.
4. Before committing in a codebase, run `node design-system/scripts/check-tokens.mjs` from the repo root (it fails on hex, rgb/hsl/oklch literals and named colours outside token files).
5. For mocks and slides, produce static HTML the user can open. For production code, apply the tokens in the codebase's own stylesheet. If invoked without guidance, ask what to build.
6. Label concept pages as concepts and mark invented numbers as placeholders.
