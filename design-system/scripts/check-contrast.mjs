// Fails when a text/UI pair the system relies on drops below WCAG AA (4.5:1 text, 3:1 UI). Reads hexes from tokens/fable-maroon.css.
import { readFileSync } from "node:fs";

const css = readFileSync(new URL("../tokens/fable-maroon.css", import.meta.url), "utf8");
const hex = (name) => css.match(new RegExp(`--color-${name}:\\s*(#[0-9a-fA-F]{6})`))?.[1];
const channels = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16) / 255);
const linear = (c) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
const luminance = (h) => channels(h).map(linear).reduce((sum, c, i) => sum + c * [0.2126, 0.7152, 0.0722][i], 0);
const mix = (fg, bg, pct) => `#${channels(fg).map((c, i) => Math.round((c * pct + channels(bg)[i] * (1 - pct)) * 255).toString(16).padStart(2, "0")).join("")}`;
const ratio = (a, b) => { const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x); return (hi + 0.05) / (lo + 0.05); };

const text = readFileSync(new URL("../tokens/nocturne-base.css", import.meta.url), "utf8").match(/--color-text:\s*(#[0-9a-fA-F]{6})/)[1];
const [bg, surface] = ["bg", "surface"].map(hex);
const pairs = [
  ["card-meta text 60% on surface", mix(text, surface, 0.6), surface, 4.5],
  ["card-kicker / tag-outline accent-300 on surface", hex("accent-300"), surface, 4.5],
  ["pressed button accent-300 on bg", hex("accent-300"), bg, 4.5],
  ["btn-primary accent-400 on surface", hex("accent-400"), surface, 4.5],
  ["input border text 45% on surface", mix(text, surface, 0.45), surface, 3],
  ["input border text 45% on bg", mix(text, bg, 0.45), bg, 3],
];

let failed = 0;
for (const [name, fg, back, min] of pairs) {
  const r = ratio(fg, back);
  if (r < min) failed++;
  console.log(`${r < min ? "FAIL" : "ok  "} ${r.toFixed(2)}:1 (min ${min}) ${name}`);
}
process.exit(failed ? 1 : 0);
