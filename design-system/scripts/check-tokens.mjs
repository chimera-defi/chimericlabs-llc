// Fails if a colour literal appears outside the token files. Run from the repo root:
//   node design-system/scripts/check-tokens.mjs
// Token files (tokens/*.css, any tokens.css) and guidelines/ specimen sheets may hold literals.
import { readdirSync, readFileSync, lstatSync } from "node:fs";
import { join } from "node:path";

const named = "red|green|blue|black|white|gray|grey|orange|yellow|purple|pink|brown|cyan|magenta|teal|navy|maroon|crimson|tomato|coral|gold|silver|lime|olive|indigo|violet|salmon|khaki|ivory|beige";
const hex = "#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{4}|[0-9a-fA-F]{3})";
const patterns = [
  new RegExp(`(?<![\\w"'=.\\[])${hex}(?![\\w-])`),                       // hex in CSS values (not JS selectors such as "#feed")
  /(?<=["'])#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6})(?=["'])/,                       // quoted 6/8-digit hex: fill="#ff0000"
  /\b(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch)\(\s*(?!var\(|from\b)[\d.]/,       // colour functions with literal args
  /\bcolor\(\s*(?!var\(|from\b)[\w-]+\s+[\d.]/,                              // color(display-p3 1 0 0)
  new RegExp(`(?:color|background(?:-color)?|border(?:-[a-z]+)*|fill|stroke|outline(?:-color)?|box-shadow)\\s*:[^;{}]*\\b(?:${named})\\b`), // named colour values
  new RegExp(`\\.style\\.(?:color|background\\w*|fill|stroke|borderColor)\\s*=\\s*["'\`][^"'\`]*(?:\\b(?:${named})\\b|${hex})`), // node.style.color = "..."
];
// field-lab and research pages keep their own frozen Field Lab palette; this checks Fable pages
const skipDirs = new Set(["node_modules", ".git", "tokens", "guidelines", "field-lab", "research"]);

const walk = (dir) => readdirSync(dir).flatMap((name) => {
  const path = join(dir, name);
  if (lstatSync(path).isSymbolicLink()) return [];
  if (lstatSync(path).isDirectory()) return skipDirs.has(name) || name.startsWith(".") ? [] : walk(path);
  return /\.(html|css|js|mjs|svg)$/.test(name) && name !== "tokens.css" && name !== "check-tokens.mjs" ? [path] : [];
});

let bad = 0;
for (const file of walk(process.argv[2] ?? ".")) {
  for (const [i, line] of readFileSync(file, "utf8").split("\n").entries()) {
    // theme-color meta and the data-URI favicon cannot read CSS variables; mask #000 is alpha, not colour
    if (/name="theme-color"|rel="icon"|mask-image/.test(line)) continue;
    if (patterns.some((re) => re.test(line))) { console.log(`${file}:${i + 1}: ${line.trim().slice(0, 100)}`); bad++; }
  }
}

// The maroon token file must only use values recorded in theme.json.
const themeJson = readFileSync(new URL("../theme.json", import.meta.url), "utf8").toLowerCase();
const maroon = readFileSync(new URL("../tokens/fable-maroon.css", import.meta.url), "utf8");
for (const hex of new Set(maroon.match(/#[0-9a-fA-F]{6}\b/g) ?? [])) {
  if (!themeJson.includes(hex.toLowerCase())) { console.log(`tokens/fable-maroon.css: ${hex} not in theme.json`); bad++; }
}
console.log(bad ? `${bad} literal(s) outside token files` : "ok: no colour literals outside token files");
process.exit(bad ? 1 : 0);
