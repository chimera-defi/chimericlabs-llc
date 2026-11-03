#!/usr/bin/env python3
"""Tests for commit_sweep.py, build_daily.py and validate_daily.py. Run: python3 -I scripts/token-usage/test_daily.py"""
import csv
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_daily  # noqa: E402
import commit_sweep  # noqa: E402
import validate_daily  # noqa: E402


def git(d, *a, env=None):
    e = dict(os.environ, GIT_AUTHOR_NAME="chimera", GIT_AUTHOR_EMAIL="c@x", GIT_COMMITTER_NAME="chimera", GIT_COMMITTER_EMAIL="c@x", **(env or {}))
    return subprocess.run(["git", "-C", d, *a], capture_output=True, text=True, check=True, env=e).stdout.strip()


class Sweep(unittest.TestCase):
    def test_same_rows_from_any_worktree_and_rewritten_refs_ignored(self):
        with tempfile.TemporaryDirectory() as t:
            main, wt = os.path.join(t, "repo"), os.path.join(t, "repo-wt")
            os.mkdir(main)
            git(main, "init", "-q", "-b", "main")
            for i in range(3):
                open(os.path.join(main, f"f{i}.py"), "w").write("x\n" * (i + 1))
                git(main, "add", "."); git(main, "commit", "-q", "-m", f"c{i}")
            git(main, "worktree", "add", "-q", "-b", "feat", wt)
            open(os.path.join(wt, "b.py"), "w").write("y\n")
            git(wt, "add", "."); git(wt, "commit", "-q", "-m", "feat work", env={"GIT_AUTHOR_DATE": "2026-10-01T23:30:00-05:00"})
            git(main, "checkout", "-q", "--detach", "main")
            git(main, "commit", "-q", "--allow-empty", "-m", "pre-rewrite copy")
            git(main, "update-ref", "refs/rewritten/heads/old", "HEAD")
            git(main, "checkout", "-q", "main")
            common = os.path.join(main, ".git")
            a = [r for r, _ in commit_sweep.sweep_store(common, main)]
            b = [r for r, _ in commit_sweep.sweep_store(common, wt)]
            self.assertEqual(sorted(a), sorted(b))
            subjects = {r[10] for r in a}
            self.assertEqual(subjects, {"c0", "c1", "c2", "feat work"})  # the refs/rewritten commit is not counted
            feat = next(r for r in a if r[10] == "feat work")
            self.assertEqual(feat[2], "2026-10-02")  # 23:30 at -05:00 is 04:30 UTC the next day
            self.assertEqual(feat[9], 0)  # not on main

    def test_broken_ref_fails_loudly(self):
        with tempfile.TemporaryDirectory() as t:
            git(t, "init", "-q", "-b", "main")
            git(t, "commit", "-q", "--allow-empty", "-m", "a")
            open(os.path.join(t, ".git/refs/heads/broken"), "w").write("0" * 40 + "\n")
            with self.assertRaises(RuntimeError):
                list(commit_sweep.sweep_store(os.path.join(t, ".git"), t))

    def test_categories(self):
        c = commit_sweep.category
        self.assertEqual(c("package-lock.json"), "noise")
        self.assertEqual(c("data/x.json"), "noise")
        self.assertEqual(c("package.json"), "cfg")
        self.assertEqual(c("src/a.ts"), "src")
        self.assertEqual(c("tests/test_a.py"), "test")
        self.assertEqual(c("dist/a.js"), "noise")
        self.assertEqual(c("README.md"), "doc")


def commit_row(sha, d, added, removed, files=1, tools="", on_main=1, merge=False, scope="operator", project="p"):
    r = dict.fromkeys(["sha", "project", "date_utc", "author", "scope", "tools_scoped", "is_merge", "files", "binary_files", "on_main", "subject"], "")
    r.update(sha=sha, project=project, date_utc=d, author="chimera", scope=scope, tools_scoped=tools, is_merge=str(merge), files=str(files), binary_files="0", on_main=str(on_main), subject="s")
    for c in commit_sweep.CATS:
        r["added_" + c] = r["removed_" + c] = "0"
    r["added_src"], r["removed_src"] = str(added), str(removed)
    return r


def write_commits(path, rows):
    cols = list(rows[0].keys())
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader(); w.writerows(rows)


