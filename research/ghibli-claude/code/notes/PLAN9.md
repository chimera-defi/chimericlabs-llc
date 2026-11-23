# PLAN9: Ghibli Claude cut 9 (overnight, 2026-11-22)

Done = `out_cut9.mp4` (42-44 s, audio) + 720p copy + poster + `NOTES9.md` (per defect: what changed, before/after strip paths),
strips vs `ghibli-ref/dl/ref.mp4` pass at tunnel, palm/first crane, paper->bird and every cut boundary, and 3 independent review
rounds (Fable, Opus, Haiku) end with no blocking finding.

## Decision: one character source = the engine art
Cut 8's boy, girl and wolf sprites are the canon. Generated video is used only as image-to-video (veo3.1-fast, $0.14 / 8 s)
started from a keyframe that is built from the engine's own boy/train art, so identity holds by construction. The 13 ChatGPT/veo
clips of attempt B are NOT reused for character shots: their boy is a different child, the camera is outside the carriage, and the
tunnel clip (`clips/viaduct3d.mp4`) has a gibberish sign, a stray child's head at the portal and strangers in the tram.
The paper bird is code-drawn in every shot (white -> card -> blue with seal); clips are prompted with NO bird, so landing/takeoff
stay on the cues.

## Defects (cut 8 / hyb2 vs reference) and fix
| # | Pointer | Where (cut 8 s) | What is wrong | Fix | Owner |
|---|---|---|---|---|---|
| 1 | train on rails, IN to the tunnel, out through the arch | 9.0-13.4 | ticket: small train does enter the portal (ok). viaduct3d: glued carriage, synthetic parapet, other child in window, no tunnel exit | new shot `tunnel`: keyframe K_tun (engine train front `q3_train_front` as ref, tunnel portal + arch, rails, no people, no text) -> veo "train rolls out of the tunnel on the rails toward camera"; code push-in, bird relay, tunnel_in audio at 9.45 | gen + clip shot |
| 2 | boy inside carriage, same boy every shot | 13.4-16.8, 18.9-20, 35-37.8 | boy reads as outside/behind a post in a dark niche, flat cut-out, arm pops; viaduct3d boy is another child | K_boy: one keyframe from the engine boy sprite (`b2_boy_palm_up`) staged INSIDE (camera in carriage, boy right foreground, frame + sill behind him, arm out of the window, cat + cap on the sill). ONE veo take feeds both `boy` and `boy_b`. Dusk: K_dusk = image edit of K_boy (same boy, dusk light, sad) -> veo; `viaduct3d` removed | gen + clip shot |
| 3 | palm / first crane | 13.4-16.8 | crane sits on the sill at the cut, pops to a hover above the fingertips, oversize | code crane flies in through the window on an arc from the tunnel side, lands ON the palm at land_palm with dip; size about palm width | boy shot code |
| 4 | paper->bird reimagined: from the girl, folds from card, stamped, flies BLUE with seal | 7.2-10, 16.8-20 | hand still on screen over the sharp wide (giant hand); nothing says the hand is the girl's; stamp beat 2.1 s, crane hovers at the end | ticket: hand leaves before the rack finishes, yellow scarf tail in the corner (girl's hand); stamp: 3.0 s, card flat -> stamp -> seal visible >= 0.7 s -> card folds to blue bird with seal -> exits toward the window; brass "PAR AVION" sign with bird emblem on the sill | ticket.js, stamp.js |
| 5 | stamp scene long enough, with a sign | 16.8-18.9 | 2.1 s | retime: boy 13.4-16.6, stamp 16.6-19.6, boy_b 19.6-20.8; everything after shifts +0.8 s (duration 43.2); audio regenerated from timeline | timeline, audio |
| 6 | girl on the path, legs pedal | 3.4-7.2, 23.4-27.6 | pedalling and puddle splash exist; girl is tiny, camera barely follows | ride: stronger follow push (zoom 1.0 -> 1.35 on her), keep splash; verify with 8 fps crops | ride.js |
| 7 | cat breathes in all frames | every cat shot | window/boy/duskboy cats: verify by frame diff; clip shots: prompt "sleeping cat breathes slowly" + diff check | audit + fix |
| 8 | flying-camera feel | all | clip shots get a code push/drift; engine wides already move (check each has >= 4% zoom or pan) | clip lib, per shot |
| 9 | keep | wolf twist, sad faces at the bite, blue stamped bird, splashes, end fade/howl | untouched unless a boundary strip fails | - |

## Build steps
0. Gate (blocks everything generated): K_boy image -> view at full res vs engine boy; one veo probe from it -> check face drift,
   softness, 24 fps conform. If APIMart returns an error, record the exact text and fall back to the zero-spend plan (code fixes
   on engine shots only, no clips with faces).
