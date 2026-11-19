// news-image-20261118 — "Sum up 18 November's world news in one image".
// Entry program: copies the baked front-page image (entry.png, drawn
// deterministically by draw.py) to /output/entry.png.
// Node 22, stdlib only. No network. Deterministic: byte-identical output.
import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const SRC = join(__dirname, "entry.png");
const OUT_DIR = process.env.OUTPUT_DIR || "/output";
const DST = join(OUT_DIR, "entry.png");

function main() {
  mkdirSync(OUT_DIR, { recursive: true });
  copyFileSync(SRC, DST);
  console.log(`wrote ${DST}`);
}

main();
