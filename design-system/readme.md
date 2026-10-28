# Fable design system

Fable = **Nocturne** (Claude Design's dark, compact system) re-themed **maroon**, plus a small data-colour layer for charts. It came out of the Breakout mock (28 Oct 2026) and is now the house theme for Chimeric Labs pages such as DispatchBench.

## Use it
- Link one file: `design-system/styles.css`. It imports the Nocturne base (tokens + component classes), the maroon override, the data colours and the page patterns.
- Use Nocturne's classes as-is: `.btn`, `.tag`, `.card`, `.field`, `.input`, `.seg`, `.nav`, `.table`, `.dialog`. Override **variables only**, never classes.
- Every colour, font, space, radius and shadow is a `var(--*)`. Chart category colours are `var(--data-*)`.
- Full guide for the base system: `guidelines/nocturne-guide.md`. Theme sheet: `guidelines/palette.html`. Machine-readable tokens with contrast: `theme.json`.

## Visual foundations
- **Ground** #1d1f27, **surface** #2b2d37 (Nocturne lifted two steps), **text** #e9e9ed. One radial glow from top-right (accent-800 at 70%) is the only gradient.
- **Accent** #f65b6f, hue 16° (between wine and maroon), lifted to L .68 so accent-coloured button labels clear 4.3:1 on cards. Maroon proper lives in 700–900: tag fills, tinted tiles, the glow. Never darken the line accent toward #800020 — it drops to 1.5:1 and vanishes.
- Ramp roles: 100 text on tags · 200 text on 900 tints · 300 accent at paragraph size · 400 kickers, step numbers · 500 lines, outlines, labels · 600 hover depth only · 700–900 fills.
- **Type** Inter, headings ≤500. H1 clamp(40px,6vw,80px); H2 32px −0.012em; kicker 13px uppercase .06em accent-400; lede 15.5/28 at 78%; body 15/22; meta 13px neutral-300 with `'tnum'`.
- **Layout** left-aligned, asymmetric, max 1200px, side padding clamp(20px,5vw,72px). Dividers fade over 48px at each end. Buttons outlined, never filled. Flex/grid with gap.
- **Elevation** `--shadow-sm/md/lg` only: a hairline plus ambient dark.
- **Motion** opacity/transform ≤200ms; live tickers ~2.2s; respect prefers-reduced-motion.
- **Data** (addition, see tokens/fable-data.css): category hues at the ramp's 400 lightness; the accent is reserved for "best / selected / frontier".

## Content fundamentals
Plain, short sentences. Numbers before adjectives. No emoji, no decorative stats, no filler. Say what you measured and how ("60 tries, median seconds"). Flag estimates with ~.

## Iconography
Phosphor icons, inline SVG on currentColor. No icon fonts, no emoji.

## Files
- `styles.css` — the entry point (imports only).
- `components/patterns.css` — page patterns Nocturne lacks (listing + sticky panel, readout, feed, tool mock, steps, diagram, page shell), built from tokens only.
- `scripts/check-tokens.mjs` — fails on colour literals outside token files.
- `guidelines/site-guide.md` — how Chimeric Labs pages use this system.
- `dispatchbench/` — the benchmark page theme, consumed by the bench repo.
- `tokens/nocturne-base.css` — base system, verbatim from Nocturne.
- `tokens/fable-maroon.css` — the maroon theme (grounds, accent ramp, section tokens, body glow).
- `tokens/fable-data.css` — chart colours (intentional addition).
- `theme.json` — tokens with OKLCH + WCAG contrast.
- `guidelines/` — Nocturne guide, theme sheet, specimen cards.
- `SKILL.md` — agent skill for Claude Code.

## Intentional additions
- `--data-*` colours: Nocturne is mono; benchmark charts need categorical hues.

## To share across Claude Design
Upload this folder as its own project and set File type → **Design System** in the Share menu. Other projects can then attach it. For Claude Code, install the folder as a skill (`~/.claude/skills/fable-design`, a symlink to this folder works). The folder is self-contained.
