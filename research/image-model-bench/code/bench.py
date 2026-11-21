"""APIMart image bench: submit, poll, download, time. IPv4 only (key is allowlisted on IPv4)."""
import json, sys, time, pathlib, socket, requests
import urllib3.util.connection as uc
uc.allowed_gai_family = lambda: socket.AF_INET
KEY = open(pathlib.Path.home() / "secrets/apimart_api_key").read().strip()
H = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
B = "https://api.apimart.ai"
OUT = pathlib.Path(__file__).parent / "out"; OUT.mkdir(exist_ok=True)

def run(model, prompt, slug, extra=None, timeout=300):
    body = {"model": model, "prompt": prompt, "size": "16:9", "n": 1, **(extra or {})}
    t0 = time.time()
    r = requests.post(f"{B}/v1/images/generations", headers=H, json=body, timeout=60)
    j = r.json()
    rec = {"model": model, "prompt": slug, "submit": j}
    try:
        tid = j["data"][0]["task_id"]
    except Exception:
        rec["error"] = j; return rec
    while time.time() - t0 < timeout:
        time.sleep(4)
        s = requests.get(f"{B}/v1/tasks/{tid}", headers=H, timeout=60).json()
        st = (s.get("data") or {}).get("status")
        if st in ("completed", "succeeded", "failed", "error"):
            rec["task"] = s; break
    rec["seconds"] = round(time.time() - t0, 1)
    return rec

if __name__ == "__main__":
    model, slug, prompt = sys.argv[1], sys.argv[2], sys.argv[3]
    extra = json.loads(sys.argv[4]) if len(sys.argv) > 4 else None
    rec = run(model, prompt, slug, extra)
    print(json.dumps(rec, indent=1)[:1800])
