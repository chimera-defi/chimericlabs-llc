#!/usr/bin/env python3
"""Compare the scheduled jobs on this host with research/wren/jobs/index.html.

Reads `systemctl --user list-timers` and `crontab -l`, then the job names listed
on the page (the <code> items). Prints what is on the host but not the page and
the reverse, and whether each group heading's number matches its items.
Crypto jobs are never named on the page: they are only checked as a count.
Exit 1 on any difference, so it can gate a refresh.

Run on the server that owns the jobs: python3 scripts/check_wren_jobs.py
Python 3 standard library only.
"""
import os
import re
import subprocess
import sys

PAGE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "research", "wren", "jobs", "index.html")

# cron script basename -> name on the page, where the two differ
CRON_NAMES = {
    "qmd-refresh-all": "qmd-refresh",
    "run_paper_track_cron": "paper-track",
    "check_paper_track_cron_status": "paper-track-status",
    "run_forward_trackers_cron": "forward-trackers",
    "check_forward_trackers_cron_status": "forward-trackers-status",
}


def host_jobs():
    out = subprocess.run(["systemctl", "--user", "list-timers", "--all", "--no-legend"], capture_output=True, text=True, check=True).stdout
    timers = {w[:-6] for line in out.splitlines() for w in line.split() if w.endswith(".timer")}
    cron = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout
    jobs = set(timers)
    for line in cron.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if "crypto" in line:
            jobs.add("crypto-cron")
            continue
        scripts = re.findall(r"([\w.-]+)\.(?:sh|py)\b", line)
        if not scripts:
            sys.exit(f"cron line with no script name, add it to CRON_NAMES: {line[:80]}")
        jobs.add(CRON_NAMES.get(scripts[0], scripts[0]))
    return jobs


def page_jobs(path):
    html = open(path, encoding="utf-8").read()
    names = re.findall(r"<code>([\w.-]+)</code>", html)
    groups = re.findall(r"<h2[^>]*>([^<(]+)\((\d+)\)</h2>(.*?)(?=<h2|</article>)", html, re.S)
    bad = [f"{g.strip()}: heading says {n}, lists {len(re.findall('<code>', body))}" for g, n, body in groups if "Crypto" not in g and int(n) != len(re.findall("<code>", body))]
    return set(names), bad


def main():
    host = host_jobs()
    crypto = {j for j in host if "crypto" in j}
    page, bad_groups = page_jobs(PAGE)
    missing = sorted(host - crypto - page)
    extra = sorted(page - host)
    print(f"host: {len(host)} jobs ({len(crypto)} crypto, not named on the page); page names {len(page)}")
    for label, items in (("on host, not on page", missing), ("on page, not on host", extra), ("group counts", bad_groups)):
        if items:
            print(f"{label}: " + "; ".join(items))
    return 1 if missing or extra or bad_groups else 0


if __name__ == "__main__":
    sys.exit(main())
