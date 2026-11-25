#!/usr/bin/env python3 -I
"""Write research/data/events.csv (date,label,kind,source): the only event list the Tokens over Time chart reads.
usage: events.py HANDOFF_DIR      (run from refresh.sh after export.py). No network, no model calls.
Rows with source 'raw: ...' are DERIVED every run: first day each Claude model has tokens in claude_daily_dim.csv (>= 1M own tokens),
and first/last day each Codex model appears in codex_session_files.csv (>= 200 session files). 'last' is dropped if the model is still in use.
Every other row (kind tooling | policy | plan) is kept as is: the source column holds a URL, or 'unsourced: ...' when none is on record.
A plan-price row needs a URL; the check fails the run otherwise."""
import csv, datetime as dt, re, sys
from collections import defaultdict
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / 'research/data/events.csv'
H = Path(sys.argv[1])
rd = lambda p: list(csv.DictReader(open(p)))
nice = lambda m: re.sub(r'(\d)-(\d)', r'\1.\2', m.removeprefix('claude-')).replace('-', ' ').title()

claude_first, claude_tot = {}, defaultdict(int)
for r in rd(H / 'claude_daily_dim.csv'):
    own = int(r['input']) + int(r['output'])
    if own > 0:
        claude_first[r['model']] = min(claude_first.get(r['model'], '9'), r['date']); claude_tot[r['model']] += own
codex = defaultdict(lambda: ['9', '', 0])
for r in rd(H / 'codex_session_files.csv'):
    if r['first_ts']:
        a = codex[r['model']]; a[0] = min(a[0], r['first_ts'][:10]); a[1] = max(a[1], r['last_ts'][:10]); a[2] += 1
end = max(a[1] for a in codex.values()); start = min(a[0] for a in codex.values())   # a model already in use on the first data day has no known start

rows = []
for m, d in claude_first.items():
    if claude_tot[m] >= 1_000_000 and not m.startswith('claude-haiku-4'):
        rows.append((d, nice(m) + ' first appears', 'model', 'raw: claude_daily_dim.csv (first day with tokens)'))
for m, (a, b, n) in codex.items():
    if n >= 200:
        if a != start: rows.append((a, f'Codex {m} first used', 'model', 'raw: codex_session_files.csv (first session start)'))
        if (dt.date.fromisoformat(end) - dt.date.fromisoformat(b)).days > 7:
            rows.append((b, f'Codex {m} last used', 'model', 'raw: codex_session_files.csv (last session end)'))
keep = [(r['date'], r['label'], r['kind'], r['source']) for r in rd(OUT) if not r['source'].startswith('raw:')] if OUT.exists() else []
for d, label, kind, src in keep:
    assert kind in ('tooling', 'policy', 'plan'), (label, kind)
    assert kind != 'plan' or src.startswith('https://'), f'plan-price row needs a source URL: {label}'
rows = sorted(set(rows + keep))
with open(OUT, 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['date', 'label', 'kind', 'source']); w.writerows(rows)
print(f'events.csv: {len(rows)} rows ({len(keep)} kept by hand, rest derived from raw data)')
