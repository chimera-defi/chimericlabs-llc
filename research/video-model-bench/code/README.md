# Video model bench (APIMart, test run 2026-11-21; film clips 21 and 22 Nov)

Image-to-video test: 9 models, two start frames from the painted film (the boy at the train window, the wolf over the viaduct), one run per cell. 16 clips, $4.90.

- `video_results.json`: one row per clip (model, start frame, cost in USD, seconds to finish, status, file). The clips are in `../video/`, re-encoded at 640 px.
- `video_scores.json`: identity, motion and clean scores (0 to 5, one reviewer), price per clip, clip length and a note per model.
- `prompts.json`: every prompt on the page, verbatim: the bench prompts, film attempt B (13 ChatGPT keyframes and 13 veo3.1-fast clips) and cut 9 (4 gpt-image-2.6-flare keyframes, 5 veo3.1-fast takes). Image inputs are named, not included.
- `charts.fragment.txt`: the three video charts, written by `../../image-model-bench/code/build_charts.py`, which also writes the combined `models.json` and `models.csv` in that folder.

The generation scripts read a local API key and local film frames, so they are not in this repo. Image bench: [../../image-model-bench/code/](../../image-model-bench/code/README.md).
