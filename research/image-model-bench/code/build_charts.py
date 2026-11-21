"""Builds the two cost-vs-quality charts (inline SVG with hover tooltips) and models.json/csv.
Run: python3 build_charts.py  -> writes charts.fragment.txt (fragments) and models.json, models.csv next to it."""
import json, csv, html, os
here = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(here, 'scores.json')))
R = json.load(open(os.path.join(here, 'results2.json')))
R3 = json.load(open(os.path.join(here, 'results3.json')))
import collections
cost = collections.defaultdict(list)
for r in R + R3:
    if r.get('cost'): cost[r['model']].append(r['cost'])
cols = S['pass2_score_columns']
img = []
for m, sc in S['pass2_scores'].items():
    c = cost[m]; q = sum(sc) / len(sc)
    rep = [v for p in S['repeat'].values() for k, v in p.items() if k == m]
    extra = [S['single'][k][m] for k in ('cine', 'pair') if m in S['single'][k]]
    img.append(dict(kind='image', model=m, cost=round(sum(c) / len(c), 4), unit='per image', quality=round(q, 2),
                    detail={k: v for k, v in zip(cols, sc)}, pass3=(dict(repeat_runs=rep, cine_pair=extra) if rep else None)))
# video: scores 0-5 in half steps by one reviewer from the 4-frame strips and the clips; see verdict
V = [  # model, $ per clip, seconds, identity, motion, clean, note
 ('wan2.6-i2v-flash', .084, 5.0, 3.5, 3.0, 2.0, 'cheapest; background drifts, train changed shape and colour'),
 ('MiniMax-Hailuo-2.3-Fast', .1488, 5.9, 5.0, 2.5, 5.0, 'most faithful, clean wolf push-in, little motion'),
 ('veo3.1-fast', .14, 7.9, 4.5, 4.0, 3.5, 'natural blink, crane moves; thin line across the wolf'),
 ('veo3.1-quality', 1.0, 8.0, 4.5, 4.0, 3.5, 'good but slight background change; 7x the price of fast'),
 ('kling-v3 (std)', .336, 5.0, 4.5, 4.5, 4.0, 'livelier, crane flies, wolf walks forward'),
 ('kling-v4-flash', .4286, 5.0, 4.0, 4.5, 3.5, 'similar to v3 with a slight face and scene shift'),
 ('seedance-2.0', .33, 5.0, 3.0, 4.0, 3.5, '480p; background swaps, strong push-in'),
 ('seedance-2.5-flash', .3183, 5.0, 3.0, 4.5, 3.5, '480p; background drifts, strongest push-in'),
 ('wan2.7', .332, 5.0, 2.5, 3.0, 3.5, 'one clip: the boy changed expression, zoom'),
]
vid = [dict(kind='video', model=m, cost=round(c / d, 4), unit='per second', cost_per_clip=c, seconds=d, quality=round((i + mo + cl) / 3, 2),
            detail=dict(identity=i, motion=mo, clean=cl), note=n) for m, c, d, i, mo, cl, n in V]
