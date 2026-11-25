#!/usr/bin/env python3 -I
"""Write handoff/project_donut.html: the building page's commits-by-project donut, for the token page's Commits section.
usage: project_donut.py OUT_HTML
Same data file (research/data/projects.json) and the same functions as research/building (scripts/build_building_page.py), so names, groups and
colours cannot differ. Names the public leak scan refuses on this page are folded (rules below)."""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import build_building_page as bp

# The public leak scan refuses these names on this page (campaign identity, sensitive project name), though the building page shows them.
# Private ones join "Other private work"; the rest join the public long tail, named by its repo count.
PRIVATE = re.compile(r'^(Claudefolio|DispatchBench)$')
TAIL = re.compile(r'^(eth2-quickstart|SharedStake|Other public)$')
pj = json.load(open(os.path.join(bp.DATA, 'projects.json')))
groups = bp.build_groups(pj['projects'], pj.get('carried', []))
total = sum(g['n'] for g in groups.values())
slices = bp.donut_slices(groups, total)
priv = next(s for s in slices if s['key'] == 'other-private')
tail = [s for s in slices if TAIL.search(s['label'])]
for s in [s for s in slices if PRIVATE.search(s['label'])]: priv['n'] += s['n']
repos = sum(len(groups[s['key']]['repos']) for s in tail)
slices = [s for s in slices if not (PRIVATE.search(s['label']) or s in tail)]
slices.append({'key': 'other', 'label': f'Other ({repos} repos)', 'n': sum(s['n'] for s in tail), 'colour': 'var(--data-effort-medium)'})
slices.sort(key=lambda s: (s['key'] in ('other', 'other-private'), -s['n']))
figure, css = bp.donut_html(slices, total, pj['data_through'])
rule = ':root{--data-1:var(--data-codex);--data-2:var(--data-pipeline);--data-3:var(--data-grok);--data-4:var(--data-claude);--data-5:var(--data-sol);--data-6:var(--data-sonnet);--data-7:color-mix(in srgb,var(--data-grok) 45%,var(--data-claude));--data-8:color-mix(in srgb,var(--data-sonnet) 50%,var(--data-pipeline));--data-9:var(--data-effort-high);--data-10:var(--data-luna);--data-11:var(--data-frontier);--data-12:var(--data-beaten)}'
# The page keeps big counts compact (check_v5); inline svg needs no xmlns.
def compact(m):
    n = int(m[0].replace(',', ''))
    return f'{n / 1000:.1f}K' if n < 1_000_000 else f'{n / 1e6:.1f}M'
figure = figure.replace(' xmlns="http://www.w3.org/2000/svg"', '')
figure = re.sub(r'(<svg\b[^>]*>)', r'\1<title>Commits by project</title>', figure, count=1)  # check_v5: every svg carries a title
figure = re.sub(r'>([^<]*)<', lambda m: '>' + re.sub(r'\d{1,3}(?:,\d{3})+', compact, m[1]) + '<', figure)
open(sys.argv[1], 'w').write(f'<style>{rule}{css}</style>{figure}\n')
