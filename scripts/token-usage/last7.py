#!/usr/bin/env python3 -I
"""Rebuild handoff/last7.json and last7_daily.csv: the last 7 complete UTC days before data_through.
Claude comes from claude_daily_dim.csv, Codex totals from codex_daily_corrected.csv, fresh/output split from codex_daily_split.csv. Aggregates only.
usage: last7.py HANDOFF_DIR [OUT_DIR]   (OUT_DIR defaults to HANDOFF_DIR)"""
import csv, json, sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

H = Path(sys.argv[1]); OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else H
through = (H/'data_through.txt').read_text().strip()
t = datetime.fromisoformat(through.replace('Z', '+00:00')).astimezone(timezone.utc)
today = t.date()
days = [(today - timedelta(days=n)).isoformat() for n in range(7, 0, -1)]
partial = today.isoformat()


def cache_read_weight(model):
    m = (model or '').lower()
    if 'fable' in m: return .025
    if m in ('claude-opus-5-5', 'claude-sonnet-5-5'): return .05
    return .1


claude = defaultdict(lambda: dict(fresh_input=0, output=0, cache_write=0, cache_read=0, weighted=0.0))
for r in csv.DictReader((H/'claude_daily_dim.csv').open()):
    if r['model'] == '<synthetic>': continue
    c = claude[r['date']]
    c['fresh_input'] += int(r['input']); c['output'] += int(r['output'])
    c['cache_write'] += int(r['cache_creation']); c['cache_read'] += int(r['cache_read'])
    c['weighted'] += int(r['input']) + int(r['cache_creation']) + int(r['output']) + cache_read_weight(r['model'])*int(r['cache_read'])
codex = defaultdict(lambda: dict(fresh_input=0, cached_input=0, output=0))
for r in csv.DictReader((H/'codex_daily_split.csv').open()):
    c = codex[r['date']]
    c['fresh_input'] += int(r['fresh_input']); c['cached_input'] += int(r['cached_input']); c['output'] += int(r['output'])
# Own-token totals come from the corrected series the daily table and the main chart use; the event-date split only supplies fresh and output.
corrected = {r['date']: int(r['own_tokens_corrected']) for r in csv.DictReader((H/'codex_daily_corrected.csv').open())}
for d, x in codex.items():
    if d not in corrected: raise SystemExit(f'codex_daily_corrected.csv has no row for {d}')
    if d in corrected: x['cached_input'] = max(0, corrected[d] - x['fresh_input'] - x['output'])
for d in days:
    if d not in claude or d not in codex:
        sys.exit(f'last7: no Claude or Codex data for complete day {d}; refresh the inputs first')

head = 'date,complete_day,claude_fresh_input,claude_output,claude_cache_write,claude_cache_read,claude_weighted,codex_fresh_input,codex_output,codex_cached_input,codex_total_own'.split(',')
rows = []
for d in days + [partial]:
    c, x = claude.get(d), codex.get(d)
    if c is None or x is None: continue
    flag = 'yes' if d in days else f'partial (data through {t:%H:%M}Z)'
    rows.append([d, flag, c['fresh_input'], c['output'], c['cache_write'], c['cache_read'], round(c['weighted']),
                 x['fresh_input'], x['output'], x['cached_input'], x['fresh_input'] + x['cached_input'] + x['output']])
with (OUT/'last7_daily.csv').open('w', newline='') as f:
    w = csv.writer(f); w.writerow(head); w.writerows(rows)

body = [r for r in rows if r[1] == 'yes']
s = lambda i: sum(r[i] for r in body)
doc = {
    'data_through': through,
    'window': f'{days[0]}..{days[-1]} (last 7 complete UTC days)',
    'partial_today': partial,
    'claude': {'fresh_input': s(2), 'output': s(3), 'cache_write': s(4), 'cache_read': s(5), 'weighted': s(6),
               'weighting': 'input+cache_write+output+cache_read*0.05 (opus/sonnet-5.5; 0.025 fable; 0.1 other)',
               'source': 'data_refresh/claude_daily_dim.csv'},
    'codex': {'fresh_input': s(7), 'cached_input': s(9), 'output': s(8), 'total_own': s(10),
              'weighted': 'NOT_ESTABLISHED (no published Codex cache weights)',
              'source': 'codex_daily_corrected.csv totals (as the daily table); fresh and output from codex_daily_split.csv, cache is the remainder'},
}
(OUT/'last7.json').write_text(json.dumps(doc, indent=1))
print('last7', doc['window'], 'claude weighted', doc['claude']['weighted'], 'codex own', doc['codex']['total_own'])
