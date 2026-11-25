# Video model bench: source and data

Page: https://chimericlabs.xyz/research/video-model-bench/ . Units: cost in USD per clip (from the task result), time in seconds from submit to finished clip (polled every 8 s; the Flow clips: 10 s polls in a browser), scores 0 to 5 from one reviewer.
Key: set `APIMART_API_KEY`; `run_video.py` uses the client in `../../image-model-bench/code/bench.py`, which falls back to `~/secrets/apimart_api_key`. The key is never printed or stored here.

## Files
| file | what it is |
|---|---|
| `run_video.py` | the bench script: one image-to-video clip, `run_video.py MODEL boy\|wolf TAG OPTIONS_JSON`; `@IMG` in the options is replaced by the start-frame URL from `in/urls.json` (not in the repo: write your own, `{"boy": "<start frame URL>", "wolf": "<start frame URL>"}`, public URLs) |
| `video_results.json` | one row per clip (model, start frame, cost in USD, seconds to finish, status, file). The clips are in `../video/`, re-encoded at 640 px |
| `video_scores.json` | identity, motion and clean scores (0 to 5, one reviewer), price per clip, clip length and a note per model |
| `prompts.json` | every prompt on the page, verbatim: the bench prompts, film attempt B (13 ChatGPT keyframes and 13 veo3.1-fast clips), cut 9 (4 gpt-image-2.6-flare keyframes, 5 veo3.1-fast takes) and the cut 10 first+last frame sets. Image inputs are named, not included |
| `native_resolution.json` | ffprobe of the 16 original clips: width, height, fps and length per model; the two Flow rows are from the browser player (no fps, wolf size not read), and their clips were not saved here |
| `charts.fragment.txt` | the three video charts as SVG, pasted into the page |

Built elsewhere: `../../image-model-bench/code/build_charts.py` writes `charts.fragment.txt` here and the combined `models.json` and `models.csv` (image and video rows) in that folder.

Not recoverable: the per-model request options (image field, duration, resolution) were passed on the command line and not logged, so a rerun needs them from each model's API docs. The film clips (attempt B, cut 9, cut 10) were made with the private film toolkit and are not rerunnable from here; the film's notes and prompts are in `../../ghibli-claude/code/`.
