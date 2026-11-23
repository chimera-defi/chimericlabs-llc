# SPEC11: Ghibli Claude cut 11, a re-roll on film-kit

Written by Wren (Claude Opus 5.5) on behalf of chimera-defi. 2026-11-23.

Cut 11 is the cut 10 story and timeline (43.8 s, 13 shots), rebuilt in a film dir made by `python3 -m filmkit new` and drawn
only through film-kit's compositor, helpers and recipes. Anything we had to copy from `ghibli-fable2` that the toolkit should
have given us is listed in `FRICTION.md` and fixed in film-kit.

Order of work: (1) port every shot unchanged and prove parity with the cut 10 raw render; (2) then change the shots that hold
an open defect; (3) measure. A port that only matches cut 10 cannot win a blind ranking, so the visible changes are named
here in advance.

## Shot list (technique and why)
Times are cut 10's. "Port" means the cut 10 drawing, moved to film-kit with no visible change (parity gate below).

| # | shot | s | technique | why | change in cut 11 |
|---|---|---|---|---|---|
| 1 | reed | 0-3.4 | code: plate layers, reed sprite, beetle rig, train on a rail | a camera pull-back over painted layers is free; train is rigid | port |
| 2 | ride | 3.4-7.2 | code: walk-cycle (`girl_back` 6-cell pedal cycle, frame from distance) + rigid bike in the cells, camera dolly that catches her | the bike is rigid (NOTES10 lesson: no video model on rigid vehicles); the cycle already exists | **restaged like the reference**: she rides away up the path and the camera catches up, so she grows from about 120 px to about 430 px tall; legs readable; spokes and puddle splash kept |
| 3 | ticket | 7.2-10.4 | keyframe + code: hand plate, `fold` helper (ticket into bird), rack focus by pre-blurred plates, train on a rail into the portal | the fold must hit cues; generated video would invent paper | port |
| 4 | tunnel | 10.4-13.8 | rigid-vehicle recipe: empty generated plate + code train in fitted perspective, sway map, code water and petals | NOTES10: three veo probes morphed the train | port; **pantograph darkened inside the tunnel** |
| 5 | boy | 13.8-16.8 | veo i2v take (`boy_close`, cut 9) + code bird landing on a tracked palm, cat breath warp | face, hair and hand: code reads fake here | **pose swap at source frame 59 -> 60 (15.8 s) replaced by 3 optical-flow in-betweens** |
| 6 | stamp | 16.8-20.0 | code: sill plate, card, stamp, `fold`, rig cat | cue-locked paper action | port (cat breath .09 kept, measured locked) |
| 7 | boy_b | 20.0-21.4 | the same take played backwards + code blue bird | one source of costume pixels (cut 9 round 5) | **bird enters from the plate side, no closer than 300 px to the palm on the first frame** |
| 8 | lake | 21.4-24.8 | code: plate, train on a rail, doves, water, splashes | rigid train, cue-locked birds | port |
| 9 | window | 24.8-29.0 | code: window frame, lake plate, girl side cycle, wolf back cycle, cat | rigid bike; wolf run is a cycle | **girl bigger (legs readable), wolf scale locked to the bible** |
| 10 | bell | 29.0-34.0 | code: girl close-up poses, hair and scarf rigs, wolf bite | registered pose sheet already exists | port; wolf scale and markings checked against the bible |
| 11 | lick | 34.0-36.4 | code: wolf face, lick | same | port; wolf scale checked |
| 12 | duskboy | 36.4-39.2 | veo i2v take (`dusk`, cut 9) + code wing landing | face acting | **head drop (held on threes over source 49-70) re-timed to ones with chained flow in-betweens (`filmkit.cut.seam`); played at 1x with a slow push-in; the rolled sleeve, which the take itself dissolves over source 52-60, is held from source 51 with a drift-tracked patch (`seam --hold`; framing it out cut the face and cat); wing lands on cue 38.0** |
| 13 | duskwide | 39.2-43.8 | code: dusk plate, bridge, train, doves, splashes, girl, wolf | rigid train, cue-locked splashes | **splashes visible at 720p; girl bigger** |

New generation is allowed only where code cannot do it: faces, hair, cloth, water, fur. The plan above needs none; the
$2.50 cap ($1.50 veo) is held for a fix that fails in code (the sleeve is handled by framing, so no new dusk take is planned).

## Continuity bible
- Boy: red cap with a black band and a gold button, dark curls, white shirt with rolled sleeves (both sleeves rolled in every
  shot), navy sailor collar with two white stripes. One take family (`boy_close`, `dusk`), so face and costume hold by construction.
- Girl: dark wind-blown bob, white short-sleeved blouse, yellow scarf (tail streams back), dark skirt; red-brown bicycle with a
  brass bell. Same sprite family in ride, window, bell and duskwide.
- Cat: grey-brown tabby asleep on the sill, curled, the boy's navy cap beside it; it breathes in every shot it is in (boy, stamp,
  boy_b, window, duskboy).