def data_json(path, days, rows, last):
    json.dump({"coverage": {"token_start": days[0]}, "partial_today": last, "data_through": last + " 05:00:00 UTC", "rows": rows, "commits": [{"date": d} for d in days], "loc": {"daily": []}}, open(path, "w"))


class Daily(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.mkdtemp()
        self.c, self.j, self.o = (os.path.join(self.t, n) for n in ("c.csv", "d.json", "o.csv"))
        self.days = ["2026-10-01", "2026-10-02", "2026-10-03"]
        rows = [
            commit_row("a", "2026-10-01", 10, 2, tools="claude|codex"),
            commit_row("b", "2026-10-01", 10, 2, tools="claude|codex"),  # same change after a rebase: counted once
            dict(commit_row("b2", "2026-10-01", 10, 2), subject="other change, same size"),  # different message: kept
            commit_row("c", "2026-10-01", 5, 0, on_main=0),            # branch copy of a squash: all_refs only
            commit_row("d", "2026-10-02", 100000, 0, files=500),        # bulk import: no code lines
            commit_row("e", "2026-10-02", 1, 1, merge=True),
            commit_row("f", "2026-10-02", 3, 0, scope="third_party"),
            commit_row("g", "2026-10-03", 4, 4, tools="codex"),
        ]
        write_commits(self.c, rows)
        tok = [["2026-10-01", "claude_transcripts:cli", 1, 2, 3, 4, 1], ["2026-10-02", "codex_corrected", None, None, None, None, None, 50], ["2026-10-03", "codex_corrected", None, None, None, None, None, 7]]
        data_json(self.j, self.days, tok, "2026-10-03")
        build_daily.sys.argv = ["x", self.c, self.j, self.o]
        build_daily.main()
        self.rows = {r["date"]: r for r in csv.DictReader(open(self.o))}

    def test_counts(self):
        r = self.rows
        self.assertEqual((r["2026-10-01"]["commits_landed"], r["2026-10-01"]["commits_all_refs"], r["2026-10-01"]["commits_landed_claude_codex"]), ("2", "4", "1"))
        self.assertEqual((r["2026-10-02"]["commits_landed"], r["2026-10-02"]["commits_merge"], r["2026-10-02"]["code_touched"], r["2026-10-02"]["all_added_raw"]), ("1", "1", "0", "100001"))
        self.assertEqual(r["2026-10-03"]["day_status"], "partial")
        self.assertEqual((r["2026-10-01"]["tokens_claude"], r["2026-10-02"]["tokens_codex"], r["2026-10-02"]["claude_token_status"]), ("10", "50", "unmeasured"))

    def test_validate(self):
        self.assertEqual(validate_daily.validate(self.o, self.j, legacy=True)[0], [])
        self.assertTrue(any('no "daily"' in e for e in validate_daily.validate(self.o, self.j)[0]))
        d = json.load(open(self.j)); d["daily"] = list(csv.DictReader(open(self.o)))
        d["loc"]["daily"] = [{"date": r["date"], "actor": "human", "added": int(r["code_added"]), "removed": int(r["code_removed"])} for r in d["daily"]]
        json.dump(d, open(self.j, "w"))
        d["commits"] = [dict(x, total=int(r["commits_landed"])) for x, r in zip(d["commits"], csv.DictReader(open(self.o)))]
        json.dump(d, open(self.j, "w"))
        self.assertEqual(validate_daily.validate(self.o, self.j)[0], [])
        d["commits"][0]["total"] = 99999
        json.dump(d, open(self.j, "w"))
        self.assertTrue(any("page total 99999" in e for e in validate_daily.validate(self.o, self.j)[0]))

    def test_validate_catches_disagreement(self):
        d = json.load(open(self.j)); d["commits"] = d["commits"][:-1]; d["rows"][0][2] = 999
        json.dump(d, open(self.j, "w"))
        errs = validate_daily.validate(self.o, self.j, legacy=True)[0]
        self.assertTrue(any("commits covers 2 of 3" in e for e in errs), errs)
        self.assertTrue(any("table tokens" in e for e in errs), errs)
        rows = list(csv.reader(open(self.o)))
        del rows[2]
        csv.writer(open(self.o, "w", newline="")).writerows(rows)
        self.assertTrue(any("contiguous" in e for e in validate_daily.validate(self.o, self.j, legacy=True)[0]))


if __name__ == "__main__":
    unittest.main()
