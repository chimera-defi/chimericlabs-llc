# Ghibli Claude film: notes, prompts and review material

Page: https://chimericlabs.xyz/research/ghibli-claude/ . These are copies from the private working repos (film engine, film toolkit, scratch folder), which stay private. The engine code and the large videos are not here; the 720p cuts are on the page.
Units: cost in USD per call (`cost.log`), times in seconds of film, strips are frames sampled at the fps their notes give.
Local paths were rewritten: `/home/.../workspace/` was dropped (so `ghibli-scratch/...` means that working folder), session scratch folders read `<scratchpad>` and other temp folders `<tmp>/`. `NOTES10.md` names the strips under `work/c10/strips/`; here they are in `strips/`.

## Files
| file | what it is |
|---|---|
| `reviews/REVIEW12.md` | cut 12: the blind gate against cut 10 and a hidden re-encoded cut 10 twin (Fable, Opus, Haiku), the control read, what was kept, fixed and left |
| `reviews/REVIEW11_opus.md` | cut 11 from the Opus lead: checks, blind rounds, spend, and its A/B record of the two runs |
| `reviews/REVIEW11_fable.md` | cut 11 from the Fable lead: checks, blind rounds, spend, and its A/B record with the head-to-head judges |
| `notes/SPEC11_opus.md` | the cut 11 spec the Opus lead wrote before building |
| `notes/SPEC11_fable.md` | the cut 11 spec the Fable lead wrote before building, with its acceptance checklist (a pass rule per defect, set before the work) |
| `notes/METRICS11_fable.md` | the Fable lead's cut 11 run: wall time, renders, spend, friction rows |
| `notes/LESSONS-cut11-ab.md` | the cut 11 A/B lessons, with the operator's neutral blind rank (cut 10, then Opus cut 11, then Fable cut 11) |
| `notes/NOTES10.md` | cut 10: the code-drawn train, the three tunnel options with costs, the blind review, the polish pass and the open defects |
| `notes/NOTES9.md` | cut 9: each defect, what changed and the before/after strips |
| `notes/PLAN9.md` | the cut 9 plan and its done gate |
| `notes/SHOTS.md` | shot-by-shot directions (the spec the engine shots follow) |
| `notes/CONTRACT.md` | the frozen build contract the engine was first built against (written for the first Fable cut, 41 s) |
| `timeline.json` | cut 10 timeline: 1920x1080, 60 fps, 43.8 s, shot ids with start and end seconds and the cut type |
| `cost.log` | every generation call from attempt B on (tab separated): tag, model, cost in USD ($0 rows included), and a status column filled only for the cut 10 rows; cut 9 tags `c9_*`, cut 10 tags `c10_*`, the rest attempt B |
| `prompts/gen9.py` | cut 9 keyframe and clip helper (gpt-image-2.6-flare, veo3.1-fast) |
| `prompts/gen10.py` | cut 10 veo3.1-fast clip, with the first+last frame mode used for option A |
| `prompts/genkeysA.py` | the four option A keyframes of the same train, prompts verbatim |
| `reviews/review_tmpl.txt` | the prompt template every cut 9 review round used |
| `reviews/plan_prompt.txt`, `plan_fable.txt` | the cut 9 plan review: prompt and Fable's answer |
| `reviews/rN_prompt.txt`, `rN_fable.txt`, `rN_opus.txt`, `rN_haiku.txt` | cut 9 review rounds 1 to 7: the prompt and each reviewer's answer |
| `reviews/cut10_blind_key.txt` | the label key for the cut 10 blind strip review (the answers are summarised in `NOTES10.md`) |
| `strips/` | cut 10 strips named in `NOTES10.md` (before and after, options A, B and C, cut boundaries, keyframe sheet), downsized to at most 1600 px wide |
| `strips/polish/` | the cut 10 polish pass strips (old against new, sway map, light, pantograph, wolf scale) |

The cut 11 and cut 12 files cite evidence paths (`review/blind12/`, sheets, takes, `out/`) in the private film folders; those are not copied. The cut 9 strips named in `NOTES9.md` (129 MB) and the reference-film strips are not copied. All prompts, including the video bench ones, are also in `../../video-model-bench/code/prompts.json`.

## Rerun
The scripts need the private film toolkit (`film-kit`) or the scratch `api.py` client, so they do not run from this folder alone. The toolkit (`gen10.py`, `genkeysA.py`) reads the key from `GEN_API_KEY`, else `~/secrets/apimart_api_key`; the scratch client (`gen9.py`) reads only that file. Neither prints it. Example: `python3 gen10.py vid TAG "PROMPT" start.png end.png` makes one 8 s veo3.1-fast clip in first+last frame mode.