- Wolf: white spirit wolf, red face markings, fades at the edges when it leaves. Scale: head width about 2.3x the girl's head
  width in every shot where both appear (window, bell); in lick it fills the frame. Markings: same red brow and cheek stripes.
- Paper bird: white (girl's ticket) -> stamped card -> blue with a cream seal; the white bird is never blue before the stamp.
- Light and time of day: shots 1-11 are day (high sun, from upper left in the wides, cool cyan field, one warm accent: red train,
  yellow scarf, red cap); lick dissolves to lilac late afternoon; 12-13 dusk (low sun behind the far hills, warm rim, violet sky).
  The palette changes only at a cut, never inside a shot (except the lick dissolve).
- Palette per shot: reed, ride, ticket, tunnel = noon cyan and green; boy, stamp, boy_b = noon, warm sill mahogany; lake =
  azure (regraded from sunset in cut 9); window, bell = noon; lick = lilac; duskboy, duskwide = violet and orange.

## Acceptance checklist (each item: test, then pass or fail in REVIEW11.md; no silent skips)
Thresholds for the automated tests are set on cut 10 first: a test must FAIL cut 10 where cut 10 has the defect.

(a) Open defects from NOTES9 and NOTES10:
1. Pose swap at 15.8 s: the largest frame-to-frame change inside the boy shot (face box, 30 fps) is below the calibrated pop
   threshold, and a 30 fps crop strip 15.6-16.0 s shows the head turn over at least 3 frames.
2. Pose swap at 37.8-38.6 s: same test on the duskboy shot.
3. Sleeve ghost near 38.0 s: a 30 fps crop 37.7-38.5 s shows no half-transparent sleeve in any frame (the sleeve is either whole or
   out of frame). Changed during the build: framing it out cut the face, so cut 11 repairs it with `seam --hold` (REVIEW11 says so).
4. Wolf scale: wolf head width / girl head width in window and bell within 2.0-2.6 (measured on full-res frames).
5. End splashes: each of splash_1..3 shows a crown at least 40 px across at 720p for at least 0.3 s (crop strip).
6. Cat breathing in the stamp shot: with the camera locked (`--lock`), the back edge moves at least 10 px (frame difference).
7. Bike girl comes toward the camera like the reference: her height in frame grows at least 2.5x across the ride shot.
8. Pantograph: inside the tunnel dark (10.6-10.8 s) the pantograph's mean luma is within 25 of the surrounding dark.
9. Bird near the palm at 20.0 s: on the first frame of boy_b the bird is at least 300 px from the palm.
10. Girl legs readable in the wides: in window and duskwide the girl is at least 110 px tall at 1080 and the legs change pose
    across a 10 fps crop strip.
11. Parity: each ported shot without a planned change matches the cut 10 engine still at 3 times (start + .3 s, middle, end - .3 s;
    `render.js --still`, both engines): mean abs difference at most 3/255 and no 240 x 180 block above 6/255. Calibrated on the `boy`
    pilot: a missing haze band showed as blocks of 13-16; a correct port of a take shot sits at 2.4-2.6 mean, block max 3.1 (the
    seam re-encode floor). ride and duskboy are restaged and exempt.

(b) Continuity script (`filmkit/review/continuity.py`): per shot mean luma, saturation and Lab a*/b*; adjacent shots must not jump
by more than the threshold unless the bible names a palette change at that cut; a character crop sheet (boy, girl, cat, wolf) across
shots for the reviewers.
(c) Pop detector (`filmkit/review/pops.py`): frame differences at every frame inside each shot plus the 3 frames each side of
every cut, and a 5 fps pass; flags intra-shot spikes above k x the shot's median. Must flag cut 10 at 15.8 and 38.0 s.
(d) Lip and audio cue list: every timeline cue with its picture frame and the audio onset found in the track; pass if each onset is within
3 frames (0.1 s).
(e) Blind ranking: cuts 8, 9, 10 and 11 on identical strip sets (same beats by shot id, beat-aligned because cut 8 is 42.4 s; 2 fps
whole film plus 30 fps crops at the changed beats), labels shuffled to neutral letters. Three reviewers (Fable `reviewer`, Opus, Haiku),
scores 1-10 per criterion: continuity, motion, fidelity to the reference, polish. Pass: cut 11 ranks first on at least 3 of 4
criteria for every reviewer. Ties count as not first. Else iterate (max 3 rounds). Plus a side-by-side of cut 11 against the
reference at the 13 reference shots.

## Strip spec (frozen before building)
- Whole film: 2 fps, 480 px, timestamps.
- Beats (by shot id, each cut's own times): ride, ticket, tunnel, boy, stamp, boy_b, window, bell, duskboy, duskwide at 6 frames each.
- 30 fps crops: 15.6-16.0 (boy face), 37.7-38.5 (dusk face and sleeve), 19.95-20.4 (bird at the cut), ride 3.4-7.2 at 5 fps.
