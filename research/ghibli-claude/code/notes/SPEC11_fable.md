# SPEC11: cut 11, a re-roll on filmkit (Fable lead)

Written before any build (2026-11-23, 03:23Z start). Film dir made by `python3 -m filmkit new` from `film-kit-wt-fable`
(branch `cut11-fable` off main d27b862). Sources read: `film-kit` QUICKSTART, INDEX, recipes, `docs/CANVAS.md`;
`ghibli-fable2` NOTES9, NOTES10, PLAN9, PROPS; the bench pages; `ghibli-ref/dl/ref.mp4` (strips only, read-only).

## Finish line
`out_cut11.mp4` (1920x1080, 30 fps, audio, filmkit `finish.sh`) + 720p + poster + before/after strips vs cuts 9 and 10 +
`REVIEW11.md` where every row of the checklist below says PASS or FAIL with an evidence path, and the blind ranking table
is filled. Then `code_only.mp4`, then the toolkit merge. No site publish.

## Two phases (a faithful port only ties cut 10, and a tie fails gate E)
1. **Port to parity.** All 13 shots run on filmkit (`FK.*`), art and takes imported by a filmkit tool. Gate P: every
   untouched shot matches the cut 10 raw render at 4 sample times (mean abs diff <= 2/255) before any change.
2. **Visible wins**, biggest first: ride, the 15.8 and 38.0 s seams, the 20.0 s bird, legs in wides, wolf, lake sky,
   pantograph. Each is one checklist row.

## Shot list (times are cut 11; boy_b is 0.4 s longer than cut 10, so everything after shifts +0.4 s; total 44.2 s)
| # | shot | time (s) | technique | why this technique |
|---|---|---|---|---|
| 1 | reed | 0-3.4 | code | A train on a measured rail, a reed in wind and a rack focus are what code does without error. Passed since cut 7. |
| 2 | ride | 3.4-7.2 | keyframe + veo i2v, code camera and overlays | In the reference the girl rides from far left toward the camera, passes large and goes on up the path. At that size hair, scarf, skirt and legs are organic motion; a 6-frame cut-out reads as a puppet in a close shot. Gate R below runs the free code version first. |
| 3 | ticket | 7.2-10.4 | code | Hand, ticket fold to bird, rack focus, whip-back, train into the portal on the rail: all on cues, all rigid or folded paper. |
| 4 | tunnel | 10.4-13.8 | rigid-vehicle (code train in fitted perspective over an empty plate) | Video models morph a train (cut 9, three cut 10 probes). The code train won the cut 10 blind review 3 of 3. |
| 5 | boy | 13.8-16.8 | veo i2v take (existing `boy_close`) + code crane | Face and hand acting. The take is good except one seam; fix the seam with in-between frames, not a new take (a new take would also break `boy_b` and the palm track). |
| 6 | stamp | 16.8-20.0 | code | Stamp, seal, fold and the sill cat are rigid or rigged; every beat is on a cue. |
| 7 | boy_b | 20.0-21.8 | same take reversed + code bird | Same pixels as shot 5, so costume holds. +0.4 s so the bird can rise from the sill instead of starting on the palm. |
| 8 | lake | 21.8-25.2 | code | Train on a rail, doves, water, splashes. The sky regrade is redone without banding. |
| 9 | window | 25.2-29.4 | code, walk-cycle rule for the girl and wolf (frame from distance) | A wide: parallax layers and cycles. Girl drawn larger so her legs read. |
| 10 | bell | 29.4-34.4 | code | Close-up held by rig: hair and scarf warp, face strokes, wolf bite on cues. Reviewers liked it in cuts 8 to 10. |
| 11 | lick | 34.4-36.8 | code | Wolf head rig, tongue, scraps. Dissolve in. |
| 12 | duskboy | 36.8-39.6 | veo i2v take (new take from the existing `key_dusk`), code wing | Face acting: the smile falls. The cut 9 take morphs the sleeve and swaps pose; a re-take with a simpler motion prompt is the fix. Fallback: old take with in-betweens. |
| 13 | duskwide | 39.6-44.2 | code | Wide with train, doves, splashes, wolf, far bell. Girl and splashes sized to read at playback. |

Rule for generated video (NOTES10): never first+last-frame mode; one start keyframe; prompt only what is in the frame;
keep the usable window only; code owns rigid objects, timing, camera and overlays; reject a take that reframes.

### Gate R (ride), in this order
1. Free: `girl_side` / `girl_back` cycles at reference scale (about 40 % of frame height) on the ride plate, 8 fps strip.
2. If it reads as a puppet (legs or hair frozen, bike sliding): one keyframe (ride plate and girl art as refs) and one
   veo3.1-fast take; second take only if the first reframes or morphs the bike.
