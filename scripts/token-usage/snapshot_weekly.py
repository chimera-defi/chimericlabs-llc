#!/usr/bin/env python3
"""Append today's claude.ai weekly-limit reading to a CSV, one row per UTC date.

Reads `claude -p /usage` (the CLI's own local slash command: no model call, no token handled here).
usage: snapshot_weekly.py [--csv PATH] [--sync-from PATH]
  --csv PATH        file to append to (default research/token-usage/weekly_limit.csv in this repo)
  --sync-from PATH  also copy rows out of PATH (the timer's state file); they replace same-date rows in --csv
Product split (Claude Code / Chats / Cowork / Other) is only on the web Settings > Usage page; the CLI does
not print it, so those columns stay empty until something supplies them.
"""
import argparse, csv, datetime as dt, re, subprocess, sys
from pathlib import Path
from zoneinfo import ZoneInfo

COLS = ["date", "week_reset", "percent_used", "fable_percent",
        "split_claude_code", "split_chats", "split_cowork", "split_other"]
ROW = re.compile(r"Current week \((all models|Fable)\): (\d+)% used · resets (\w{3}) (\d{1,2}), (\d{1,2})(?::(\d\d))?(am|pm) \(([\w/+-]+)\)")
MONTHS = {m: i for i, m in enumerate("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(), 1)}


def read_usage(now):
    out = subprocess.run(["claude", "-p", "/usage"], capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL, cwd="/tmp").stdout
    found = {m.group(1): m for m in ROW.finditer(out)}
    if "all models" not in found:
        sys.exit("no 'Current week (all models)' line in `claude -p /usage` output; is the CLI signed in?\n" + out[:500])
    m = found["all models"]
    tz = ZoneInfo(m.group(8))
    hour = int(m.group(5)) % 12 + (12 if m.group(7) == "pm" else 0)
    local = now.astimezone(tz)
    reset = dt.datetime(local.year, MONTHS[m.group(3)], int(m.group(4)), hour, int(m.group(6) or 0), tzinfo=tz)
    if reset < local - dt.timedelta(days=1):   # the line carries no year: a reset that already passed means next year
        reset = reset.replace(year=reset.year + 1)
    fable = found.get("Fable")
    return {"week_reset": reset.isoformat(), "percent_used": m.group(2), "fable_percent": fable.group(2) if fable else ""}


def load(path):
    return list(csv.DictReader(open(path))) if path.exists() else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path, default=Path(__file__).resolve().parents[2] / "research/token-usage/weekly_limit.csv")
    ap.add_argument("--sync-from", type=Path)
    a = ap.parse_args()
    now = dt.datetime.now(dt.timezone.utc)
    rows = {r["date"]: r for r in load(a.csv)}
    if a.sync_from:
        for r in load(a.sync_from):
            rows[r["date"]] = r   # the timer's late-day reading beats an earlier refresh reading
    today = now.date().isoformat()
    if today not in rows:
        rows[today] = {"date": today, **read_usage(now)}
    a.csv.parent.mkdir(parents=True, exist_ok=True)
    tmp = a.csv.with_suffix(".tmp")
    with open(tmp, "w", newline="") as f:
        w = csv.DictWriter(f, COLS, restval="")
        w.writeheader()
        w.writerows(rows[d] for d in sorted(rows))
    tmp.replace(a.csv)
    print(f"{a.csv}: {len(rows)} rows, today {rows[today]}")


if __name__ == "__main__":
    main()
