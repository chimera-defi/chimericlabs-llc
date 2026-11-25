#!/usr/bin/env python3 -I
"""Write the token series into research/data/ from the generator's handoff files. No network, no model calls.
usage: export.py HANDOFF_DIR            (run from scripts/token-usage/refresh.sh, last step)
Writes tokens_daily.csv, weekly_limit.csv, burn_daily.csv and the tokens/weekly_limit/advisor sections of meta.json.
Commit series (commits_daily.csv, commits_monthly.csv, projects.json, before_ai.json) belong to the building page's export; meta.json section "commits".
tokens_daily.csv: date,source,model,input,cache_write,cache_read,output,total; source = main | subagent | advisor (Claude) | codex | unattributed.
 advisor = Fable advisor calls (usage.iterations in transcripts), added to claude_daily_dim.csv by the acquisition refresh; every page total includes them.
 Codex per-model rows start 18 Oct 2026 and use event dates; the daily table uses session dates. A `codex,gap` row (total only) holds days before the split and, from 18 Oct, a signed date-shift so each day ties.
 `unattributed` rows hold days the per-model files lack (recovered or ledger-only days): total only, so every day sums to the daily table."""
import csv, datetime as dt, json, sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
D, TU = REPO / 'research/data', REPO / 'research/token-usage'
H = Path(sys.argv[1])
rd = lambda p: list(csv.DictReader(open(p)))
now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()

rows = defaultdict(lambda: [0, 0, 0, 0])   # (date, source, model) -> input, cache_write, cache_read, output
for r in rd(H / 'claude_daily_dim.csv'):
    a = rows[(r['date'], 'advisor' if r['entrypoint'] == 'advisor' else 'subagent' if r['sidechain'] == 'True' else 'main', r['model'])]
    for i, k in enumerate(('input', 'cache_creation', 'cache_read', 'output')): a[i] += int(r[k])
for r in rd(H / 'codex_daily_split.csv'):
    a = rows[(r['date'], 'codex', r['model'])]
    a[0] += int(r['fresh_input']); a[2] += int(r['cached_input']); a[3] += int(r['output'])
out = [(d, s, m, *v, sum(v)) for (d, s, m), v in rows.items()]
have = defaultdict(int)
for d, s, m, *v, t in out: have['claude' if s in ('main', 'subagent', 'advisor') else 'codex', d] += t
for r in rd(TU / 'daily.csv'):   # days or amounts the model files lack: keep the daily table whole, say so in the source column
    for actor in ('claude', 'codex'):
        gap = int(r['tokens_' + actor]) - have[actor, r['date']]
        if gap > 0 or (gap < 0 and actor == 'codex'): out.append((r['date'], 'unattributed' if actor == 'claude' else 'codex', '-' if actor == 'claude' else 'gap', 0, 0, 0, 0, gap))
out.sort()
D.mkdir(exist_ok=True)
with open(D / 'tokens_daily.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow('date,source,model,input,cache_write,cache_read,output,total'.split(',')); w.writerows(out)
wk = rd(TU / 'weekly_limit.csv'); cols = list(wk[0])
with open(D / 'weekly_limit.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, cols); w.writeheader(); w.writerows(wk)
# burn_daily.csv: who spends, per day: main vs subagent vs advisor, list-price weight (cache read at 0.05 of input; advisor input at full price)
burn = defaultdict(lambda: defaultdict(int))
for d, s, m, i, cw, cr, o, t in out:
    if s in ('main', 'subagent', 'advisor'): burn[d][s] += i + cw + o + cr // 20
adv = [r for r in out if r[1] == 'advisor']
with open(D / 'burn_daily.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow('date,main_weighted,subagent_weighted,advisor_weighted,advisor_share'.split(','))
    for d in sorted(burn):
        b = burn[d]; tot = b['main'] + b['subagent'] + b['advisor']
        w.writerow([d, b['main'], b['subagent'], b['advisor'], round(b['advisor'] / tot, 4) if tot else 0])

meta_p = D / 'meta.json'
meta = json.load(open(meta_p)) if meta_p.exists() else {}
meta['generated_at'] = now
meta['tokens'] = dict(generated_at=now, rows=len(out), first=out[0][0], last=out[-1][0], source='usage-audit per-model csvs (Claude), Codex session logs, daily table',
    method='Claude weighted = input + cache write + output + cache read x 0.05. Subagent = sidechain transcripts. unattributed = Claude tokens in the daily table that the per-model files lack: recovered days (totals only) and a few measured days where the per-model files are short (23 to 30 Sep 2026). Codex own tokens, parent history not counted. Advisor (source=advisor) is included in every Claude total.')
meta['advisor'] = dict(generated_at=now, rows=len(adv), first=adv[0][0] if adv else '', last=adv[-1][0] if adv else '', source='advisor_message rows in usage.iterations of Claude transcripts still on disk',
    method='A floor: transcripts the host has deleted are missing; compressed .zst transcripts are read. One row per unique message id and request id. Weighted at full input price, cache read at 0.05.')
meta['weekly_limit'] = dict(generated_at=now, rows=len(wk), first=wk[0]['date'], last=wk[-1]['date'], source='claude -p /usage, one sample a day (sampled_at is blank before 24 Nov 2026)',
    method='Integer percent used of the weekly limit, all models and Fable. Pace = percent used / share of the week elapsed at sampled_at.')
meta_p.write_text(json.dumps(meta, indent=1, sort_keys=True) + '\n')
print(f'tokens_daily {len(out)} rows, advisor {len(adv)}, weekly {len(wk)}')
