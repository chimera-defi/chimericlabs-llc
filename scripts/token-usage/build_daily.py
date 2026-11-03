#!/usr/bin/env python3
"""Build the consolidated daily table: one row per UTC date, every series on the token-usage page.

usage: build_daily.py COMMITS_CSV DATA_JSON OUT_CSV
  COMMITS_CSV  output of commit_sweep.py
  DATA_JSON    research/token-usage/data.json (token rows, coverage, data_through)
  OUT_CSV      research/token-usage/daily.csv

data.json must be built from this table. validate_daily.py fails when it is not.
Definitions are in docs/commit-and-token-series.md. Python 3 standard library only.
"""
import csv
import datetime
import json
import sys

BULK_FILES = 100
ACTORS = ("claude", "codex", "claude_codex", "other", "human")
COLUMNS = (
    ["date", "day_status"]
    + ["commits_landed"] + ["commits_landed_" + a for a in ACTORS]
    + ["commits_all_refs", "commits_merge"]
    + ["code_added", "code_removed", "code_touched", "all_added_raw", "all_removed_raw"]
    + ["tokens_claude", "tokens_codex", "tokens_other", "tokens_total", "claude_token_status", "codex_token_status"]
)


def actor(tools):
    t = {x for x in tools.split("|") if x}
    if not t:
        return "human"
    if t == {"claude"}:
        return "claude"
    if t == {"codex"}:
        return "codex"
    if t == {"claude", "codex"}:
        return "claude_codex"
    return "other"


def token_total(row):
    if len(row) > 7 and row[7] is not None:
        return row[7]
    return sum(v or 0 for v in row[2:6])


def days(start, end):
    d = datetime.date.fromisoformat(start)
    stop = datetime.date.fromisoformat(end)
    while d <= stop:
        yield d.isoformat()
        d += datetime.timedelta(days=1)


def load_commits(path, start, end):
    """Rows for the window. landed = non-merge on main, with copies of the same change collapsed.

    A rebase, cherry-pick or amend gives the same change a new SHA, so SHA dedupe alone keeps every copy.
    Copies share project, author, UTC date, subject, files changed and lines added/removed; only the first is kept.
    This is a fingerprint, not a patch comparison: two different changes with the same message, size and day would
    merge into one (rare; the sweep keeps no patch ids because hashing every diff costs minutes).
    """
    out = {d: dict.fromkeys(COLUMNS[2:], 0) for d in days(start, end)}
    seen = set()
    with open(path, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            d = r["date_utc"]
            if r["scope"] == "third_party" or d not in out:
                continue
            o = out[d]
            added = sum(int(r["added_" + c]) for c in ("src", "test", "doc", "cfg", "other", "noise"))
            removed = sum(int(r["removed_" + c]) for c in ("src", "test", "doc", "cfg", "other", "noise"))
            o["all_added_raw"] += added
            o["all_removed_raw"] += removed
            if r["is_merge"] == "True":
                o["commits_merge"] += 1
                o["commits_all_refs"] += 1
                continue
            o["commits_all_refs"] += 1
            if r["on_main"] != "1":
                continue
            if added + removed:
                fp = (r["project"], r["author"], d, r["subject"], r["files"], added, removed)
                if fp in seen:
                    continue
                seen.add(fp)
            o["commits_landed"] += 1
            o["commits_landed_" + actor(r["tools_scoped"])] += 1
            if int(r["files"]) <= BULK_FILES:
                a = int(r["added_src"]) + int(r["added_test"])
                rm = int(r["removed_src"]) + int(r["removed_test"])
                o["code_added"] += a
                o["code_removed"] += rm
                o["code_touched"] += a + rm
    return out


def load_tokens(data, out):
    claude_days, codex_days, recovered_only = set(), set(), {}
    for row in data["rows"]:
        d, prov = row[0], row[1]
        if d not in out:
            continue
        t = token_total(row)
        if prov.startswith("claude"):
            out[d]["tokens_claude"] += t
            claude_days.add(d)
            recovered_only[d] = recovered_only.get(d, True) and prov == "claude_recovered_quarantine"
        elif prov.startswith("codex"):
            out[d]["tokens_codex"] += t
            codex_days.add(d)
        else:
            out[d]["tokens_other"] += t
    for d, o in out.items():
        o["tokens_total"] = o["tokens_claude"] + o["tokens_codex"] + o["tokens_other"]
        o["claude_token_status"] = "unmeasured" if d not in claude_days else "recovered" if recovered_only[d] else "measured"
        o["codex_token_status"] = "measured" if d in codex_days else "unmeasured"


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    commits_csv, data_json, out_csv = sys.argv[1:]
    with open(data_json, encoding="utf-8") as fh:
        data = json.load(fh)
    start = data["coverage"]["token_start"]
    last = data["partial_today"]  # the data_through day; still filling
    table = load_commits(commits_csv, start, last)
    load_tokens(data, table)
    with open(out_csv, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(COLUMNS)
        for d, o in table.items():
            w.writerow([d, "partial" if d == last else "complete"] + [o[c] for c in COLUMNS[2:]])
    print(f"wrote {len(table)} days {start}..{last} to {out_csv}")


if __name__ == "__main__":
    main()
