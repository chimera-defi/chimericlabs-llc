#!/usr/bin/env python3 -I
"""Write handoff/update_note.json: the "What changed since the last update" lines (numbers computed from files).
usage: update_note.py OLD_DATA_JSON NEW_DATA_JSON DAILY_CSV WEEKLY_LIMIT_CSV OUT_JSON CHANGELOG_CSV [DIM_CSV]
OLD_DATA_JSON is the previously published data.json (git show origin/main:research/token-usage/data.json).
Commit and token totals are summed from daily.csv rows (landed = non-merge, on main, copies collapsed); the old totals
come from the old data.json 'daily' rows, so both sides use one definition. Pace comes from the weekly sample's sampled_at.
Dated events a person decided (cuts applied, test results, restated days) live in research/data/changelog.csv (date,text) and are
shown for 10 days; no figure is typed into this script."""
import csv, datetime as dt, json, sys
args = sys.argv[1:]
old, new = (json.load(open(p)) for p in args[:2])
rows = list(csv.DictReader(open(args[2])))
wk = list(csv.DictReader(open(args[3])))[-1]
log = list(csv.DictReader(open(args[5])))
adv = [r for r in csv.DictReader(open(args[6])) if r['entrypoint'] == 'advisor'] if len(args) > 6 else []
o, n = old['daily'], new['daily']
d0, d1 = old['data_through'][:10], new['data_through'][:10]
assert [r['date'] for r in rows] == [r['date'] for r in n], 'daily.csv and data.json disagree'
def tot(daily, col): return sum(int(r[col]) for r in daily)
c = lambda x: f'{x/1000:.1f}K' if x >= 1000 else str(x); b = lambda x: f'{x/1e9:.1f}B'
t0, t1 = tot(o, 'tokens_total'), tot(n, 'tokens_total')
lines = [
  f"Data now runs to {d1}, from {d0}.",
  f"Landed commits: {c(tot(o,'commits_landed'))} then, {c(tot(n,'commits_landed'))} now.",
  f"Tokens, Claude + Codex, with recovered days: {b(t0)} then, {b(t1)} now.",
  f"Recovered days in that total: {b(sum(int(r['tokens_claude']) for r in rows if r['claude_token_status'] == 'recovered'))}. Headline tiles leave them out.",
  f"Weekly limit: {wk['percent_used']}% used on {wk['date']}.",
]
if wk.get('sampled_at'):
    now, reset = dt.datetime.fromisoformat(wk['sampled_at']), dt.datetime.fromisoformat(wk['week_reset'])
    gone = 1 - (reset - now) / dt.timedelta(days=7)
    if 0.05 <= gone <= 1:   # just after a reset the ratio is noise; a stale reset date is a bug, so say nothing rather than a wrong pace
        lines.append(f"Week gone: {gone*100:.0f}%. Pace: {int(wk['percent_used'])/100/gone:.1f}x the limit's.")
lines.append(f"The last day, {d1}, is partial, UTC so far. Its short bars are not a fall.")
if adv:
    a = sum(int(r['input']) + int(r['output']) for r in adv if r['date'] > (dt.date.fromisoformat(d1) - dt.timedelta(days=8)).isoformat() and r['date'] < d1)
    lines.append(f"Advisor tokens, input plus output, last 7 days: {a/1e6:.1f}M. Now in every total.")
cut = (dt.date.fromisoformat(d1) - dt.timedelta(days=10)).isoformat()
lines += [r['text'] for r in log if r['date'] >= cut]
json.dump({'data_through': d1, 'lines': lines, 'weekly': {k: wk[k] for k in ('date', 'week_reset', 'percent_used')}}, open(args[4], 'w'), indent=1)
print('\n'.join(lines))
