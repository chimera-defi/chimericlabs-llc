# Image model bench: source and data

Page: https://chimericlabs.xyz/research/image-model-bench/ . Units: cost in USD per image (from the task result), time in seconds from submit until the task finishes (polled every 4 s; the image download comes after), quality 0 to 5 from one reviewer.
Key: set `APIMART_API_KEY`; `bench.py` falls back to `~/secrets/apimart_api_key`. The key is never printed or stored here. Run every script from this folder.

## Files
| file | what it is |
|---|---|
| `bench.py` | shared client: submit one image request, poll every 4 s until the task finishes, time it (IPv4 only; the key is allowlisted on IPv4); the pass scripts download the image |
| `run_all.py` | pass 1: 15 models x 3 prompts, writes `results.json` |
| `run2_prompts.py` | the four pass 2 prompts, also used by passes 3 and 4 |
| `run2.py` | pass 2: the four prompts, `run2.py MODEL[,MODEL...] CAP_USD`, appends to `results2.json` |
| `ref.py` | reference test: which models accept a style reference image sent as `image_urls`, writes `ref_results.json` |
| `run3.py` | pass 3: repeat run plus the `cine` and `pair` prompts, `run3.py CAP_USD`, writes `results3.json` |
| `run4.py` | passes 4 and 5: one request at a time under a spend cap, `run4.py MODEL[,MODEL...] CAP [PROMPT,...]`, writes `results4.json`; `RUN4_RESULTS` and `RUN4_OUT` give a later pass its own file and image folder |
| `conc.py` | concurrency test: `conc.py [N]` sends N gpt-image-2 calls at once on the pass 2 valley prompt, writes `concurrency_results.json` |
| `alpha.py` | the real-alpha check (clear > 0.4, half < 0.03), `alpha.py FILE...`, one JSON line per file |
| `sheets3.py` | contact sheets, run 2 against run 3 per prompt |
| `film_frames_gen_v2.py` | the 16 reference-image stills for the film variant, `film_frames_gen_v2.py KEY[,KEY...] MODEL[,MODEL...]`; reads its reference images from the folder set in `R` at the top (not in the repo) |
| `film-frames-ledger.json` | model, prompt, cost and seconds for each of those stills (the script writes it as `ledger.json`) |
| `reference-frame-03.jpg` | the girl used as the reference image in the pass 3 `pair` prompt |
| `chatgpt_images.js` | Playwright script that drives ChatGPT image generation in a Chrome you signed in to yourself (not verified end to end) |
| `results.json` | pass 1, one row per request: model, prompt, status, seconds, cost (USD), file, error |
| `results2.json` | pass 2, same shape |
| `results3.json` | pass 3, same shape |
| `results4.json` | pass 4, same shape |
| `results5.json` | pass 5, same shape |
| `concurrency_results.json` | the 2026-11-23 concurrency run: batch seconds and one row per call (status, seconds, cost). The 2026-11-22 run kept no raw file |
| `alpha_results.jsonl` | `alpha.py` over every props image from passes 1 to 5 |
| `ref_results.json` | reference test: model, param, status, cost, err, file |
| `scores.json` | every quality score (0 to 5) with notes; pass 4 and 5 reasons in `pass4_note` and `pass5_note` |
| `table.md` | pass 1 table: ok of 3, average seconds, average USD per image |
| `table2.md` | pass 2 table with the style, emotion, text-free and alpha scores |
| `build_charts.py` | builds the six charts on both bench pages and writes `models.json` and `models.csv` |
| `models.json` | every scored model, image and video rows, as used by the charts |
| `models.csv` | the same rows: kind, model, USD per unit, unit, quality 0 to 5, median seconds, runs timed, detail |
| `charts.fragment.txt` | the three image charts as SVG, pasted into the page |
| `../chart-toggle.js` | the chart explorer script on both bench pages |

Rebuild the charts after any new run: `python3 build_charts.py`. The video data is in `../../video-model-bench/code/`.

## Run notes
Pass 1 (2026-11-21): Quick pass: 15 models x 3 prompts at 1K, 16:9, one image each. 38 of 45 came back, total $0.93.
Prompts (run_all.py): `props` transparent painted prop sheet, `fear` frightened children and a giant white wolf (does the model get the emotion), `plate` wide Ghibli-style background plate.
Sheets: sheet_props.jpg, sheet_fear.jpg, sheet_plate.jpg (alpha shown on dark green). Raw images: out/. Per-run data: results.json. Cost and time per image come from the task result.
The key is allowlisted on IPv4 only; bench.py forces IPv4.

## Findings
- Real transparency (PNG with alpha, clear > 0.4, half < 0.03): gpt-image-2, gpt-image-2.5-flare, seedream-5-5. Later passes added gpt-image-2.6-flare and sunburst, wan2.7-image-pro and gpt-image-1.5; see `alpha_results.jsonl`. The rest drew a fake checkerboard or a white/cream background, so they are not usable as cut-outs.
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
Run the scripts next to `bench.py`, with the key in `APIMART_API_KEY` (or `~/secrets/apimart_api_key`).

## Charts and the video split (2026-11-22)
`build_charts.py` builds all six charts: the three image charts go to `charts.fragment.txt` here, the three video charts to `../../video-model-bench/code/charts.fragment.txt`. It reads the video runs and scores from `../../video-model-bench/code/` (`video_results.json`, `video_scores.json`) and writes one `models.json` / `models.csv` with image and video rows. Each dot carries `data-model`, `data-family`, `data-x` and `data-y` for the page explorer (`../chart-toggle.js`, shared by both bench pages).
The video test, clips and prompts live in [../../video-model-bench/code/](../../video-model-bench/code/README.md).

## Pass 4 (2026-11-22)
`run4.py MODEL[,MODEL...] CAP [PROMPT,...]` runs the pass-2 prompts one request at a time and refuses any request that could take spend past `CAP` (an unpriced model is assumed to cost $0.20 or the dearest image seen, whichever is more; gpt-image-1.5 billed $0.163). Results go to `results4.json`; `build_charts.py` reads them with passes 2 and 3. Scores are in `scores.json` (`pass2_scores`, reasons in `pass4_note`). Ran flux-3-image-klein, mai-image-2.6-flash (4 prompts each) and gpt-image-1.5 (props only, $0.163), $0.25 in all.

## Pass 5 (2026-11-23)
`RUN4_RESULTS=results5.json RUN4_OUT=<folder> run4.py flux-3-image-klein,mai-image-2.7-flash,z-image-turbo 0.45`: the 4 pass-2 prompts, 12 of 12 returned, $0.10. Scored by Wren (Claude Opus 5.5) beside the pass-2 and pass-4 images; reasons in `scores.json` `pass5_note`. klein's second run gives it repeat runs (run A pass 4, run B pass 5). `build_charts.py` reads `results5.json`.

## Concurrency (2026-11-23)
`conc.py 20`: 20 of 20 completed, median call 21.9 s, batch 34.6 s, $0.17. Images are not downloaded.
