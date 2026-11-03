#!/usr/bin/env python3
"""Fail when the page's series disagree with the consolidated daily table or with each other.

usage: validate_daily.py DAILY_CSV DATA_JSON [--legacy] [--monthly MONTHLY_CSV]
Checks (each failure is printed, exit 1 if any):
  1. Dates: one row per UTC day, contiguous, starting at HISTORY_START and ending at the data_through day.
  2. Definitions: landed commits = sum of the actor columns; touched = added + removed; token total = sum of providers;
     landed <= all_refs; merge <= all_refs; the partial day is the last row and only the last.
  3. data.json["daily"] (the table the page is built from) equals DAILY_CSV, row for row.
  4. Every per-day series (strict mode also compares commit totals and code lines per day; token statuses are always compared with the rows) in data.json (token rows, commits, loc.daily) lies inside the table's date range, and the
     table's token columns equal the token rows. A date with no token row must be marked unmeasured, not 0.
  5. With --monthly: MONTHLY_CSV is exactly the sum of the daily rows, month by month (default: monthly.csv beside DAILY_CSV, if present).
  --legacy  demote check 3 and the value comparisons of check 4 to warnings or skip them, for data.json files from before the page was switched to the table.
Python 3 standard library only.
"""
import csv
import datetime
import json
import os
import sys

sys.path.insert(0, __import__("os").path.dirname(__file__))
from build_daily import ACTORS, COLUMNS, HISTORY_START, MONTHLY_COLUMNS, monthly, token_total  # noqa: E402

INT_COLS = [c for c in COLUMNS if c not in ("date", "day_status", "claude_token_status", "codex_token_status")]


