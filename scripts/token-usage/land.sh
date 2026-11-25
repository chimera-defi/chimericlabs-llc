#!/usr/bin/env bash
# Unattended landing of a data-only refresh: refresh in a scratch worktree, open a PR, merge it with a merge commit when the checks are green.
# usage: land.sh            (run by token-usage-refresh.service; NOT enabled until the operator says so: merging deploys the live site)
# Refuses to land anything outside research/ and docs/. Never force-pushes; keeps the branch. Exit 1 = read the journal.
set -euo pipefail
MAIN="$(cd "$(dirname "$0")/../.." && pwd)"; GH=chimera-defi/chimericlabs-llc
DAY=$(date -u +%F); BR="data-refresh/$DAY"; WT="$HOME/workspace/chimericlabs-data-refresh"
git -C "$MAIN" fetch -q origin main:refs/remotes/origin/main
git -C "$MAIN" worktree remove --force "$WT" 2>/dev/null || true
git -C "$MAIN" worktree add -q -B "$BR" "$WT" refs/remotes/origin/main
cd "$WT"
bash scripts/token-usage/refresh.sh                       # a full run: --quick would fill new days with zero commits
python3 scripts/data/check_data.py --fresh && python3 scripts/build_building_page.py --check
git add -A
[ -n "$(git status --porcelain)" ] || { echo "nothing changed"; exit 0; }
if git diff --cached --name-only | grep -qvE '^(research|docs)/'; then echo "refusing: files outside research/ and docs/"; git diff --cached --name-only; exit 1; fi
git commit -q -m "Data refresh through $DAY (unattended)

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
git push -q origin "$BR"
URL=$(gh pr create -R "$GH" --base main --head "$BR" --title "Data refresh through $DAY" --body "Unattended refresh by token-usage-refresh.service. Data-only diff; check_data.py --fresh and the building check passed before this PR.

🤖 Generated with [Claude Code](https://claude.com/claude-code)")
gh pr merge "$URL" -R "$GH" --merge && echo "landed $URL"
