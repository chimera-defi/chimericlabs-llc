# REVIEW11: cut 11 against cuts 8, 9, 10 and the reference

Written by Wren (Claude Opus 5.5) on behalf of chimera-defi. 2026-11-23.

Film: `out/out_cut11.mp4` (1920x1080, 30 fps, 43.8 s, AAC), `out/out_cut11_720p.mp4`, `out/poster.jpg`. Built on film-kit
(`film-kit-c11`, branch `cut11-kit`), no new generation: spend $0.00 of the $2.50 cap (no `cost.log` line was needed).
Post pipeline: `tools/post.sh` (finish, 720p, poster, every check below, strips); blind sets: `tools/blind.py`; reference side by side:
`tools/sbs.py` -> `review/strips/sbs_ref.jpg`.

## Blind ranking (SPEC11 e)
Pass rule: cut 11 first on at least 3 of the 4 criteria (continuity, motion, fidelity, polish) for every reviewer. Three
reviewers on three models, each run with `claude -p --tools Read` (`filmkit/review/reviewers.sh`), the same prompt and 12 images
per round: whole film at 2 fps, 10 beats x 6 frames, and 30 fps crops (`tools/blind.py`; each cut at its own shot times). Letters
were shuffled by seed each round; the key was kept outside the review folder until the answers came back. Fable use is logged in
the Fable ledger. Bias: the 30 fps crops sit at the beats cut 11 set out to fix (boy, duskboy, the cut into boy_b, ride), and the
prompt's story line says the boy smiles at dusk. Both favour a cut that fixed those beats. The whole-film and 10-beat sheets are neutral.

**Round 3 (final): PASS.** Seed 3011, key A = cut 11, B = 8, C = 10, D = 9. Answers: `review/blind3/r3_{fable,opus,haiku}.txt`.

| reviewer | cut 11 (A): continuity / motion / fidelity / polish | cut 8 (B) | cut 10 (C) | cut 9 (D) | cut 11 first on | pass |
|---|---|---|---|---|---|---|
| Fable | **8 / 7 / 8 / 8** | 4 / 6 / 6 / 4 | 7 / 5 / 7 / 6 | 6 / 5 / 7 / 5 | 4 of 4 | yes |
| Opus | **8 / 6 / 8 / 8** | 5 / 7 / 6 / 5 | 7 / 6 / 7 / 6 | 7 / 6 / 7 / 6 | 3 of 4 (motion: cut 8) | yes |
| Haiku | **8 / 7 / 8 / 8** | 5 / 5 / 6 / 4 | 6 / 6 / 7 / 6 | 7 / 6 / 7 / 5 | 4 of 4 | yes |

All three named cut 11 the overall VERDICT. The reasons they cite for cut 11 match the fixes: a clean duskboy window (no
see-through pole), a whole white sleeve, a straight cut to the wolf at 34.25 s (cuts 9 and 10 show a girl-and-wolf double
exposure there), the bird rising from the sill into the palm, the cat present in the stamp insert, and the train carried from ride
into tunnel at one scale.

Reviewer claims against cut 11, checked:
- Opus: the boy's eyes go from open to shut in one frame (boy +0.10-0.13 s). **True**, at 15.733 -> 15.767 s, and identical in
  cut 10: it is the take's smile-close, kept hard (an in-between ghosts the eye). Open, not fixed. `review/fixes/boy_blink_c11_c10.jpg`.
- Fable: the rider "grows several-fold ... drifts in scale". That growth is the brief's a7 (>= 2.5x); kept.
- Fable: a head-scale jump at boy beat column 6 (about 16.3 s), "shared by A, C and D". Not seen in 30 fps crops 16.10-16.43 s, cuts 11 and 10 alike: the head grows smoothly with the camera push. `review/fixes/boy_head_16.1_16.4_c11_c10.jpg`.

**Round 2: FAIL.** Seed key A = cut 8, B = 10, C = 11, D = 9 (`review/blind2/`).

| reviewer | cut 11 (C) scores | first place per criterion | cut 11 first on |
|---|---|---|---|
| Fable | 8 / 8 / 8 / 8 | cut 11 on all 4 | 4 of 4 |
| Opus | 7 / 8 / 7 / 8 | cut 11 motion and polish; cut 9 (8) continuity and fidelity | 2 of 4 |
| Haiku | 4 / 4 / 5 / 4 | cut 8, 8 / 8 / 8 / 8 | 0 of 4 |

Haiku's two main claims against cut 11 were false: a translucent girl and wolf at 34.25 s and a train smear at 13.25-13.75 s.
Full-resolution frames at those times show a clean cut and a clean train.

**Round 1: FAIL.** Key A = cut 11, B = 8, C = 9, D = 10 (`review/blind/`).