3. Pick by strip: the take unless bike or girl change identity; else the code version with the larger girl.

## Continuity bible
| item | canon | checked in shots |
|---|---|---|
| Boy | red cap, black band, gold button on the right side, dark curls, white sailor shirt with navy collar and one white stripe, rolled white sleeve | boy, boy_b, duskboy |
| Girl | black bob blown back, yellow scarf, white short-sleeved blouse, dark shorts, brown bike with a brass bell | ride, window, bell, duskwide |
| Cat | grey tabby asleep on the sill beside a navy cap, breathing in every shot it is in | boy, stamp, boy_b, window, duskboy |
| Wolf | white spirit wolf, red face markings, amber eyes. Head height = 2.0 to 2.8 x the girl's head at the same depth | window, bell, lick, duskwide |
| Bird | white paper crane until the stamp, then blue with the cream seal; never white after 19.0 s | ticket to bell |
| Train | red lower body, cream upper, grey roof, two round lamps, pantograph | reed, ticket, tunnel, lake, duskwide |

Light and palette per shot (sun direction is screen-space, toward the light):
| shots | time of day | key light | palette |
|---|---|---|---|
| reed, ride, ticket, tunnel | noon | high, from upper left | azure sky and water, fresh green, lilac wisteria, cream stone |
| boy, stamp, boy_b | noon, interior | daylight through the window from the left; warm mahogany and brass inside | same exterior, warm interior |
| lake | early afternoon | upper left | azure and white (no pink, no violet) |
| window, bell | afternoon | upper left | azure, green, warm skin; yellow scarf is the accent |
| lick | first dusk (dissolve) | low, from the left | rose and violet field, white fur |
| duskboy, duskwide | dusk | low sun at the horizon, left of centre | violet, rose and orange; lamps lit |
The palette changes between shots, never inside one. One warm accent per shot.

## Acceptance checklist (pre-registered; REVIEW11.md reports every row, no silent skips)
**P. Port parity.** Each untouched shot vs the cut 10 raw render at 4 times: mean abs diff <= 2/255 (`filmkit.review.same`).

**A. Defects left open in NOTES9 / NOTES10** (each: a measurement, and the same measurement on cut 10 as a control)
| id | defect | test | pass when |
|---|---|---|---|
| A1 | pose swap at 15.8 s (eyes shut and head shift inside one frame) | `pops` at 30 fps, boy head crop | no frame-to-frame jump above the shot's own 99th percentile x 2; cut 10 must flag |
| A2 | pose swap and sleeve ghost near 38.0 s | `pops` at 30 fps, dusk boy crop + a 30 fps strip read by eye | same rule; no double sleeve in any frame; cut 10 must flag |
| A3 | wolf scale and markings | head boxes in `review/continuity.json`, ratio per shot | every ratio in 2.0-2.8 (cut 9 window wide measures about 5.8); red markings visible in the wide crops |
| A4 | end splashes faint | crop strip at 720p, and ring diameter in px | each of the 3 rings >= 60 px wide at 1080p and visible in a 720p frame |
| A5 | cat breathing in the stamp close-up | locked-camera render (`--lock`), back edge travel | >= 8 px peak to peak at 1080p; also >= 3 px in boy and duskboy |
| A6 | bike girl comes toward the camera like the reference | girl height per frame in ride | grows from <= 15 % to >= 35 % of frame height, then leaves along the path |
| A7 | pantograph grey in the tunnel dark | crop at the portal, mean luminance of the pantograph vs the tunnel interior | difference <= 25/255 while inside the portal |
| A8 | bird already on the palm at the 20.0 s cut | bird-to-palm distance on the first frame after the cut | >= 250 px, and it reaches the palm over >= 0.35 s |
| A9 | girl's legs unreadable in the wides | girl height in window and duskwide; 8 fps crop | >= 170 px (window) and >= 90 px (duskwide) at 1080p; pedal frames change in the crop |
| A10 | lake sky banding (seen at full size in cut 10) | crop of the lake sky, cut 10 vs 11 | no dither pattern at 200 % |

**B. Continuity script** (`filmkit.review.continuity`, generic; crop boxes are film data in `review/continuity.json`):
per shot mean L, a, b, saturation and 5th/95th luminance percentiles; character crops side by side across shots.
Pass: inside one light group no shot differs from the group median by more than 12 L or 10 in a/b; cap red, scarf
yellow and collar navy stay within delta E 15 of their own median across shots of one light group; a contact sheet is written.