json.dump(dict(image=img, video=vid), open(os.path.join(here, 'models.json'), 'w'), indent=1)
with open(os.path.join(here, 'models.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['kind', 'model', 'usd_per_unit', 'unit', 'quality_0_5', 'detail'])
    for d in img + vid: w.writerow([d['kind'], d['model'], d['cost'], d['unit'], d['quality'], json.dumps(d['detail'])])

import math
def frontier(pts):
    pts = sorted(pts, key=lambda p: (p['cost'], -p['quality'])); best = -1; out = []; lastc = None
    for p in pts:
        if p['quality'] > best or (p['quality'] == best and p['cost'] == lastc): out.append(p['model']); lastc = p['cost']
        best = max(best, p['quality'])
    return set(out)

def chart(pts, cid, xlab, ylab, xt, ylo, yhi, title, desc):
    W, H, L, Rr, T, B = 900, 540, 70, 24, 24, 64
    xs = [p['cost'] for p in pts]; lo, hi = min(xs) * .8, max(xs) * 1.25
    X = lambda v: L + (math.log(v) - math.log(lo)) / (math.log(hi) - math.log(lo)) * (W - L - Rr)
    Y = lambda v: T + (yhi - v) / (yhi - ylo) * (H - T - B)
    fr = frontier(pts)
    o = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="{cid}t {cid}d" id="{cid}"><title id="{cid}t">{html.escape(title)}</title><desc id="{cid}d">{html.escape(desc)}</desc>']
    v = ylo
    while v <= yhi + 1e-9:
        o.append(f'<line class="pg" x1="{L}" x2="{W-Rr}" y1="{Y(v):.1f}" y2="{Y(v):.1f}"/><text class="pa2" x="{L-10}" y="{Y(v)+5:.1f}" text-anchor="end">{v:g}</text>'); v += .5
    for t in xt:
        o.append(f'<line class="pg" x1="{X(t):.1f}" x2="{X(t):.1f}" y1="{T}" y2="{H-B}"/><text class="pa2" x="{X(t):.1f}" y="{H-B+22}" text-anchor="middle">${t:g}</text>')
    o.append(f'<text class="pa2" x="{(L+W-Rr)/2}" y="{H-12}" text-anchor="middle">{xlab}</text><text class="pa2" transform="translate(18 {(T+H-B)/2}) rotate(-90)" text-anchor="middle">{ylab}</text>')
    fp = sorted([p for p in pts if p['model'] in fr], key=lambda p: p['cost'])
    # nudge points that would overlap
    pos = {}
    for p in pts:
        x, y = X(p['cost']), Y(p['quality'])
        while any(abs(x - a) < 15 and abs(y - b) < 15 for a, b in pos.values()): x += 15
        pos[p['model']] = (x, y)
    o.append('<polyline class="pf" points="' + ' '.join(f'{pos[p["model"]][0]:.1f},{pos[p["model"]][1]:.1f}' for p in fp) + '"/>')
    placed = [(pos[p['model']][0]-11, pos[p['model']][1]-11, pos[p['model']][0]+11, pos[p['model']][1]+11) for p in pts]
    placed += [(a[0]-4, a[1]-8, a[0]+4, a[1]+8) for a in []]
    for p in sorted(pts, key=lambda p: p['model'] not in fr):
        x, y = pos[p['model']]; on = p['model'] in fr
        tip = f"{p['model']}\n${p['cost']:.4f} {p['unit']}\nquality {p['quality']:.2f} of 5\n" + ', '.join(f'{k} {v}' for k, v in p['detail'].items())
        if p.get('pass3'): tip += f"\nrepeat runs {p['pass3']['repeat_runs']}, cine/pair {p['pass3']['cine_pair']}"
        if p.get('note'): tip += '\n' + p['note']
        tip += '\n' + ('on the frontier' if on else 'beaten by a cheaper or better model')
        o.append(f'<circle class="{"pb" if on else "pd"}" cx="{x:.1f}" cy="{y:.1f}" r="{9 if on else 7}" tabindex="0" data-tip="{html.escape(tip)}" aria-label="{html.escape(tip.replace(chr(10), ", "))}"/>')
        name = p['model'].replace('gpt-image-', 'gpt-img-')
        w = 7.2 * len(name)
        for dx, dy, anc in [(14, 5, 'start'), (-14, 5, 'end'), (0, -16, 'middle'), (0, 28, 'middle'), (14, -14, 'start'), (-14, 22, 'end'), (14, 22, 'start'), (-14, -14, 'end')]:
            lx = x + dx; x0 = lx if anc == 'start' else lx - w if anc == 'end' else lx - w / 2
            box = (x0, y + dy - 12, x0 + w, y + dy + 4)
            if x0 < 4 or x0 + w > W - 4 or box[1] < 2: continue
            if any(not (box[2] < b[0] or box[0] > b[2] or box[3] < b[1] or box[1] > b[3]) for b in placed): continue
            placed.append(box); o.append(f'<text class="{"pl" if on else "pl2"}" x="{lx:.1f}" y="{y+dy:.1f}" text-anchor="{anc}">{html.escape(name)}</text>'); break
    o.append('</svg>')
    return '\n'.join(o), len(fr)

ic, nf = chart(img, 'ci', 'Cost per image (log scale)', 'Quality (mean of 4 scores, 0 to 5)', [.01, .02, .05, .1], 2, 5,
               'Quality against cost per image for 13 image models',
               'Scored models. Frontier: gpt-image-2 at $0.0085 scoring 4.5, then gpt-image-2.6-flare and gpt-image-2.6-sunburst at $0.026 scoring 5.0 (tied, drawn side by side).')
vc, nv = chart(vid, 'cv', 'Cost per second of video (log scale)', 'Quality (mean of identity, motion, clean; 0 to 5)', [.02, .05, .1], 2, 5,
               'Quality against cost per second for 9 video models',
               'Image-to-video test with two start frames. Frontier models are cheapest or best at their price.')
open(os.path.join(here, 'charts.fragment.txt'), 'w').write(f'<!--image {nf}-->\n{ic}\n<!--video {nv}-->\n{vc}\n')
print('image frontier', nf, 'video frontier', nv)
