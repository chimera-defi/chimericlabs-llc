# chimericlabs-llc: how we write code here

- **Content is frozen.** Restyles change classes, CSS and JS only: same words, links, sections, order and meta. Prove it with lab-rig's `tools/content-diff.mjs`.
- **Replace, don't override.** The Tailwind CDN loads after our stylesheets, so a utility beats an `fl-*` class. Swap the utility string; never add `body .x` or `!important` to fight it.
- **Field Lab v3 tokens and classes first** (`assets/field-lab/`), then Tailwind utilities mapped to those tokens.
- **Plain, readable JS.** No build step: native `<script type="module">`, `const`, arrow callbacks, `for…of`, `?.`/`??`, `AbortController` for listener teardown. No IIFEs, no `var`, no `#private`/`_underscore` names.
- **Less code.** Delete before adding; CSS for motion and theming; respect `prefers-reduced-motion`; pause work that is off screen.
- **Comments say why, in one line.**
- **Look at it.** Screenshot light and dark at 1440 and 390, check there is no horizontal scroll or console error.
