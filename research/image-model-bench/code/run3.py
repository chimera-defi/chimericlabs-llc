"""Round 3: repeat run of 6 models on the 4 round-2 prompts, plus two new prompts (pair with reference, cine). Usage: run3.py CAP_USD"""
import json, sys, threading, base64, io, pathlib, requests
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from bench import run, OUT
import run2_prompts as R
O3 = OUT.parent/"out3"; O3.mkdir(exist_ok=True)
S = R.S
P = dict(R.P)
P["cine"] = S+"Ultra-wide cinematic establishing shot: a giant white wolf walking along a lake shore at golden dusk, a small train on a long bridge far away, layered mountains, huge sky of glowing clouds, no people."
PAIR = S+"Same girl as in the reference image (black wavy hair, yellow scarf, white shirt), same painting style, now standing still on a quiet train platform at dusk looking up at a small white paper crane, full body, no text."
im = Image.open(pathlib.Path(__file__).parent/"reference-frame-03.jpg").convert("RGB"); im.thumbnail((768,768))
b = io.BytesIO(); im.save(b, "JPEG", quality=85)
URI = "data:image/jpeg;base64,"+base64.b64encode(b.getvalue()).decode()
M = ["gpt-image-2.6-flare","gpt-image-2.6-sunburst","gpt-image-2","flux-3-image","seedream-5-0-pro","gemini-3-pro-image-preview"]
EX = {"gpt-image-2.6-flare":{"quality":"high"},"gpt-image-2.6-sunburst":{"quality":"high"}}
CAP = float(sys.argv[1]); spent=[0.0]; lock=threading.Lock()
jobs = [(m,p) for m in M for p in ["fear","wolf","props","valley","cine"] if not (p=="cine" and False)] + [(m,"pair") for m in M]
def job(a):
    m,p = a
    if spent[0] > CAP: return {"model":m,"prompt":p,"skipped":"cap"}
    ex = {"resolution":"1k", **EX.get(m,{})}
    prompt = PAIR if p=="pair" else P[p]
    if p=="pair": ex["image_urls"]=[URI]
    try: rec = run(m, prompt, p, ex)
    except Exception as e: rec = {"error": repr(e)}
    d = (rec.get("task") or {}).get("data") or {}
    with lock: spent[0] += d.get("cost",0) or 0
    out = {"model":m,"prompt":p,"status":d.get("status"),"seconds":rec.get("seconds"),"cost":d.get("cost")}
    if not d: out["error"] = str(rec.get("error") or rec.get("submit"))[:300]
    try:
        u = d["result"]["images"][0]["url"]; u = u[0] if isinstance(u,list) else u
        r = requests.get(u, timeout=60); ext = "png" if r.content[:4]==b"\x89PNG" else "jpg"
        f = O3/f"{m}__{p}.{ext}"; f.write_bytes(r.content); out["file"]=f.name
    except Exception as e: out["dl"]=repr(e)[:100]
    print(out, flush=True); return out
with ThreadPoolExecutor(6) as ex_: res = list(ex_.map(job, jobs))
json.dump(res, open("results3.json","w"), indent=1); print("spent", round(spent[0],3))
