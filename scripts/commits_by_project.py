#!/usr/bin/env python3
"""Build commits_by_project.csv, the commit input of build_building_page.py, from a commit sweep.

Reads commits_scoped.csv (one row per commit, SHA-deduped across clones and branches, with
`scope` and `tools_scoped` columns) and keeps operator and agent commits, dropping upstream authors.
github_repo and visibility are copied from the previous commits_by_project.csv. A project
that is new since then gets no GitHub repo and is treated as private, so it can only ever
appear under "Other private work" until someone fills its row in.

usage: commits_by_project.py SCOPED_CSV PREVIOUS_CSV OUT_CSV [--through YYYY-MM-DD]
Python 3 standard library only.
"""
import argparse
import csv
import sys

SINCE = "2025-10-01"
ACTORS = ("claude", "codex", "other")
PRIVATE = "local_only_no_github_remote"


def actor(tools):
    kinds = {"claude": "claude", "codex": "codex"}
    found = {kinds.get(t, "other") for t in tools.split("|") if t}
    return "+".join(a for a in ACTORS if a in found) or "human"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("scoped")
    ap.add_argument("previous")
    ap.add_argument("out")
    ap.add_argument("--through", default="9999-12-31", help="ignore commits after this UTC date")
    args = ap.parse_args()

    with open(args.previous, encoding="utf-8", newline="") as fh:
        prev = {r["project"]: r for r in csv.DictReader(fh)}
        cols = list(next(iter(prev.values())).keys())
    count_cols = [c for c in cols if c.startswith("commits_since_2025-10_") and c != "commits_since_2025-10_total"]

    stats = {}
    with open(args.scoped, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            if r["scope"] == "third_party" or r["date_utc"] > args.through:
                continue
            s = stats.setdefault(r["project"], {"by": {}, "since": 0, "all": 0, "first": r["date_utc"], "last": r["date_utc"]})
            s["all"] += 1
            s["first"] = min(s["first"], r["date_utc"])
            s["last"] = max(s["last"], r["date_utc"])
            if r["date_utc"] >= SINCE:
                s["since"] += 1
                a = actor(r["tools_scoped"])
                s["by"][a] = s["by"].get(a, 0) + 1

    rows = []
    for project, s in stats.items():
        if not s["since"]:
            continue
        old = prev.get(project, {})
        row = {"project": project, "github_repo": old.get("github_repo", ""), "visibility": old.get("visibility", PRIVATE)}
        for c in count_cols:
            row[c] = s["by"].get(c.removeprefix("commits_since_2025-10_"), 0)
        row.update({"commits_since_2025-10_total": s["since"], "first_commit_all_history": s["first"], "last_commit": s["last"], "commits_all_history_total": s["all"]})
        rows.append(row)
        if project not in prev:
            print(f"new project, treated as private: {project} ({s['since']} commits)", file=sys.stderr)
    rows.sort(key=lambda r: (-r["commits_since_2025-10_total"], r["project"]))
    with open(args.out, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} projects, {sum(r['commits_since_2025-10_total'] for r in rows)} commits since {SINCE}")


if __name__ == "__main__":
    main()
