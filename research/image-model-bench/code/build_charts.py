"""Builds the six bench charts (inline SVG with hover tooltips) and models.json/csv.
Run: python3 build_charts.py  -> writes charts.fragment.txt here (image charts), ../../video-model-bench/code/charts.fragment.txt (video charts),
and models.json, models.csv here (image and video rows in one file, the format film-kit reads)."""
import json, csv, html, os
here = os.path.dirname(os.path.abspath(__file__))
vhere = os.path.join(here, '..', '..', 'video-model-bench', 'code')
S = json.load(open(os.path.join(here, 'scores.json')))
R = json.load(open(os.path.join(here, 'results2.json')))
R3 = [r for fn in ('results3.json', 'results4.json', 'results5.json') for r in json.load(open(os.path.join(here, fn)))]
import collections
cost = collections.defaultdict(list)
for r in R + R3:
    if r.get('cost'): cost[r['model']].append(r['cost'])
import statistics
secs = collections.defaultdict(list)
for fn in ('results.json', 'results2.json', 'results3.json', 'results4.json', 'results5.json'):
    for r in json.load(open(os.path.join(here, fn))):
        if r.get('status') == 'completed' and r.get('seconds'): secs[r['model']].append(r['seconds'])
VR = collections.defaultdict(list)
for r in json.load(open(os.path.join(vhere, 'video_results.json'))):
    if r.get('status') == 'completed': VR[r['model']].append(r['latency_s'])
cols = S['pass2_score_columns']
img = []
for m, sc in S['pass2_scores'].items():
    c = cost[m]; q = sum(sc) / len(sc)
    rep = [v for p in S['repeat'].values() for k, v in p.items() if k == m]
    extra = [S['single'][k][m] for k in ('cine', 'pair') if m in S['single'][k]]
    img.append(dict(kind='image', model=m, secs=round(statistics.median(secs[m]), 1), secs_n=len(secs[m]), cost=round(sum(c) / len(c), 4), unit='per image', quality=round(q, 2),
                    detail={k: v for k, v in zip(cols, sc)}, pass3=(dict(repeat_runs=rep, cine_pair=extra) if rep else None)))
# ChatGPT Instant: plan-priced browser lane, speed measured (13 keyframes, median 70 s), cost = $20/(n*30) at n=50/day, never scored
instant = dict(kind='image', model='ChatGPT Instant', secs=70.0, secs_n=13, cost=round(20 / (50 * 30), 4), unit='per image (model: $20 / (50 per day x 30))', quality=None, detail={}, unscored=True)
# video: scores 0-5 in half steps by one reviewer from the 4-frame strips and the clips; see the video bench verdict
V = json.load(open(os.path.join(vhere, 'video_scores.json')))['models']
vid = []
for v in V:
    t = VR[v.get('results_name', v['model'])]
    vid.append(dict(kind='video', model=v['model'], secs=round(statistics.median(t), 1), secs_n=len(t), cost=round(v['usd_per_clip'] / v['clip_seconds'], 4), unit='per second',
                    cost_per_clip=v['usd_per_clip'], seconds=v['clip_seconds'], quality=round((v['identity'] + v['motion'] + v['clean']) / 3, 2),
                    detail=dict(identity=v['identity'], motion=v['motion'], clean=v['clean']), note=v['note']))
