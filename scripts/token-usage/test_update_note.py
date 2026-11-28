#!/usr/bin/env python3
"""update_note.py after a UTC rollover: daily.csv runs to today, data.json still ends yesterday. Run: python3 -I scripts/token-usage/test_update_note.py"""
import csv, json, os, subprocess, sys, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
COLS = ["date", "commits_landed", "tokens_total", "tokens_claude", "claude_token_status"]

def row(d, c=1): return {"date": d, "commits_landed": str(c), "tokens_total": "5", "tokens_claude": "5", "claude_token_status": "measured"}

def run(csv_dates, json_dates):
    with tempfile.TemporaryDirectory() as t:
        P = lambda n: os.path.join(t, n)
        data = lambda ds: {"data_through": ds[-1] + " 09:00:00 UTC", "daily": [row(d) for d in ds]}
        for n in ("old.json", "new.json"):
            with open(P(n), "w") as f: json.dump(data(json_dates), f)
        with open(P("d.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, COLS, extrasaction="ignore"); w.writeheader(); w.writerows(row(d) for d in csv_dates)
        open(P("w.csv"), "w").write("date,week_reset,percent_used,sampled_at\n2026-11-26,2026-11-30T00:00:00+00:00,50,\n")
        open(P("c.csv"), "w").write("date,section,text\n")
        return subprocess.run([sys.executable, "-I", os.path.join(HERE, "update_note.py"), P("old.json"), P("new.json"), P("d.csv"), P("w.csv"), P("o.json"), P("c.csv")], capture_output=True, text=True)

class T(unittest.TestCase):
    def test_equal(self): self.assertEqual(run(["2026-11-25", "2026-11-26"], ["2026-11-25", "2026-11-26"]).returncode, 0)
    def test_rollover_extra_days(self): self.assertEqual(run(["2026-11-25", "2026-11-26", "2026-11-27", "2026-11-28"], ["2026-11-25", "2026-11-26"]).returncode, 0)
    def test_mismatch_still_fails(self): self.assertNotEqual(run(["2026-11-24", "2026-11-26"], ["2026-11-25", "2026-11-26"]).returncode, 0)
    def test_missing_days_fail(self): self.assertNotEqual(run(["2026-11-25"], ["2026-11-25", "2026-11-26"]).returncode, 0)

if __name__ == "__main__": unittest.main()
