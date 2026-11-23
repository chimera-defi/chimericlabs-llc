# REVIEW11: cut 11 (Fable lead) against the SPEC11 checklist

Written by Wren (Claude Fable 5.2) on behalf of chimera-defi.

Film: `out_cut11.mp4` (1920x1080, 30 fps, 45.0 s, 1350 frames, sound), `out_cut11_720.mp4`, `poster11.jpg`.
It is the fourth full render. Render 4 differs from render 3 only inside the dusk window shot (36.8 to 40.4 s), where
a darker box behind the cat was removed; outside that shot the two renders are identical (0.000 at 15 instants,
`filmkit.review.same`). Rows A, P and D were measured on render 3. The change is a colour grade inside one shot, so they were not
measured again. B and C were re-run on render 4 with the same result; E round 3 was judged on render 4. Nothing is skipped; a row that fails says so.

## Result in five lines
1. All ten open defects from NOTES9 and NOTES10 are closed by their own measurement (A1 to A10). Two with a caveat:
   A1 trades the pose swap for an eye that is ghosted for two frames, and A3 passes close to its upper limit.
2. The blind gate (E) is FAIL after all three allowed rounds. No round had cut 11 first on 3 of 4 criteria for every
   judge. Round 3: Opus and Haiku pass (3 of 4 each); Fable does not (1 of 4), though it names cut 11 best overall, 30
   points to cut 10's 29. What cost the gate is the restaged ride: the Fable judge put cut 11 last on fidelity in all
   three rounds, and in round 3 it broke two ties with cut 10 against cut 11 because of it.
3. The pop check (C) is FAIL by its written rule: four fast, intended moves are flagged. Every cut and both old seams
   are clean.
4. The continuity check (B) fails three rows on the number. Two are shots unchanged from cut 10, which fails the same
   rows; one is the scarf in the new ride shot.
5. Still worse than the reference: the list is at the end, under F.

## Pictures first
| what | file |
|---|---|
| cut 9, cut 10, cut 11 at the same story moment, one image per beat | `review/strips/{ride,tunnel,boy,bird_rise,window,duskboy,duskwide}.jpg` |
| the two repaired seams at film rate (30 fps), cut 9 / 10 / 11 | `review/strips/seam_noon30.jpg`, `review/strips/seam_dusk30.jpg` |
| the same seams at 15 and 12 fps | `review/strips/seam_noon.jpg`, `review/strips/seam_dusk.jpg` |
| reference over cut 11, whole film | `review/strips/ref_vs_cut11.jpg` |
| what each blind judge saw | `review/blind_r1/<judge>/`, `blind_r2`, `blind_r3` (label keys in `KEY.json`; the images stay on disk, not in git) |
| this cut against the other run's cut 11, whole film | `out/ab/whole_fable.jpg`, `out/ab/whole_opus.jpg` |

## P. Port parity: PASS on 38 of 39 instants; one has no counterpart
All 13 shots went from the cut 10 engine to the kit through `filmkit.port` and `filmkit.art`. Before any change, each
shot was compared with cut 10 at three instants (`filmkit.review.same`): mean difference 0.147 to 0.433 on a 0..255
scale, limit 2, at 38 of the 39 instants. The 39th is the last instant of boy_b, which was already 0.4 s longer than
cut 10's shot and has no counterpart there; against cut 10's last frames it reads 4.601. Log: `review/out/parity.txt`
(recomputed from the stills of the port run; the stills are in `out/p/` on disk, not in git).

