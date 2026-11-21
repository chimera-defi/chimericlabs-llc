import json, sys, threading, requests
from concurrent.futures import ThreadPoolExecutor
from bench import run, OUT
O2 = OUT.parent/"out2"; O2.mkdir(exist_ok=True)
S="Ghibli-inspired hand-painted gouache style, soft film-still look, no text. "
P = {
 "fear": S+"Two frightened children clutching an empty birdcage on a dusk train platform, wide eyes, pale faces, huddled close, lamplight and violet dusk.",
 "wolf": S+"A giant white wolf looming over a stone viaduct, a tiny train crossing below, misty mountains, epic scale.",
 "props": S+"Prop sheet on a fully transparent background, six separate objects well spaced with hard clean edges and no shadows: a cat, a bell, a birdcage, a ticket, a lantern, a bird.",
 "valley": S+"Wide misty valley background plate, layered hills, soft fog, 16:9, no people.",
}
M = sys.argv[1].split(",")
EX = {"gpt-image-2.6-flare":{"quality":"high"},"gpt-image-2.5-flare":{"quality":"high"},"gpt-image-2.6-sunburst":{"quality":"high"}}
CAP=float(sys.argv[2]); spent=[0.0]; lock=threading.Lock()
def job(a):
    m,p=a
    if spent[0]>CAP: return {"model":m,"prompt":p,"skipped":"cap"}
    ex={"resolution":"2K" if m=="kling-v4-image" else "1k",**EX.get(m,{})}
    try: rec=run(m,P[p],p,ex)
    except Exception as e: rec={"model":m,"prompt":p,"error":repr(e)}
    d=(rec.get("task") or {}).get("data") or {}
    with lock: spent[0]+=d.get("cost",0) or 0
    out={"model":m,"prompt":p,"status":d.get("status"),"seconds":rec.get("seconds"),"cost":d.get("cost")}
    if not d: out["error"]=str(rec.get("error") or rec.get("submit"))[:300]
    try:
        u=d["result"]["images"][0]["url"]; u=u[0] if isinstance(u,list) else u
        r=requests.get(u,timeout=60); ext="png" if r.content[:4]==b"\x89PNG" else "jpg"
        f=O2/f"{m}__{p}.{ext}"; f.write_bytes(r.content); out["file"]=f.name
    except Exception as e: out["dl"]=repr(e)[:100]
    print(out,flush=True); return out
with ThreadPoolExecutor(6) as ex_: res=list(ex_.map(job,[(m,p) for m in M for p in P]))
old=json.load(open("results2.json")) if __import__("os").path.exists("results2.json") else []
json.dump(old+res,open("results2.json","w"),indent=1); print("spent",round(spent[0],3))