json.dump(dict(image=img + [instant], video=vid), open(os.path.join(here, 'models.json'), 'w'), indent=1)
with open(os.path.join(here, 'models.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['kind', 'model', 'usd_per_unit', 'unit', 'quality_0_5', 'median_seconds', 'runs_timed', 'detail'])
    for d in img + [instant] + vid: w.writerow([d['kind'], d['model'], d['cost'], d['unit'], '' if d['quality'] is None else d['quality'], d['secs'], d['secs_n'], json.dumps(d['detail'])])

import math
# maker, for the explorer's "Colour by" select
def family(m):
    for k, f in (('gpt-', 'openai'), ('ChatGPT', 'openai'), ('flux', 'bfl'), ('kling', 'kling'), ('wan', 'alibaba'), ('qwen', 'alibaba'), ('seed', 'bytedance'), ('veo', 'google'), ('Hailuo', 'minimax'), ('hy-', 'tencent')):
        if k in m: return f
    return 'other'

def frontier2(pts, xk, yk, ylog):
    if not ylog: 
        pts = sorted(pts, key=lambda p: (p[xk], -p[yk])); best = -1; out = []; lastx = None
        for p in pts:
            if p[yk] > best or (p[yk] == best and p[xk] == lastx): out.append(p['model']); lastx = p[xk]
            best = max(best, p[yk])
        return set(out)
    # both lower-is-better (cost vs seconds): keep points no other point beats on both
    return {p['model'] for p in pts if not any(q is not p and q[xk] <= p[xk] and q[yk] <= p[yk] and (q[xk] < p[xk] or q[yk] < p[yk]) for q in pts)}

def chart(pts, cid, xlab, ylab, xt, ylo, yhi, title, desc, xk='cost', yk='quality', xf=lambda t: f'${t:g}', ylog=False, yt=None):
    W, H, L, Rr, T, B = 900, 540, 70, 24, 24, 64
    xs = [p[xk] for p in pts]; lo, hi = min(xs) * .8, max(xs) * 1.25
    X = lambda v: L + (math.log(v) - math.log(lo)) / (math.log(hi) - math.log(lo)) * (W - L - Rr)
    Y = (lambda v: T + (math.log(yhi) - math.log(v)) / (math.log(yhi) - math.log(ylo)) * (H - T - B)) if ylog else (lambda v: T + (yhi - v) / (yhi - ylo) * (H - T - B))
    fr = frontier2(pts, xk, yk, ylog)
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="{cid}t {cid}d" id="{cid}"><title id="{cid}t">{html.escape(title)}</title><desc id="{cid}d">{html.escape(desc)}</desc>']
    yvals = yt or [ylo + .5 * i for i in range(int((yhi - ylo) / .5) + 1)]
    for v in yvals:
        o.append(f'<line class="pg" x1="{L}" x2="{W-Rr}" y1="{Y(v):.1f}" y2="{Y(v):.1f}"/><text class="pa2" x="{L-10}" y="{Y(v)+5:.1f}" text-anchor="end">{xf(v) if ylog else format(v, "g")}</text>')
    for t in xt:
        o.append(f'<line class="pg" x1="{X(t):.1f}" x2="{X(t):.1f}" y1="{T}" y2="{H-B}"/><text class="pa2" x="{X(t):.1f}" y="{H-B+22}" text-anchor="middle">{xf(t)}</text>')
    o.append(f'<text class="pa2" x="{(L+W-Rr)/2}" y="{H-12}" text-anchor="middle">{xlab}</text><text class="pa2" transform="translate(18 {(T+H-B)/2}) rotate(-90)" text-anchor="middle">{ylab}</text>')
    fp = sorted([p for p in pts if p['model'] in fr], key=lambda p: p[xk])
    # nudge points that would overlap
    pos = {}
    for p in pts:
        x, y = X(p[xk]), Y(p[yk])
        while any(abs(x - a) < 15 and abs(y - b) < 15 for a, b in pos.values()): x += 15
        pos[p['model']] = (x, y)
    o.append('<polyline class="pf" points="' + ' '.join(f'{pos[p["model"]][0]:.1f},{pos[p["model"]][1]:.1f}' for p in fp) + '"/>')
    placed = [(pos[p['model']][0]-11, pos[p['model']][1]-11, pos[p['model']][0]+11, pos[p['model']][1]+11) for p in pts]
    for p in sorted(pts, key=lambda p: p['model'] not in fr):
        x, y = pos[p['model']]; on = p['model'] in fr
        tip = f"{p['model']}\n${p['cost']:.4f} {p['unit']}\n{p['secs']:g} s median to finish ({p['secs_n']} runs)\n" + ('quality unscored' if p.get('unscored') else f"quality {p['quality']:.2f} of 5\n" + ', '.join(f'{k} {v}' for k, v in p['detail'].items()))
        if p.get('pass3'): tip += f"\nrepeat runs {p['pass3']['repeat_runs']}, cine/pair {p['pass3']['cine_pair']}"
        if p.get('note'): tip += '\n' + p['note']
        tip += '\n' + ('on the frontier' if on else 'beaten on this chart')
        o.append(f'<circle class="{"pb" if on else "pd"}" cx="{x:.1f}" cy="{y:.1f}" r="{9 if on else 7}" tabindex="0" data-model="{html.escape(p["model"])}" data-family="{family(p["model"])}" data-x="{p[xk]:g}" data-y="{p[yk]:g}" data-tip="{html.escape(tip)}" aria-label="{html.escape(tip.replace(chr(10), ", "))}"/>')
        name = p['model'].replace('gpt-image-', 'gpt-img-') + (' (unscored)' if p.get('unscored') else '')
        w = 7.2 * len(name)
        for dx, dy, anc in [(14, 5, 'start'), (-14, 5, 'end'), (0, -16, 'middle'), (0, 28, 'middle'), (14, -14, 'start'), (-14, 22, 'end'), (14, 22, 'start'), (-14, -14, 'end')]:
            lx = x + dx; x0 = lx if anc == 'start' else lx - w if anc == 'end' else lx - w / 2
            box = (x0, y + dy - 12, x0 + w, y + dy + 4)
            if x0 < 4 or x0 + w > W - 4 or box[1] < 2: continue
            if any(not (box[2] < b[0] or box[0] > b[2] or box[3] < b[1] or box[1] > b[3]) for b in placed): continue
            placed.append(box); o.append(f'<text class="{"pl" if on else "pl2"}" data-model="{html.escape(p["model"])}" x="{lx:.1f}" y="{y+dy:.1f}" text-anchor="{anc}">{html.escape(name)}</text>'); break
    o.append('</svg>')
    return '\n'.join(o), len(fr)

fr_img = sorted((p for p in img if p['model'] in frontier2(img, 'cost', 'quality', False)), key=lambda p: (p['cost'], p['model']))
ic, nf = chart(img, 'ci', 'Cost per image (log scale)', 'Quality (mean of 4 scores, 0 to 5)', [.01, .02, .05, .1], 2, 5,
               f'Quality against cost per image for {len(img)} image models',
               'Scored models. Frontier, cheapest first: ' + ', '.join(f"{p['model']} at ${p['cost']:g} scoring {p['quality']:g}" for p in fr_img) + ' (a tie at one price is drawn side by side).')
vc, nv = chart(vid, 'cv', 'Cost per second of video (log scale)', 'Quality (mean of identity, motion, clean; 0 to 5)', [.02, .05, .1], 2, 5,
               'Quality against cost per second for 9 video models',
               'Image-to-video test with two start frames. Frontier models are cheapest or best at their price.')
sec_t = lambda t: f'{t:g} s'
isq, n1 = chart(img, 'cis', 'Median seconds to finish (log scale)', 'Quality (mean of 4 scores, 0 to 5)', [10, 20, 40, 60], 2, 5,
                'Quality against seconds per image', 'Scored image models: median submit-to-file time against quality.', xk='secs', xf=sec_t)
isc, n2 = chart(img + [instant], 'cic', 'Median seconds to finish (log scale)', 'Cost per image', [10, 20, 40, 70], .008, .1,
                'Cost against seconds per image', 'Scored image models plus ChatGPT Instant (unscored, plan-priced cost model at 50 images a day): cost against median time. Lower left is better.', xk='secs', yk='cost', xf=lambda t: f'{t:g}' if t >= 1 else f'${t:g}', ylog=True, yt=[.01, .02, .05, .1])
vsq, n3 = chart(vid, 'cvs', 'Median seconds to finish (log scale)', 'Quality (mean of identity, motion, clean; 0 to 5)', [50, 70, 100, 150, 200], 2, 5,
                'Quality against seconds per clip', 'Video models: median generation time against quality.', xk='secs', xf=sec_t)
vsc, n4 = chart(vid, 'cvc', 'Median seconds to finish (log scale)', 'Cost per second of video', [50, 70, 100, 150, 200], .015, .2,
                'Cost against seconds per clip', 'Video models: cost per second of video against generation time. Lower left is better.', xk='secs', yk='cost', xf=lambda t: f'{t:g}', ylog=True, yt=[.02, .05, .1, .2])
open(os.path.join(here, 'charts.fragment.txt'), 'w').write(f'<!--image {nf}-->\n{ic}\n<!--image speed-->\n{isq}\n<!--image cost speed-->\n{isc}\n')
open(os.path.join(vhere, 'charts.fragment.txt'), 'w').write(f'<!--video {nv}-->\n{vc}\n<!--video speed-->\n{vsq}\n<!--video cost speed-->\n{vsc}\n')
print('image frontier', nf, 'video frontier', nv)