## A. Open defects from NOTES9 and NOTES10
| id | defect | cut 11 | cut 10 (control) | result | evidence |
|---|---|---|---|---|---|
| A1 | pose swap at the noon landing (15.8 s) | head crop at 30 fps: frame-to-frame change stays 8.0 to 10.8; no pop flag from 15.3 to 16.4 s | spikes of 19.2, 18.3, 16.1, 14.2 every third frame over a base of 5 to 7; flagged 15.90 to 16.30 s | PASS | `out/chk/seam/noon11.jpg`, `noon10.jpg`, `review/out/pops_30fps_full.json` |
| A2 | pose swap and doubled sleeve at the dusk landing | new take with in-betweens; no pop flag from 37.8 to 39.6 s; no doubled sleeve in the 30 fps strip | changes at 38.03 to 38.10 s (beside the wing cue) and a flag at 38.33 s | PASS | `review/strips/seam_dusk30.jpg` |
| A3 | wolf too large against the girl; markings | wolf head / girl head (ear tip to jaw against hair top to chin). Window: two hand readings, 2.7 (112 px / 42 px) and 2.5 (114 px / 45 px). Dusk wide: 2.4 (78 px / 32 px). Pass band 2.0 to 2.8. Red face marks visible in both | cut 9 window measured about 5.8 | PASS, near the upper limit in the window (reading error about 0.2). Read by hand on a grid, not by the script the plan named | `out/chk/fin/a3a9.jpg` (20 px grid), `out/chk/fin/a3_heads_window.jpg` (10 px grid) |
| A4 | end splashes faint | three rings, each wider than 60 px at 1080p and visible at 720p | faint | PASS | `out/chk/splash4.jpg` |
| A5 | cat does not breathe in the stamp close-up | back edge travel with the camera locked: stamp about 13 px, boy 9 px, dusk boy 11 px (limits 8, 3, 3) | none visible | PASS | `out/a5/` |
| A6 | bike girl should come toward the camera | her height grows from 93 px (8.6 % of the frame) to 735 px (68 %), never shrinking; above 35 % from 2.75 s; then she leaves along the path. Background moves at most 9.2 px per frame | rides away, small | PASS | `out/chk/r2/ride4.jpg` |
| A7 | pantograph light grey inside the dark tunnel | bars minus the tunnel dark behind them: +1.3, -13.4, -16.9 at 10.5, 10.7, 10.9 s (limit 25 either way). Bar brightness 33, 20, 18 of 255 | +55.6, +73.5, +49.3; bar brightness 87, 107, 85 | PASS. The bars were picked as the pixels where cut 10 is more than 30 brighter than cut 11, so this measures the repainted pixels; the dark is the pixels in the same box where both cuts agree and are under 60 | `out/chk/fin/a7_pantograph.jpg` (cut 10 above, cut 11 below) |
| A8 | bird already on the palm at the 20.0 s cut | it starts on the sill and rises about 354 px over 0.55 s (limits 250 px, 0.35 s) | on the palm at the first frame | PASS | `out/me/boyb.jpg`, `review/strips/bird_rise.jpg` |
| A9 | girl's legs unreadable in the wides | girl alone, head to sandal: window 195 px, dusk wide 142 px (limits 170, 90); the pedalling leg changes in every frame of an 8 fps crop | smaller | PASS | `out/chk/fin/a3a9.jpg`, `out/chk/fin/a9_legs_window.jpg` |
| A10 | dither in the lake sky | cloud edges smooth at 200 % | hard stepped edges with a pixel pattern | PASS | `out/chk/fin/a10_lake_sky.jpg` |

Two honest notes on these rows.
- A1: at 30 fps the stepping is gone, but the head in-betweens are cross-blends: for two frames the open eye shows
  through the closing eye (`out/m/noon30b.jpg`; the Fable judge marked it in rounds 2 and 3). The other cut 11 run
  left this eye close hard and called its row partial; this row is the same kind of partial. Sampled at 15 fps the blink and the nod still fall inside two frames, and one blind
  judge (Fable, round 1) marked that. The hand outside the repaired head area is still drawn on threes.
- A6: the rule passes, but the staging differs from the reference. There she is seen three-quarters from behind, below
  the cliff viaduct. Ours is a front view on a meadow path. The judges disagree on which is closer (see E).

## B. Continuity script: FAIL (3 rows of 21)
`python3 -m filmkit.review.continuity out_cut11.mp4 timeline.json review/continuity.json --out review/out/continuity`
Report: `review/out/continuity/report.txt`. Crops side by side: `review/out/continuity/all_crops.jpg`.
The commands in B and C are the tools as they were before the two runs' kits were merged (kit tag
`cut11-fable-review`). The merged kit keeps the other run's versions of these tools with different flags. Re-run on
render 4 with the tagged tools: the same three rows fail, with the same numbers.

