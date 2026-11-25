#!/usr/bin/env bash
# One command: refetch the source data, rebuild the token-usage page, check it, copy it into this repo.
# usage: scripts/token-usage/refresh.sh [--quick]
#   --quick  reuse the commit, line-count, model and campaign sweeps from the last full run (skips ~20 min); token data is always refetched
# env: TOKEN_USAGE_SRC  working folder (default ~/claude-usage-audit): sweeps, ledgers, handoff data and the generator (a local git repo) live there
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
SRC="${TOKEN_USAGE_SRC:-$HOME/claude-usage-audit}"
ACQ="$SRC/dashboard-v3-20261031"      # acquisition tree: refresh.sh, sweeps, ledgers
PAGE="$SRC/dashboard-v5-20261031"     # generator: build_v5.py, check_v5.py, handoff/ (sole input), public/ (output)
QUICK=0; [ "${1:-}" = "--quick" ] && QUICK=1
for d in "$ACQ" "$PAGE"; do [ -d "$d" ] || { echo "missing $d (set TOKEN_USAGE_SRC)"; exit 1; }; done
# The generator is a local git repo in $PAGE (kept out of this public repo: its redaction rules name withheld projects). Build only committed code, and say which.
git -C "$PAGE" diff --quiet HEAD -- build_v5.py check_v5.py public_leak_scan.py site_shell.py codex_daily.py || { echo "generator has uncommitted edits: commit them in $PAGE first"; exit 1; }
echo "generator commit: $(git -C "$PAGE" rev-parse --short HEAD)"

echo "== 1/6 tokens: usage-audit, Claude csvs, Codex sessions, ledger, MCP, storage"
( cd "$ACQ" && TOKEN_REPO="$REPO" ./refresh.sh )
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
python3 -I "$REPO/scripts/token-usage/snapshot_weekly.py" --csv "$REPO/research/token-usage/weekly_limit.csv" --sync-from "${WEEKLY_LIMIT_STATE:-$HOME/.local/state/chimericlabs-llc/weekly_limit.csv}"
cp "$REPO/research/token-usage/weekly_limit.csv" "$PAGE/handoff/weekly_limit.csv"   # the page draws it
python3 -I "$REPO/scripts/token-usage/project_donut.py" "$PAGE/handoff/project_donut.html"   # the building page's donut, same data file
python3 -I "$REPO/scripts/token-usage/last7.py" "$PAGE/handoff"
python3 -I "$REPO/scripts/token-usage/case_studies.py" "$PAGE/handoff"   # section 9 snippet + data, from the same cutoff
cp "$REPO/research/token-usage/case_studies.html" "$PAGE/handoff/case_studies.html"   # the script writes into the repo; the build reads handoff/
echo "== 4b consolidated daily table: one commit sweep, then rows for every UTC day (tokens from the last published data.json until the first build below refreshes them)"
if [ "$QUICK" = 0 ] || [ ! -f "$ACQ/commits/commits_unified.csv" ]; then
  python3 -I "$REPO/scripts/token-usage/commit_sweep.py" "$ACQ/commits/commits_unified.csv"
