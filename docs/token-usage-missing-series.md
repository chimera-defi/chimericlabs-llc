# Token usage page: Grok log, Benchmark, Router, Task runs

Checked 2026-11-03.

## What happened
The four chips are disabled checkboxes by design. `data.json` `nonadditive[]` holds one lifetime total per source, and `build_v5.py` (around line 1323) never wrote daily rows, so the chart had nothing to toggle. Nothing was deleted. The source CSVs exist and the acquisition `refresh.sh` already regenerates them through `non_codex_audit_v2.py`.

## Recovered
`scripts/token-usage/nonadditive_daily.py` turns the four handoff CSVs into `research/token-usage/nonadditive_daily.json` (schema `nonadditive-daily-v1`, row `[date, requests, input, cached, output]`, input includes cached). It runs in `refresh.sh` and fails if a series does not reconcile with `data.json` `nonadditive[]`. Cutoff is today's data; coverage is below.

| Series | Days | Range | Source |
|---|---|---|---|
| Grok log | 1 | 2026-10-28 | `~/.grok/logs/unified.jsonl` |
| Benchmark | 9 | 2026-10-22 .. 2026-11-02 | `~/workspace/dispatchbench/results/*.jsonl` |
| Router | 49 | 2026-05-24 .. 2026-10-28 | `artifacts/*-delegate/events.jsonl` |
| Task runs | 23 | 2026-10-06 .. 2026-10-30 | `agent-host-chat-control/state/state.sqlite` `task_runs` |

## Unrecoverable
- Grok before 2026-10-28 and after: `unified.jsonl` holds log lines for 10-28, 10-30 and 11-01 only, and `shell.turn.inference_done` (the token event) appears only on 10-28 (136 requests). The 250 `~/.grok/sessions` folders carry no token counts. Grok traffic of 10-26..10-28 still shows up as 217 `cli=grok` rows in the Benchmark series.
- Task runs after 2026-10-30: no `task_runs` or `tasks` rows exist after 10-30 (501 runs, last 10-30). Later `state/tasks/` folders hold a prompt file only and are not in the database.
- Router after 2026-10-28: no delegate ledger has an event after that date (Kimi retired 10-25, last Devin events 10-28). Wrapper-estimated tokens only.

## Capture next
- Grok: copy the daily `inference_done` counts out of `unified.jsonl` into an append-only csv at each refresh, as `ledger_update.py` does for Claude. The log rotates, so skipping a day loses it.
- Task runs: confirm with the server owner whether dispatch writes `task_runs` at all after 10-30. Until it does, the series ends there.
- Router: nothing to capture until a delegate wrapper logs again.
