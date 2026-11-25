#!/usr/bin/env python3 -I
"""Advisor tokens per UTC day and model, from Claude transcripts (read-only). The usage-audit csvs skip these:
a message's usage.iterations holds `advisor_message` rows (a second model reading the whole chat) that the top-level usage omits.
usage: advisor_scan.py OUT_CSV [SINCE_YYYY-MM-DD]   columns: date,model,calls,input,cache_write,cache_read,output
One row per unique message id + requestId (forks and resumes copy lines; the first file wins). Aggregates only: no names, paths or ids leave this script."""
import csv, glob, json, os, subprocess, sys
from collections import defaultdict
from multiprocessing import Pool

ROOT = os.path.expanduser('~/.claude/projects')
SINCE = sys.argv[2] if len(sys.argv) > 2 else '2026-07-01'


def scan(path):
    out = []
    proc = subprocess.Popen(['zstd', '-dc', path], stdout=subprocess.PIPE) if path.endswith('.zst') else None   # old transcripts are compressed; no zstd = loud failure, not an undercount
    for line in (proc.stdout if proc else open(path, 'rb')):
        if b'advisor_message' not in line: continue
        try: d = json.loads(line)
        except Exception: continue
        m, ts = d.get('message') or {}, d.get('timestamp', '')
        for i, it in enumerate((m.get('usage') or {}).get('iterations') or []):
            if it.get('type') == 'advisor_message' and ts[:10] >= SINCE:
                cc = it.get('cache_creation_input_tokens', 0) or 0
                out.append(((m.get('id') or '') + '|' + (d.get('requestId') or '') + f'#{i}', ts[:10], it.get('model', '?'),
                            it.get('input_tokens', 0) or 0, cc, it.get('cache_read_input_tokens', 0) or 0, it.get('output_tokens', 0) or 0))
    if proc and proc.wait() != 0: raise SystemExit(f'zstd failed on a transcript (exit {proc.returncode})')
    return out


if __name__ == '__main__':
    files = sorted(glob.glob(ROOT + '/**/*.jsonl', recursive=True) + glob.glob(ROOT + '/**/*.jsonl.zst', recursive=True))
    seen, agg = set(), defaultdict(lambda: [0, 0, 0, 0, 0])
    with Pool(8) as pool:
        for rows in pool.imap(scan, files, chunksize=8):
            for key, day, model, i, cw, cr, o in rows:
                if key in seen: continue
                seen.add(key); a = agg[(day, model)]
                a[0] += 1; a[1] += i; a[2] += cw; a[3] += cr; a[4] += o
    with open(sys.argv[1], 'w', newline='') as f:
        w = csv.writer(f); w.writerow('date,model,calls,input,cache_write,cache_read,output'.split(','))
        for (day, model), a in sorted(agg.items()): w.writerow([day, model, *a])
    print(f'{len(files)} transcripts, {len(seen)} advisor calls, {min((k[0] for k in agg), default="-")}..{max((k[0] for k in agg), default="-")}')
