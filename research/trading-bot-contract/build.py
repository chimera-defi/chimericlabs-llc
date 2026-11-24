#!/usr/bin/env python3 -I
"""Render index.html from page.src.html + data.json. Stdlib only, no network.
usage: build.py [--strict]     (run from anywhere; --strict fails if a bare number sits in the source text)
Tokens in page.src.html:
  {{path|fmt}}   a value in data.json. fmt: k signed dollars (+$28k), ku unsigned ($28k), m dollars in millions ($24.1M), n integer with commas, s as is
  {{chart:daily}} {{table:daily}} {{chart:curve}} {{table:curve}}   figures drawn from data.json
A missing path, an unknown token or a leftover {{ fails the build, so a number cannot be typed by hand and go stale."""
import json, re, sys
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
D = json.load(open(HERE / 'data.json'))
MINUS = '−'


def get(path):
    v = D
    for p in path.split('.'):
        try:
            v = v[int(p)] if isinstance(v, list) else v[p]
        except (KeyError, IndexError, ValueError):
            sys.exit(f'build: no data at {path!r}')
    return v


def k(v, sign=True):
    a = abs(v)
    s = f'${round(a / 1000):,}k' if a >= 1000 else f'${round(a):,}'
    return (('+' if v >= 0 else MINUS + '\u2060') if sign else '') + s


FMT = {'k': k, 'ku': lambda v: k(v, False), 'm': lambda v: f'${v / 1e6:.1f}M', 'n': lambda v: f'{round(v):,}', 's': str}


def sub(m):
    path, _, fmt = m.group(1).partition('|')
    return escape(FMT[fmt or 's'](get(path)), quote=False)


# ---- charts -----------------------------------------------------------------------------------------------------------------
def nice_ticks(lo, hi, step=100_000):
    t = [0]
    x = step
    while x <= hi: t.append(x); x += step
    x = -step
    while x >= lo: t.append(x); x -= step
    return sorted(t)


def daily():
    rows, hs = D['rows'], D['sets']['all']
    n = len(rows)
    X0, X1, TOP, BOT = 64, 346, 40, 292
    vals = [r['all'] for r in rows]
    lo, hi = min(vals + [hs['all']['ci95'][0]]), max(vals + [hs['all']['ci95'][1]])
    ticks = nice_ticks(lo, hi)
    span = max(ticks[-1], hi) - min(ticks[0], lo)
    top, bot = max(ticks[-1], hi) + 75_000, min(ticks[0], lo) - 75_000
    y = lambda v: TOP + (top - v) / (top - bot) * (BOT - TOP)
    pitch = (X1 - X0) / n
    bw = pitch * .72
    z = y(0)
    o = []
    for t in ticks:
        o.append(f'<line class="{"zero" if t == 0 else "grid"}" x1="{X0}" x2="{X1}" y1="{y(t):.1f}" y2="{y(t):.1f}"/>')
        o.append(f'<text class="ax" x="{X0 - 6}" y="{y(t) + 5:.1f}" text-anchor="end">{"$0" if t == 0 else k(t)}</text>')
    xs = X0
    o.append(f'<rect class="cib" x="{xs:.1f}" y="{y(hs["all"]["ci95"][1]):.1f}" width="{X1 - xs:.1f}" height="{y(hs["all"]["ci95"][0]) - y(hs["all"]["ci95"][1]):.1f}"/>')
    for i, r in enumerate(rows):
        x = X0 + i * pitch + (pitch - bw) / 2
        v = r['all']
        rest = r['all_ex'] if r['is_fill_day'] else v
        cls = 'dpos' if rest >= 0 else 'dneg'
        yt, yb = sorted((y(rest), z))
        o.append(f'<rect class="{cls}" x="{x:.1f}" y="{yt:.1f}" width="{bw:.1f}" height="{max(yb - yt, .8):.1f}"/>')
        if r['is_fill_day']:
            yt2, yb2 = sorted((y(v), y(rest)))
            o.append(f'<rect class="dfill" x="{x:.1f}" y="{yt2:.1f}" width="{bw:.1f}" height="{yb2 - yt2:.1f}"/>')
        if (abs(v) >= 60_000 and v > 0) or r['is_fill_day']:
            up = v >= 0
            yy = (y(v) - 5) if up else (y(v) + 5)
            o.append(f'<text class="note" transform="translate({x + bw / 2 + 4:.1f} {yy:.1f}) rotate({-90 if up else 90})">{k(v)}</text>')
        if i % 2 == (n - 1) % 2:
            o.append(f'<text class="ax" x="{x + bw / 2:.1f}" y="{BOT + 16}" text-anchor="middle">{r["day"].split()[0]}</text>')
    mean = y(hs['all']['mean'])
    o.append(f'<line class="mean" x1="{xs:.1f}" x2="{X1}" y1="{mean:.1f}" y2="{mean:.1f}"/>')
    o.append(f'<text class="note" x="{X1 + 6}" y="{mean - 2:.1f}">mean</text><text class="note" x="{X1 + 6}" y="{mean + 14:.1f}">{k(hs["all"]["mean"])}</text>')
    o.append(f'<line class="wh" x1="{xs:.1f}" x2="{X1}" y1="{BOT + 30}" y2="{BOT + 30}"/>')
    o.append(f'<text class="ax" x="{X1}" y="{BOT + 48}" text-anchor="end">all {n} days</text>')
    lt = D['sets']['latest']['days']
    o.append(f'<line class="wh" x1="{X1 - lt * pitch:.1f}" x2="{X1}" y1="{BOT + 58}" y2="{BOT + 58}"/>')
    o.append(f'<text class="ax" x="{X1}" y="{BOT + 76}" text-anchor="end">latest {lt} days</text>')
    label = '; '.join(f'{r["day"]}: {k(r["all"])}' for r in rows)
    aria = (f'Bar chart: net US dollars per day, five minutes after each trade and after tips and gas, {n} days. '
            f'Over all {n} days the mean is {k(hs["all"]["mean"])} with a 95% range of {k(hs["all"]["ci95"][0])} to {k(hs["all"]["ci95"][1])}. {label}')
    return (f'<svg class="chart" viewBox="0 0 400 {BOT + 86}" role="img" aria-label="{escape(aria)}"><defs><pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" '
            f'patternTransform="rotate(45)"><line class="hl" x1="0" y1="0" x2="0" y2="6"/></pattern></defs>' + ''.join(o) + '</svg>')


