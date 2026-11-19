import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

// Entry program for news-image-20261118 (round 2): copy the pre-rendered
// front page (drawn deterministically by draw.py) to /output/entry.png.
// Paths resolve via import.meta.url so the grader can run this from any cwd.
const here = dirname(fileURLToPath(import.meta.url));
const outDir = "/output";
mkdirSync(outDir, { recursive: true });
copyFileSync(join(here, "entry.png"), join(outDir, "entry.png"));
