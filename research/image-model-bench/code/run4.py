"""Pass 4: new cheap candidates on the pass-2 prompts, one request at a time under a hard cap.
Run: python3 run4.py MODEL[,MODEL...] CAP [PROMPT,...]  -> appends to results4.json, images in out4/."""
import json, os, sys, time, requests
from bench import run, OUT, B, H
from run2_prompts import P
EX = {"gpt-image-1.5": {"size": "1536x1024"}}  # 1.5 rejects "16:9"; 3:2 is its widest size
# RUN4_RESULTS / RUN4_OUT give a later pass its own file and folder (pass 5: results5.json).
O4 = OUT.parent / os.environ.get("RUN4_OUT", "out4"); O4.mkdir(exist_ok=True)
FN = os.environ.get("RUN4_RESULTS", "results4.json")
old = json.load(open(FN)) if os.path.exists(FN) else []
spent = sum(r.get("cost") or 0 for r in old)
CAP = float(sys.argv[2])
prompts = sys.argv[3].split(",") if len(sys.argv) > 3 else list(P)
# An unpriced model may cost more than anything seen (gpt-image-1.5 billed $0.163), so reserve $0.20 or the dearest seen.
seen = {r["model"]: r["cost"] for r in old if r.get("cost")}
for m in sys.argv[1].split(","):
    for p in prompts:
        est = seen.get(m, max([0.20, *seen.values()]))
        if spent + est > CAP:
            print("skip", m, p, "cap", round(spent, 4)); continue
        rec = run(m, P[p], p, {"resolution": "1k", **EX.get(m, {})})
        tid = ((rec.get("submit") or {}).get("data") or [{}])[0].get("task_id")
        # A timed-out task can still finish and bill, so wait for its end state before the next request.
        while tid and "task" not in rec:
            time.sleep(10)
            s = requests.get(f"{B}/v1/tasks/{tid}", headers=H, timeout=60).json()
            if (s.get("data") or {}).get("status") in ("completed", "succeeded", "failed", "error"): rec["task"] = s
        d = (rec.get("task") or {}).get("data") or {}
        out = {"model": m, "prompt": p, "status": d.get("status"), "seconds": rec.get("seconds"), "cost": d.get("cost")}
        if not d: out["error"] = str(rec.get("error") or rec.get("submit"))[:300]
        elif d.get("status") != "completed": out["error"] = str(d.get("fail_reason") or d.get("error") or "")[:300]
        spent += out["cost"] or 0
        if out["cost"]: seen[m] = out["cost"]
        try:
            u = d["result"]["images"][0]["url"]; u = u[0] if isinstance(u, list) else u
            r = requests.get(u, timeout=60); ext = "png" if r.content[:4] == b"\x89PNG" else "jpg"
            f = O4 / f"{m}__{p}.{ext}"; f.write_bytes(r.content); out["file"] = f.name
        except Exception as e: out["dl"] = repr(e)[:100]
        print(out, "spent", round(spent, 4), flush=True)
        old.append(out); json.dump(old, open(FN, "w"), indent=1)
        if out.get("error") and not out.get("cost"): break  # rejected: try the next model
print("spent", round(spent, 4))
