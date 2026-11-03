#!/usr/bin/env bash
# One command: refetch the source data, rebuild the token-usage page, check it, copy it into this repo.
# usage: scripts/token-usage/refresh.sh [--quick]
#   --quick  reuse the commit, line-count, model and campaign sweeps from the last full run (skips ~20 min); token data is always refetched
# env: TOKEN_USAGE_SRC  generator checkout (default ~/claude-usage-audit); it is not part of this repo
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
SRC="${TOKEN_USAGE_SRC:-$HOME/claude-usage-audit}"
ACQ="$SRC/dashboard-v3-20261031"      # acquisition tree: refresh.sh, sweeps, ledgers
PAGE="$SRC/dashboard-v5-20261031"     # generator: build_v5.py, check_v5.py, handoff/ (sole input), public/ (output)
QUICK=0; [ "${1:-}" = "--quick" ] && QUICK=1
for d in "$ACQ" "$PAGE"; do [ -d "$d" ] || { echo "missing $d (set TOKEN_USAGE_SRC)"; exit 1; }; done

echo "== 1/6 tokens: usage-audit, Claude csvs, Codex sessions, ledger, MCP, storage"
( cd "$ACQ" && ./refresh.sh )
if [ "$QUICK" = 0 ]; then
  echo "== 2/6 commits and lines of code (sweeps every git repo under ~/workspace; ~20 min)"
  ( cd "$ACQ/commits" && python3 -I commit_sweep.py && python3 -I commit_scope.py )
  ( cd "$ACQ/loc" && python3 -I loc_sweep.py > sweep.log 2>&1 && python3 -I loc_agg.py )
  echo "== 3/6 models by week, eth2 campaign"
  ( cd "$ACQ" && python3 -I models/model_weekly.py && python3 -I eth2/eth2_campaign.py )
else
  echo "== 2/6 and 3/6 skipped (--quick)"
fi
echo "== 4/6 Codex daily split, then copy datasets into handoff/ and rebuild the last-7-days files"
( cd "$ACQ" && python3 -I analysis/codex_daily_split.py 2026-10-18 )
python3 -I "$REPO/scripts/token-usage/sync_handoff.py" "$ACQ" "$PAGE/handoff"
( cd "$ACQ" && python3 -I headline_refresh.py "$PAGE/handoff" )
python3 -I "$REPO/scripts/token-usage/last7.py" "$PAGE/handoff"
python3 -I "$REPO/scripts/token-usage/case_studies.py" "$PAGE/handoff"   # section 9 snippet + data, from the same cutoff
echo "== 5/6 build (private + public), verify, leak scan"
( cd "$PAGE" && python3 -I build_v5.py && python3 -I build_v5.py --public && python3 -I check_v5.py && python3 -I public_leak_scan.py )
echo "== 6/6 copy into repo and run the repo's own check"
cp "$PAGE/public/index.html" "$REPO/research/token-usage/index.html"
cp "$PAGE/public/data.json" "$REPO/research/token-usage/data.json"
echo "== 6b traffic: who talks to Fable and how (bus + transcripts) -> data.json[traffic], section-10 snippet"
python3 -I "$REPO/scripts/token-usage/fable_callers.py" "$PAGE/handoff/fable_callers.json" --merge "$REPO/research/token-usage/data.json" --snippet "$REPO/research/token-usage/section10-snippet.html"
( cd "$REPO" && node scripts/check-tokens.mjs )
echo "== 6b/6 consolidated daily table: one sweep, one row per UTC day, then validate"
if [ "$QUICK" = 0 ] || [ ! -f "$ACQ/commits/commits_unified.csv" ]; then
  python3 -I "$REPO/scripts/token-usage/commit_sweep.py" "$ACQ/commits/commits_unified.csv"
fi
python3 -I "$REPO/scripts/token-usage/build_daily.py" "$ACQ/commits/commits_unified.csv" "$REPO/research/token-usage/data.json" "$REPO/research/token-usage/daily.csv"
python3 -I "$REPO/scripts/token-usage/validate_daily.py" "$REPO/research/token-usage/daily.csv" "$REPO/research/token-usage/data.json" --legacy
echo "DONE: data through $(cat "$ACQ/data_through.txt"). Review 'git diff --stat' and open a PR; do not push to main."
