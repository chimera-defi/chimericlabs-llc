"""Video bench: one image-to-video clip, timed and costed.
Run: python3 run_video.py MODEL boy|wolf TAG OPTIONS_JSON  (@IMG in OPTIONS_JSON is replaced by the start-frame URL from in/urls.json)."""
import sys,json,time,base64,pathlib
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[2]/'image-model-bench'/'code'))
from bench import B, H, requests  # key: APIMART_API_KEY, see bench.py
H2={**H,"Content-Type":"application/json"}
D=pathlib.Path(__file__).parent
STYLE=" Studio Ghibli hand-painted animation look, same art style as the input frame, locked camera, no text, no subtitles, no morphing or changing of the face, characters keep identical appearance."
P={"boy":"The boy breathes gently, blinks slowly, his hair moves softly in the wind, his open hand turns slightly as the paper crane drifts. Locked camera."+STYLE,
   "wolf":"The giant wolf looms over the viaduct, slow push-in camera, drifting mist rolling past, fur moving slightly in the wind."+STYLE}
def run(model,img,tag,extra,timeout=900):
    uri=json.load(open(D/'in/urls.json'))[img]
    body={"model":model,"prompt":P[img],**json.loads(json.dumps(extra).replace("@IMG",uri))}
    t0=time.time(); r=requests.post(B+"/v1/videos/generations",headers=H2,json=body,timeout=120)
    try: j=r.json()
    except Exception: j={"raw":r.text[:500]}
    rec={"model":model,"img":img,"tag":tag,"submit":j}
    try: tid=j["data"][0]["task_id"]
    except Exception: rec["error"]=True; return rec
    while time.time()-t0<timeout:
        time.sleep(8)
        s=requests.get(f"{B}/v1/tasks/{tid}",headers=H,timeout=60).json()
        st=(s.get("data") or {}).get("status")
        if st in("completed","succeeded","failed","error","cancelled"): rec["task"]=s;break
    rec["seconds"]=round(time.time()-t0,1)
    try:
        d=rec["task"]["data"]; res=d.get("result") or d
        url=(res.get("videos") or [{}])[0].get("url"); 
        if isinstance(url,list): url=url[0]
        if url:
            (D/'out').mkdir(exist_ok=True)
            open(D/f'out/{tag}_{img}.mp4','wb').write(requests.get(url,timeout=180).content); rec["file"]=f'out/{tag}_{img}.mp4'
    except Exception as e: rec["dlerr"]=str(e)
    return rec
if __name__=="__main__":
    model,img,tag,extra=sys.argv[1],sys.argv[2],sys.argv[3],json.loads(sys.argv[4])
    (D/'out').mkdir(exist_ok=True)  # a failed submit still saves its record
    rec=run(model,img,tag,extra)
    json.dump(rec,open(D/f'out/{tag}_{img}.json','w'),indent=1)
    print(json.dumps(rec)[:1500])
