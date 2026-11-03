#!/usr/bin/env python3 -I
"""Daily series for the four non-additive sources (Grok log, Benchmark, Router, Task runs).
The page build keeps only their lifetime totals (data.json nonadditive[]); this writes the per-day rows as
research/token-usage/nonadditive_daily.json so the page can plot them. Never added into hero totals.
Every series uses the same row: [date, requests, input, cached, output]; input INCLUDES cached (cached is a subset).
usage: nonadditive_daily.py HANDOFF_DIR OUT_JSON [DATA_JSON]
  DATA_JSON (optional) is checked: per-series input+output must equal its nonadditive[] raw total, else exit 1."""
import csv, json, sys
from collections import defaultdict
from pathlib import Path

H, OUT = Path(sys.argv[1]), Path(sys.argv[2])
DATA = Path(sys.argv[3]) if len(sys.argv) > 3 else None
rd = lambda f: [r for r in csv.DictReader((H/f).open()) if r['date']]

def fold(rows, f):
    acc = defaultdict(lambda: [0, 0, 0, 0])
    for r in rows:
        for i, x in enumerate(f(r)): acc[r['date']][i] += x
    return [[d, *v] for d, v in sorted(acc.items())]

SERIES = [
    ('Grok log', 'OVERLAPS', 'grok_requests_daily.csv',
     lambda r: (int(r['requests']), int(r['prompt_tokens']), int(r['cached_prompt_subset']), int(r['completion_tokens']))),
    ('Benchmark', 'OVERLAPS', 'dispatchbench_requests_daily.csv',
     lambda r: (int(r['requests']), int(r['input']), int(r['cached_subset']), int(r['output']))),
    ('Router', 'ESTIMATE', 'delegate_router_daily.csv',
     lambda r: (int(r['invocations']), int(r['wrapper_input_tokens']), 0, int(r['wrapper_output_tokens']))),
    # Claude task rows report input without cache reads, Codex rows with them; fold both to input-including-cached.
    ('Task runs', 'SUBSET', 'server_task_runs_daily.csv',
     lambda r: (int(r['runs']), max(int(r['input']), 0) + int(r['cached_input']) if r['agent'] == 'claude' else int(r['input']),
                int(r['cached_input']), int(r['output']))),
]
series = [{'name': n, 'tag': t, 'source': s, 'fields': ['date', 'requests', 'input', 'cached', 'output'], 'rows': fold(rd(s), f)}
          for n, t, s, f in SERIES]
out = {'schema': 'nonadditive-daily-v1',
       'through': max(r[0] for s in series for r in s['rows']),
       'note': 'input includes cached. Series overlap the additive lanes or each other and are never summed into totals.',
       'series': series}
bad = []
if DATA:
    raw = {x['name']: x['raw'] for x in json.loads(DATA.read_text())['nonadditive']}
    for s in series:
        got = sum(r[2] + r[4] for r in s['rows'])
        if raw.get(s['name']) != got: bad.append(f"{s['name']}: daily {got} != data.json {raw.get(s['name'])}")
if bad: sys.exit('MISMATCH ' + '; '.join(bad))
OUT.write_text(json.dumps(out, separators=(',', ':')) + '\n')
for s in series: print(f"{s['name']}: {len(s['rows'])} days {s['rows'][0][0]}..{s['rows'][-1][0]}")
