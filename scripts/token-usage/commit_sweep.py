#!/usr/bin/env python3
"""One pass over every git repo on this host: one row per commit, with its actor, scope, landed flag and lines by file category.

Replaces the three sweeps that disagreed with each other (commit_sweep.py, commit_scope.py, loc_sweep.py):
they walked the repos separately and gave 27,671, 28,776 and 28,780 commits.

Rules (the doc is docs/commit-and-token-series.md):
- Refs: --branches --remotes --tags plus the HEAD of every worktree. Never --all. --all also reads per-worktree
  refs (refs/rewritten/*, refs/bisect/*), which only the checkout you ask can see, so the count depended on which
  worktree the sweep happened to open. In one monorepo that was 687 commits (646 pre-rewrite backup refs).
- One row per SHA across all clones and worktrees of a repo (object store).
- date_utc is the author date converted to UTC. Every series on the page uses the same day.
- landed = non-merge commit reachable from main/master (local or origin). Merge commits are kept, flagged is_merge.
- Lines are counted per file category (rules below). Binary files count as 0 lines. Renames are not followed,
  so a moved file is an add plus a delete. Merge commits carry 0 lines (git log --numstat prints no diff for them);
  the lines of a merged branch are counted on its own commits.
- If a commit is in several clones of one project, it is landed when it is on main in any of them.
usage: commit_sweep.py OUT_CSV [--roots DIR ...]   Python 3 standard library only, no network.
"""
import argparse
import csv
import datetime
import os
import re
import subprocess
import sys

ROOTS = ["/home/agents/workspace", "/home/agents/.sessions", "/home/agents/worktrees"]
CATS = ["src", "test", "doc", "cfg", "other", "noise"]
BULK_FILES = 100  # a commit touching more files than this is an import or mass move; excluded from the code basis

# Path rules. noise = never counted as code: dependencies, build output, lockfiles, generated or vendored files,
# data dumps (.csv/.tsv/.jsonl/.parquet and non-config .json), snapshots, images/notebooks/logs/databases, chain artifacts.
NOISE = re.compile(
    r"(^|/)(node_modules|vendor|third_party|dist|build|out|\.next|\.nuxt|coverage|__snapshots__|\.terraform|broadcast|"
    r"artifacts|cache|deployments|generated|__generated__|\.venv|site-packages)/"
    r"|(\.lock|\.min\.js|\.min\.css|\.map|\.snap|\.tfstate|\.pb\.go|_pb2\.py|\.csv|\.tsv|\.jsonl|\.ndjson|\.parquet|\.svg|"
    r"\.ipynb|\.log|\.sqlite|\.db|\.wasm|\.abi)$"
    r"|(^|/)(package-lock\.json|yarn\.lock|pnpm-lock\.yaml|Cargo\.lock|poetry\.lock|go\.sum|uv\.lock|Gemfile\.lock|"
    r"composer\.lock|bun\.lockb)$", re.I)
JSON_DATA = re.compile(r"\.json$", re.I)
JSON_CFG = re.compile(r"(^|/)(package|tsconfig[^/]*|composer|\.eslintrc|\.prettierrc|vercel|turbo|biome|deno|jsconfig)\.json$", re.I)
DOC = re.compile(r"\.(md|mdx|txt|rst|adoc)$", re.I)
CFG = re.compile(r"\.(ya?ml|toml|ini|cfg|conf|env\.example|gitignore|dockerignore)$|(^|/)(Dockerfile|Makefile|\.github/)", re.I)
TEST = re.compile(r"(^|/)(tests?|__tests__|spec|specs|e2e|mocks?|__mocks__|fixtures)/|(\.|_)(test|spec)\.[a-z]+$|(^|/)test_[^/]+$", re.I)
CODE = re.compile(r"\.(py|js|jsx|ts|tsx|go|rs|sol|sh|bash|rb|java|kt|c|h|cc|cpp|hpp|cs|swift|php|lua|sql|html|css|scss|vue|svelte|nix|tf|proto|vy|move|zig)$", re.I)

# Scope: who wrote it. third_party = upstream authors in forks and vendored clones; dropped from every series.
OPERATOR = re.compile(r"^(chimera|root$)", re.I)
AGENT_AUTHOR = re.compile(r"^(Claude$|Claude (Sonnet|Opus|Haiku|Fable)|GPT|Codex|Cursor Agent|Devin|OpenClaw|Agent Host|Worktree Recovery|Fable|Opus|Sonnet|Haiku)", re.I)


def category(path):
    if NOISE.search(path) or (JSON_DATA.search(path) and not JSON_CFG.search(path)):
        return "noise"
    if TEST.search(path):
        return "test"
    if DOC.search(path):
        return "doc"
    if CODE.search(path):
        return "src"
    if CFG.search(path) or JSON_CFG.search(path):
        return "cfg"
    return "other"


def tools_from_message(text, author, email):
    t = set()
    if re.search(r"Co-Authored-By:\s*Claude", text, re.I) or re.search(r"Generated with \[?Claude Code", text):
        t.add("claude")
    if re.search(r"Co-authored-by:\s*[^<\n]*(?:Codex|GPT|OpenAI)", text, re.I) or re.search(r"\[Agent:\s*[^\]]*(GPT|Codex)", text):
        t.add("codex")
    if re.search(r"cursoragent|Cursor Agent|cursor\.com|Co-authored-by:\s*Cursor", text, re.I):
        t.add("cursor")
    if re.search(r"copilot", text + author + email, re.I):
        t.add("other_agent")
    if re.search(r"aider|Co-authored-by:\s*(Gemini|Devin|Grok)|devin-ai|gemini", text, re.I):
        t.add("other_agent")
    return t


