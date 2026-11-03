#!/usr/bin/env python3 -I
"""Copy freshly produced csv/txt datasets from the acquisition tree into the page's handoff/ folder.
Only files that already exist in handoff/ are replaced (same name), so the folder's set of inputs never grows by accident.
Hand-written files (SOURCES.md, notes, mac_codexbar*, the cost file, headline_counts.json) are never touched.
usage: sync_handoff.py ACQ_DIR HANDOFF_DIR"""
import csv, io, shutil, sys
from pathlib import Path

ACQ, H = Path(sys.argv[1]), Path(sys.argv[2])
SUBDIRS = ['.', 'data_refresh', 'ledger', 'commits', 'loc', 'models', 'eth2']
NEVER = {'headline_counts.json', 'costs'+'_ledger.csv', 'LIFETIME_TOKENS_DAILY_20261029.csv', 'commits.csv', 'commits_daily.csv',
         'commits_actor_daily.csv', 'last7_daily.csv', 'claude_daily_best.csv'}
RENAME = {'codex_files.csv': 'codex_session_files.csv'}  # acquisition name -> handoff name
changed = []

def merge_dim(old, new):
    """Claude prunes old transcripts, so a fresh export loses early days. Per date keep the larger copy; fresh wins ties."""
    def split(b):
        rows = list(csv.DictReader(io.StringIO(b.decode()))); out = {}
        for r in rows: out.setdefault(r['date'], []).append(r)
        return rows[0].keys(), out
    def total(rs): return sum(int(r[k]) for r in rs if r['model'] != '<synthetic>' for k in ('input', 'output', 'cache_creation', 'cache_read'))
    cols, o = split(old); _, n = split(new)
    buf = io.StringIO(); w = csv.DictWriter(buf, fieldnames=list(cols), lineterminator='\n'); w.writeheader()
    for d in sorted(set(o) | set(n)):
        pick = o[d] if d in o and (d not in n or total(o[d]) > total(n[d])) else n[d]
        w.writerows(pick)
    return buf.getvalue().encode()
for sub in SUBDIRS:
    for src in sorted((ACQ/sub).glob('*')):
        if not src.is_file() or src.suffix not in ('.csv', '.txt') or src.name in NEVER: continue
        dst = H/RENAME.get(src.name, src.name)
        if not dst.exists(): continue
        data = src.read_bytes()
        if dst.name == 'claude_daily_dim.csv': data = merge_dim(dst.read_bytes(), data)
        if dst.read_bytes() != data:
            dst.write_bytes(data); changed.append(dst.name)
extra = [(ACQ/'analysis'/'codex_daily_split.csv', H/'codex_daily_split.csv')]
extra += [(src, H/'other_sources'/src.name) for src in sorted((ACQ/'other_sources').glob('*.csv'))]
for src, dst in extra:
    if src.exists() and dst.exists() and dst.read_bytes() != src.read_bytes():
        shutil.copy2(src, dst); changed.append(str(dst.relative_to(H)))
print('synced', len(changed), 'files:', ', '.join(changed))
