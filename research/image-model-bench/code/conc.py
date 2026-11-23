"""Concurrency test: N gpt-image-2 calls sent at once on the pass-2 valley prompt.
Run: python3 conc.py [N]  -> concurrency_results.json (one row per call, plus the batch wall time)."""
import json, sys, time
from concurrent.futures import ThreadPoolExecutor
from bench import run
from run2_prompts import P
N = int(sys.argv[1]) if len(sys.argv) > 1 else 20
t0 = time.time()
with ThreadPoolExecutor(N) as ex:
    recs = list(ex.map(lambda i: run("gpt-image-2", P["valley"], f"valley_{i}", {"resolution": "1k"}), range(N)))
wall = round(time.time() - t0, 1)
rows = []
for r in recs:
    d = (r.get("task") or {}).get("data") or {}
    rows.append({"status": d.get("status"), "seconds": r.get("seconds"), "cost": d.get("cost"), "error": None if d else str(r.get("error"))[:200]})
out = {"date": time.strftime("%Y-%m-%d"), "model": "gpt-image-2", "n": N, "batch_seconds": wall, "calls": rows}
json.dump(out, open("concurrency_results.json", "w"), indent=1)
ok = [x for x in rows if x["status"] == "completed"]
print(N, "sent", len(ok), "completed", "batch", wall, "s", "cost", round(sum(x["cost"] or 0 for x in rows), 4))