def tools_from_author(author):
    t = set()
    if re.search(r"^(Claude|Fable|Opus|Sonnet|Haiku)", author, re.I):
        t.add("claude")
    if re.search(r"^(GPT|Codex)", author, re.I):
        t.add("codex")
    for name, pat in (("cursor", r"^Cursor"), ("devin", r"^Devin"), ("openclaw", r"^OpenClaw")):
        if re.search(pat, author, re.I):
            t.add(name)
    return t


def git(d, *args):
    return subprocess.run(["git", "-C", d, *args], capture_output=True, text=True, errors="replace", timeout=1500)


def git_ok(d, *args):
    """Like git(), but a failure stops the sweep: a broken ref must not turn into silently missing history."""
    p = git(d, *args)
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args[:3])} failed in {d}: {p.stderr.strip()[:200]}")
    return p.stdout


def find_checkouts(roots):
    found = set()
    for r in roots:
        for dp, dn, fn in os.walk(r):
            if ".git" in dn or ".git" in fn:
                found.add(dp)
                dn[:] = [x for x in dn if x not in (".git", "node_modules", ".venv")]
            if dp[len(r):].count("/") >= 3:
                dn[:] = []
    stores = {}
    for d in sorted(found):
        p = git(d, "rev-parse", "--path-format=absolute", "--git-common-dir")
        if p.returncode == 0:
            stores.setdefault(p.stdout.strip(), d)
    return stores


def sweep_store(common, d):
    """Yield one row per commit of one object store. Deterministic: does not depend on which worktree d is."""
    project = os.path.basename(os.path.dirname(common)) if common.endswith("/.git") else os.path.basename(common)
    tips = [h for h in (git(d, "rev-parse", "HEAD").stdout.strip(),) if h]
    for line in git(d, "worktree", "list", "--porcelain").stdout.splitlines():
        if line.startswith("HEAD "):
            tips.append(line.split()[1])
    main = set()
    for ref in ("refs/heads/main", "refs/heads/master", "refs/remotes/origin/main", "refs/remotes/origin/master"):
        if git(d, "rev-parse", "--verify", "-q", ref).returncode == 0:
            main |= set(git(d, "rev-list", "--no-merges", ref).stdout.split())
    rs, us = "\x1e", "\x1f"
    fmt = rs + us.join(["%H", "%P", "%an", "%ae", "%aI", "%s", "%B"]) + us + "END"
    out = git_ok(d, "log", "--branches", "--remotes", "--tags", *sorted(set(tips)), "--no-renames", "--numstat", "--format=" + fmt)
    for rec in out.split(rs)[1:]:
        head, _, stat = rec.partition(us + "END")
        f = head.split(us)
        if len(f) < 7 or "\0" in f[0]:
            continue
        sha, parents, author, email, adate, subject, body = f[0], f[1].split(), f[2], f[3], f[4], f[5], us.join(f[6:])
        add = dict.fromkeys(CATS, 0)
        rem = dict.fromkeys(CATS, 0)
        files = binary = 0
        for l in stat.strip().splitlines():
            x = l.split("\t")
            if len(x) != 3:
                continue
            files += 1
            if not x[0].isdigit():
                binary += 1
                continue
            c = category(x[2])
            add[c] += int(x[0])
            rem[c] += int(x[1]) if x[1].isdigit() else 0
        scope = "operator" if OPERATOR.search(author) else "agent_author" if AGENT_AUTHOR.search(author) else "third_party"
        tools = tools_from_message(body + " " + subject, author, email)
        if scope == "agent_author":
            tools |= tools_from_author(author)
        date_utc = datetime.datetime.fromisoformat(adate).astimezone(datetime.timezone.utc).strftime("%Y-%m-%d")
        yield [sha[:12], project, date_utc, author, scope, "|".join(sorted(tools)), len(parents) > 1, files, binary,
               1 if sha in main else 0, subject[:100]] + [add[c] for c in CATS] + [rem[c] for c in CATS], sha


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("out")
    ap.add_argument("--roots", nargs="*", default=ROOTS)
    ap.add_argument("--strict", action="store_true", help="exit 1 if any repo could not be read (default: warn, skip it, exit 0)")
    args = ap.parse_args()
    stores = find_checkouts(args.roots)
    print(f"object stores: {len(stores)}", file=sys.stderr)
    seen, rows, skipped = {}, [], []
    for common, d in stores.items():
        try:
            swept = list(sweep_store(common, d))
        except RuntimeError as e:
            skipped.append(str(e))
            print(f"WARNING skipped unreadable repo: {e}", file=sys.stderr)
            continue
        for row, full in swept:
            if full in seen:  # same commit in two clones of one project: keep one row, OR the landed flag
                seen[full][9] = max(seen[full][9], row[9])
                continue
            seen[full] = row
            rows.append(row)
        print(f"{os.path.basename(os.path.dirname(common)) or common}: {len(rows)}", file=sys.stderr, flush=True)
    rows.sort(key=lambda r: (r[2], r[0]))
    header = ["sha", "project", "date_utc", "author", "scope", "tools_scoped", "is_merge", "files", "binary_files", "on_main", "subject"] \
        + ["added_" + c for c in CATS] + ["removed_" + c for c in CATS]
    with open(args.out, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)
    print(f"wrote {len(rows)} commits to {args.out}; skipped {len(skipped)} unreadable repos")
    if skipped and args.strict:
        sys.exit(1)


if __name__ == "__main__":
    main()
