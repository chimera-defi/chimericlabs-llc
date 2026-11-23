"""Option A keyframes: the same train at 4 more positions, edit mode from the cut 9 keyframe (key_tunnel = the mid keyframe) + the train sprite."""
import sys
sys.path.insert(0, 'film-kit')
from filmkit.gen import Gen
S = '<scratchpad>'
g = Gen(out='keysA', log='ghibli-scratch/cost.log')
BASE = ("Edit the first image. Keep the painting exactly the same: same framing and camera, same stone arch with wisteria, tunnel, track, parapets, sea, town, clouds, "
        "same hand-painted gouache style and light. Keep the SAME train exactly as drawn (the second image shows it): red lower body with a thin gold stripe, cream upper body, "
        "three front windows, one big round lamp on the roof above the windows and two round lamps low on the front, a diamond pantograph on the roof, grey-blue roof, "
        "carriages joined by dark bellows. Only move the train along the same track: ")
POS = {
  'k1': "the train is far away, just coming out of the dark tunnel mouth: only the front of the first carriage is out, small, its three lamps glowing; the rest is still inside the dark tunnel.",
  'k2': "the train is about one third of the way from the tunnel toward the viewer, smaller than in the first image, its first carriage fully out of the tunnel and the second carriage coming out.",
  'k4': "the train is close to the viewer: the front of the first carriage is large, about twice the size it is in the first image, standing on the track in the lower middle of the picture, with the carriages stretching back to the tunnel.",
  'k5': "the train is passing very close to the viewer: the front of the first carriage is at the left of the picture, very large, cut by the bottom edge, and the side of the carriages fills the middle and right of the picture back to the tunnel.",
}
for k, p in POS.items():
    try: print(k, g.image('c10_A_' + k, BASE + p + " No text, no people.", refs=[S + '/key_tunnel_small.jpg', S + '/train_ref.jpg'], model='gpt-image-2.6-flare'))
    except Exception as e: print(k, 'FAIL', e)