1. `engine/lib/clip.js` (<= 60 lines): `L.clip.frame(g, id, tClip, {zoom, fx, fy})` draws frame n of a JPEG sequence
   (`work/gen/clips/<id>/f%04d.jpg`, 1920x1080, upscaled lanczos + light unsharp, conformed by playing 24 fps source at film time x speed).
   Frames are listed in `engine/extra_art/manifest.json` as a cycle so the loader preloads only the shots in a chunk.
2. Shots: `tunnel.js`, `boy.js` (rewritten as clip shot + code crane; old one kept as `boy_v8.js`), `boy_b.js`, `duskboy.js`
   (clip + falling blue scrap + cat), `stamp.js` (3.0 s + sign), `ticket.js` (hand/scarf), `ride.js` (push).
3. Timeline retime + `make_audio.py` rerun; check `cue_table.txt`.
4. Render 30 fps (`render_all.sh 1 30 OUT 3`, `finish.sh`), strips, fix, repeat.
5. Reviews, notes, commit on branch `cut9`, `git merge --no-ff` to local main. No push.

## Review rubric (each round: fresh process, sees ref strips + cut 9 strips + this pointer list, not my notes)
Blocking = any of: a train off the rails or passing through stone; no visible tunnel entry + exit; the boy reads as outside the
carriage or is a visibly different child in any shot; crane not landing on the palm / popping; bird colour or seal breaking the
white -> stamped -> blue chain; a cat frozen across a shot; a cut boundary with a jump in place, light or bird position that a
first-time viewer would notice; legs not pedalling; any morphing/garbled text/extra people from generated clips; missing wolf
twist, sad faces, splashes or end fade; audio cue more than 3 frames off picture.
Non-blocking = taste notes. Evidence per round: 2-4 fps strips of the whole film, 8 fps crops for cat/legs/palm, full-res frame
pairs at each clip<->code boundary, the mp4 itself.

## Budget
APIMart about $7.48 left. Plan: 6 keyframes (about $0.10 each with refs on gpt-image-2.6-flare; gpt-image-2 at $0.0085 first where
it passes) + up to 12 veo clips ($1.68). Hard stop at $5 spent; log every call in `ghibli-scratch/cost.log`.

## Gate result (02:xx, after first generations)
- `k9/kboy_a.png` (wide: boy at right, sill in front, frame behind his head) and `k9/kboy_b.png` (close: boy large in right
  foreground, arm through the window, palm at frame centre) both show the engine boy (red cap, black band, gold button, dark curls,
  sailor collar) and match the reference's own wide -> close grammar at 14.0 / 15.0 s.
- veo probe from kboy_a (`clips9/boy_probe.mp4`, strip `strips/c9_boy_probe.jpg`): identity holds for 8 s, cat and landscape alive,
  a telegraph pole passes (good parallax). Fault: veo invented a paper scrap at 0.5-3.0 s although the prompt said "no paper";
  usable window 4.6-7.9 s. Lesson: never name the forbidden object; describe only what is there.
- Use: `boy` (landing) = close clip from kboy_b + code crane landing on the palm; `boy_b` (blue bird leaves) = wide clip
  (probe window 4.6-7.9 s) + code bird. Engine `duskboy` stays if a side-by-side with the clip boy passes; else K_dusk edit.

## Plan review (Fable, `ghibli-scratch/overnight/rev/plan_fable.txt`): REVISE, 6 blocking; what was done
1. Landing shot unprobed -> probed: `clips9/boy_close.mp4` from kboy_b; palm tracked per frame, bird lands on source frame 56 as the hand sinks.
2. Dusk boy gated on identity only -> K_dusk made the default: `k9/kdusk.png` (dusk edit of kboy_b) -> `clips9/dusk_a.mp4`; new
   `duskboy.js` is a clip shot (same carriage, sill, cat), code wing lands on the tracked palm. Old cut-out kept as `duskboy_v8.js`.
3. Tunnel had no gate/fallback -> K_tun probed twice (`tunnel_a` rejected: reframed, train hardly moved; `tunnel_b` used). Entry
   stays in `ticket` (train on the measured rail line into the portal). Fallback if the take had failed: `viaduct.js` (cut 7 engine shot).
4. Crane -> flat card had no owner -> `stamp.js`: the white bird arrives from the palm side (top-left), settles and flattens INTO the
   card (the card does not exist before), stamp, seal, blue soak, fold, blue bird stands, leaves up toward the hand.
5. Stamp sill between two generated shots -> checked side by side (`<tmp>/trk/trio.jpg`): same varnished sill, same brass plate as in
   both takes, same lake; kept the engine plate and engraved the plate (PAR AVION / No 27).
6. Scarf tail alone -> the girl's own scarf art (`part_girl_scarf`) blows in beside the hand; the hand now leaves before the rack
   focus ends. Handlebar not added (would put a second large object over the fold).
C/D: palm anchors are tracked per take; takes play 1 source frame = 1 output frame (1.25x). Pushes on the boy takes kept small
(<= 1.12) because the operator asked for camera moves.