| row | cut 11 | limit | cut 10 (control) | reading |
|---|---|---|---|---|
| noon group, reed: colour distance from the group median | 11.0 | 10 | 11.3 | FAIL in both. The shot is unchanged. It is a whole-frame mean, and this frame is mostly lake |
| noon group, lake | 11.8 | 10 | 12.9 | FAIL in both, same reason |
| noon group, ride | 4.6 | 10 | 10.6 | PASS in cut 11 (new plate), FAIL in cut 10 |
| scarf yellow, ride against bell | delta E 22.9 | 15 | not sampled | FAIL. The scarf is about 12 px thick here and under the shot's shade tint; the sample is 8 px and takes in skin |
| cap red (noon, dusk), collar navy, scarf in bell | delta E 0.0 to 3.2 | 15 | | PASS |
| afternoon group, dusk group | at most 7.1 | 10 | | PASS. Dusk window against dusk wide: 0.6 in lightness, 5.3 in colour |

The dusk row is new work: round 1 had the window shot in navy and orange against a rose and violet wide. A grade in
`shots/duskboy.js` moved it (`out/chk/r2/dusk_a.jpg`).

## C. Pop detector: FAIL by the written rule (four flagged moves); cuts and seams clean
`python3 -m filmkit.review.pops out_cut11.mp4 --timeline timeline.json --fps 30 --k 1.7 --floor 3 --near 0.2`
- All 12 cuts show as cuts (frame difference 46.0 to 67.0); the bell to lick dissolve is a smooth ramp.
- Control: the same command on cut 10 flags 18 frames in 6 groups, with the two known seams among them (15.90 to 16.30 s
  and 38.33 s; 38.03 to 38.10 s sits beside the wing cue). Cut 11 flags 12 frames in 4 groups and none at either seam.
- `--near 0.2` sets aside jumps within 0.2 s of a sound cue (a stamp hit is meant to jump). It did not hide the seams:
  cut 11's set-aside list has 13 frames (stamp hit, three wolf thuds, bite, bell, gulp) and none at the noon landing or
  the wing cue. Cut 10's list has both (15.80 s and 38.03 to 38.10 s).
- Flagged in cut 11 (ratio to the local median 1.7 to 2.6, threshold 1.7). Each was opened at 30 fps:

| time | what it is | in cut 10 too |
|---|---|---|
| 7.23, 7.27 s | the hand settles in the first frames of the ticket insert | no flag (same shot; 1.8 against a threshold of 1.7) |
| 18.33 to 18.47 s | the stamp hand leaves the frame | yes |
| 35.17 to 35.23 s | the wolf's head turns | yes, at 34.77 to 34.83 s |
| 36.23 to 36.27 s | the lick | yes, at 35.83 to 35.87 s |

The pre-registered rule was "no jump above threshold away from a cut". By that wording this row is a FAIL with four
fast, intended moves. Face crop run: 10 flags of the same four kinds (`review/out/pops_30fps_face.json`).
- Render 4, same command: the same 12 frames in the same 4 groups. The merged kit's tool
  (`pops out_cut11.mp4 --timeline timeline.json --k 1.7 --floor 3 --near 0.2`) reports "cuts: 12 of 12 as planned" and
  21 frames: the same four moves (it counts 11 frames of the ticket hand settling, 7.23 to 7.57 s) plus three frames
  of the bell close-up (32.33, 32.40, 33.37 s, ratio 1.8): the wolf's head lunges up behind her with open jaws, then
  drops after the bite. Opened at 30 fps: `out/ab/bell_flags.jpg`. None at either seam.
- At 5 fps (`review/out/pops_5fps.json`) the tool flags 9.0, 9.2, 18.2 and 20.4 s and marks seven cuts "FAIL". Those
  cuts measure 45.7 to 67.1, far above anything inside a shot. The ratio rule breaks when a shot has fast motion next to
  the cut. Read the difference column at 5 fps, not the PASS column. This limit is written in the kit's review README.

## D. Cue alignment: PASS
`audio/cue_table.txt`. Every sound event starts +0.0 to +11.0 ms from its cue (limit 100 ms). Loudness -16.00 LUFS,
true peak -1.50 dBTP, no clipped sample. The table's second column is an onset detector on the effects stem; it reads
-100 ms for the tunnel rumble, which fades in before its cue by design.

## E. Blind ranking: FAIL
Method. One script (`filmkit.review.blind`) cut the same strips from cuts 8, 9, 10 and 11, shuffled the labels per judge
and kept the key outside the pack. Each judge was a fresh agent that could read only its pack. Scores are 1 to 10.
Gate: cut 11 first on at least 3 of 4 criteria for every judge.

