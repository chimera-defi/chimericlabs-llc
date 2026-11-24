#!/usr/bin/env python3
"""Commit series for research/data/: per project per day and month, from the one commit sweep.

usage: commits.py UNIFIED_CSV OUT_DIR [--map commits_by_project.csv] [--aliases building-aliases.json] [--through YYYY-MM-DD]
UNIFIED_CSV is scripts/token-usage/commit_sweep.py output (one row per SHA). Same rules as
scripts/token-usage/build_daily.py: UTC author date, outside authors out, commits_landed = non-merge on
main/master with copies of one change collapsed, commits_all_refs = every commit on any branch, remote or tag.
--map (host-only, not in the repo) gives each directory its GitHub repo and visibility; a directory it does
not know is private. Only display labels are written: private repos fold into "Other private work" unless
--aliases (host-only) gives the directory a label. Writes commits_daily.csv, commits_monthly.csv, projects.json,
before_ai.json and the "commits" section of meta.json. Python 3 standard library only."""
import argparse, csv, datetime, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from build_building_page import GROUPS, BEFORE_AI, FIRST_COMMIT_FIXES, OTHER_PUBLIC, OTHER_PRIVATE

SINCE = "2025-10-01"
HOME = os.path.expanduser("~")
MAP = HOME + "/claude-usage-audit/dashboard-v5-20261031/handoff/commits_by_project.csv"
ALIASES = HOME + "/.config/chimericlabs/building-aliases.json"


# Public projects with no checkout on this host: last counted figure, shown on the card, left out of every total.
CARRIED = []


def label_of(project, info, aliases):
    """Display label. A directory the map does not know, or a private one without an alias, is Other private work."""
    if info.get("visibility") == "public":
        for _, label, repos in GROUPS:
            if info.get("github_repo") in repos:
                return label
        return OTHER_PUBLIC[1]
    return aliases.get(project, OTHER_PRIVATE[1])


def export(unified, out_dir, map_csv=MAP, aliases_path=ALIASES, through=None):
    with open(map_csv, encoding="utf-8", newline="") as fh:
        info = {r["project"]: r for r in csv.DictReader(fh)}
    with open(aliases_path, encoding="utf-8") as fh:
        aliases = json.load(fh)
    per, seen, first, last, urls = {}, set(), {}, {}, {}
    with open(unified, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            d = r["date_utc"]
            if r["scope"] == "third_party" or (through and d > through):
                continue
            lab = label_of(r["project"], info.get(r["project"], {}), aliases)
            repo = info.get(r["project"], {}).get("github_repo", "")
            gh = FIRST_COMMIT_FIXES.get(repo)
            first[lab] = min(first.get(lab, d), gh or d)
            last[lab] = max(last.get(lab, d), d)
            if d < SINCE:
                continue
            c = per.setdefault((d, lab), [0, 0])
            c[1] += 1  # all refs, merges included
            if repo and info[r["project"]].get("visibility") == "public":
                urls.setdefault(lab, {}).setdefault(repo, 0)
                urls[lab][repo] += 1
            if r["is_merge"] == "True" or r["on_main"] != "1":
                continue
            lines = sum(int(r[k]) for k in r if k.startswith(("added_", "removed_")))
            if lines:
                fp = (r["project"], r["author"], d, r["subject"], r["files"], lines)
                if fp in seen:
                    continue
                seen.add(fp)
            c[0] += 1
    os.makedirs(out_dir, exist_ok=True)
    end = through or max(d for d, _ in per)
    with open(out_dir + "/commits_daily.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["date", "project", "commits_landed", "commits_all_refs"])
        for (d, lab), (a, b) in sorted(per.items()):
            w.writerow([d, lab, a, b])
    months = {}
    for (d, lab), (a, b) in per.items():
        m = months.setdefault((d[:7], lab), [0, 0])
        m[0] += a
        m[1] += b
    with open(out_dir + "/commits_monthly.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["month", "project", "commits_landed", "commits_all_refs", "days"])
        for (m, lab), (a, b) in sorted(months.items()):
            y, mo = int(m[:4]), int(m[5:])
            full = (datetime.date(y + mo // 12, mo % 12 + 1, 1) - datetime.timedelta(days=1)).day
            days = min(full, int(end[8:])) if m == end[:7] else full
            w.writerow([m, lab, a, b, days])
    tot = {}
    for (d, lab), (a, b) in per.items():
        t = tot.setdefault(lab, [0, 0])
        t[0] += a
        t[1] += b
    projects = [{"label": lab, "first": first[lab], "last": last[lab], "commits_landed": a, "commits_all_refs": b,
                 "repos": dict(sorted(urls.get(lab, {}).items()))} for lab, (a, b) in sorted(tot.items(), key=lambda kv: (-kv[1][1], kv[0]))]
    write_json(out_dir + "/projects.json", {"since": SINCE, "data_through": end, "projects": projects, "carried": CARRIED})
    write_json(out_dir + "/before_ai.json", BEFORE_AI)
    meta_path = out_dir + "/meta.json"
    meta = json.load(open(meta_path)) if os.path.exists(meta_path) else {}
    meta["commits"] = {"generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                       "source": "scripts/token-usage/commit_sweep.py", "rows": len(per),
                       "method": "UTC author date; outside authors out; commits_landed = non-merge on main/master, copies of one change collapsed; commits_all_refs = every commit on a branch, remote or tag, merges included; private repos fold into Other private work"}
    write_json(meta_path, meta)
    return end, sum(a for a, _ in tot.values()), sum(b for _, b in tot.values())


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1, sort_keys=True, ensure_ascii=False)
        fh.write("\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("unified"); ap.add_argument("out_dir")
    ap.add_argument("--map", default=MAP); ap.add_argument("--aliases", default=ALIASES); ap.add_argument("--through")
    a = ap.parse_args()
    print("through %s: landed %d, all refs %d" % export(a.unified, a.out_dir, a.map, a.aliases, a.through))
