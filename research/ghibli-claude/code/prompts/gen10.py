"""Cut 10 generation. gen10.py vid TAG PROMPT START.png [END.png]  -> gen/TAG.mp4 (veo3.1-fast, 8 s; END given = first+last frame mode).
Never regenerates an existing file; costs to ghibli-scratch/cost.log. Key read by film-kit load_key, never printed."""
import sys, pathlib, requests
sys.path.insert(0, 'film-kit')
from filmkit.gen.gen import ApiMart, Gen
from PIL import Image
O = pathlib.Path(__file__).parent / 'gen'
class FL(ApiMart):
    def __init__(self, end=None): super().__init__(); self.end = end
    def up(self, p):
        return requests.post(self.base + "/v1/uploads/images", headers={"Authorization": self.h["Authorization"]},
                             files={"file": (pathlib.Path(p).name, open(p, "rb"), "image/jpeg")}, timeout=120).json()["url"]
    def submit_video(self, model, prompt, image, seconds):
        urls = [self.up(image)] + ([self.up(self.end)] if self.end else [])
        body = {"model": model, "prompt": prompt, "duration": 8, "aspect_ratio": "16:9", "image_urls": urls}
        if self.end: body["generation_type"] = "frame"
        return self._post("/v1/videos/generations", body)
def jpg(p, tag):
    im = Image.open(p).convert('RGB'); im = im.resize((1280, 720), Image.LANCZOS); q = O / f'_{tag}.jpg'; im.save(q, quality=93); return str(q)
if __name__ == '__main__':
    _, kind, tag, prompt, start, *end = sys.argv
    O.mkdir(exist_ok=True)
    s = jpg(start, tag + '_a'); e = jpg(end[0], tag + '_b') if end else None
    g = Gen(provider=FL(e), out=O, log='ghibli-scratch/cost.log')
    print(g.video('c10_' + tag, prompt, s, model='veo3.1-fast', seconds=8))
