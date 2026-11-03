# Token usage page

`index.html` and `data.json` here are generated. Do not hand-edit them.

## Refresh

```bash
scripts/token-usage/refresh.sh          # full run, about 25 minutes
scripts/token-usage/refresh.sh --quick  # skips the commit, lines-of-code, model and campaign sweeps
```

One command refetches the source data, rebuilds the page, runs the checks and copies the result here.
Then it runs `node scripts/check-tokens.mjs`. Review `git diff --stat` and open a PR. Never push to `main`.

Stages:

1. Tokens: usage audit, Claude session csvs, Codex sessions, ledger, MCP log, storage.
2. Commits and lines of code across every git repo under `~/workspace` (full run only).
3. Models by week and the node-operations campaign (full run only).
4. Codex daily split. Fresh csv and txt files are copied into the generator's `handoff/` folder. The last-7-days files are rebuilt.
5. `build_v5.py` (private and `--public`), `check_v5.py`, `public_leak_scan.py`.
6. Copy the public page and data here.

The cutoff is the current UTC day. The build stops with "Stale daily input" if any daily source ends before it.

## Where the generator lives

`TOKEN_USAGE_SRC` (default `~/claude-usage-audit`) is the generator checkout. It is not part of this repo.

- `dashboard-v3-*`: data acquisition.
- `dashboard-v5-*/build_v5.py`: generates the page.
- `dashboard-v5-*/check_v5.py`: copy, word-budget and data checks.

To change page copy, edit `build_v5.py` and the matching `check_v5.py` assertion, then refresh.

## Things to know

- Claude deletes old session transcripts after about 30 days. A fresh export loses the early days, so the sync keeps the larger copy of each day in `claude_daily_dim.csv`. Do not clear `handoff/`.
- Not refreshed by the script, edit by hand when they change: `SOURCES.md`, `OTHER_SOURCES.md`, the notes in `handoff/`, `mac_codexbar.csv` (laptop snapshot) and the cost file.
- Cost data and anything marked internal never reach the public page. `public_leak_scan.py` enforces it.
- Crypto content stays out of this page. Crypto-named projects and senders are grouped or masked in the build.

## Share link

The Tokens Over Time chart has a **Share** button. It copies this page's URL with `#hero?...`, which restores the chart state: range, granularity, metric, cumulative, event markers, measurement, lanes and overlay. Defaults are left out, and an unknown value falls back to the default. The link holds no personal data.
