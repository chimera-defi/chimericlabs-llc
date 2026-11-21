# Image Model Bench (APIMart, 2026-11-21)

Quick pass: 15 models x 3 prompts at 1K, 16:9, one image each. 38 of 45 came back, total $0.93.
Prompts (run_all.py): `props` transparent painted prop sheet, `fear` frightened children and a giant white wolf (does the model get the emotion), `plate` wide Ghibli-style background plate.
Sheets: sheet_props.jpg, sheet_fear.jpg, sheet_plate.jpg (alpha shown on dark green). Raw images: out/. Per-run data: results.json. Cost and time per image come from the task result.
Key lives in ~/secrets/apimart_api_key (mode 600). The key is allowlisted on IPv4 only; bench.py forces IPv4.

## Findings
- Real transparency (PNG with alpha, clear > 0.4, half < 0.03): gpt-image-2, gpt-image-2.5-flare, seedream-5-5. The rest drew a fake checkerboard or a white/cream background, so they are not usable as cut-outs.
- Emotion test: fearful, backing-away kids with the wolf as the threat: gpt-image-2.5-flare, gpt-image-2, seedream-5-0-pro, flux-3-image, qwen-image-3.0, mai-image-2.7-flash. Calm or smiling kids (miss): flux-2-pro, gemini-3-pro-image-preview, minimax-h3 highspeed (stiff, no fear).
- Plates: all models were good; gpt-image-2.5-flare and flux-3-image were the richest.
- Failures: imagen-4.0-apimart failed all three (KeyError 'result', about 62 s each); grok-imagine-image-2.0 rejects the `size` parameter (needs its own request shape, not retried); seedream-5-5 failed the fear prompt (status failed, $0, reason not read).
- Not tested: image editing, consistency across a character, native 2K/4K, Midjourney, FLUX Kontext, Qwen Pro, Wan, Kling.

## Table
| model | ok/3 | avg s | avg $/img |
|---|---|---|---|
| gemini-3.1-flash-lite-image | 3 | 21 | 0.027 |
| gemini-nano-banana-2.1 | 3 | 46 | 0.032 |
| gemini-3-pro-image-preview | 3 | 25 | 0.020 |
| gpt-image-2.5-flare | 3 | 21 | 0.026 |
| gpt-image-2 | 3 | 24 | 0.009 |
| seedream-5-0-pro | 3 | 62 | 0.036 |
| seedream-5-5 | 2 | 24 | 0.016 |
| flux-3-image | 3 | 27 | 0.038 |
| flux-2-pro | 3 | 19 | 0.036 |
| qwen-image-3.0 | 3 | 9 | 0.021 |
| minimax-h3-image-highspeed | 3 | 21 | 0.036 |
| grok-imagine-image-2.0 | 0 | 0 | 0.000 |
| z-image-turbo | 3 | 6 | 0.010 |
| mai-image-2.7-flash | 3 | 16 | 0.008 |
| imagen-4.0-apimart | 0 | 0 | 0.000 |
## Round 3 (2026-11-21)
`run3.py`: 6 models x the 4 round-2 prompts again (run B), plus two new prompts: `cine` (ultra-wide wolf plate) and `pair` (the same girl as in `reference-frame-03.jpg`, via `image_urls`). 36 images, 36 completed, $0.9385 (`results3.json`). Scores for both runs: `scores.json`; contact sheets come from `sheets3.py`.
`film_frames_gen_v2.py` and `film-frames-ledger.json`: the 16 reference-image frames made for the Ghibli film variant.
Run the scripts next to `bench.py`, with the key in `~/secrets/apimart_api_key`.
