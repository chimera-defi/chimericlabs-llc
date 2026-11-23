# CONTRACT (frozen by the planner; builders do not change it, they report a problem instead)

Film: "The Paper Bird (and the Wolf)", 41.0 s, 1920x1080, 60 fps. Story and shot list: `../PLAN.md`.
All work lives under `ghibli-fable/work/`.

## Layout
```
work/timeline.json     single source of truth: shots (id, start, end, transition in), cues (absolute seconds)
work/art_src/          the 73 original pictures, read-only
work/art/              prepped art + manifest.json            (owner: art builder)
work/engine/           index.html, engine.js, lib/*.js, shots/<id>.js, render.js, render_all.sh, finish.sh, LIB_API.md
work/audio/            make_audio.py -> track.wav             (owner: audio builder)
work/out/              stills, sheets, previews (anyone; prefix files with your job name)
work/tools/            small scripts
work/venv/             python venv (numpy, scipy, pillow, tinysoundfont) -> use work/venv/bin/python
```

## Timeline
`timeline.json`: `shots[i] = {id, start, end, in:{type, dur}}`, seconds. Transition types: `cut`, `fade` (from
black), `dissolve` (crossfade over `dur`, starting at the incoming shot's `start`; the outgoing shot keeps
being drawn with its own clock running past its end, so every shot must draw correctly up to `end + 0.7 s`).
`end_fade` fades the film to black. `cues` are absolute times that picture and sound both hit.
Nobody hard-codes a cue time: picture reads it with `L.cue('bite')` (returns shot-local seconds), audio reads
the JSON.

## Art manifest (`art/manifest.json`)
```json
{
 "images": { "<id>": {"file": "img/<id>.png", "w": 1536, "h": 1024, "ax": 768, "ay": 1024,
                       "blur": {"8": "img/<id>_b8.jpg", "24": "img/<id>_b24.jpg"}, "note": "..."} },
 "cycles": { "<id>": {"fps": 12, "w": 520, "h": 480, "ax": 260, "ay": 470, "faces": "right",
                       "frames": ["cyc/<id>_0.png", "..."], "wheels": [[cx, cy, r], [cx, cy, r]], "note": "..."} },
 "groups": { "<id>": {"members": ["b1", "b2", "b2e", "b3", "b4"], "note": "poses registered to one another"} }
}
```
- `images`: single pictures. Plates are opaque. Sprites are trimmed to their alpha box; `ax, ay` is the
  anchor in pixels of the trimmed file (plates: centre; standing things: ground contact; hands: wrist edge).
  `blur` (plates only): pre-blurred JPEG copies at Gaussian sigma 8 and 24 px (plate pixels), same size.
- `cycles`: animation loops. Every frame of a cycle is the SAME pixel size and is registered, so drawing all
  frames at one position gives no jitter. `ax, ay` = ground contact point (cyclist: midpoint between the two
  tyre contact points; wolf: ground line under the body centre; birds: body centre). Frames are in playing
  order. `wheels` (cyclist only): wheel centres and radius in frame pixels.
- `groups`: poses of one character that were registered to each other (same canvas size, same anchor), so a
  hard swap between members does not jump: boy `b1 b2 b2e b3 b4`; girl close-up `g1 g2 g3`; wolf head
  `w3_wolf_head_open w3_wolf_head_closed`. Group members are stored as images of identical size.
- Image ids are the original file names without `.png` (cycle ids: `girl_side`, `girl_back`, `wolf_side`,
  `wolf_back`, `bird_white`, `bird_blue`, `dove`).

## Shot interface (`engine/shots/<id>.js`)
```js
SHOTS.register({
  id: 'reed',
  assets: ['p1_plate_bridge_lake', 'girl_side'],   // manifest image ids and cycle ids used by this shot
  draw(g, t, u, L) { /* g: 2D context, 1920x1080 logical px; t: seconds since shot start; u = t/length; L: lib */ }
});
```
- `draw` is a pure function of `t`: no state kept between calls, no Math.random (use `L.rand(seed)` /
  `L.noise`), no Date. Frames render in any order and in parallel processes.
- A shot draws only through `g` and `L`, never touches the DOM or another shot.
- The compositor (engine.js) owns cuts, dissolves, the opening fade and `end_fade`. Shots do not fade themselves.
- Rack focus happens INSIDE a shot (plate blur level changes while the subject stays sharp). Cuts are clean.

## House rules for the picture (from the operator's notes on an earlier cut; every shot must obey)
1. Clean cuts and motivated camera moves; no blur-dissolve between different pictures; no ghost crossfades
   between two poses of a character: swap poses on one frame and cover the swap with a blink, a 3-4 frame
   squash/pop, or an action.
2. Things line up: the bike's tyres touch the path and follow its perspective and scale; the train sits on
   its rails and its wheels are hidden where a parapet or railing would hide them; a character inside the
   train has window frame or sill in front of him.
3. Birds face the way they fly, on smooth arcs, wings flapping; nothing zips or teleports. The bird's origin
   and destination are always readable.
4. Something moves at two or more depths in every half second (camera drift counts as one). No frozen frames
   after a cut: start camera moves already in motion (ease out or linear, never ease-in from rest).
5. Character animation plays on twos (12 fps poses) while the camera and backgrounds run at 60 fps.
6. Sprites must sit in the plate's light: contact shadow on the ground, a tint toward the plate's key colour
   (multiply or soft-light, never a flat milky veil), and the same sharpness as their depth in the plate.
7. One boy (b1, b2, b2e, b3, b4 only) and one girl (c1, c2, c6, g1, g2, g3 only). Keep the cat (c7).
8. Plates are 1536 px wide (1.25x at full frame). Do not zoom a plate past about 1.35x cover scale.

## Rules for every builder
- No Codex, no Grok, no Devin, no subagents, no advisor calls; you are the cheapest lane and do the work
  yourself. Do not read `ghibli-astra/` code (this cut is built independently).
- Write only inside your own directory under `work/` (plus `work/out/`). `art_src/` is read-only.
- Never run pkill or killall; kill only a PID you started and recorded.
- Never play video. Look at frames with ffmpeg stills, and view them DOWNSCALED (contact sheets at most
  1920 px wide; single stills at most 1280 px wide) to save tokens. Check your own work by looking at it.
- No secrets, no network except what your brief names.
- Finish with a report of at most 25 lines: what exists (paths), how to run it, what you checked by eye,
  and known gaps. Say plainly what does not work.
