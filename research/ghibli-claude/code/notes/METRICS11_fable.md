# METRICS (for the Opus vs Fable comparison)
- start: 2026-11-23T03:23Z (first tool call of the session)
- SPEC11.md written: 2026-11-23T03:31Z
- lead model: Claude Fable 5.2; builders Sonnet (`builder`); reviewers Fable / Opus / Haiku
| milestone | time (UTC) | note |
|---|---|---|
| SPEC11.md | 03:31 | shot list, bible, checklist |
| port of 13 shots committed, parity gate passed | 03:53 | 0.147 to 0.433 against cut 10 at 38 of 39 instants (`review/out/parity.txt`) |
| shot changes committed | 04:15 | ride, seams, dusk take, A-rows |
| render 1 | 04:23 | 1350 frames |
| blind round 1 packs | 04:36 | render 2 |
| code_only.mp4 | 04:38 | 18 s, 1280x720 |
| render 3 (the film) | 04:54 | after round 1 findings |
| blind round 2 packs | 05:06 | Opus 404 s (171,818 tokens), Haiku 79 s, Fable 1854 s (67,364 tokens) |
| kit branch commit `726808c` | 05:20 | 20 node tests, 34 Python tests pass |
| first read of the other run's kit code | 05:22 | on film-kit main, after it merged there; needed for the merge. Render 3 and the REVIEW11.md draft already existed. The other run's film folder was not opened |
| REVIEW11.md, film commit `1cf08eb` | 05:32 | Fable round 2 verdict still pending at this commit |
| kit merge with the other run's kit, commit `37b7db4` | 05:40 | main is the contract; the film renders the same on it (0.000) |
| render 4 (cat box fix only) | 05:51 | first start failed with no frames (`Error: Cannot find module 'playwright'`, PW not exported) |
| blind round 3 packs (no twin, 53 files) | 05:58 | Opus 234 s (145,064 tokens), Haiku 68 s (114,905 tokens), Fable 783 s (179,470 tokens) |
| kit clean-up commit `7049cb5` | 06:02 | duplicate helpers dropped, docs match the merged tools; 20 node, 52 Python tests |
| kit merged to main, `c0a6a27` (--no-ff) | 06:06 | tests pass on main; `film-kit-live` refreshed; branches kept; no push |
| first read of the other run's film folder | 06:09 | after render 4, REVIEW11.md and the Opus and Haiku round 3 verdicts |
| Fable round 3 verdict; gate final (FAIL) | 06:11 | |
| head to head of the two cut 11 films (outside the gate) | 06:14 | Opus 117 s (90,141 tokens), Haiku 33 s (77,124 tokens) |
| kit main `47a305c` (--no-ff): the port recipe's parity figure corrected | 06:22 | docs only, tests not re-run; `film-kit-live` refreshed |

- spend: $0.1655 of $2.50 (veo $0.14 of $1.50); 4 paid calls, all in `cost.log`
- full renders: 4 (each 3 parallel jobs), plus one failed start that wrote no frames
- friction rows: 22 (21 fixed in the kit, 1 open)
- defects closed: 10 of 10 (A1 to A10); checks B, C and E fail by their written rules (see REVIEW11.md)
- blind gate, cut 11 first on (Fable / Opus / Haiku): round 1: 3, 4, 0 of 4; round 2: 1, 3, 1; round 3: 1, 3, 3. FAIL in every round
- lead tokens: not visible from inside the session
- wall time: 03:23 to about 06:25 UTC, about 3 h 02 m (film and first REVIEW11 at 2 h 09 m)
- subagent tokens seen in this session's notices: blind judges only (round 2: Opus 171,818, Fable 67,364; round 3: 145,064 / 179,470 / 114,905; head to head 90,141 / 77,124). Builders and round 1 are not totalled here
