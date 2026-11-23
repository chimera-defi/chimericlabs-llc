#!/usr/bin/env python3 -I
"""Write handoff/update_note.json: the "What changed since the last update" lines (numbers only, from files).
usage: update_note.py OLD_DATA_JSON NEW_DATA_JSON DAILY_CSV WEEKLY_LIMIT_CSV OUT_JSON [--reason TEXT]
  --reason TEXT  why earlier days changed (checked by hand); without it the line states the change and no reason
OLD_DATA_JSON is the previously published data.json (git show origin/main:research/token-usage/data.json).
Commit and token totals are summed from daily.csv rows (landed = non-merge, on main, copies collapsed); the old totals
come from the old data.json 'daily' rows, so both sides use one definition."""
import csv, json, sys
args = sys.argv[1:]
reason = ''
if '--reason' in args:
    i = args.index('--reason'); reason = args[i + 1]; del args[i:i + 2]
sys.argv = [sys.argv[0]] + args
old, new = (json.load(open(p)) for p in sys.argv[1:3])
rows = list(csv.DictReader(open(sys.argv[3])))
wk = list(csv.DictReader(open(sys.argv[4])))[-1]
def tot(daily, col): return sum(int(r[col]) for r in daily)
o, n = old['daily'], new['daily']
d0, d1 = old['data_through'][:10], new['data_through'][:10]
assert [r['date'] for r in rows] == [r['date'] for r in n], 'daily.csv and data.json disagree'
zero = [r['date'] for r in o if r['commits_landed'] == '0' and r['date'] > '2026-11-01' and r['date'] <= d0]  # incl. the old partial last day
fixed = sum(int(r['commits_landed']) for r in n if r['date'] in zero)
c = lambda x: f'{x/1000:.1f}K' if x >= 1000 else str(x); b = lambda x: f'{x/1e9:.1f}B'
t0, t1 = tot(o, 'tokens_total'), tot(n, 'tokens_total')
nz = {r['date'] for r in o} - set(zero)
delta = sum(int(r['commits_landed']) for r in n if r['date'] in nz) - sum(int(r['commits_landed']) for r in o if r['date'] in nz)  # earlier days, restated
lines = [
  f"Data now runs to {d1}, from {d0}.",
  f"Landed commits: {c(tot(o,'commits_landed'))} then, {c(tot(n,'commits_landed'))} now.",
  f"Tokens, all sources: {b(t0)} then, {b(t1)} now.",
  f"Weekly limit: {wk['percent_used']}% used on {wk['date']}.",
]
if zero:
    lines.append(f"The old table showed zero commits for {zero[0]}..{zero[-1]}: its sweep stopped early. Those days hold {c(fixed)} landed commits.")
if delta: lines.append(f"Earlier days changed by {delta:+d} commits" + (f": {reason}." if reason else "."))
json.dump({'data_through': new['data_through'][:10], 'lines': lines, 'weekly': {k: wk[k] for k in ('date', 'week_reset', 'percent_used')}}, open(sys.argv[5], 'w'), indent=1)
print('\n'.join(lines))
