# Cut 10: the tunnel/train shot (10.4-13.8 s)

Output: `out_cut10.mp4` (1920x1080, 30 fps, 43.8 s, audio), `out_cut10_720p.mp4`, `out_cut10_poster.jpg`. Cut 9 files untouched.
The first landing changed only shot `tunnel`; the polish pass (below) also changed window, stamp, duskwide and (splash fix) lake.

Problem (operator): in cut 9 the train morphs. The shot was one veo3.1-fast take from one keyframe, and nose, lamps, car count and
perspective drifted. The old shot is kept as `work/engine/shots/tunnel_v9.js` (id `tunnel_v9`).

## What changed
- `work/engine/lib/train3d.js`: a rigid painted train (`q3_train_front`) driven along the measured track by a pinhole camera fitted to
  the plate. The 1.435 m gauge gives the camera height. The sprite is drawn as 5 px column strips pinned to 3D lines; car 2 repeats to 5
  cars; the part past the portal is darkened and clipped to the tunnel opening. Motion blur is a zoom about the vanishing point.
- `work/engine/shots/tunnel.js`: the empty plate (`c10_plate_notrain`, the cut 9 keyframe with the train painted out) plus the code
  train, contact shadow, lamps, car rock, end shake, code water and petals, a foreground mask (arch, pillar, parapet wisteria) over the
  train, and the cut 9 camera move. The bird path was retimed so it leaves ahead of the nose; it no longer sits on the windscreen.
- Optional plate `"tunnelPlate": "veo"` in the timeline (option C): the stabilised veo take of the empty scene from `work/c10/mkplateC.py`.

## Options (cost from `ghibli-scratch/cost.log`, tags `c10_*`; total $0.94, of which veo $0.56 of the $1.2 cap)
| option | what | cost | result |
|---|---|---|---|
| cut 9 | one veo take, one keyframe | (cut 9) | morphs: nose, lamps, car count; perspective swims |
| A | 4 keyframes of the same train (image edit with refs) + veo first+last-frame spans | $0.35 keys + $0.42 (3 probes) | FAILED in all 3 probes. FL mode is always 8 s. Far->mid (A13): a different all-red loco, a second lit train in the tunnel and a pass-by. The two adjacent spans mid->mid (A32) and mid->near (A34): within 0.7 s the take jumps to a new wide framing with the train back in the mouth, re-runs the whole approach and only meets the end key at 8 s. No short span between two keys exists to retime. Chain not bought |
| **B** | code train over the empty still plate | $0.03 | **won**: one rigid train, wheels on rails, tail in the tunnel dark |
| C | B over a veo take of the empty scene (aligned 0.88x + shift, stabilised to <1 px) | $0.03 + $0.14 | rigid train and wisteria sway, but veo painted oversized petal blobs that sit on the roof and pantograph |

Blind strip review (same strip spec for all: 12 frames over the shot + the last 1.4 s at 8 fps; labels W=B, X=A, Y=cut 9, Z=C):
- Fable `reviewer`: W > Z > Y > X ("W is the one to use", no morph found; X morphs: railcar becomes a louvred loco, second train).
- Opus: W > Y > Z > X. Haiku: W > Y > Z > X.
- Fixed after review: bird pasted on the windscreen at the end (path retimed, it now leaves left ahead of the nose before the cut to the
  boy, who holds it in the next shot), end blur too heavy (shutter 0.5 -> 0.3). The reviewers saw the version before these two fixes;
  the final strip from `out_cut10_720p.mp4` is `after_cut10.jpg`.
- The A probes A32/A34 were bought after the review (to test the adjacent-span version of A fairly); strips `A32_probe.jpg`, `A34_probe.jpg`.
- Decided: no steam or wheel dust in B. It is an electric train; Opus and Fable both called cut 9's wheel plume odd.

Strips (`work/c10/strips/`): before `before_c9.jpg`; after `after_cut10.jpg` (graded film, same spec), `B_tunnel.jpg` + `B_detail.jpg`; options `A13_probe.jpg`, `keysA_sheet.jpg`, `C_tunnel.jpg`; cut boundaries `cut10_b1040.jpg`, `cut10_b1380.jpg` (both clean: train in the mouth at 10.4 s, near train to the boy at 13.8 s). Unchanged shots match cut 9 to grain level (mean abs diff < 1/255 at 5, 20.9, 30 s).

