#!/usr/bin/env python3 -I
"""Checks on research/data/. Exit 1 with every failure listed. Two modes:
  check_data.py          CI mode: files only (repo checkout). Series reconcile with the pages' daily table, no day vanishes, pages agree with the data.
  check_data.py --fresh  host mode: also fails when the data is older than 2 days or ends before yesterday (needs the host's clock, so not for CI).
A series that drops a day or shrinks by more than 1% needs an entry in research/data/changelog.csv dated that day with the word 'restated'."""
import csv, datetime as dt, json, re, subprocess, sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
D, TU = REPO / 'research/data', REPO / 'research/token-usage'
rd = lambda p: list(csv.DictReader(open(p)))
bad = []
def fail(msg): bad.append(msg)

meta = json.load(open(D / 'meta.json'))
for name in ('tokens', 'advisor', 'weekly_limit'):  # commits section is checked by its own export
    s = meta.get(name) or {}
    for k in ('generated_at', 'source', 'rows', 'method'):
        if not s.get(k): fail(f'meta.json {name}.{k} missing')
daily = {r['date']: r for r in rd(TU / 'daily.csv')}

# 1. reconcile: tokens_daily per day and actor == daily table; commits (building's files) == daily table
tok = defaultdict(int)
for r in rd(D / 'tokens_daily.csv'):
    tok['claude' if r['source'] in ('main', 'subagent', 'advisor', 'unattributed') else 'codex', r['date']] += int(r['total'])
for d, r in daily.items():
    for a in ('claude', 'codex'):
        if tok[a, d] != int(r['tokens_' + a]): fail(f'{d} {a}: tokens_daily {tok[a, d]} != daily table {r["tokens_" + a]}')
if (D / 'commits_daily.csv').exists():
    c = defaultdict(lambda: [0, 0])
    for r in rd(D / 'commits_daily.csv'): c[r['date']][0] += int(r['commits_landed']); c[r['date']][1] += int(r['commits_all_refs'])
    for d, r in daily.items():
        if c[d] != [int(r['commits_landed']), int(r['commits_all_refs'])]: fail(f'{d}: commits_daily {c[d]} != daily table {r["commits_landed"]}/{r["commits_all_refs"]}')
else: fail('commits_daily.csv missing (building export)')
if rd(D / 'weekly_limit.csv') != rd(TU / 'weekly_limit.csv'): fail('weekly_limit.csv differs between research/data and research/token-usage')

adv = [r for r in rd(D / 'tokens_daily.csv') if r['source'] == 'advisor' and r['date'] >= str(dt.date.fromisoformat(max(daily)) - dt.timedelta(days=30))]
if not adv: fail('no advisor rows in the last 30 days: the acquisition step that adds them did not run')

# 2. no series drops: compare with the committed version on origin/main
log = rd(D / 'changelog.csv') if (D / 'changelog.csv').exists() else []
LAST = max(daily)   # a restatement excuses an older day only when it is entered on this refresh's data-through day
def stated(day): return any(r['date'] >= LAST and r['date'] >= day and 'restated' in r['text'].lower() for r in log)
def base_ref():   # the commit before this one (CI checks out the pushed commit, so origin/main would be this very data); the host checkout has no parent to compare, so it uses origin/main
    for ref in ('HEAD^1', 'refs/remotes/origin/main'):
        if subprocess.run(['git', 'rev-parse', '--verify', '-q', ref + '^{commit}'], cwd=REPO, capture_output=True).returncode == 0 \
           and subprocess.run(['git', 'rev-parse', ref], cwd=REPO, capture_output=True, text=True).stdout != subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=REPO, capture_output=True, text=True).stdout:
            return ref
BASE = base_ref()
if not BASE: print('note: no earlier commit to compare with (shallow checkout); drop check skipped') if '--fresh' not in sys.argv else fail('no base commit for the drop check')
def old(path):
    if not BASE: return []
    p = subprocess.run(['git', 'show', BASE + ':' + path], cwd=REPO, capture_output=True, text=True)
    return list(csv.DictReader(p.stdout.splitlines())) if p.returncode == 0 and p.stdout else []
for fname, key, col in (('tokens_daily.csv', 'date', 'total'), ('commits_daily.csv', 'date', 'commits_landed')):
    if not (D / fname).exists(): continue
    before, after = defaultdict(int), defaultdict(int)
    for r in old('research/data/' + fname): before[r[key]] += int(r[col])
    for r in rd(D / fname): after[r[key]] += int(r[col])
    for d, v in before.items():
        if d not in after: fail(f'{fname}: day {d} vanished'); continue
        if after[d] < v * 0.99 and not stated(d) and not (d == max(before)): fail(f'{fname}: {d} fell {v} -> {after[d]} with no "restated" changelog entry')

# 3. pages agree with the data: every data-exact count on the token page's last-7-days block must come from the series
page = (TU / 'index.html').read_text()
m = re.search(r'last7-values">Fresh input \+ output, with advisor · Claude <span[^>]*data-exact="(\d+)"', page)
if not m: fail('token page 7-day Claude figure not found (label changed? update this check)')
else:
    lo, hi = sorted(tok_d for tok_d in daily)[-8], sorted(daily)[-2]   # last 7 complete days
    want = sum(int(r['input']) + int(r['output']) for r in rd(D / 'tokens_daily.csv') if r['source'] in ('main', 'subagent', 'advisor') and lo <= r['date'] <= hi)
    if abs(int(m.group(1)) - want) > want * 0.01: fail(f'token page 7-day Claude {m.group(1)} != data {want} (input+output, {lo}..{hi})')

wkl = rd(D / 'weekly_limit.csv')[-1]
if f'{wkl["percent_used"]}% used on {wkl["date"]}' not in page: fail(f'token page weekly limit does not show the last sample ({wkl["percent_used"]}% on {wkl["date"]})')

# 4. host mode: freshness
if '--fresh' in sys.argv:
    today = dt.datetime.now(dt.timezone.utc).date()
    if max(daily) < str(today - dt.timedelta(days=1)): fail(f'daily table ends {max(daily)}, today is {today}')
    gen = dt.datetime.fromisoformat(meta['generated_at'])
    if dt.datetime.now(dt.timezone.utc) - gen > dt.timedelta(days=2): fail(f'meta.generated_at {gen:%F} is over 2 days old')
    wk = rd(D / 'weekly_limit.csv')[-1]
    if wk['date'] < str(today - dt.timedelta(days=1)): fail(f'weekly limit last sample {wk["date"]}, today is {today}')
if bad: print('\n'.join('FAIL ' + b for b in bad)); sys.exit(1)
print('data checks ok')
