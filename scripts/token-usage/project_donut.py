#!/usr/bin/env python3 -I
"""Write handoff/project_donut.html: the building page's commits-by-project donut, for the token page's Commits section.
usage: project_donut.py OUT_HTML
Same data file (research/data/projects.json) and the same functions as research/building (scripts/build_building_page.py), so names, groups and
colours cannot differ. The exact names are allowlisted in public_leak_scan.py; the eth2 repo gets a generic label."""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import build_building_page as bp

# Same groups, names and order as the building page. One label is generic: the public leak scan refuses the eth2 name (campaign identity).
GENERIC = {'eth2': 'Staking tools'}
pj = json.load(open(os.path.join(bp.DATA, 'projects.json')))
groups = bp.build_groups(pj['projects'], pj.get('carried', []))
total = sum(g['n'] for g in groups.values())
slices = bp.donut_slices(groups, total)
for s in slices:
    s['label'] = GENERIC.get(s['key'], s['label'])
figure, css = bp.donut_html(slices, total, pj['data_through'])
rule = ':root{--data-1:var(--data-codex);--data-2:var(--data-pipeline);--data-3:var(--data-grok);--data-4:var(--data-claude);--data-5:var(--data-sol);--data-6:var(--data-sonnet);--data-7:color-mix(in srgb,var(--data-grok) 45%,var(--data-claude));--data-8:color-mix(in srgb,var(--data-sonnet) 50%,var(--data-pipeline));--data-9:var(--data-effort-high);--data-10:var(--data-luna);--data-11:var(--data-frontier);--data-12:var(--data-beaten)}'
# The page keeps big counts compact (check_v5); inline svg needs no xmlns.
def compact(m):
    n = int(m[0].replace(',', ''))
    short = f'{n / 1000:.1f}K' if n < 1_000_000 else f'{n / 1e6:.1f}M'
    return f'<span title="{m[0]}">{short}</span>'  # exact count in the tooltip, as elsewhere on the page
figure = figure.replace(' xmlns="http://www.w3.org/2000/svg"', '')
figure = re.sub(r'(<svg\b[^>]*>)', r'\1<title>Commits by project</title>', figure, count=1)  # check_v5: every svg carries a title
figure = re.sub(r'>([^<]*)<', lambda m: '>' + re.sub(r'\d{1,3}(?:,\d{3})+', compact, m[1]) + '<', figure)
open(sys.argv[1], 'w').write(f'<style>{rule}{css}</style>{figure}\n')