Round 1 (render 2, 45 files per judge). First place per criterion:
| judge | continuity | motion | fidelity | polish | cut 11 first on | gate |
|---|---|---|---|---|---|---|
| Fable | cut 11 | cut 11 | cut 8 (cut 11 last) | cut 11 | 3 of 4 | pass |
| Opus | cut 11 | cut 11 | cut 11 | cut 11 | 4 of 4 | pass |
| Haiku | cut 10 | cut 10 | cut 8 | cut 10 | 0 of 4 (last on all) | FAIL |

Scores for cut 11 / cut 10 / cut 9 / cut 8 (continuity, motion, fidelity, polish):
Fable 7 7 5 7 / 6 5 6 7 / 5 5 6 6 / 5 6 7 5. Opus 6 7 6 6 / 5 5 6 6 / 4 4 5 4 / 4 5 5 3. Haiku 5 5 4 4 / 8 7 6 7 / 6 5 5 5 / 7 6 7 6.

What the judges pointed at, and what was done before round 2:
| finding | judge | action |
|---|---|---|
| the cut pairs showed two frames of the new shot | Fable | bug in the kit's `blind.py`; fixed, packs rebuilt |
| in the ride she is a speck for half the shot, and the background "morphs" | Fable, Opus | the path now starts part-way down; the camera pulls back once, slowly (render 3) |
| the dusk window shot is darker than the wide that follows | Fable | grade toward the wide's palette (render 3) |
| the noon seam still reads as a one-frame nod at 15 fps | Fable | 30 fps seam strips added to the pack, since the repair is only visible at film rate |
| ride is a front view on a meadow, not the reference staging | Fable | kept; listed under F |

Round 2 (render 3, 66 files per judge). Two changes to the design, both stated here because they depart from the plan:
30 fps seam strips were added for every cut, and cut 10 was entered twice under two labels as a hidden twin, to see
whether a judge scores identical strips the same.
| judge | continuity | motion | fidelity | polish | cut 11 first on | gate |
|---|---|---|---|---|---|---|
| Fable | cut 10 | cut 11 | cut 8 (cut 11 last) | cut 10 | 1 of 4 | FAIL |
| Opus | cut 11 | cut 11 | cut 8 (cut 11 second) | cut 11 | 3 of 4 | pass |
| Haiku | cut 10 | cut 11 | cut 9 | cut 10 | 1 of 4 | FAIL |

Scores for cut 11 / cut 10 / cut 9 / cut 8: Fable 5 7 5 6 / 7 5 6 7 / 6 5 6 6 / 4 6 7 5. Opus 6 7 6 7 / 6 6 5 6 / 5 5 5 5 / 5 5 7 5.
Haiku 6 6 6 6 / 7 6 6 7 / 5 6 6 5 / 5 5 5 6. Fable gave the twin the same scores as cut 10.

Round 2 got worse with the Fable judge (3 of 4 in round 1, 1 of 4 in round 2). Its three findings on cut 11, each opened:
| finding (Fable, round 2) | checked | action |
|---|---|---|
| the cat is lighter and greyer at the dusk seam, and a darker rectangle sits behind the cat in the dusk window shot | true (`out/chk/fin/cat_box.jpg`). The grade added for round 2 ran before the two clip overlays that make the cat breathe, so their boxes stayed ungraded | grade moved after every clip draw in `shots/duskboy.js`; render 4 (`out/chk/fin/cat_fixed.jpg`, `cat_r4_30fps.jpg`) |
| the place changes from the ride (wide valley, far viaduct) to the cliff-side viaduct; she is a speck in ride frames 1 to 6 of 15 | true: she is small for about the first 2 s (`out/m/ride_sheet.jpg`) | kept; under F |
| the noon-seam in-betweens are cross-blends: the open eye shows over the closing eye for two frames, bird and hand doubled | true (`out/m/noon30b.jpg`) | the other run's flow tool (`filmkit.cut.seam`) was tried on the same frames and ghosts about as much (`out/m/noon_cmp2.jpg`); kept; under F |
It also wrote that cut 11 "has the best landings: its dusk landing closes the eyes gradually with no pose swap".

How far to trust each judge.
- All three judges saw that the twin was pixel-identical to cut 10 and scored the two the same. Haiku said it knew
  from the file sizes, so for Haiku the twin measured little.
