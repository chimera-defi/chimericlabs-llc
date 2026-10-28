// Fails if a colour literal appears outside the token files. Run from the repo root:
//   node design-system/scripts/check-tokens.mjs
// Token files (tokens/*.css, any tokens.css) and guidelines/ specimen sheets may hold literals.
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";

const named = "red|green|blue|black|white|gray|grey|orange|yellow|purple|pink|brown|cyan|magenta|teal|navy|maroon|crimson|tomato|coral|gold|silver|lime|olive|indigo|violet|salmon|khaki|ivory|beige";
// hex (3/4/6/8 digits), colour functions with literal args, and named colours used as a colour value
const literal = new RegExp(`(?<![\\w"'=.\\[])#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{4}|[0-9a-fA-F]{3})(?![\\w-])|\\b(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch|color)\\(\\s*(?!var\\(|from\\b)[\\d.]|(?:color|background(?:-color)?|border(?:-[a-z]+)*|fill|stroke|outline(?:-color)?|box-shadow)\\s*:[^;{}]*\\b(?:${named})\\b`, "g");
const skipDirs = new Set(["node_modules", ".git", "tokens", "guidelines", "scripts", "skills", "research", "copy"]);

const walk = (dir) => readdirSync(dir).flatMap((name) => {
  const path = join(dir, name);
  if (statSync(path).isDirectory()) return skipDirs.has(name) ? [] : walk(path);
  return /\.(html|css|js)$/.test(name) && name !== "tokens.css" ? [path] : [];
});

let bad = 0;
for (const file of walk(process.argv[2] ?? ".")) {
  for (const [i, line] of readFileSync(file, "utf8").split("\n").entries()) {
    // theme-color meta and the data-URI favicon cannot read CSS variables; mask #000 is alpha, not colour
    if (/name="theme-color"|rel="icon"|mask-image/.test(line)) continue;
    if (literal.test(line)) { console.log(`${file}:${i + 1}: ${line.trim().slice(0, 100)}`); bad++; }
    literal.lastIndex = 0;
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