def validate(daily_csv, data_json, legacy=False, monthly_csv=None):
    errors, warnings = [], []
    with open(daily_csv, encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != COLUMNS:
            return [f"columns differ from schema: {reader.fieldnames}"], []
        rows = list(reader)
    with open(data_json, encoding="utf-8") as fh:
        data = json.load(fh)
    if not rows:
        return ["daily table is empty"], []

    # 1. dates
    dates = [r["date"] for r in rows]
    start, last = HISTORY_START, data["partial_today"]
    expect = []
    d = datetime.date.fromisoformat(start)
    while d.isoformat() <= last:
        expect.append(d.isoformat())
        d += datetime.timedelta(days=1)
    if dates != expect:
        missing, extra = sorted(set(expect) - set(dates)), sorted(set(dates) - set(expect))
        errors.append(f"dates are not {start}..{last} contiguous: missing {missing[:5]}, extra {extra[:5]}, duplicates {len(dates) - len(set(dates))}")
    if not data["data_through"].startswith(last):
        errors.append(f"data_through {data['data_through']} is not the last row date {last}")
    partial = [r["date"] for r in rows if r["day_status"] == "partial"]
    if partial != [rows[-1]["date"]]:
        errors.append(f"exactly the last day must be partial, got {partial}")

    # 2. definitions
    for r in rows:
        v = {c: int(r[c]) for c in INT_COLS}
        if v["commits_landed"] != sum(v["commits_landed_" + a] for a in ACTORS):
            errors.append(f"{r['date']}: commits_landed != sum of actors")
        if v["code_touched"] != v["code_added"] + v["code_removed"]:
            errors.append(f"{r['date']}: code_touched != added + removed")
        if v["tokens_total"] != v["tokens_claude"] + v["tokens_codex"] + v["tokens_other"]:
            errors.append(f"{r['date']}: tokens_total != sum of providers")
        if v["commits_landed"] > v["commits_all_refs"] or v["commits_merge"] > v["commits_all_refs"]:
            errors.append(f"{r['date']}: landed or merge commits exceed all-refs commits")
        if r["claude_token_status"] in ("unmeasured", "before_start") and v["tokens_claude"]:
            errors.append(f"{r['date']}: claude tokens present but marked unmeasured")
        if r["codex_token_status"] == "unmeasured" and v["tokens_codex"]:
            errors.append(f"{r['date']}: codex tokens present but marked unmeasured")

    # 3. data.json is built from the table
    table = [dict(r) for r in rows]
    if data.get("daily") is None:
        (warnings if legacy else errors).append('data.json has no "daily" key: the page is not built from the consolidated table')
    elif data["daily"] != table:
        diff = [a["date"] for a, b in zip(data["daily"], table) if a != b]
        msg = f'data.json["daily"] differs from {daily_csv}: {len(data["daily"])} vs {len(table)} rows, first differing days {diff[:5]}'
        (warnings if legacy else errors).append(msg)

    # 4. other series in data.json
    tok = {}
    for row in data["rows"]:
        tok.setdefault(row[0], [0, 0, 0])
        i = 0 if row[1].startswith("claude") else 1 if row[1].startswith("codex") else 2
        tok[row[0]][i] += token_total(row)
    series = {
        "token rows": sorted(tok),
        "commits": [x["date"] for x in data.get("commits", [])],
        "loc.daily": [x.get("date") for x in data.get("loc", {}).get("daily", [])],
    }
    for name, ds in series.items():
        if not ds:
            continue
        outside = [x for x in ds if x < dates[0] or x > dates[-1]]
        if outside and name == "loc.daily":
            warnings.append(f"loc.daily keeps {len(outside)} days of pre-window history (ignored)")
        elif outside:
            errors.append(f"{name} has dates outside the table range: {outside[:5]}")
        if name != "loc.daily" and set(ds) != set(dates):
            gap = sorted(set(dates) - set(ds))
            msg = f"{name} covers {len(set(ds))} of {len(dates)} days; missing {gap[:5]}{'...' if len(gap) > 5 else ''}"
            (errors if name == "commits" and not legacy else warnings).append(msg)
    if not legacy:
        # page series must carry the table's definitions, not just its dates
        if not data.get("commits"):
            errors.append("data.json has no commits series")
        by = {r["date"]: r for r in rows}
        for x in data.get("commits", []):
            if x["date"] in by and x.get("total") != int(by[x["date"]]["commits_landed"]):
                errors.append(f"commits {x['date']}: page total {x.get('total')} != table commits_landed {by[x['date']]['commits_landed']}")
        loc = {}
        for x in data.get("loc", {}).get("daily", []):
            a = loc.setdefault(x["date"], [0, 0])
            a[0] += x["added"]; a[1] += x["removed"]
        for r in rows:
            got = loc.get(r["date"], [0, 0])
            if got != [int(r["code_added"]), int(r["code_removed"])]:
                errors.append(f"loc.daily {r['date']}: page {got} != table code lines {[int(r['code_added']), int(r['code_removed'])]}")
    claude_rows, codex_rows = {}, set()
    for row in data["rows"]:
        if row[1].startswith("claude"):
            claude_rows[row[0]] = claude_rows.get(row[0], True) and row[1] == "claude_recovered_quarantine"
        elif row[1].startswith("codex"):
            codex_rows.add(row[0])
    for r in rows:
        d = r["date"]
        if d < data["coverage"]["token_start"]:
            if (r["claude_token_status"], r["codex_token_status"]) != ("before_start",) * 2 or int(r["tokens_total"]):
                errors.append(f"{d}: before token_start both statuses must be before_start with 0 tokens")
            continue
        want_claude = "unmeasured" if d not in claude_rows else "recovered" if claude_rows[d] else "measured"
        if r["claude_token_status"] != want_claude:
            errors.append(f"{d}: claude_token_status {r['claude_token_status']} but token rows say {want_claude}")
        if r["codex_token_status"] != ("measured" if d in codex_rows else "unmeasured"):
            errors.append(f"{d}: codex_token_status {r['codex_token_status']} disagrees with token rows")
    for r in rows:
        want = tok.get(r["date"], [0, 0, 0])
        got = [int(r["tokens_claude"]), int(r["tokens_codex"]), int(r["tokens_other"])]
        if want != got:
            errors.append(f"{r['date']}: table tokens {got} != data.json token rows {want}")

    # 5. monthly rollup
    if monthly_csv and os.path.exists(monthly_csv):
        with open(monthly_csv, encoding="utf-8", newline="") as fh:
            mr = csv.DictReader(fh)
            if mr.fieldnames != MONTHLY_COLUMNS:
                errors.append(f"monthly columns differ from schema: {mr.fieldnames}")
            else:
                got = {r["month"]: {c: int(r[c]) for c in MONTHLY_COLUMNS[1:]} for r in mr}
                want = monthly(rows)
                for m in sorted(set(got) | set(want)):
                    if got.get(m) != want.get(m):
                        errors.append(f"monthly {m}: {got.get(m)} != sum of daily rows {want.get(m)}")
    elif monthly_csv:
        errors.append(f"{monthly_csv} not found")
    return errors, warnings


def main():
    argv = sys.argv[1:]
    monthly_csv = None
    if "--monthly" in argv:
        i = argv.index("--monthly")
        monthly_csv = argv[i + 1] if i + 1 < len(argv) else None
        del argv[i:i + 2]
    args = [a for a in argv if a != "--legacy"]
    if len(args) != 2:
        sys.exit(__doc__)
    if monthly_csv is None:
        monthly_csv = os.path.join(os.path.dirname(os.path.abspath(args[0])), "monthly.csv")
    errors, warnings = validate(args[0], args[1], "--legacy" in sys.argv, monthly_csv)
    for w in warnings:
        print("WARN", w)
    for e in errors:
        print("FAIL", e)
    print(f"{len(errors)} failures, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
