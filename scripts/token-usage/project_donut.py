#!/usr/bin/env python3 -I
"""Write handoff/project_donut.html: the building page's commits-by-project donut, for the token page's Commits section.
usage: project_donut.py OUT_HTML
Same data file (research/data/projects.json) and the same functions as research/building (scripts/build_building_page.py), so names, groups and
colours cannot differ. The exact names are allowlisted in public_leak_scan.py; bp.DONUT_LABELS gives the eth2 repo a generic label on both pages."""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import build_building_page as bp

pj = json.load(open(os.path.join(bp.DATA, 'projects.json')))
groups = bp.build_groups(pj['projects'], pj.get('carried', []))
total = sum(g['n'] for g in groups.values())
slices = bp.donut_slices(groups, total)
figure, css = bp.donut_html(slices, total, pj['data_through'])
# Slice colours and layout rules come from the building page's own stylesheet, so the two pages cannot differ.
page = open(bp.DEFAULT_PAGE, encoding='utf-8').read()
palette = ''.join(f'--data-{n}:{v};' for n, v in re.findall(r'--data-(\d+):\s*([^;]+?);', page))
# Wrapping flex instead of the building page's media query: the public scan bans the at sign, and a figure this size needs no breakpoint.
layout = '.donut-wrap{display:flex;flex-wrap:wrap;gap:var(--space-8);align-items:center}.article-donut svg{width:190px;flex:0 0 auto;margin:0 auto}.donut-legend{flex:1 1 260px;list-style:none;padding:0;margin:0;display:grid;gap:var(--space-3);font-size:var(--article-type)}.donut-legend li{display:grid;grid-template-columns:var(--space-4) 1fr auto;gap:var(--space-3);align-items:center}.donut-legend .swatch{width:var(--space-4);height:var(--space-4);border-radius:var(--radius-sm)}.donut-n{font-variant-numeric:tabular-nums}.donut-total{font-size:var(--article-heading)!important;font-weight:var(--font-heading-weight)}'
sizes = ''.join(f'--article-{n}:{v};' for n, v in re.findall(r'--article-(type|small|heading):\s*([^;]+?);', page))
rule = ':root{' + palette + sizes + '}' + layout + '.article-donut .chart-small{font-size:var(--article-small,14px)}.article-donut .donut-legend .swatch{display:block}.article-donut .donut-legend li,.article-donut .donut-legend p{margin:0;line-height:1.25}.article-donut .donut-n{color:var(--muted)}.article-donut h3{margin:0 0 8px}'
# The page keeps big counts compact (check_v5); inline svg needs no xmlns.
def compact(m):
    n = int(m[0].replace(',', ''))
    short = f'{n / 1000:.1f}K' if n < 1_000_000 else f'{n / 1e6:.1f}M'
    return f'<span title="{m[0]}">{short}</span>'  # exact count in the tooltip, as elsewhere on the page
figure = figure.replace(' xmlns="http://www.w3.org/2000/svg"', '')
figure = re.sub(r'(<svg\b[^>]*>)', r'\1<title>Commits by project</title>', figure, count=1)  # check_v5: every svg carries a title
def shorten(m):
    n = int(m[0].replace(',', ''))
    return f'{n / 1000:.1f}K' if n < 1_000_000 else f'{n / 1e6:.1f}M'
svg_end = figure.index('</svg>')
figure = (re.sub(r'\d{1,3}(?:,\d{3})+', shorten, figure[:svg_end]) +  # a span is not valid inside svg text
          re.sub(r'>([^<]*)<', lambda m: '>' + re.sub(r'\d{1,3}(?:,\d{3})+', compact, m[1]) + '<', figure[svg_end:]))
open(sys.argv[1], 'w').write(f'<style>{rule}{css}</style>{figure}\n')
