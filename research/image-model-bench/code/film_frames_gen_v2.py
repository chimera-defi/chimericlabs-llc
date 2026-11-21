import sys, json, base64, pathlib, requests, threading
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, ".")  # run next to bench.py
import bench
R = pathlib.Path("/tmp/v2ref")
def ref(*names): return [ "data:image/jpeg;base64,"+base64.b64encode((R/n).read_bytes()).decode() for n in names]
S = ("Hand-painted Studio Ghibli gouache film still matching the reference images' art style, palette and character designs "
     "(the boy has messy brown hair, a red cap with gold button and a navy-trimmed white sailor collar; the girl has black wavy hair, a yellow scarf and white shirt). No text, no watermark. ")
F = {
 "loom": (["r_11.5.jpg","r_33.4.jpg"], "Wide establishing shot: a colossal white wolf with red face markings, as in the second reference, towers and looms over the long stone arched railway viaduct of the first reference, its huge head and shoulders rising above the arches in dusk mist, a tiny red train on the viaduct far below. Violet-pink dusk sky, menace and awe, calm composition with empty sky at the top."),
 "kids_wide": (["r_36.0.jpg","r_27.6.jpg"], "Wide shot of the boy in red cap and the girl in yellow scarf standing close together on a stone railway platform at dusk, looking up in terror at something huge off-frame at upper right, the girl clutching an empty open birdcage, both pale with wide frightened eyes and trembling, no smiles, long violet shadows."),
 "kids_med": (["r_36.0.jpg","r_27.6.jpg"], "Medium shot of the boy in red cap and the girl in yellow scarf huddled together, both with hands pressed over their mouths, eyes wide with fear and tears running down their cheeks, looking up and to the right, dusk light, an empty birdcage hanging at the edge of frame."),
 "boy_close": (["r_36.0.jpg"], "Close-up of the boy in the red cap, face crumpled in fear and grief, big tears on his cheeks, small trembling mouth, wide shining eyes looking up, soft dusk rim light, painterly, no smile."),
 "girl_close": (["r_27.6.jpg"], "Close-up of the girl with black wavy hair and yellow scarf, terrified, tears streaming, hands over her mouth, wide eyes looking up, sea-blue dusk background, painterly, no smile."),
 "cage": (["r_36.0.jpg"], "Insert close-up of a small empty brass birdcage with its little door open, hanging on a hook at a train-station post at dusk, a single pale blue feather caught on the floor of the cage, soft violet bokeh background of a lake and sunset clouds, melancholy, painterly."),
 "grief": (["r_36.0.jpg","r_27.6.jpg"], "Close shot of the girl in yellow scarf crouching, cupping a single pale blue feather in both hands against her chest, eyes closed, a tear on her cheek, quiet deep grief, dusk lake behind, soft warm rim light, painterly."),
 "quiet": (["r_36.0.jpg","r_27.6.jpg"], "Quiet reconciliation: the boy in red cap and the girl in yellow scarf sitting side by side on a grassy lakeside bank at golden dusk, her head leaning on his shoulder, exhausted, gently sad but together, a small blue feather resting between them, the white wolf lying asleep far away on the path, wide 16:9 scene."),
}
M = {"flare": ("gpt-image-2.6-flare", {"quality":"high"}), "flux": ("flux-3-image", {})}
led = pathlib.Path("ledger.json"); L = json.loads(led.read_text()) if led.exists() else {}
lock = threading.Lock()
def job(a):
    k, mk = a; key = f"{k}__{mk}"
    if key in L: return
    m, ex = M[mk]; refs, p = F[k]
    if sum(v["cost"] for v in L.values()) > 7.0: print("CAP"); return
    try: rec = bench.run(m, S+p, key, {**ex, "image_urls": ref(*refs)})
    except Exception as e: print(key, repr(e)[:200]); return
    d = (rec.get("task") or {}).get("data") or {}
    try:
        u = d["result"]["images"][0]["url"]; u = u[0] if isinstance(u, list) else u
        b = requests.get(u, timeout=120).content
        pathlib.Path(f"{key}.png").write_bytes(b)
    except Exception as e:
        print(key, "FAIL", str(rec.get("error") or rec.get("task") or rec.get("submit"))[:300]); return
    with lock:
        L[key] = {"model": m, "prompt": p, "cost": d.get("cost") or 0, "sec": rec.get("seconds")}; led.write_text(json.dumps(L, indent=1))
    print(key, d.get("cost"), rec.get("seconds"), flush=True)
if __name__ == "__main__":
    ks = sys.argv[1].split(","); ms = sys.argv[2].split(",")
    with ThreadPoolExecutor(4) as ex: list(ex.map(job, [(k, m) for k in ks for m in ms]))
