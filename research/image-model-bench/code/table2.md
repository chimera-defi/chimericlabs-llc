| model | ok/4 | avg s | avg $/img | style | emotion/faces | text-free | edge/alpha | real alpha |
|---|---|---|---|---|---|---|---|---|
| gpt-image-2.6-flare | 4 | 12 | 0.026 | 5 | 5 | 5 | 5 | True |
| gpt-image-2.6-sunburst | 4 | 29 | 0.026 | 5 | 5 | 5 | 5 | True |
| flux-2-max | 4 | 34 | 0.080 | 3 | 3 | 5 | 2 | False |
| flux-kontext-max | 4 | 22 | 0.064 | 2 | 2 | 5 | 1 | False |
| qwen-image-3.0-pro | 4 | 13 | 0.029 | 4 | 4 | 3 | 2 | False |
| kling-v4-image | 4 | 35 | 0.057 | 4 | 2 | 2 | 2 | False |
| flux-3-image | 4 | 24 | 0.038 | 4 | 3 | 5 | 2 | False |
| flux-2-flex | 4 | 25 | 0.080 | 4 | 3 | 5 | 2 | False |
| seedream-5-0-pro | 4 | 53 | 0.036 | 4 | 3 | 5 | 2 | False |
| gpt-image-2.5-flare | 4 | 22 | 0.026 | 4 | 4 | 5 | 5 | True |
| gpt-image-2 | 4 | 24 | 0.009 | 4 | 4 | 5 | 5 | True |
| wan2.7-image-pro | 4 | 29 | 0.054 | 3 | 3 | 5 | 4 | True |
| midjourney | 0 | 0 | 0.000 | 0 | 0 | 0 | 0 | - |
| hy-image-v3.5-preview | 4 | 20 | 0.019 | 3 | 3 | 4 | 3 | False |

midjourney: all 4 rejected (model_price_error: price not configured on APIMart). Kling-v4-image needs resolution 2K+ (run at 2K) and painted a sign and a lantern in kanji, so it fails text-free. Qwen 3.0 pro put Japanese text on the ticket.

## Verdicts
- Faces/emotion: gpt-image-2.6-flare (best expression, true fear, wide eyes, huddled, cheapest of the top tier at about $0.026); 2.6-sunburst equal but slower. Of the Flux line, flux-2-flex and flux-3-image are decent but calmer faces; flux-2-max has a speckled, noisy texture and kontext-max is weak (tiny distant kids).
- Plates (valley, wolf/viaduct): gpt-image-2.6-flare/sunburst richest; flux-3-image is a good second with the best Ghibli background feel at 0.038; seedream-5-0-pro and qwen-3.0-pro are clean. Expensive flux-2-max (0.08) is not better than flux-3-image.
- Prop sheets: only gpt-image-2/2.5/2.6 (flare, sunburst) and wan2.7-image-pro give true alpha; use gpt-image-2.6-flare (cleanest, hard edges). Flux and Seedream draw a fake checkerboard or white backdrop.
- Cost-efficient: gpt-image-2 at $0.0085 is the pick for props and bulk; gpt-image-2.6-flare at $0.026 when quality matters.

## Reference image
All six tested (gpt-image-2.5-flare, flux-kontext-max, seedream-5-0-pro, gemini-3-pro-image-preview, qwen-image-3.0-pro, flux-3-image) accept `image_urls: [<url or data:image/jpeg;base64,...>]` in the same request. Sheet: sheet2_ref.jpg. All kept the style and layout; the Gemini and gpt outputs reproduced the reference composition most closely, seedream and flux-3 restyled the bridge more freely. Cost: $0.200 for the six.

Total round 2 spend: $2.38 (cap $6).
