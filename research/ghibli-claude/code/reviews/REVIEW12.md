# Cut 12 receipt

Written by Wren (Claude Opus 5.5) on behalf of chimera-defi.

**Gate: PASS.** In one blind round, Fable, Opus and Haiku each put cut 12 first on all 4 criteria. The pack held cut 12, cut 10 and a hidden re-encoded twin of cut 10, with 30 fps sheets around all four seams and the window exit. Scores, answers and the key are in `review/blind12/`.

- **Control.**
  - Fable and Opus scored cut 10 and its twin identically.
  - Haiku scored them 2 apart on polish. Its margins over the better cut 10 entry are only 1-2, so by the rule fixed before judging its whole pass is within its noise. The gate stands as computed, but it rests on Fable and Opus.
- **What the judges credited.** The lick straight cut, the duskboy (no see-through sleeve, no blurred posts) and the wolf at the window exit. Fable saw no difference at seams 1, 2, 4, 6 and 7, so the eye in-betweens and the smear fix went unseen at 320 px. Fable and Opus scored the bird rise into boy_b against cut 12.
- **Disclosed.** The 28.2-29.2 s window-exit sheet was added by the builder, outside the operator's four seams, and all three judges cite it. Fable and Opus credit cut 12 with a closed-eye smile to the end. At 1080p the mouth turns down from 38.9 s; 320 px hides it.
- **Base.** Cut 10 at 43.8 s, with cut 10's timing and score. Every cut 11 change not on the list was reverted. Parity against the cut 10 engine passes on 10 shots, also on kit main 09fe65f.
- **Kept or ported.**
  - The bird rise into boy_b.
  - The straight cut to the wolf at 34.0 s (the lick).
  - Fable's eye in-betweens at 15.8 s, imported with `filmkit import clip_boy_close=boy_close`.
  - The "wolf snap at the crane" is the bell bite. Fable's frames are identical to cut 10's, and cut 12's bite passes parity against cut 10 at 32.3, 32.45 and 32.6 s, so there was nothing to port.
- **Fixed.**
  - The crane smear (the take's own bird remnant over the lake, source frames 63-91), painted out with `seam --hold 62 --src 95 --keep-warm 40`.
  - The wolf leaves the window at the cut (28.97 s), not 0.6 s early: it now runs at 1080 px/s and the thud times are unchanged.
  - The dusk window: the cut 11 duskboy (retimed, 0.59x tail, sleeve hold) has no blurred posts.
- **Ride.** Cut 10 framing (RESTAGE=false).
- **Residuals the judges named against cut 12.**
  - In boy_b the bird enters low by the sill after leaving the stamp shot through the top (19.97 s).
  - The wolf thins out at the right edge in its last frames (28.8-28.97 s).
  - The take's frown from 38.9 s is kept, as in cut 10.
- **Spend.** $0 new API spend. The judges and the advisor ran on Claude CLI, and all three Fable uses are in the ledger.
- **Decided.** Wolf snap = no-op. "Blurred post" = the dusk window posts. No fixes after the gate.
