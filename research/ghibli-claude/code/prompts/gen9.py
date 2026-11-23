"""Cut 9 generation helper. gen9.py img TAG MODEL "PROMPT" ref1.jpg ...   |   gen9.py vid TAG START.jpg "PROMPT" [MODEL] [SECONDS]
Outputs k9/TAG.png or clips9/TAG.mp4; never regenerates an existing file; costs go to ../cost.log. The key is read by api.py, never printed."""
import sys, pathlib
sys.path.insert(0, 'ghibli-scratch')
from lib import *
from PIL import Image
O = pathlib.Path(__file__).parent
def do_img(tag, model, prompt, refs):
    out = O / f'k9/{tag}.png'
    if out.exists(): return print(tag, 'exists')
    small = []
    for r in refs:
        im = Image.open(r).convert('RGB'); im.thumbnail((1536, 1536)); p = f'<tmp>/g9_{tag}_{len(small)}.jpg'; im.save(p, quality=90); small.append(p)
    print(tag, img('c9_' + tag, prompt, refs=small, model=model, out=out))
def do_vid(tag, start, prompt, model='veo3.1-fast', seconds=8):
    out = O / f'clips9/{tag}.mp4'
    if out.exists(): return print(tag, 'exists')
    im = Image.open(start).convert('RGB'); im.thumbnail((1280, 720)); p = f'<tmp>/g9v_{tag}.jpg'; im.save(p, quality=92)
    r = requests.post(B + "/v1/uploads/images", headers=H, files={"file": (tag + ".jpg", open(p, 'rb'), "image/jpeg")}, timeout=120).json()
    try: u = r['url']
    except Exception: return print(tag, 'UPLOAD FAIL', str(r)[:400])
    r = requests.post(B + "/v1/videos/generations", headers=HJ, json={"model": model, "prompt": prompt, "duration": int(seconds), "image_urls": [u]}, timeout=120).json()
    try: tid = r["data"][0]["task_id"]
    except Exception: return print(tag, 'SUBMIT FAIL', str(r)[:400])
    st = poll(tid, 900, 8)
    try:
        log('c9_' + tag, model, st['data'].get('cost')); out.write_bytes(requests.get(url_of(st, 'videos'), timeout=180).content); print(tag, 'ok', st['data'].get('cost'))
    except Exception: print(tag, 'FAIL', str(st)[:400])
if __name__ == '__main__':
    a = sys.argv
    if a[1] == 'img': do_img(a[2], a[3], a[4], a[5:])
    else: do_vid(a[2], a[3], a[4], *(a[5:6] or ['veo3.1-fast']), *(a[6:7] or [8]))
