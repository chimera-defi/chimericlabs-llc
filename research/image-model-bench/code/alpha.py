"""Real-alpha check for prop sheets. A PNG passes when more than 40% of pixels are fully clear
and fewer than 3% sit in the middle band, alpha 64 to 191 of 255 (a drawn checkerboard or backdrop has no clear pixels).
Run: python3 alpha.py FILE... -> one JSON line per file (alpha_results.jsonl holds the run over every prop sheet)."""
import json, sys
from PIL import Image
for f in sys.argv[1:]:
    im = Image.open(f); row = {"file": f.split("/")[-2] + "/" + f.split("/")[-1], "mode": im.mode}
    if "A" in im.getbands():
        a = im.getchannel("A"); h = a.histogram(); n = sum(h)
        row["clear"] = round(sum(h[:8]) / n, 3); row["half"] = round(sum(h[64:192]) / n, 3)
        row["real_alpha"] = row["clear"] > 0.4 and row["half"] < 0.03
    else:
        row["real_alpha"] = False
    print(json.dumps(row))
