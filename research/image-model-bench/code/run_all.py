import json, sys, time, pathlib, requests, threading
from concurrent.futures import ThreadPoolExecutor
from bench import run, OUT
P = {
 "props": "Painted gouache sheet in a Ghibli-inspired style: six small objects well apart on a fully transparent background, hard clean edges, no shadows and no ground: a brass bicycle bell, a folded paper crane, a ticket stub, a red conductor cap, a yellow scarf, a small brown suitcase. No text, no people.",
 "fear": "Ghibli-style anime film still: a boy and a girl on a seaside path at dusk, both frightened, eyes wide, faces pale, backing away from a giant white wolf looming at the edge of frame. The boy's open empty hands tremble; their pet paper bird is gone. Soft painterly light, no text.",
 "plate": "Wide painterly background plate, Ghibli-inspired: a stone railway viaduct and a tunnel mouth on a flowering cliff above a blue sea, wisteria, golden afternoon light, no people, no text.",
}
M = ["gemini-3.1-flash-lite-image","gemini-nano-banana-2.1","gemini-3-pro-image-preview","gpt-image-2.5-flare","gpt-image-2","seedream-5-0-pro","seedream-5-5","flux-3-image","flux-2-pro","qwen-image-3.0","minimax-h3-image-highspeed","grok-imagine-image-2.0","z-image-turbo","mai-image-2.7-flash","imagen-4.0-apimart"]
CAP = 4.0; spent = [0.0]; lock = threading.Lock(); results = []
def job(a):
    m, p = a
    if spent[0] > CAP: return {"model": m, "prompt": p, "skipped": "cap"}
    try: rec = run(m, P[p], p, {"resolution": "1k"})
    except Exception as e: rec = {"model": m, "prompt": p, "error": repr(e)}
    d = (rec.get("task") or {}).get("data") or {}
    with lock: spent[0] += d.get("cost", 0) or 0
    try:
        u = d["result"]["images"][0]["url"]; u = u[0] if isinstance(u, list) else u
        f = OUT / f"{m}__{p}.jpg"; f.write_bytes(requests.get(u, timeout=60).content); rec["file"] = f.name
    except Exception as e: rec["dl"] = repr(e)
    rec["cost"] = d.get("cost"); rec["status"] = d.get("status")
    rec.pop("submit", None); (rec.get("task") or {}).pop("data", None) if False else None
    print(m, p, rec.get("status"), rec.get("seconds"), rec.get("cost"), rec.get("file") or rec.get("error") or rec.get("dl"), flush=True)
    return {k: rec.get(k) for k in ("model","prompt","status","seconds","cost","file","error","dl","skipped")}
with ThreadPoolExecutor(6) as ex: results = list(ex.map(job, [(m, p) for p in P for m in M]))
json.dump(results, open("results.json", "w"), indent=1); print("total cost", round(spent[0], 3))
