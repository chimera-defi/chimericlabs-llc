"""Contact sheets for round 3: run 2 vs run 3 per prompt (and the new prompts)."""
import glob, sys
from PIL import Image, ImageDraw
W,H=480,270
def cell(path,label,alpha=False):
    c=Image.new("RGB",(W,H),(30,60,40) if alpha else (20,20,20))
    try:
        im=Image.open(path).convert("RGBA"); im.thumbnail((W,H)); c.paste(im,((W-im.width)//2,(H-im.height)//2),im)
    except Exception: pass
    ImageDraw.Draw(c).rectangle((0,0,W,16),fill=(0,0,0)); ImageDraw.Draw(c).text((3,2),label,fill=(255,255,255)); return c
def f(d,m,p):
    g=glob.glob(f"{d}/{m}__{p}.*"); return g[0] if g else None
M5=["gpt-image-2.6-flare","gpt-image-2.6-sunburst","gpt-image-2","flux-3-image","seedream-5-0-pro"]
M6=M5+["gemini-3-pro-image-preview"]
for p in ["fear","wolf","props","valley"]:
    S=Image.new("RGB",(W*2,H*5)); 
    for i,m in enumerate(M5):
        S.paste(cell(f("out2",m,p),f"{m} run A",p=="props"),(0,i*H)); S.paste(cell(f("out3",m,p),f"{m} run B",p=="props"),(W,i*H))
    S.save(f"sheet3_{p}.jpg",quality=85)
for p in ["cine","pair"]:
    S=Image.new("RGB",(W*3,H*2))
    for i,m in enumerate(M6): S.paste(cell(f("out3",m,p),m),((i%3)*W,(i//3)*H))
    S.save(f"sheet3_{p}.jpg",quality=85)
