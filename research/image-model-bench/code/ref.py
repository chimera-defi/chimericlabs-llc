import base64,json,requests
from bench import run, OUT
O2=OUT.parent/"out2"
img=O2/"gpt-image-2.6-flare__valley.png"
import io
from PIL import Image
im=Image.open(img).convert("RGB"); im.thumbnail((768,768)); b=io.BytesIO(); im.save(b,"JPEG",quality=85)
uri="data:image/jpeg;base64,"+base64.b64encode(b.getvalue()).decode()
P="Same hand-painted Ghibli gouache style and palette as the reference image: a small steam train crossing a stone bridge in a misty valley, no people, no text."
res=[]
for m,key in [("gpt-image-2.5-flare","image_urls"),("flux-kontext-max","image_urls"),("seedream-5-0-pro","image_urls"),("gemini-3-pro-image-preview","image_urls"),("qwen-image-3.0-pro","image_urls"),("flux-3-image","image_urls")]:
    rec=run(m,P,"ref",{"resolution":"1k",key:[uri]})
    d=(rec.get("task") or {}).get("data") or {}
    o={"model":m,"param":key,"status":d.get("status"),"cost":d.get("cost"),"err":None if d else str(rec.get("error") or rec.get("task"))[:250]}
    try:
        u=d["result"]["images"][0]["url"]; u=u[0] if isinstance(u,list) else u
        r=requests.get(u,timeout=60); f=O2/f"ref__{m}.png"; f.write_bytes(r.content); o["file"]=f.name
    except Exception: pass
    print(o,flush=True); res.append(o)
json.dump(res,open("ref_results.json","w"),indent=1)
