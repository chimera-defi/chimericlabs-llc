# Shot directions (planner). Times are shot-local seconds unless marked abs. Cues come from timeline.json via L.cue().

General staging: the girl always travels screen-right or away from camera; the wolf always comes from where
she has been. Nobody ever looks at the wolf. The paper bird is WHITE (cycle `bird_white`) for the whole film.
Girl cyclist on screen = pedalling cycle on twos + rotating spokes + contact shadow + hair/scarf wind.
Every shot: camera already moving on frame 0, something moving at two depths in every half second, sprites
tinted toward the plate light with a contact shadow. Look at the plate first and find the real path/rail/
parapet lines in it; place things on those lines.

## 2 ride (3.4-7.2 abs, 3.8 s) plate p3b_plate_coast_wide (try p3_plate_cliff_coast if the path reads better)
Girl from behind (cycle `girl_back`) rides away from camera up the dirt path toward the village; she starts
large low in frame (about 45% of frame height) and shrinks along the path's perspective as she goes (scale
and position follow the path centre line you trace from the plate; tyres on the path). Camera follows: slow
push in and a slight tilt up, so the plate drifts. Foreground: fg_grass_blur streaking past along the bottom
edge (fast, motion-blurred, near depth), fg_foliage_tl wisteria swaying top-left (wind warp), bollard (crop
the bollard half of bollard_puddle; do NOT use the puddle) standing beside the path, passing by parallax.
Cloud band drifting. Dust puffs behind the rear tyre.
Wolf gag 1, from cue wolf_speck (2.6 s local) to the cut: a tiny white wolf (cycle `wolf_side`, about 3-4% of
frame height, hazed toward the sky/cliff colour so it sits far away) bounds along the skyline of the far
headland or cliff top, left to right, toward the village: the same way she is heading. It must read as
"something white is running up there", small and easy to miss on first viewing. No reaction from anyone.
Last 0.25 s: nothing special; clean cut.