## Polish pass (branch `cut10-polish`; no new generation, $0)
Tunnel defects from the first landing, all fixed in code:
- Wisteria sway: `work/c10/mksway.py` builds a cluster map (`x_tun10_sway`, 15 clusters, weight 0 at the stem, 1 at the tip);
  `tunnel.js` backward-warps plate and foreground with it, each cluster with its own phase, ~2 px at the tip plus a small push as
  the train passes. A locked-camera frame difference shows only the clusters moving (the other motion there is the code water).
- Pantograph in frame: the train stops ~1 m further out (s = 4 m) and the camera ends on the plate top; ~100 px of sky stays above
  the pantograph in the last frames (`strips/polish/pantograph_top.jpg`).
- Paint light: `train3d.js` takes `grade(s)` per column; cool shade for 3.5 m out of the portal, then a warm sun catch.

Whole-film review at 5 fps against the reference (frames pulled from the playing video, not stills); top 5:
| # | defect | status |
|---|---|---|
| 1 | wolf oversized in the window wide (head ~5.8x the girl's vs 2.4x in the bite shot) | fixed: scale .95 (was 1.95), now ~2.3x |
| 2 | dove splashes in the end wide invisible at playback size | fixed: bigger crown, 12 droplets, wider rings; the droplet sign bug in `L.splash.crown` (droplets left downward) fixed, which also touches the lake takeoff splashes (≤0.4/255 frame difference) |
| 3 | stamp cat breathing unreadable | fixed: amplitude .06 -> .09 (locked-camera back edge ~9 -> ~16 px) |
| 4 | boy pose swaps at 15.8 s and 37.8-38.6 s (head turn and eye close inside one frame, between generated takes) | open: needs a take edit or an in-between |
| 5 | faint sleeve ghost near 38.0 s (same take seam) | open |
Other shots: raw renders of the 9 unchanged shots are identical (mean abs diff 0.0).

Review (frozen pack: before/after strips, measurements, reference sheets): Opus found that the doubled crown drew its centre
column in front of the dove like a spike, with the droplets going down (blocking); fixed (column .3, crown behind the dove,
droplets up) and re-rendered, `strips/polish/dusk_oldnew.jpg`. Haiku: no blocker; its pantograph worry came from a thumbnail and
the full-res crop shows it clear. Fable `reviewer`: not blocking; pantograph, wolf and cat fixed (cat back +2.5 px at inhale vs old), shade visible
at 10.8-11.6 s, sway under its 720p tracker noise (the locked-camera diff map is the evidence), same splash finding as Opus (saw
the render before that fix). Not changed: the warm catch is a pulse ~4.5 m out of the portal, after it the paint is the sprite's
own sunlit paint (by design); the pantograph passes in front of the top-centre wisteria, which hangs at the portal behind the
train (the near-arch wisteria is in the foreground mask); the pantograph reads pale grey in the tunnel dark at 10.6-10.8 s (minor).
Strips: `work/c10/strips/polish/` (`ba_*.jpg` old vs new at 5 fps, `sway_diffmap.jpg`, `light_cmp.jpg`, `row2.jpg`, `wolfcmp.jpg`).

## Remaining defects
- Boy pose swaps at 15.8 s and 37.8-38.6 s, and the sleeve ghost near 38.0 s (take seams; cost a take edit).
- The paint light ramp is subtle at 720p (reviewers: shade visible, warm catch faint); sway is ~2 px, below a 720p tracker.
- Pantograph reads pale grey inside the tunnel dark (10.6-10.8 s).
- In ride our girl is small and rides away while the reference girl approaches.

## Lesson
More keyframes do not fix a rigid object in a video model: in three probes first+last-frame mode (always 8 s) either invented a
different train or restarted the approach instead of moving between two nearby keys. Code
the rigid object along measured geometry and keep generation for what deforms. Recipe: `film-kit/recipes/rigid-vehicle.md`.