fi
python3 -I "$REPO/scripts/token-usage/build_daily.py" "$ACQ/commits/commits_unified.csv" "$REPO/research/token-usage/data.json" "$PAGE/handoff/daily.csv"
git -C "$REPO" show refs/remotes/origin/main:research/token-usage/data.json > "$PAGE/handoff/.old_data.json"   # the note says what changed since the page now live
python3 -I "$REPO/scripts/token-usage/update_note.py" "$PAGE/handoff/.old_data.json" "$PAGE/public/data.json" "$PAGE/handoff/daily.csv" "$REPO/research/token-usage/weekly_limit.csv" "$PAGE/handoff/update_note.json" "$REPO/research/data/changelog.csv" "$PAGE/handoff/claude_daily_dim.csv"
rm -f "$PAGE/handoff/.old_data.json"
echo "== 4d events: derived model markers from the raw files, one events file the chart reads"
python3 -I "$REPO/scripts/data/events.py" "$PAGE/handoff" && cp "$REPO/research/data/events.csv" "$PAGE/handoff/events.csv"
echo "== 5/6 build twice (traffic needs the first build's MCP totals), verify, leak scan"
( cd "$PAGE" && python3 -I build_v5.py && python3 -I build_v5.py --public )
# tokens in the daily table must come from this build's data.json, so build the table again and rebuild
python3 -I "$REPO/scripts/token-usage/build_daily.py" "$ACQ/commits/commits_unified.csv" "$PAGE/public/data.json" "$PAGE/handoff/daily.csv"
# section 10: who talks to Fable and how (bus + transcripts); the second build reads these two handoff files
python3 -I "$REPO/scripts/token-usage/fable_callers.py" "$PAGE/handoff/fable_callers.json" --mcp-data "$PAGE/data.json" --snippet "$PAGE/handoff/section10-snippet.html"
( cd "$PAGE" && python3 -I build_v5.py && python3 -I build_v5.py --public && python3 -I check_v5.py && python3 -I public_leak_scan.py )
echo "== 6/6 copy into repo and run the repo's own check"
cp "$PAGE/public/index.html" "$REPO/research/token-usage/index.html"
cp "$PAGE/public/data.json" "$REPO/research/token-usage/data.json"
echo "== 6b traffic block into data.json (paused consumer masked: its name never ships), snippet copy"
python3 -I "$REPO/scripts/token-usage/fable_callers.py" "$PAGE/handoff/fable_callers.json" --merge "$REPO/research/token-usage/data.json" --snippet "$REPO/research/token-usage/section10-snippet.html"
python3 -I - "$REPO/research/token-usage/data.json" "$REPO/research/token-usage/section10-snippet.html" <<'PY'
import json, sys
data_path, snippet_path = sys.argv[1:3]
data = json.load(open(data_path))
data.get("traffic", {}).pop("kepler", None)
text = json.dumps(data, indent=2, ensure_ascii=False).replace("Kepler", "Another consumer")
open(data_path, "w").write(text + "\n")
snippet = open(snippet_path).read().replace(", Codex or Kepler", " or Codex").replace("Kepler", "Another consumer")
open(snippet_path, "w").write(snippet)
PY
# the leak scan ran on the built pages before this merge, so check the repo files it wrote
if grep -qiE 'kepler|crypto' "$REPO/research/token-usage/data.json" "$REPO/research/token-usage/section10-snippet.html"; then echo "LEAK: paused-consumer or crypto name in traffic output"; exit 1; fi
# reconcile the daily non-additive series with the totals the build just wrote, then publish them
python3 -I "$REPO/scripts/token-usage/nonadditive_daily.py" "$PAGE/handoff" "$REPO/research/token-usage/nonadditive_daily.json" "$REPO/research/token-usage/data.json"
( cd "$REPO" && node scripts/check-tokens.mjs )
echo "== 6c/6 daily table into the repo, then validate it against data.json (one commit definition)"
cp "$PAGE/handoff/daily.csv" "$PAGE/handoff/monthly.csv" "$REPO/research/token-usage/"
python3 -I "$REPO/scripts/token-usage/validate_daily.py" "$REPO/research/token-usage/daily.csv" "$REPO/research/token-usage/data.json"
echo "== 7 research/data/: the shared series every page reads (export, building's commit series, checks)"
python3 -I "$REPO/scripts/data/export.py" "$PAGE/handoff"
python3 -I "$REPO/scripts/data/commits.py" "$ACQ/commits/commits_unified.csv" "$REPO/research/data" --through "$(cut -c1-10 "$ACQ/data_through.txt")"   # building page's series, same sweep
python3 -I "$REPO/scripts/data/check_data.py" --fresh
echo "DONE: data through $(cat "$ACQ/data_through.txt"). Review 'git diff --stat' and open a PR; do not push to main."