## 3 ticket (7.2-10.0 abs, 2.8 s) plate p3_plate_cliff_coast (the village with the viaduct and tunnel)
Starts with the plate strongly blurred (blur 24) and slightly zoomed (1.25). An open hand holding the ticket
(h1_hand_ticket) rises in from the bottom-left, sharp, with a small settle (overshoot). At cue fold (1.0 s
local): the ticket folds into the paper bird: squash the ticket region to a line over 4 frames with a small
white puff/sparkle, hard-swap to hand without ticket (h0_hand_empty is a different arm; if h0 does not match
h1, keep h1 and cover the ticket with the bird, then slide the hand out) with the bird (bird_white, first
frame, wings folded) popping up on the palm with a 4-frame scale pop. The bird hops, flaps twice. At cue
bird_takeoff_hand (1.6 s local) it takes off up and to the right; the hand dips with the push-off and sinks
out of frame; focus racks from near to far (plate blur 24 -> 0 over 0.5 s) and the camera eases back to 1.0;
on the now sharp viaduct the 3-car train (q2_train_side, small, tinted to the plate) rolls along the viaduct
deck toward the tunnel; the bird flies toward the train, shrinking with distance, facing its direction.
The origin of the bird (the girl's ticket) and its destination (the train) must be readable.

## 4 viaduct (10.0-13.4 abs, 3.4 s) plate p4_plate_viaduct_wall, carriage q4_train_window_side
The carriage (close, right side, boy at a window) slides in from the right along the rails and keeps
sliding slowly the whole shot (never parks; its base follows the rail direction in the plate). Camera drifts
right with a small push. The paper bird enters from the left (continuing its flight from shot 3), flies
across toward the boy's window on a smooth arc, flapping, growing as it nears; in the last 0.4 s it is at
the window. Wisteria (fg_foliage_tl) sways in the near foreground, top-left; a couple of swallows
(c4b_swallows, small, far) cross the sky. Wheels/underside of the carriage must not float above the rails.

## 5 boy (13.4-18.6 abs, 5.2 s) plate p5_plate_window_day (interior + window), boy group b1/b2/b2e/b3/b4
The boy sits at the window, right side of frame, in profile facing left; he must read as INSIDE the train:
draw him over the plate, then redraw the plate's near window frame/sill strip (crop from the plate) over his
lower body/arm edge where the sill would cover him, and add the cat with cap (c7_cat_cap) on the sill at
the far left, breathing (slow 2% scale). The landscape outside drifts left at a steady rate (train moving):
since the plate has interior and exterior painted together, fake travel with: a slow camera drift, the
cloud band and far swallows moving, light flicker bands crossing the interior (soft dark vertical bars
passing, as poles go by), and the small outside sprites moving right to left.
Beats: 0.0 b1 (rest) -> 0.5 swap to b2 (palm up) with a 3-frame pop; blink once (b2e for 5 frames) around
1.2. The bird (bird_white) flies in from the upper left on an arc, facing right, and lands on the palm at
cue land_palm (2.2 s local): hard swap b2 -> b3 (bird drawn on palm) exactly at landing, hide the separate
bird sprite, palm dips 10 px and recovers (overshoot). He blinks happily (use b2e only if the bird is then
drawn separately on top; otherwise no blink while b3 is up).
Wolf gag 2 (background, outside the window, on the path in the plate): at 2.4 s local the tiny girl
(girl_side, about 5% frame height, facing and moving right, slowly, since the train is moving the same way)
cycles along the far path; at cue wolf_background (3.2 s local) the wolf
(wolf_side, about 2.3x her height) bounds along behind her at the same speed, gap about 1.5 bike lengths.
Both slightly desaturated/hazed by distance and behind the window glass (a faint reflection streak over
them). The boy never turns.
At cue takeoff_palm (4.5 s local): swap b3 -> b2, bird sprite lifts off toward the left/out of the window
and exits; the boy keeps his palm up, then swap to b4 (arm down, smiling, eyes closed) at 5.0 s.

## 6 lake (18.6-22.0 abs, 3.4 s) plate q1_plate_flooded_rail, train q3_train_front
Wide. The train (front three-quarter view) comes along the flooded line toward camera: it starts small far
down the track and grows along the rail perspective you trace from the plate (base on the rails, a soft
reflection/dark contact strip under it on the water, never hovering). Slow push in plus slight truck right
so the near poles/signal move against the far shore. Water shimmer over the lake area; mist wisps
(s06_mist_wisps) drifting low over the far water; cloud band drifting. The paper bird flies from the train
(it left the boy's window) out over the water toward the right foreground, growing, on a rising arc, and
exits right near the end (it is heading for the girl). A soft wake line at the train's base is optional.

## 7 window (22.0-26.2 abs, 4.2 s) plate q5b_plate_path_wide seen through q6_window_frame; cat c7_cat_cap
We are inside the carriage looking out through the brass-framed window; the landscape slides steadily
right-to-left behind the frame (the train is moving the same way as the girl, a little slower than she
is, so she gains on the window). The plate is wider than the frame opening: pan it continuously. Frame stays still except shakes. Cat with cap sleeps on the sill at lower left, breathing.
Beats: the girl (girl_side, about 22% of frame height, tyres on the dirt path in the plate) is entering
from the left at cue girl_in_window (0.4 s local) and crosses to exit right by about 2.4 s; the paper bird
flies just above and ahead of her, flapping. A 0.5 s beat of empty path (only her dust settling).
At cue wolf_in_window (2.2 s local) the wolf (wolf_side, 2.3x her height, so it nearly fills the window's
height) enters from the left and crosses in about 1.5 s with a bounding arc; at each wolf_thud_N cue it
lands: frame shakes (8-10 px, decaying 0.25 s), dust bursts at the paws, the cat's cap hops a few px and
settles, the cat does not wake. Wolf tinted to daylight with a strong contact shadow on the path.
Interior: the frame sprite and a dark warm interior surround; a faint glass reflection streak.

## 8 bell (26.2-31.2 abs, 5.0 s) plate q7_plate_lake_closeup_bg (blurred 8, scrolling), girl group g1/g2 (not g3)
The money shot. Staging was mocked by the planner: see work/out/pl_bell_mock.jpg, RIGHT half (that is the
bite frame to hit: wolf head BEHIND the girl, jaws around the bird in the open sky at upper right, she smiles
ahead and sees nothing). Close on the girl riding to the right, three-quarter front, sprite at about scale
1.0 with its left edge near x=300 (she fills the left two thirds; upper right is open sky for the bite).
Background plate blurred (8), scrolling right-to-left steadily with a slow bob; her sprite bobs slightly out
of phase; hair and scarf streaming (wind warp on the left part of the sprite where hair and scarf are,
pinned toward the head/neck; keep the face, hands and bell rigid).
The manifest note for the bell top is WRONG; the bell top (where the bird's feet go) is at about x=1085,
y=800 in the 1418x1032 girl canvas. Check by eye.
Beats (local times; all from cues):
- 0.0-1.8: g1 (delighted, mouth open). The white paper bird (bird_white) flies alongside at upper right,
  level with her eyes, flapping, facing right, drifting down toward the bell.
- cue bell_land (1.8): the bird lands on the bell top (small squash of the bird, 3-frame pop, two ring-flash
  arcs = ting). Same frame: hard swap g1 -> g2 (soft smile). The bird sits there (wings folded frame,
  small bob) for 0.6 s.
- cue wolf_rise (2.4): the bird hops off the bell and flutters up and ahead of her to the open sky at upper
  right (around x=1430, y=350), flapping in place there with a small bob, facing right. At the same time,
  BEHIND her (drawn between plate and girl), the wolf head (w3_wolf_head_open, flipped so the snout points
  right, scale about 1.15) rises from the lower left behind her back and slides up and right over 0.9 s
  (ease out, with a slow breath wobble) until its open jaws frame the bird (mouth centre of the flipped
  head = (1040-351, 652) in head px; put it on the bird). The head image has straight cut edges at its
  canvas borders (neck side and top): keep those hidden behind her hair/body or off-frame at every frame.
  The plate darkens a little as the head rises (its shadow). Wolf sharp, slightly cool-tinted, thin rim.
- cue bite (3.4): on ONE frame swap to w3_wolf_head_closed (it has a white paper scrap in its teeth), bird
  gone. Hit-stop: hold the whole picture for 5 frames with a hard 12 px shake, then 10 paper scraps burst
  from the jaws and tumble away on the wind (leftward), one drifts past her face. Then the head sinks back
  down-left behind her and out over 0.7 s (two small chewing bobs on the way).
- After: she is still g2, smiling ahead. At cue bell_ring (4.4): her bell hand twitches (4 px) and two
  ring-flash arcs pop at the bell (ting-ting): she is calling the bird. Last 0.5 s: one last scrap crosses.
Draw order: plate, shadow tint, wolf head, bird (when ahead of her), girl, bird (when on the bell), scraps,
grade. The bite frame must read in a single still: teeth, bird, her calm smile.

## 9 lick (31.2-33.6 abs, 2.4 s) plate q8b_plate_dusk_lake_wide blurred 24, wolf w4_wolf_lick
Smash cut. The wolf, front on, fills most of the frame (head and ruff, about 85% of frame height, centred
slightly right), dusk light: tint it warm-violet toward the plate and give it a warm rim from the sunset
side. Slow push in (1.0 -> 1.08). It breathes (2% vertical squash at 0.8 Hz), fur ruffles in the wind
(wind warp, small), head tilts 2 degrees. At cue lick (0.3): a 4-frame squash pop (the lick), again at
0.75. One paper scrap sits on its nose and at cue gulp (1.5) the head bobs down-up (gulp) and the scrap
blows off and tumbles away right. A few paper scraps drift down through the frame the whole shot.

## 10 duskboy (33.6-36.4 abs, 2.8 s) plate q10b_plate_dusk_clean (window with shutters, dusk lake), boy group
The boy at the window at dusk, palm up (b2), waiting; same placement logic as shot 5 (he is inside: sill in
front of him), tinted to dusk (warm-violet multiply, warm rim from the window). Cat with cap on the sill.
The post with plate 27 (s09_post27) slides past outside from right to left in the first second (near
depth, fast), lake outside shimmering, cloud band drifting. He blinks (b2e, 5 frames) at 0.6.
A single torn paper wing (one white tumbling quad, bigger than the scraps) flutters down from the upper left
on a falling-leaf path and lands on his palm at cue wing_land (1.6 local); palm dips 6 px. He blinks again
and at 2.2 swaps to b4 (arm down, content smile, eyes closed) with a 3-frame pop; the paper wing slides off.

## 11 duskwide (36.4-41.0 abs, 4.6 s) plate q8b_plate_dusk_lake_wide (or q8_plate_dusk_trestle if the
trestle reads better), train q2_train_side, foreground q9_foxglove_foreground and fg_pampas
Wide dusk. The small train crosses the trestle left to right, base on the deck, dusk-tinted, windows
glowing (small warm additive dots are fine), reflection hint in the lake. The girl (girl_side, about 14% of
frame height at the start) cycles left to right along the grass path, tyres on the path; the wolf
(wolf_side, 2.3x her height) lopes after her, 2 bike lengths behind, slowly closing to 1.2 by the end;
both dusk-tinted with a warm rim from the sunset side and long contact shadows; dust at the paws.
Camera pulls back and up the whole shot (plate cover scale 1.3 -> 1.0, drifting), so the figures shrink;
foxgloves and pampas rise into the foreground corners (near depth, wind warp, partly blurred) as the camera
pulls back. Water shimmer, cloud drift. The compositor fades to black from 39.6 abs; keep everything moving
until the last frame. At cue bell_far (2.4 local) two tiny ring-flash arcs at her bell.
