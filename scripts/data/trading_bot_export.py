#!/usr/bin/env python3 -I
"""Write research/trading-bot-contract/data.json from the read-only on-chain sweep. No network, no model calls.
usage: trading_bot_export.py ONCHAIN_DIR      (ONCHAIN_DIR = mev-bot-0x51c728-explained/onchain, after multiday.py and topfill.py)
Reads multiday.json (one row per 7,200-block window, newest first), topfill.json and flows.json (the studied day, 15 Nov).
Every number the page shows comes out of this file: build.py renders the page from it and refuses a missing key.
Same shape as research/data/meta.json: top-level generated_at, and a meta block with rows, first, last, sources, method."""
import datetime as dt, json, random, statistics, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / 'research/trading-bot-contract/data.json'
SRC = Path(sys.argv[1])
now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
md, top, flows = (json.load(open(SRC / n)) for n in ('multiday.json', 'topfill.json', 'flows.json'))
WIN = sorted(md['windows'], key=lambda r: r['blocks'][0])           # oldest first
LATEST = 14                                                          # the headline window: the last 14 days


def boot(xs, reps=4000, seed=1):
    random.seed(seed)
    b = sorted(statistics.mean(random.choices(xs, k=len(xs))) for _ in range(reps))
    return [round(b[int(reps * .025)]), round(b[int(reps * .975) - 1])]


def stats(xs):
    return dict(n=len(xs), mean=round(statistics.mean(xs)), median=round(statistics.median(xs)), up=sum(x > 0 for x in xs),
                total=round(sum(xs)), ci95=boot(xs))


day = lambda r: dt.datetime.strptime(r['utc'][0][:10], '%Y-%m-%d').strftime('%-d %b')
fill = max((r['top_fill'] for r in WIN), key=lambda f: abs(f['gain_h300_detrended']))
assert fill['hash'] == top['hash'], 'topfill.json is for another fill: rerun topfill.py'
rows = []
for r in WIN:
    s = r['split_h300_detrended']
    row = dict(day=day(r), start_utc=r['utc'][0], blocks=r['blocks'], all=r['net_detrended_usd']['h300'], own=round(s['own_swaps_net_usd']),
               family=round(s['family_net_usd']), outside=round(s['outside_fills_usd']), trades=r['trades'], volume_usd=r['volume_usd'],
               family_cost=round(r['family_cost_usd']), top_size=r['top_fill']['size_usd'])
    row['all_ex'] = row['all'] - (fill['gain_h300_detrended'] if r['top_fill']['hash'] == fill['hash'] else 0)
    row['outside_ex'] = row['outside'] - (fill['gain_h300_detrended'] if r['top_fill']['hash'] == fill['hash'] else 0)
    row['is_fill_day'] = r['top_fill']['hash'] == fill['hash']
    rows.append(row)


def block(rs):
    return dict(days=len(rs), first=rs[0]['day'], last=rs[-1]['day'],
                all=stats([r['all'] for r in rs]), all_ex=stats([r['all_ex'] for r in rs]),
                own=stats([r['own'] for r in rs]), family=stats([r['family'] for r in rs]), family_cost=stats([r['family_cost'] for r in rs]),
                outside=stats([r['outside'] for r in rs]), outside_ex=stats([r['outside_ex'] for r in rs]),
                has_fill=any(r['is_fill_day'] for r in rs))


sets = {'latest': block(rows[-LATEST:]), 'all': block(rows)}
sd = flows
hist = [json.loads(l) for l in open(SRC / 'history.jsonl')]
dep = json.loads(open(SRC / 'raw/creator_txs.jsonl').readline())['timestamp'][:10]   # the contract-creation transaction
usd = lambda h: h['tokens_usd'] + h['eth_usd']
lifetime = dict(deployed=dt.date.fromisoformat(dep).strftime('%-d %b %Y'), first_label=dt.datetime.fromtimestamp(hist[0]['time'], dt.timezone.utc).strftime('%b %Y'),
                first_usd=round(usd(hist[0])), last_label=dt.datetime.fromtimestamp(hist[-1]['time'], dt.timezone.utc).strftime('%-d %b %Y'), last_usd=round(usd(hist[-1])),
                points=len(hist), years=round((dt.date.fromisoformat(WIN[0]['utc'][0][:10]) - dt.date.fromisoformat(dep)).days / 365.25, 1))
curves = [dict(min=p['h_min'], all=p['usd'], lo=p['ci95_hours_usd'][0], hi=p['ci95_hours_usd'][1]) for p in sd['net_after_costs_detrended']]
own_pts = sd['curves_detrended']['operator']['points']
own_cost = sd['curves_detrended']['operator']['cost_usd']
for c, o, t in zip(curves, own_pts, sd['net_after_costs']):
    c['own'] = round(o['markout_usd'] - own_cost)
    c['with_trend'] = t['usd']
data = dict(
    generated_at=now,
    meta=dict(generated_at=now, updated=dt.date.today().strftime("%-d %b %Y"), rows=len(rows), first=WIN[0]['utc'][0][:10], last=WIN[-1]['utc'][0][:10],
              last_block=WIN[-1]['blocks'][1], window_blocks=7200,
              source='Ethereum logs and transactions via public RPC and Blockscout (read-only); prices from DefiLlama 5-minute charts; Binance ETHUSDT klines for the one-fill check',
              scripts='mev-bot-0x51c728-explained/onchain/multiday.py, family.py, flows.py, topfill.py; then scripts/data/trading_bot_export.py',
              method='One window = 7,200 blocks (about one day) after the first. Net = value change of every token the bot moved, priced 5 minutes after each trade, '
                     'day trend removed, minus builder tips and gas of the bot and of the firm\'s other contracts. Ranges: bootstrap of days (4,000 resamples, seed 1).'),
    sets=sets, rows=rows,
    fill=dict(top, gain_share=round(top['gain_defillama_h300_detrended'] / sum(r['all'] for r in rows), 2), label_day=day(next(r for r in WIN if r['top_fill']['hash'] == fill['hash'])), day_all=next(r['all'] for r in rows if r['is_fill_day']), day_ex=next(r['all_ex'] for r in rows if r['is_fill_day'])),
    lifetime=lifetime,
    studied_day=dict(label='15 Nov', trades=sd['net_trades'], volume_usd=sd['net_volume_usd'], curves=curves),
)
OUT.write_text(json.dumps(data, indent=1) + '\n')
# join the shared data layer (research/data/): one CSV of the daily rows, one "trading_bot" section in meta.json (read-modify-write)
SH = REPO / 'research/data'
if SH.is_dir():
    cols = ['day', 'start_utc', 'all', 'all_ex', 'own', 'family', 'outside', 'trades', 'volume_usd', 'family_cost', 'is_fill_day']
    (SH / 'trading_bot_daily.csv').write_text(','.join(cols) + '\n' + ''.join(','.join(str(r[c]) for c in cols) + '\n' for r in rows))
    mp = SH / 'meta.json'
    meta = json.load(open(mp)) if mp.exists() else {}
    meta['trading_bot'] = dict(generated_at=now.replace('+00:00', 'Z'), method=data['meta']['method'], rows=len(rows), source='scripts/data/trading_bot_export.py (reads mev-bot-0x51c728-explained/onchain)')
    mp.write_text(json.dumps(meta, indent=1) + '\n')
print(len(rows), 'windows ->', OUT)