| reviewer | cut 11 (A) scores | first place | cut 11 first on |
|---|---|---|---|
| Fable | 7 / 6 / 7 / 7 | cut 10, 8 / 8 / 8 / 8 | 0 of 4 |
| Opus | 8 / 7 / 8 / 7 | cut 11 on all 4 | 4 of 4 |
| Haiku | 7 / 5 / 7 / 6 | cut 10, 8 / 6 / 8 / 7 | 0 of 4 |

## Checklist (SPEC11 a-d)
Every item, with the test that was run. "by eye" means a person-style read of the cited image, not a script.

| # | item | test | result | evidence |
|---|---|---|---|---|
| a1 | pose swap 15.8 s (boy, take source 59 -> 60) | SPEC11 tests: `filmkit.review.pops` face box 1300,100,600,650 below threshold, and the 15.6-16.0 s strip shows the head turn over >= 3 frames | **PARTIAL**: both spec tests pass (0 flags, cut 10 has 3 at 16.1-16.3 s; head turns over 15.6-15.73 s, 5 frames), but the eyes still close in one frame at 15.733 -> 15.767 s, the same as cut 10. The face-box detector does not catch it (FRICTION 24) | `review/checks/pops_boy_c11.txt`, `pops_boy_c10.txt`, `review/strips/boyface_c11.jpg`, `review/fixes/boy_blink_c11_c10.jpg` |
| a2 | pose swap 37.8-38.6 s (duskboy) | same, duskboy shot | **PASS**: 0 flags (cut 10: 3 flags, 38.33-38.53 s) | `pops_duskboy_c11.txt`, `pops_duskboy_c10.txt`, `review/strips/duskface_c11.jpg` |
| a3 | sleeve ghost near 38.0 s | 30 fps crop 37.7-38.5 | **PASS** (by eye): the rolled sleeve is whole in every frame; repaired with `seam --hold` from source 51 (framing it out cut the face) | `review/strips/duskface_c11.jpg` vs `duskface_c10.jpg`, `review/fixes/duskboy_sleeve_hold.jpg` |
| a4 | wolf scale 2.0-2.6 (window, bell) | head-width ratio on full-res frames | **PASS** (by eye, ±0.3): window about 2.4 (27.3 s), builder G2 2.3; bell about 2.5 (builder G3) | `review/fixes/window_sizes.jpg`, `review/fixes/bell_wolf_scale.jpg` |
| a5 | end splashes: crown >= 40 px at 720p for >= 0.3 s | 720p crops 40.0-43.0 at 10 fps, crops at 40.9 and 41.4 | **PASS** (by eye): crowns about 45-80 px at 720p, each visible 0.4-0.6 s | `review/strips/splash_720p.jpg` |
| a6 | stamp cat breathing >= 10 px, camera locked | `render.js --lock 1` stills 17.0-19.7 s | **PASS** (by eye): back edge rises and falls about 20-25 px; a column scan hit the sill rail, so no script number | `review/fixes/stamp_cat_locked_17.0_17.6_18.2_19.4.png` |
| a7 | bike girl grows >= 2.5x across ride | rider height (head to wheel) on full-res frames of the final film with a 100 px grid | **PASS**: about 150 px at 3.42 s -> about 405 px at 7.15 s, 2.7x (the rig formula gives 2.85x) | `review/strips/ride_c11.jpg` vs `ride_c10.jpg` |
| a8 | pantograph luma within 25 of the tunnel dark (10.6-10.8 s) | masked pantograph pixels vs adjacent dark box | **PASS** on the pantograph pixels: 22.4 / 24.0 / 24.0; the whole crop box including lit stone is 34.5-36.8 (over) | `review/fixes/tunnel_pantograph.jpg`, `review/strips/pantograph.jpg` |
| a9 | bird >= 300 px from the palm on the first boy_b frame | frame at 20.0 s of the final film with a 100 px grid | **PASS**: about 320 px from the palm hollow to the nearest point of the bird (about 385 px centre to centre); the bird sits on the PAR AVION plate | `review/strips/birdcut_c11.jpg` |
| a10 | girl >= 110 px and legs change in window and duskwide | full-res frames + 10 fps strips | **PASS**: window about 260 px, duskwide about 150 px; pedals turn on distance (crank) in both | `review/strips/window_legs.jpg`, `duskwide_legs.jpg` |
| a11 | parity of ported shots (mean <= 3, block <= 6) | `tools/parity.py SHOT` at 3 times | **PASS** on the 12 shots in `review/parity/` (every shot but duskboy, whose take was repaired on purpose); worst mean 2.06, worst block 5.3 (ticket 8.8 s) | `review/parity/*_pair.jpg` |
| b | continuity script | `filmkit.review.continuity`, lick and duskboy allowed (bible palette changes) | 7 flags (cut 10: 7), all at an insert or a palette change the bible names (tunnel dark, stamp/boy_b inserts, lake azure, window, duskwide fade), plus ride b* +24.7 (cut 10 has the same flag; the ride plate is warmer than reed) | `review/checks/continuity.txt`, `continuity_c10.txt` |
| c | pop detector | `filmkit.review.pops`, whole frame, all shots | 9 flags, the same 9 as cut 10: the ticket shot's opening rack (7.23-7.47 s) and the stamp hit (17.97 s), both designed; it flags cut 10 at both pose swaps with the face box (a1, a2) | `review/checks/pops_all_c11.txt`, `pops_all_c10.txt` |
| d | lip and audio cues within 3 frames | `filmkit.review.cues` on `audio/sfx.wav` | **PASS**: 28 of 28 scored cues within 1.5 frames; 6 swells (fade-ins with no onset) reported, not scored | `review/checks/cues.txt` |

