#!/usr/bin/env python3 -I
"""Write handoff/update_note.json: what changed since the last update, as lines keyed by the page section that shows them (commits, changes, gaps). Numbers are computed from files.
usage: update_note.py OLD_DATA_JSON NEW_DATA_JSON DAILY_CSV WEEKLY_LIMIT_CSV OUT_JSON CHANGELOG_CSV [DIM_CSV]
OLD_DATA_JSON is the previously published data.json (git show origin/main:research/token-usage/data.json).
Commit and token totals are summed from daily.csv rows (landed = non-merge, on main, copies collapsed); the old totals
come from the old data.json 'daily' rows, so both sides use one definition. Pace comes from the weekly sample's sampled_at.
Dated events a person decided (cuts applied, test results, restated days) live in research/data/changelog.csv (date,section,text) and are
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
# daily.csv runs to today's UTC date (DAILY_THROUGH) while this runs before the build, so data.json can lag by the days since the last build:
# the shared days must match exactly; days after data.json's last one are allowed, and carry commits only (tokens come with the build)
dn = [r['date'] for r in n]
assert [r['date'] for r in rows][:len(dn)] == dn and all(r['date'] > dn[-1] for r in rows[len(dn):]), 'daily.csv and data.json disagree'
def tot(daily, col): return sum(int(r[col]) for r in daily)
c = lambda x: f'{x/1000:.1f}K' if x >= 1000 else str(x); b = lambda x: f'{x/1e9:.1f}B'
t0, t1 = tot(o, 'tokens_total'), tot(n, 'tokens_total')
notes = {'commits': [], 'changes': [], 'gaps': []}   # each line goes to the page section it belongs to
notes['commits'].append(f"Landed commits, on the main branch only: {c(tot(o,'commits_landed'))} then, {c(tot(rows,'commits_landed'))} now.")
if d1 != d0: notes['changes'].append(f"Data now runs to {d1}, from {d0}.")   # same day: nothing to say; the page already shows the data date
notes['gaps'] += [
  f"Tokens, Claude + Codex, with recovered days: {b(t0)} then, {b(t1)} now.",
  f"Recovered days in that total: {b(sum(int(r['tokens_claude']) for r in rows if r['claude_token_status'] == 'recovered'))}. Headline tiles leave them out.",
]
read = dt.datetime.fromisoformat(wk['sampled_at']).astimezone(dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC') if wk.get('sampled_at') else wk['date']   # the reading time, so the number is not mistaken for end of day
notes['changes'].append(f"Weekly limit: {wk['percent_used']}% used, read {read}.")
if wk.get('sampled_at'):
    now, reset = dt.datetime.fromisoformat(wk['sampled_at']), dt.datetime.fromisoformat(wk['week_reset'])
    gone = 1 - (reset - now) / dt.timedelta(days=7)
    if 0.05 <= gone <= 1:   # just after a reset the ratio is noise; a stale reset date is a bug, so say nothing rather than a wrong pace
        notes['changes'].append(f"Week gone: {gone*100:.0f}%. Pace: {int(wk['percent_used'])/100/gone:.1f}x the limit's.")
# the partial last day is marked on the chart's last bar ("so far"), not in a note
if adv:
    a = sum(int(r['input']) + int(r['output']) for r in adv if r['date'] > (dt.date.fromisoformat(d1) - dt.timedelta(days=8)).isoformat() and r['date'] < d1)
    notes['changes'].append(f"Advisor tokens, input plus output, last 7 days: {a/1e6:.1f}M. Now in every total.")
cut = (dt.date.fromisoformat(d1) - dt.timedelta(days=10)).isoformat()
for r in log:
    if r['date'] >= cut: notes[r['section']].append(r['text'])   # KeyError on a missing or unknown section: fix the csv
json.dump({'data_through': d1, 'sections': notes, 'weekly': {k: wk[k] for k in ('date', 'week_reset', 'percent_used')}}, open(args[4], 'w'), indent=1)
for k, v in notes.items(): print(k + ':', *v, sep='\n  ')