def daily_table():
    th = ''.join(f'<th{" class=txt" if i == 0 else ""}>{h}</th>' for i, h in enumerate(('Day', 'All trades', 'Without the one fill', 'Own swaps', 'Other contracts', 'Quote fills')))
    body = ''.join(f'<tr><td class="txt">{r["day"]}</td><td>{k(r["all"])}</td><td>{k(r["all_ex"])}</td><td>{k(r["own"])}</td><td>{k(r["family"])}</td><td>{k(r["outside"])}</td></tr>'
                   for r in D['rows'])
    return f'<table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>'


def curve():
    c = D['studied_day']['curves']
    X0, X1 = 90, 380
    lo, hi = min(p['lo'] for p in c), max(p['hi'] for p in c)
    ticks = nice_ticks(lo, hi, 200_000)
    top, bot = max(ticks[-1], hi), min(ticks[0], lo)
    x = lambda v: X0 + (v - bot) / (top - bot) * (X1 - X0)
    o = []
    for t in ticks:
        o.append(f'<line class="{"zero" if t == 0 else "grid"}" x1="{x(t):.1f}" x2="{x(t):.1f}" y1="8" y2="208"/>')
        o.append(f'<text class="ax" x="{x(t):.1f}" y="232" text-anchor="middle">{"$0" if t == 0 else k(t)}</text>')
    for i, p in enumerate(c):
        yy = 28 + 40 * i
        o.append(f'<text class="ax" x="66" y="{yy + 5}" text-anchor="end">{p["min"]} min</text>')
        o.append(f'<line class="wh" x1="{x(p["lo"]):.1f}" x2="{x(p["hi"]):.1f}" y1="{yy}" y2="{yy}"/><line class="wh" x1="{x(p["lo"]):.1f}" x2="{x(p["lo"]):.1f}" y1="{yy - 6}" y2="{yy + 6}"/>'
                 f'<line class="wh" x1="{x(p["hi"]):.1f}" x2="{x(p["hi"]):.1f}" y1="{yy - 6}" y2="{yy + 6}"/>')
        o.append(f'<rect class="own" x="{x(p["own"]) - 6:.1f}" y="{yy - 6}" width="12" height="12"/><circle class="dot" cx="{x(p["all"]):.1f}" cy="{yy}" r="4.5"/>')
    aria = ('Dot-and-whisker chart: net US dollars of all trades after tips and gas, with the 95% range, and of its own swaps alone, by minutes after the trade. '
            + '; '.join(f'{p["min"]} min: {k(p["all"])} ({k(p["lo"])} to {k(p["hi"])}), own swaps {k(p["own"])}' for p in c))
    return f'<svg class="chart" viewBox="0 0 400 242" role="img" aria-label="{escape(aria)}">' + ''.join(o) + '</svg>'


def curve_table():
    th = ''.join(f'<th{" class=txt" if i in (0, 2) else ""}>{h}</th>' for i, h in enumerate(('Minutes after', 'After tips and gas', '95% range', 'Its own swaps, after tips and gas', 'With the trend')))
    body = ''.join(f'<tr><td class="txt">{p["min"]}</td><td>{k(p["all"])}</td><td class="txt">{k(p["lo"])} to {k(p["hi"])}</td><td>{k(p["own"])}</td><td>{k(p["with_trend"])}</td></tr>'
                   for p in D['studied_day']['curves'])
    return f'<table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>'


BLOCKS = {'chart:daily': daily, 'table:daily': daily_table, 'chart:curve': curve, 'table:curve': curve_table}

src = (HERE / 'page.src.html').read_text()
# <!--need: expr--> pins a claim in the words to the data: when new data break it, the build fails and the sentence must change
for expr in re.findall(r'<!--need: (.+?)-->', src):
    ok = eval(re.sub(r'[a-z_][\w.]*', lambda m: repr(get(m.group(0))) if m.group(0) not in ('and', 'or', 'not') else m.group(0), expr))
    if not ok:
        sys.exit(f'build: the words no longer hold: {expr}')
src_out = re.sub(r'<!--need: .+?-->\n?', '', src)
out = re.sub(r'\{\{(chart:\w+|table:\w+)\}\}', lambda m: BLOCKS[m.group(1)](), src_out)
out = re.sub(r'\{\{([\w.]+(?:\|\w+)?)\}\}', sub, out)
if '{{' in out:
    sys.exit('build: unresolved token near ' + out[out.index('{{'):][:80])
(HERE / 'index.html').write_text(out)

# coverage: numbers typed in the source outside tags, scripts, styles and tokens
txt = re.sub(r'<(script|style|svg)\b.*?</\1>', '', src, flags=re.S)
txt = re.sub(r'<[^>]+>|\{\{.*?\}\}', ' ', txt)
bare = re.findall(r'[+−$]?\d[\d,.]*', txt)
print(f'build: index.html written ({len(out):,} bytes). Numbers typed in the source text: {len(bare)}')
if '--strict' in sys.argv and bare:
    sys.exit(1)