## Before and after (cuts 9, 10, 11; same windows)
`review/strips/{boyface,duskface,birdcut,ride,whole}_{c9,c10,c11}.jpg`. Reference side by side at its 13 shots: `review/strips/sbs_ref.jpg`.

## Still worse than the reference
From the side by side (`review/strips/sbs_ref.jpg`, shot i against shot i; our story order differs from the reference after
shot 4, so read it as look, not as shot matching) and the round 3 reasons:
- The ride is a wide with a small rider (about 150 -> 428 px). The reference follows the girl close on the bike, and her legs and
  hair carry the shot. Two reviewers say the legs are too small to judge in every cut.
- Character animation in the wides is cutout and puppet motion. The reference is hand-drawn on every frame (lick: hair and scarf
  stream). Opus ranked cut 8 first on motion in round 3.
- Light: the reference keeps one saturated sea blue through midday and shifts the palette in large beats. Ours jumps at the lake
  and window shots (continuity flags b* and white, shared with cut 10).
- Two short pops remain in the generated boy take, both shared with cut 10: the one-frame eye close at 15.75 s
  (`review/fixes/boy_blink_c11_c10.jpg`) and the opening rack of the ticket insert (7.23-7.47 s, whole-frame pop flags).
- The reference is 60 fps; ours is 30 fps (the brief's format).
- The wolf (our twist) replaces the reference's girl close-up at lick. It has a story reason (it is planted in window and bell), but
  it is not in the reference's register.

## Changes during the blind rounds
- Round 1 -> 2: the ride restaged so the rider grows 2.85x and comes toward the camera (`lib/g1.js` `rideRig`). The lick cut
  changed from a 0.5 s dissolve to a straight cut (the dissolve made a girl-and-wolf double exposure).
- Round 2 -> 3: duskboy plays the take at 0.59x after the wing lands and stops on source 71, before the see-through pole (72) and
  the frown (74) (`shots/duskboy.js`). The bird rises into boy_b over 0.5 s with an ease-in-out; it was a 0.32 s ease-out, which
  read as a 3-frame jump (`shots/boy_b.js`).
- Renders: `out/out_cut11_r1.mp4` and `out/out_cut11_r2.mp4` are kept for comparison.

## A/B record (Opus lead vs Fable lead, same brief)
Read after `out/out_cut11.mp4` and this file existed, as the notice required. Fable lead column: a snapshot of its folder at 05:14 UTC, while it was still working.

| | Opus lead (this folder) | Fable lead (`ghibli-cut11-fable`) |
|---|---|---|
| start | about 03:15 UTC | 03:23 UTC (its `METRICS.md`) |
| film + REVIEW11 done | 05:14 UTC, about 2 h 00 m (3 full renders) | `out_cut11.mp4` written 04:57 UTC; no REVIEW11.md yet; blind round 2 running (with a cut 10 duplicate as a control); no answer files found in `review/blind_r1` or `blind_r2` |
| spend | $0.00 (code motion only, no generation) | $0.1655 in its `cost.log`: 3 gpt-image-2 ($0.0255) + 1 veo3.1-fast dusk retake ($0.14) |
| friction rows | 23 (22 fixed in film-kit or film, 1 wontfix) | 19, all marked fixed |
| SPEC11 (a) defects | 10 of 11 pass, a1 partial (evidence above) | not recorded yet (its TASKS.md unticked) |
| blind ranking | round 3 PASS (cut 11 first on 4/4, 3/4, 4/4) | in progress |
| toolkit | `cut11-kit` merged --no-ff to main (19f1649), tests 40 + 10 green | `cut11-fable` 1 commit (a314d7d), not merged |