**C. Pop detector** (`filmkit.review.pops`): frame difference at every cut and across the whole film at 5 fps, plus 30 fps
inside the three clip shots. Pass: every timeline cut shows as a cut; no jump above threshold away from a cut; fade and
dissolve are smooth ramps. Control: the tool must flag cut 10 at 15.8 and 38.07 s.

**D. Cue alignment** (`filmkit.review.cues`): for every cue with a sound, onset time in `track.wav` vs the cue; and for
picture, the list of cue -> frame with a still. Pass: every onset within 3 frames (0.1 s). No dialogue, so "lip" means
bite, stamp hit, bell, splashes, thuds, howl.

**E. Blind ranking.** Cuts 8, 9, 10 and 11 as strip sets built by one script from each cut's own cue times (same tiles per
beat: whole film at 2 fps; ride, tunnel, window, bite and end wide at 4 fps; palm landing, the 20.0 s hand-off and the
dusk wing at 15-30 fps; every cut boundary as a frame pair) plus the reference strip. Labels A-D shuffled per reviewer,
mapping kept outside the pack. Three fresh reviewers: Fable (`reviewer`), Opus, Haiku. Each gives forced ranks 1-4 with
no ties on continuity, motion, fidelity to the reference, polish. Pass: cut 11 ranks first on at least 3 of 4 criteria
for each of the three reviewers. If not: fix what they point at and re-run, at most 3 rounds, then report as it stands.

**F. Side by side vs the reference**: one stacked strip per beat, in REVIEW11.md, with a plain list of what is still worse.

## Spend (cap $2.50 total, veo <= $1.50; every call in `cost.log` with a `c11f_` tag; cap checked before each submit)
| item | calls | est. |
|---|---|---|
| ride keyframe (price with refs unknown: buy one, read its logged cost) | 1-2 | $0.03-0.20 |
| ride take, veo3.1-fast | 1-2 | $0.14-0.28 |
| dusk re-take from the existing keyframe | 1-2 | $0.14-0.28 |
| lake plate only if the code regrade still bands | 0-1 | $0-0.10 |
| reserve: noon boy re-take if the in-betweens fail | 0-1 | $0-0.14 |

## code_only.mp4 (deliverable 2)
One shot of this film rebuilt with code only, 18 s, 1280x720: flat plate -> parallax layers -> form shade and haze ->
particles and water -> camera move -> grade, each switched on in turn with a caption, then all on. Art: small stills cut
from this film's own plates and one cycle (listed in its README, under 1.5 MB), no generated video. Lives in
`filmkit/examples/layers/` and is rendered by the tests.

## Toolkit work this run (each is a row in FRICTION.md and a fix in filmkit, line budget in the row)
Expected from the port: wind warp, bird and cycle helpers, glints, dust, scraps, clip track / breathe / frame map,
sprite blur and rim, the rigid vehicle, `--lock` and `--shot` in the renderer, film-local libs, an art importer that
converts anchors, scaffold size flags, a spend cap in `Gen`, and the four review tools above.

## Staffing
Lead: Fable (this session). Builders: Sonnet `builder`, at most 3 at once, disjoint files, stills-only checks. Reviewers:
Fable `reviewer`, Opus, Haiku, fresh each round. At most 3 render jobs at once, builders' stills included.

## Changes from the plan (as built; the plan above is kept as written)
- Length is 45.0 s, not 44.2 s: boy_b is 0.4 s longer (the bird rises from the sill) and duskboy is 0.8 s longer (the new
  take needs room for the landing). `wing_land` is at 38.2 s. Shot starts are in `timeline.json`.
- Ride: no video take. It is one generated empty plate, one generated front cel sheet of the girl, and code motion along
  a measured path. Gate R's keyframe-plus-veo order was dropped after the plate and cel passed on stills. Round 1 of the
  blind review found her a speck for half the shot, so she now starts part-way down and the camera pulls back once.
- Dusk window: one new veo take (the only video spend), full-frame in-betweens, timing owned by code, and a grade toward
  the palette of the wide that follows.
- Noon seam: in-betweens for the head only (`filmkit.cut.tween --box`); the hand is still on threes.
- Check E changed in round 2: 30 fps seam strips were added and cut 10 was entered twice as a hidden twin, so the packs
  have five labels. Round 1 used the four-label design as written.
- "Max 3 render jobs" was read as three parallel jobs per render. There were three full renders.
- Check B's crop boxes are found by `review/findboxes.py` (colour mask median), not placed by hand.