- Haiku listed different defects for cut 10 and cut 11 in the tunnel beat ("train scale jumps" against "bird moves onto
  the train roof"). Those two strips come from the same unchanged shot. It also wrote that it "could not resolve ... the
  30 fps seam frames", which is where cut 11 differs most. It ran 79 s on 66 images; Opus ran 404 s.
- The gate was written before the rounds and it says every judge. Haiku's verdict stands as a FAIL of the gate.

Round 3 (render 4, 53 files per judge; the last round the plan allows). The twin was dropped, since every judge had
spotted it. The 30 fps seam strips stayed. The only change to the film since round 2 is the box behind the cat.
A bias to know about: the 30 fps strips were added after round 1 and sit on the two seams this run repaired. The dusk
one is not aligned on the cue either: cut 11's window is 0.3 to 1.0 s after the wing lands (38.5 to 39.2 s), where its
eyes close; cuts 9 and 10 have 0.3 s before to 0.4 s after (37.7 to 38.4 s), where their pose swap is. Both favour
cut 11 on motion. The whole-film, cut-pair and beat strips are the same moments for every cut.
| judge | continuity | motion | fidelity | polish | cut 11 first on | gate |
|---|---|---|---|---|---|---|
| Fable | cut 10 (cut 11 second, tied at 8) | cut 11 | cut 8 (cut 11 last) | cut 10 (cut 11 second, tied at 8) | 1 of 4 | FAIL |
| Opus | cut 11 | cut 11 | cut 8 (cut 11 third) | cut 11 | 3 of 4 | pass |
| Haiku | cut 11 | cut 11 | cut 11 | cut 10 (cut 11 second) | 3 of 4 | pass |

Scores for cut 11 / cut 10 / cut 9 / cut 8: Fable 8 8 6 8 / 8 6 7 8 / 7 6 7 6 / 5 5 8 5.
Opus 7 7 6 7 / 6 6 6 6 / 5 5 5 5 / 4 6 7 4.
Haiku 8 7 8 7 / 7 6 7 7 / 6 6 7 6 / 4 4 6 5. Decoder: `python3 review/decode.py review/blind_r3`.

What the judges pointed at in cut 11 in round 3, each opened:
| finding | judge | checked |
|---|---|---|
| the ride is a different place from the reference (open valley, far viaduct) and she rides toward the camera | Opus | true; F, item 1 |
| the pantograph "pops up" on the train roof between two strip frames | Opus (cut 10 and cut 11) | the train leaves the portal there and the frame comes out of the dark arch between two strip samples (the strip has 4.7 frames per second; `out/m/tunnel_11_12.jpg`). In cut 11 it is drawn dark while inside (A7), so it is there in the earlier frame. Same shot in both cuts |
| the cyclist leaves the frame as the wolf enters | Opus | true, by design: the wolf chases her |
| the dusk window has no passing posts; the eyes close late with a small head shift | Opus | true: the new take is a held plate. Cut 10's take has the posts and the pose swap. F, item 9 |
| the wolf is soft and see-through at the legs while crossing the field | Opus, Haiku (cut 10 and cut 11) | true: motion blur on the run, inherited. F, item 6 |
| the paper bird jumps position at the pantograph | Haiku | same unchanged shot as cut 10; the strip rate, as above |
| a faint blurred vertical at the left edge of the dusk window shot | Haiku (cuts 9, 10, 11) | the window post, out of focus. Not a defect |
| the noon blink is a two-frame cross-fade: eye and fringe ghosted | Fable | true (`out/m/noon30b.jpg`); F, item 4 |
| the ride: she rides toward the camera with the viaduct far behind; the reference sees her from behind riding toward it; she is very small in strip frames 1 to 4 | Fable | true; F, item 1 |
| the bird on the palm goes from flat wings to an upright crane in one frame at the noon landing | Fable (cuts 9, 10, 11) | true: the generated take, inherited; F, item 4 |

Gate after round 3: FAIL. Best overall: all three judges name cut 11. The Fable judge's reasons, in its words:
- for cut 11: it "wins both landings in the 30 fps strips: its dusk landing closes the eyes over about six drawn frames
  and its noon blink is a two-frame blend, which I judge less harmful than [cut 10's] one-frame swap with a head jump".
- against: cut 10 "wins fidelity: its ride is the rear view toward the viaduct as in ref, and its dusk shot has the window
  frame and passing poles of ref". Continuity and polish were tied at 8; the prompt allows no ties in a ranking, and
  the tie went to cut 10 ("ride geography carries into the tunnel establishing shot; [cut 11's] girl is tiny at the
  start of the ride").

So the same decision lost the gate in rounds 2 and 3: the ride was restaged as a front view on a new meadow plate. It
closes defect A6 as written (she comes toward the camera) and it moved the film away from the reference and from the
shot that follows. A fourth round is not allowed by the plan and was not run.
Haiku changed sides: cut 10 first in rounds 1 and 2, cut 11 first in round 3, on a film that changed in one corner of
one shot. That is noise in the judge, not an improvement in the film, and it is read that way here.

Findings from round 2 that were opened and are not defects of cut 11 alone:
- "Jump cut from the girl close-up to the same pose shifted" (Opus, all of cuts 9, 10, 11): the pair is taken at the
  start of the half-second bell to lick dissolve, so both frames are the girl. The dissolve itself does show the girl
  and the wolf double-exposed for a few frames (`out/chk/r2/lick.jpg`). Inherited, kept.
- "Eyes go from closed to open with a reframe in one step, and the bird leaves the palm" (Opus, all three cuts): the
  strip samples 4.4 frames per second. At 30 fps the eyes open over three frames and the bird stays until its cue
  (`out/chk/fin/boyb30.jpg`).
- "The crane on the palm changes design from frame to frame" at the noon landing (Opus, all three cuts): true. It is
  the generated take; the in-betweens repaired the head only.

## F. Against the reference
`review/strips/ref_vs_cut11.jpg`. Still worse than the reference, plainly:
1. Ride staging. The reference sees her from behind below the cliff viaduct, and the next wide continues that place.
   Ours is a front view on a meadow path. Cut 8 was first on fidelity for two judges in rounds 2 and 3; only Haiku put cut 11 first there, in round 3.
2. The wolf. The reference has none; ours has a run past the window, a close-up and the end wide. The bell to lick
   dissolve double-exposes girl and wolf.
3. The cap is red; the reference boy's is brown.
4. The noon landing take: the paper bird changes shape over five frames, and the hand is still on threes. The head
   in-betweens are cross-blends, so for two frames the open eye shows through the closing eye (`out/m/noon30b.jpg`).
5. Splash rings at the end are graphic ellipses, not painted water.
6. The end wide: the wolf on the path reads flat and slightly see-through (Opus, all cuts).
7. Flat inserts: the reference racks focus inside moving shots; ours cuts to still, blurred-background inserts.
8. No shot has the reference's forward dolly under an arch with a pillar sweeping the frame.
9. The dusk window shot is a held plate. In the reference (and in cut 10) window posts pass.
10. At dusk the reference boy smiles. Ours loses his smile and a tear runs, by design: the torn wing comes back to
    his palm (SPEC11, shot 12). It is our story, and it is further from the reference.

## Spend and renders
`cost.log`: $0.1655 of the $2.50 cap (one veo3.1-fast take $0.14 of the $1.50 veo cap; three gpt-image-2 images at
$0.0085). No spend after round 1. Four full renders, each three parallel jobs ("max 3 render jobs" was read as three
jobs at once). Generated stills used: the empty ride plate and the girl's
front cel sheet. Generated video used: the dusk window take (new) and the takes carried over from cuts 9 and 10.

## A/B record (Fable lead, this folder, against the Opus lead in `ghibli-cut11`; same brief)
The other run's folder was first opened at about 06:09 UTC, after render 4, this file and the Opus and Haiku
round 3 verdicts existed and the Fable judge was already running. Its column is copied from its `REVIEW11.md` and
`FRICTION.md` at its commit `d1640cb`; none of it was re-measured here except the last two rows.

| | Fable lead (this folder) | Opus lead (`ghibli-cut11`) |
|---|---|---|
| start | 03:23 UTC | about 03:15 UTC |
| film and REVIEW11 first committed | 05:32 UTC, 2 h 09 m | 05:14 UTC, about 2 h 00 m |
| last change to the film | render 4, 05:51 UTC; round 3 verdicts in at 06:11 | round 3 render, before 05:14 |
| film | 45.0 s, 4 full renders | 43.8 s, 3 full renders |
| spend | $0.1655 (one veo take $0.14, three images $0.0255) | $0.00, no generation |
| defects from NOTES9/10 | 10 of 10 closed by their own measurement; A1 leaves an eye ghosted for two frames | 10 of 11 pass, a1 partial (the eyes still close in one frame at the noon landing) |
| pop check | FAIL by the written rule: 12 frames in 4 groups, none at a seam (cut 10: 18 frames, both seams) | reported as 9 flags, "the same 9 as cut 10", no pass or fail given |
| continuity check | FAIL, 3 rows of 21 | reported as 7 flags (cut 10: 7), no pass or fail given |
| blind gate, own packs | FAIL in all three rounds (round 3: Fable 1 of 4, Opus 3, Haiku 3) | round 3 PASS (4, 3, 4 of 4) after two failed rounds |
| blind packs | 45, 66 and 53 images per judge; 30 fps strips added after round 1, at the two seams this run repaired (the same bias, stated under E) | 12 images per judge; its review states the 30 fps crops sit at the beats it fixed |
| friction rows | 22 (21 fixed, 1 open) | 24 in its `FRICTION.md` |
| kit | merged second, on top (`c0a6a27`, then `47a305c` for one docs line); duplicates resolved; 20 node and 52 Python tests | merged first (`19f1649`) |
| head to head, Opus judge (27 images, labels shuffled) | first on polish; scores 6 5 6 6 | first on continuity, motion, fidelity; scores 8 7 7 5; best overall |
| head to head, Haiku judge (same pack, other labels) | first on all four "because of [a] small motion edge, not because of a clear gap"; scores 6 6 7 6; best overall. It again compared file sizes to tell which strips were the same | scores 6 5 7 6 |

Head to head (outside the gate; `review/blind_h2h/`, spec `review/blind_spec_h2h.json`, the two finished films on the
round 3 beats, one Opus and one Haiku judge, 117 s and 33 s). One judge each way, so it does not settle which cut is
better. The Opus judge's findings were opened:
| finding (Opus, head to head) | checked |
|---|---|
| this cut: "hard pose swap" in the dusk landing, between the last frame of the first strip row and the first of the second | false. Those are neighbouring film frames; change between neighbours from 38.3 to 39.5 s stays 1.1 to 2.9 with no spike (`out/ab/dusk30_mine.jpg`). The round 2 and round 3 Fable judges called this landing the best of the cuts |
| this cut: the girl "vanishes" in the window shot as the wolf enters | false: she rides out at the right edge, the same in both films (`out/ab/window_exit_cmp.jpg`) |
| this cut: the ride is a front view on a meadow, unlike the reference; the scarf is a translucent smear | true (F, item 1); the scarf streams as a soft strip |
| the other cut: the bicycle is tilted and she seems to slide off it; a green wisp floats above the cat at dusk | not checked here; it is the other run's film |
| both: the wolf is a blurred, see-through shape in the window run | true (F, item 6) |
What holds from it: the other cut's ride keeps the reference staging and ours does not. Its motion verdict rests on a
pose swap that is not in the film.

The two gates are not comparable: each run built its own packs and wrote its own prompt. The other run's gate passed
on 12 images per judge against 53 here.

What this run did differently, as choices:
1. It paid for new material where a repair looked weaker: a new empty ride plate and a front cel sheet for the girl,
   and a new dusk window take. The other run generated nothing and repaired the takes it had.
2. Ride. Here: a front view on a new meadow, she comes at the camera. There: the cut 10 cliff plate kept, the rider
   seen from behind and growing 2.7 times. Their choice keeps the place and the reference staging. Ours lost the gate.
3. Noon landing. Here: head in-betweens (no pose swap; a ghosted eye for two frames). There: the one-frame eye close
   kept hard and reported as partial.
4. Dusk landing. Here: a new take with in-betweens on every frame, graded toward the wide, on a held plate. There: the
   old take slowed and stopped before its bad frames, with the sleeve repaired. Ours ends on the fallen smile and a
   tear, theirs before the frown (`out/ab/dusk_face_cmp.jpg`, ours above).
5. Lick. There: the half-second dissolve became a straight cut, which removes the double exposure. Here: kept; it is
   still a defect (F, item 2). Their fix is the better one.
6. Checks. Here every check had a pass limit written before the work, so B, C and E are reported as FAIL. Port parity
   here was 0.147 to 0.433 against a limit of 2; there, worst 2.06 against a limit of 3.
7. Blind rounds. Here a hidden twin of cut 10 measured the judges in round 2 (all three spotted it by identical files).
8. Kit. Each run wrote review tools and helpers for the same gaps. On the merge the first landing stayed the contract;
   this run's duplicates were dropped only after the film rendered the same on the other set (0.000 at 12 instants).
