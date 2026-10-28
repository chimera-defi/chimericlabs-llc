// Fails if a colour literal appears outside assets/field-lab/tokens.css. Run: node scripts/check-tokens.mjs
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

const roots = [".", "assets", "assets/field-lab", "design-system", "design-system/themes"];
const files = roots.flatMap((dir) => readdirSync(dir).filter((f) => /\.(html|css|js)$/.test(f)).map((f) => join(dir, f)));
const named = "red|green|blue|black|white|gray|grey|orange|yellow|purple|pink|brown|cyan|magenta|teal|navy|maroon|crimson|tomato|coral|gold|silver|lime|olive|indigo|violet|salmon|khaki|ivory|beige";
// hex (3/4/6/8 digits), colour functions with literal args, and named colours used as a colour value
const literal = new RegExp(`(?<![\\w"'=.\\[])#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{4}|[0-9a-fA-F]{3})(?![\\w-])|\\b(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch|color)\\(\\s*(?!var\\(|from\\b)[\\d.]|(?:color|background(?:-color)?|border(?:-[a-z]+)*|fill|stroke|outline(?:-color)?|box-shadow)\\s*:[^;{}]*\\b(?:${named})\\b`, "g");
let bad = 0;
for (const file of files) {
  if (file.endsWith("tokens.css") || file.includes("design-system/themes/")) continue; // token files may hold literals
  for (const [i, line] of readFileSync(file, "utf8").split("\n").entries()) {
    // theme-color meta and the data-URI favicon cannot read CSS variables; mask #000 is alpha, not colour
    if (/name="theme-color"|rel="icon"|mask-image/.test(line)) continue;
    if (literal.test(line)) { console.log(`${file}:${i + 1}: ${line.trim().slice(0, 100)}`); bad++; }
    literal.lastIndex = 0;
  }
}
// Every hex in the Breakout theme must come from breakout.json (the v2 export).
const themeCss = readFileSync("design-system/themes/breakout.css", "utf8");
const themeJson = readFileSync("design-system/themes/breakout.json", "utf8").toLowerCase();
for (const hex of new Set(themeCss.match(/#[0-9a-fA-F]{6}\b/g) ?? [])) {
  if (!themeJson.includes(hex.toLowerCase())) { console.log(`breakout.css: ${hex} not in breakout.json`); bad++; }
}
console.log(bad ? `${bad} literal(s) outside tokens.css` : "ok: no colour literals outside tokens.css");
process.exit(bad ? 1 : 0);
