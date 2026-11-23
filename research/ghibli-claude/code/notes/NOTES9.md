# NOTES9: Ghibli Claude cut 9 (2026-11-22)

Output: `out_cut9.mp4` (1920x1080, 30 fps, 43.8 s, audio), `out_cut9_720p.mp4`, `out_cut9_poster.jpg` (frame at 20.9 s).
Plan and gate results: `PLAN9.md`. Strips live in `ghibli-scratch/overnight/strips/` (S/ below).
Reference strips: `S/ref_all.jpg`, `S/ref_07_14.jpg` (tunnel), `S/ref_14_21.jpg` (palm, paper -> bird), `S/ref_boy_3fps.jpg`.
Before = cut 8 (`S/c8_*.jpg`) and the rejected hybrid (`S/hyb2_*.jpg`). After = `S/c9r7_*.jpg` (final render `work/out/cut9_r7.mp4`, copied to `out_cut9.mp4`). Round 6 render `work/out/cut9_r6.mp4` (`S/c9r6_*.jpg`) also passed and is the fallback.

## What changed, per owner pointer
| Pointer | Before | What changed | After |
|---|---|---|---|
| Train on rails, IN to the tunnel, OUT through the arch | `S/c8_07_14.jpg`, `S/hyb2_07_14.jpg` | New clip shot `tunnel.js` (image-to-video from a keyframe built on the engine train): the train comes out of the near arch on rails. Entry stays in `ticket.js`: train speed 760 -> 520 px/s and a closer camera, so the whole train is seen rolling into the far portal (9.2-10.4 s); the bird follows it in (flight slowed so it reaches the portal with the last carriage). | `S/c9r7_tunnel.jpg`, `S/c9r7_entry.jpg`, `S/c9r7_full_tunnel.jpg` |
| Boy inside the carriage, SAME boy in every shot | `S/c8_boy_3fps.jpg`, `S/c8_14_21.jpg` | `boy.js`, `boy_b.js`, `duskboy.js` are clip shots from one keyframe family, made from the engine boy sprite (red cap, black band, gold button, curls, sailor collar); camera sits inside, sill and cat in front. After round 5 `boy_b.js` reuses the `boy_close` take played backwards (`FROM = 78, RATE = -30`), so shirt, sleeve and collar are the same pixels in both noon shots; the `boy_wide` take is no longer used. Old cut-outs kept as `*_v8.js`. | `S/c9r7_palm.jpg`, `S/c9r7_costume.jpg` (15.9 / 20.9 / 38.8 s side by side), `S/c9r7_full_palm.jpg`, `S/c9r7_full_boyb.jpg`, `S/c9r7_full_dusk.jpg` |
| Palm / first crane | `S/c8_14_21.jpg` | Code crane flies in from the tunnel side on one arc and lands on the tracked palm exactly when the hand gives (15.67 s), palm-sized, squash and two settling flaps. After round 4 the hop to the sill plate was shortened so it is still on the way down at the cut; after round 5 it is a lift-off from the palm just before the 16.8 s cut, and the stamp shot picks the bird up in the air. | `S/c9r7_palm.jpg`, `S/c9r7_handoff.jpg`, `S/c9r7_land30.jpg` (15.3-16.1 s at 30 fps), `S/c9r7_pose30.jpg` |
| Paper -> bird reimagined, stamp long enough, with a sign | `S/c8_14_21.jpg` | The girl's own ticket (its printed face, not a blank card) folds into the white bird in her hand over 0.62 s (`L.paperbird.fold`, scarf in frame), and the bird leaves the hand into the wide. Stamp shot 2.1 -> 3.2 s on a "PAR AVION No 27" plate (same mahogany sill, brass bead and engraved plate as the boy shots): the white bird lands, flattens into a card, stamp, card turns blue with the cream seal, folds into the blue bird (15 fps in-betweens), returns to his hand and leaves on blue. After the 20.0 s cut the blue bird comes up from the plate side onto the palm over 0.24 s. Bird sprite made a deeper blue so it never reads white against cloud. | `S/c9r7_ticketfold.jpg` (8.0-8.8 s), `S/c9r7_paperbird.jpg`, `S/c9r7_folds.jpg`, `S/c9r7_full_stamp.jpg` |
| Girl on the path, legs pedal | `S/c8_a.jpg` | `ride.js` follow push on her; pedalling and puddle splash kept. | `S/c9r7_legs.jpg` |
| Cat breathes in all frames | `S/c8_boy_3fps.jpg` | `L.clip.breathe` warps the cat's torso (15 px in clip space, 21 px after round 4) with an ear flick per shot on top of the take's own motion; window-wide cat rig breathing raised from 2 % to 4.5 % and then 8.5 % (round 5). Round 7: the sill close-up (stamp shot) had no cat; the same sleeping cat now lies against the left end of the plate there and breathes (6 %). | `S/c9r7_breath.jpg` (camera locked, grid; rows: boy, boy_b, dusk, window wide), `S/c9r7_breath_stamp.jpg` (stamp close-up at 16.94 / 18.50 / 19.54 s; that camera pushes in, so read the back against the plate), `S/c9r7_cat.jpg` |
| Flying-camera feel | `S/c8_all.jpg` | Every clip shot has a code push or pull; lake wide pulls back and trucks right (was locked); ticket shot whips back from her hand to the wide and then pushes in on the portal. After round 5: the tunnel shot trucks with the train (clamp removed), the window wide pushes in, the boy shot pushes 14 %. | `S/c9r7_cam.jpg`, `S/c9r7_all_a.jpg` .. `_d.jpg` |
| Kept: wolf twist, sad faces, blue stamped bird, splashes, end fade | `S/c8_c.jpg`, `S/c8_d.jpg` | Bell shot: plate-only grade, bird stays blue in the jaws, blue paper in the closed jaw; a pale bar under the handlebar (the wolf's stretched body layer showing through a gap) is erased. Dusk: only a torn blue wing with a piece of the seal lands on his palm; the wing turns flat before it lands instead of growing in one frame, and the stretch of the take where the boy's rolled sleeve dissolves (source frames 44-56) plays at 3x straight after the landing (`map` option in `L.clip.n`). | `S/c9r7_bite.jpg`, `S/c9r7_wolfin.jpg`, `S/c9r7_full_bite.jpg`, `S/c9r7_wing.jpg`, `S/c9r7_cry30.jpg`, `S/c9r7_all_d.jpg` |
| Cut boundaries | `S/c8_all.jpg` | Lake plate regraded from sunset to day (violet -> azure, pink clouds -> white) so noon -> lake -> noon no longer swings; bell -> lick is a 0.5 s dissolve into dusk; bird position carried across every cut. | `S/c9r7_cuts.jpg`, `S/c9r7_full_lake.jpg`, `S/c9r7_laketrain.jpg` |

Timeline: 43.8 s (cut 8 was 42.4 s): stamp 2.1 -> 3.2 s, ticket 2.8 -> 3.2 s, `tunnel` (3.4 s) replaces `viaduct3d`, boy 3.4 -> 3.0 s, boy_b 1.1 -> 1.4 s; dusk shots keep their lengths. Audio regenerated from the cue table (`work/audio/make_audio.py`, `work/audio/cue_table.txt`); timeline and track are unchanged since the round 5 commit (38fa965).

## Review rounds (fresh `claude -p` processes, Read-only, same prompt: `ghibli-scratch/overnight/rev/rN_prompt.txt`)
| Round | Render | Fable | Opus | Haiku | Blocking findings -> fix |
|---|---|---|---|---|---|
| plan | - | REVISE (6) | - | - | all six answered in `PLAN9.md` |
| 1 | `work/out/cut9_r1.mp4` | FAIL | FAIL | FAIL | lake dusk between noon shots; girl's hair/face change in bell; bell -> lick light jump; fold snaps; cat still -> regrade, plate-only grade, dissolve, fold in-betweens, breathe warp |
| 2 | `cut9_r2.mp4` | FAIL (1) | FAIL (1) | FAIL (1) | bird reads white at 28.8-29.7 s; lake wide locked; tunnel entry not visible -> deeper blue sprite; pull-back + truck; slower train, closer camera |
| 3 | `cut9_r3.mp4` | PASS | FAIL (1) | FAIL (1) | lake still pink-lilac between blue shots; bird jump at the boy -> stamp cut -> cloud whitening; earlier, longer hop to the plate |
| 4 | `cut9_r4.mp4` | FAIL (1) | FAIL (1) | FAIL (1) | stamp close-up window (honey sill, plain frame, lettered plate) did not match the boy shots; crane's drop played twice across the 16.8 s cut; wolf "pop" at 26.5-27.0 s (2 fps sampling, not in the film) -> sill and post graded to mahogany, brass bead, plates in the boy shots engraved; shorter hop that is still on the way down at the cut; 10 fps wolf-entry strip added |
| 5 | `cut9_r5.mp4` | FAIL (1) | FAIL (1) | FAIL (1) | boy's costume differs in `boy_b` (plain sleeve, other collar); camera locked on the tunnel beat; window wide locked -> `boy_b` rebuilt on the `boy_close` take played backwards; tunnel truck unclamped, ticket whip-back and push-in; window push-in. Same pass, by class: real ticket fold, lift-off hand-off, window cat 8.5 %, boy 14 % push |
| 6 | `cut9_r6.mp4` | PASS | PASS | PASS | none blocking. Items Fable could not settle from 2-10 fps strips (pose changes at 15.8 / 20.4 s, the cry at 38 s) were answered on the same render with 30 fps strips `S/c9r6_cry30.jpg`, `S/c9r6_pose30.jpg` |
| 7 | `cut9_r7.mp4` (final) | PASS | PASS | PASS | none blocking. Polish before it, from notes two or more reviewers shared in round 6: dusk sleeve dissolve and wing landing, cat missing from the sill close-up, bar under the handlebar. Evidence added after it on the same render: `S/c9r7_breath_stamp.jpg`, `S/c9r7_land30.jpg` |

Versus the reference in round 7 (Fable / Opus / Haiku): tunnel better / better / equal; palm and first crane equal / better / equal; paper -> bird better / better / equal.
Review files: `ghibli-scratch/overnight/rev/r1_*.txt` .. `r7_*.txt`.

## Spend (APIMart, `ghibli-scratch/cost.log`, entries `c9_*`)
$1.09 total: 4 keyframe images (gpt-image-2.6-flare, $0.39) and 5 veo3.1-fast image-to-video takes ($0.70). Log ids: `c9_boy_probe`, `c9_boy_close`, `c9_tunnel_a`, `c9_tunnel_b`, `c9_dusk_a`. Three clips are in the film (`boy_close`, `tunnel` = `tunnel_b`, `dusk`); `tunnel_a` was rejected (`PLAN9.md`); the 8 s probe (`boy_wide` in `work/clips_src`) fed `boy_b` until round 5 and is no longer used.
No spend after the first render.

## Left as is (decisions) and open notes
- Lake train faces the camera with its lamps on but drops back past the signal (same as the reference); doves' look; wolf's red face markings (cut 8 design).
- Beetle now flies off up and right as the wolf rises (three reviewers read "wolf eats the beetle"); the bite takes the blue bird alone. Opus (round 7) still finds the beetle on the bell a distraction.
- Wolf fades at the edges as it leaves the bell shot (spirit look, cut 8 design); wolf scale and drawing differ between the window wide, the bite and the lick shot.
- Pose changes at 15.8 s and 38.0 s are one-to-two-frame swaps in the takes; a faint sleeve ghost remains for a frame or two at 38.0 s (`S/c9r7_cry30.jpg`).
- The blue bird is already close to the palm on the first frame after the 20.0 s cut (cut on the action; all three reviewers noted it, none blocked).
- Stamp hand comes in while the boy's eyes are closed in the shot before; the folds change behind sparkles; the cream ticket reads white once folded.
- Cat's breath is a few pixels in the boy shots (`S/c9r7_breath.jpg`); in the stamp close-up the breath is in the code (rig cat, 6 %) but cannot be read from `S/c9r7_breath_stamp.jpg`, because the push-in changes the cat's scale across the three frames: not confirmed by evidence. The girl is too small in the window and end wides to check her legs there.
- End splashes are faint; the lake wide is a painted plate and looks flatter than the takes; the boy shots move by a slow push only.
- Crane on the palm at 15.3-16.1 s (`S/c9r7_land30.jpg`, asked for by Haiku in round 7): it stays about one palm long from touch-down on; the silhouette changes are wing beats and the landing squash, and the change of the hand near 15.8 s is the pose swap listed above.
- Check on master after the merge: stills at frames 555, 780, 1141, 1142, 1144 and 1150 match the same frames of `work/out/cut9_r7_raw.mp4` (PSNR 34-37 dB, JPEG against H.264); bell frames 966 and 990 show the same picture with 26-32 dB (camera shake and paper bits sampled 4 ms apart).
- Reviews were done on strips and stills (2-30 fps), not on the playing video.

## How to rebuild
`cd work/engine && python3 clips.py && ./render_all.sh 1 30 ../out/raw.mp4 3 && ./finish.sh ../out/raw.mp4 ../audio/track.wav ../out/cut9.mp4`
Evidence: `ghibli-scratch/overnight/mkstrips.sh IN.mp4 TAG`, `mkbreath.sh OUT.jpg`.
