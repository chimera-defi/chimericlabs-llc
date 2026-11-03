#!/usr/bin/env python3
"""Refresh the generated regions of research/building/index.html.

Reads from --handoff DIR:
  commits_by_project.csv        per-project commit counts and first/last dates
  headline_counts.json          data_through date, Codex own tokens and Claude best measured tokens
  codex_daily_corrected.csv     Codex own tokens per day, for the July–August share
  commits_scoped.csv            one row per commit, for the commits-per-month chart

Reads --ranges FILE (default: data.json next to the handoff directory), the
token study's range_summaries: per range [Claude main, Claude subagents, Codex,
recovered Claude]. The page leads with the window where both tools were measured.

Optional --aliases FILE is JSON {directory_name: display_label}. Keep it outside
the repo. Only rows that are not public and whose directory name is in the alias
file are shown, under their display label. Every other private row rolls into
"Other private work", so private repositories are never named.

Only the text between a marker pair is rewritten. HTML pages use
<!-- gen:NAME --> ... <!-- /gen:NAME -->. Inside <style>, use
/* gen:NAME */ ... /* /gen:NAME */ instead, because HTML comments there break
the CSS rule that follows them. Nothing outside the markers is touched, no
timestamps are written, and the output is deterministic, so re-running the
script produces no diff.

Python 3 standard library only. No JavaScript, no external resources.
"""
import argparse
import csv
import html
import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_PAGE = os.path.join(REPO_ROOT, "research", "building", "index.html")

# key, label, GitHub repos that roll into this group (public rows only)
GROUPS = [
    ("experiments", "Experiments monorepo", ["chimera-defi/Etc-mono-repo"]),
    ("eth2", "eth2-quickstart", ["chimera-defi/eth2-quickstart"]),
    ("crss", "crss", ["chimera-defi/claude-remote-session-skill"]),
    ("sharedstake", "SharedStake", ["SharedStake/SharedStake-ui", "chimera-defi/SharedDeposit"]),
    ("intelex", "Intelex", ["chimera-defi/ethglobal-cannes-2026-intelligence-exchange"]),
    ("walletradar", "Wallet Radar", ["chimera-defi/walletradar"]),
    ("skills", "Agent skills", ["chimera-defi/token-reduce-skill", "chimera-defi/devin-delegate", "chimera-defi/kimi-delegate-skill", "chimera-defi/delegate-skill", "chimera-defi/grok-delegate"]),
    ("specforge", "SpecForge", ["chimera-defi/specforge"]),
    ("dispatchbench", "DispatchBench", ["chimera-defi/dispatchbench"]),
    ("site", "This site", ["chimera-defi/chimericlabs-llc"]),
]

# Skill-card breakdown: label as printed, GitHub repo
SKILL_MEMBERS = [
    ("token-reduce", "chimera-defi/token-reduce-skill"),
    ("Devin", "chimera-defi/devin-delegate"),
    ("Kimi", "chimera-defi/kimi-delegate-skill"),
    ("index", "chimera-defi/delegate-skill"),
    ("Grok", "chimera-defi/grok-delegate"),
]

FOLD_BELOW_PCT = 1.5
OTHER_PUBLIC = ("other-public", "Other public")
OTHER_PRIVATE = ("other-private", "Other private work")
COMMITS_COL = "commits_since_2025-10_total"
SPARE_SLICE_COLOURS = 12  # --data-1 .. --data-12 cycle for named and aliased slices
GAP_UNITS = 3  # visible gap between donut slices, in pathLength units (out of 1000)

# First-commit corrections, checked against GitHub, for repos whose handoff date is wrong.
# chimericlabs-llc: the handoff says 2026-04-30; GitHub's first commit is 2026-03-30.
FIRST_COMMIT_FIXES = {"chimera-defi/chimericlabs-llc": "2026-03-30"}

# First day both Claude and Codex logs are complete (the token study's "since" range).
SAME_WINDOW_START = "2026-09-07"

# Before-AI baseline, pulled 2026-11-03 from GitHub's GraphQL API, once per calendar year:
#   user(login: "chimera-defi") { contributionsCollection(from: "YYYY-01-01T00:00:00Z",
#     to: "YYYY-12-31T23:59:59Z") { totalCommitContributions restrictedContributionsCount } }
# totalCommitContributions 2021: 289, 2022: 9, 2023: 204, 2024: 112. This account only;
# earlier employer work is not in it. Same field, 2026-01-01 to 2026-10-31: 5,433.
# (restrictedContributionsCount is left out: it is not commits only.)
BEFORE_AI = {"from": "2021", "to": "2024", "commits": 289 + 9 + 204 + 112, "months": 48,
             "github_2026": 5433, "github_2026_span": "January to October 2026", "github_2026_months": 10,
             "pulled": "2026-11-03"}


def slugify(label):
    return re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")


def read_inputs(handoff, aliases_path):
    with open(os.path.join(handoff, "commits_by_project.csv"), encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    with open(os.path.join(handoff, "headline_counts.json"), encoding="utf-8") as fh:
        headline = json.load(fh)
    aliases = {}
    if aliases_path:
        with open(aliases_path, encoding="utf-8") as fh:
            aliases = json.load(fh)
    return rows, headline, aliases


def assign_group(row, aliases):
    """Return (key, label, aliased) for one CSV row."""
    if row["visibility"] == "public":
        for key, label, repos in GROUPS:
            if row["github_repo"] in repos:
                return key, label, False
        return OTHER_PUBLIC[0], OTHER_PUBLIC[1], False
    if row["project"] in aliases:
        label = aliases[row["project"]]
        return slugify(label), label, True
    return OTHER_PRIVATE[0], OTHER_PRIVATE[1], False


def build_groups(rows, aliases):
    groups = {}
    for key, label, _ in GROUPS:
        groups[key] = {"key": key, "label": label, "n": 0, "first": None, "last": None, "aliased": False}
    groups[OTHER_PUBLIC[0]] = {"key": OTHER_PUBLIC[0], "label": OTHER_PUBLIC[1], "n": 0, "first": None, "last": None, "aliased": False}
    groups[OTHER_PRIVATE[0]] = {"key": OTHER_PRIVATE[0], "label": OTHER_PRIVATE[1], "n": 0, "first": None, "last": None, "aliased": False}
    for row in rows:
        key, label, aliased = assign_group(row, aliases)
        g = groups.setdefault(key, {"key": key, "label": label, "n": 0, "first": None, "last": None, "aliased": aliased})
        g["n"] += int(row[COMMITS_COL])
        first = FIRST_COMMIT_FIXES.get(row["github_repo"], row["first_commit_all_history"][:10])
        last = row["last_commit"][:10]
        g["first"] = first if g["first"] is None else min(g["first"], first)
        g["last"] = last if g["last"] is None else max(g["last"], last)
    for key, label, _ in GROUPS:
        if groups[key]["n"] == 0:
            sys.exit(f"no commits matched named group {key}")
    return groups


def donut_slices(groups, total):
    """Named and aliased groups above the fold, then Other public, then Other private work."""
    named = [g for g in groups.values() if g["key"] in {k for k, _, _ in GROUPS}]
    aliased = [g for g in groups.values() if g["aliased"]]
    kept, folded = [], 0
    for g in named:
        if 100.0 * g["n"] / total < FOLD_BELOW_PCT:
            folded += g["n"]
        else:
            kept.append(g)
    kept += aliased
    kept.sort(key=lambda g: (-g["n"], g["label"]))
    slices = [dict(g, colour=None) for g in kept]
    other_pub = groups[OTHER_PUBLIC[0]]["n"] + folded
    if other_pub:
        slices.append({"key": OTHER_PUBLIC[0], "label": OTHER_PUBLIC[1], "n": other_pub, "colour": "var(--data-effort-medium)"})
    other_priv = groups[OTHER_PRIVATE[0]]["n"]
    if other_priv:
        slices.append({"key": OTHER_PRIVATE[0], "label": OTHER_PRIVATE[1], "n": other_priv, "colour": "var(--data-effort-low)"})
    spare = 0
    for s in slices:
        if s["colour"] is None:
            s["colour"] = f"var(--data-{spare % SPARE_SLICE_COLOURS + 1})"
            spare += 1
    return slices


def tenths(slices, total):
    """Percentages to one decimal that add up to exactly 100.0 (largest remainder)."""
    raw = [1000.0 * s["n"] / total for s in slices]
    out = [int(r) for r in raw]
    order = sorted(range(len(raw)), key=lambda i: (out[i] - raw[i], i))
    for i in order[:1000 - sum(out)]:
        out[i] += 1
    return [t / 10 for t in out]


def donut_html(slices, total, data_through):
    circles, legend, css = [], [], []
    cum = 0
    pcts = tenths(slices, total)
    for i, s in enumerate(slices, start=1):
        start = round(1000 * cum / total)
        cum += s["n"]
        end = round(1000 * cum / total)
        length = max(end - start - GAP_UNITS, 1)
        circles.append(
            f'<circle cx="100" cy="100" r="70" fill="none" stroke-width="36" class="slice slice-{i}" '
            f'pathLength="1000" stroke-dasharray="{length} {1000 - length}" stroke-dashoffset="{-start}"></circle>'
        )
        pct = pcts[i - 1]
        legend.append(
            f'<li><i class="swatch slice-bg-{i}" aria-hidden="true"></i><span>{html.escape(s["label"])}</span>'
            f'<span class="donut-n">{s["n"]:,} · {pct:.1f}%</span></li>'
        )
        css.append(f".slice-{i} {{ stroke: {s['colour']}; }} .slice-bg-{i} {{ background: {s['colour']}; }}")
    ranked = sorted(range(len(slices)), key=lambda i: (-slices[i]["n"], i))[:3]
    top = [f'{html.escape(slices[i]["label"])} {pcts[i]:.1f}%' for i in ranked]
    aria = (f"Commits by project since October 2025, {total:,} in all. Largest: "
            f"{top[0]}, {top[1]}, {top[2]}.")
    figure = "\n".join([
        '<figure class="article-chart article-donut">',
        '<h3>Commits by project since October 2025</h3>',
        '<div class="donut-wrap">',
        f'<svg viewBox="0 0 200 200" role="img" aria-label="{aria}" xmlns="http://www.w3.org/2000/svg">',
        '<g transform="rotate(-90 100 100)">',
        *circles,
        '</g>',
        f'<text x="100" y="96" text-anchor="middle" class="donut-total">{total:,}</text>',
        '<text x="100" y="118" text-anchor="middle" class="chart-small">commits</text>',
        '</svg>',
        '<ol class="donut-legend">',
        *legend,
        '</ol>',
        '</div>',
        f'<figcaption>Data through {data_through}. Private repos are not named; their commits are in “Other private work”.</figcaption>',
        '</figure>',
    ])
    return figure, "\n".join(css)


def monthly_commits(handoff, data_through):
    """Operator and agent commits per calendar month, from 2025-10 to the last full month."""
    counts = {}
    with open(os.path.join(handoff, "commits_scoped.csv"), encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            if r["scope"] == "third_party" or not ("2025-10-01" <= r["date_utc"][:10] <= data_through):
                continue
            counts[r["date_utc"][:7]] = counts.get(r["date_utc"][:7], 0) + 1
    return sorted((m, n) for m, n in counts.items() if m < data_through[:7])


def monthly_html(months):
    """Bar chart of commits per month with a dashed before-AI reference line."""
    names = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
    month_name = lambda m: f"{names[int(m[5:]) - 1]} {m[:4]}"
    if len(months) < 2:
        sys.exit("monthly chart needs at least two full months of commits")
    base = BEFORE_AI["commits"] / BEFORE_AI["months"]
    left, right, top, bottom, w, h = 52, 56, 12, 28, 420, 220
    top_n = -(-max(n for _, n in months) // 1000) * 1000
    slot = (w - left - right) / len(months)
    y = lambda v: top + (h - top - bottom) * (1 - v / top_n)
    parts = []
    for t in range(0, top_n + 1, 1000):
        parts.append(f'<line class="bars-grid" x1="{left}" x2="{w - right}" y1="{y(t):.1f}" y2="{y(t):.1f}"></line>')
        parts.append(f'<text x="{left - 6}" y="{y(t) + 4:.1f}" text-anchor="end" class="chart-small">{t:,}</text>')
    for i, (m, n) in enumerate(months):
        x = left + i * slot + slot * 0.15
        label = f"{names[int(m[5:]) - 1]} {m[:4]}: {n:,} commits"
        parts.append(f'<rect class="bars-bar" x="{x:.1f}" y="{y(n):.1f}" width="{slot * 0.7:.1f}" height="{y(0) - y(n):.1f}"><title>{label}</title></rect>')
        if i % 3 == 0:
            parts.append(f'<text x="{x + slot * 0.35:.1f}" y="{h - 8}" text-anchor="middle" class="chart-small">{names[int(m[5:]) - 1]} ’{m[2:4]}</text>')
    parts.append(f'<line class="bars-base" x1="{left}" x2="{w - right}" y1="{y(base):.1f}" y2="{y(base):.1f}"></line>')
    parts.append(f'<text x="{w - right + 4}" y="{y(base) - 4:.1f}" class="chart-small">≈{base:.0f}/mo</text>')
    first, last = months[0], months[-1]
    aria = (f"Commits per month, {names[int(first[0][5:]) - 1]} {first[0][:4]} to {names[int(last[0][5:]) - 1]} {last[0][:4]}, "
            f"rising from {first[1]:,} to {last[1]:,}. A dashed line at about {base:.0f} a month marks the "
            f"{BEFORE_AI['from']}–{BEFORE_AI['to']} average before AI agents.")
    return "\n".join([
        '<figure class="article-chart article-bars">',
        '<h3>Commits per month, against the before-AI baseline</h3>',
        f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{aria}" xmlns="http://www.w3.org/2000/svg">',
        *parts,
        '</svg>',
        '<p class="article-legend"><span><i class="swatch-bars" aria-hidden="true"></i>Commits that month</span>'
        f'<span><i class="swatch-base" aria-hidden="true"></i>Before AI agents ({BEFORE_AI["from"]}–{BEFORE_AI["to"]}, this GitHub account): about {base:.0f} commits a month</span></p>',
        '</figure>',
    ])


def skill_counts(rows):
    by_repo = {r["github_repo"]: int(r[COMMITS_COL]) for r in rows if r["visibility"] == "public"}
    return [by_repo.get(repo, 0) for _, repo in SKILL_MEMBERS]


def fill(text, name, body):
    """Replace the body of exactly one marker pair named NAME. Accepts HTML or CSS-comment markers."""
    hits = 0
    for open_m, close_m in (
        (f"<!-- gen:{name} -->", f"<!-- /gen:{name} -->"),
        (f"/* gen:{name} */", f"/* /gen:{name} */"),
    ):
        opens, closes = text.count(open_m), text.count(close_m)
        if opens == closes == 0:
            continue
        a, b = text.find(open_m), text.find(close_m)
        if opens != 1 or closes != 1 or b < a:
            sys.exit(f"marker gen:{name}: {opens} opening and {closes} closing, expected one pair in order")
        hits += 1
        text = text[:a + len(open_m)] + body + text[b:]
    if hits != 1:
        sys.exit(f"marker gen:{name} found {hits} times, expected 1")
    return text


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--handoff", required=True, help="directory with the three handoff inputs")
    ap.add_argument("--aliases", help="JSON file {directory_name: display_label}, kept outside the repo")
    ap.add_argument("--page", default=DEFAULT_PAGE, help="page to rewrite (default: research/building/index.html)")
    ap.add_argument("--ranges", help="token study data.json with range_summaries (default: HANDOFF/../data.json)")
    args = ap.parse_args()

    rows, headline, aliases = read_inputs(args.handoff, args.aliases)
    data_through = headline["data_through"][:10]
    ranges_path = args.ranges or os.path.join(args.handoff, os.pardir, "data.json")
    with open(ranges_path, encoding="utf-8") as fh:
        ranges = json.load(fh)["range_summaries"]
    groups = build_groups(rows, aliases)
    total = sum(int(r[COMMITS_COL]) for r in rows)
    named_keys = [k for k, _, _ in GROUPS]

    # Biggest project: largest group that is not an "Other" catch-all.
    projects = [g for g in groups.values() if g["key"] in named_keys or g["aliased"]]
    biggest = max(projects, key=lambda g: g["n"])
    biggest_word = "biggest" if biggest["n"] >= groups[OTHER_PRIVATE[0]]["n"] else "biggest named project"
    if biggest["label"] == "Claudefolio":
        biggest_line = f"Claudefolio, a portfolio research platform for AI agents, is the {biggest_word}: {biggest['n']:,} commits."
    else:
        biggest_line = f"{html.escape(biggest['label'])} is the {biggest_word}: {biggest['n']:,} commits."

    claude_total = int(headline["claude_tokens_best_measured"])
    codex_total = int(headline["codex_own_tokens_lifetime_on_host"])

    hero = "\n".join([
        f"<li>{total:,} commits since October 2025, across the projects below and other public and private work.</li>",
        f"<li>{biggest_line}</li>",
    ])
    slices = donut_slices(groups, total)
    donut_figure, donut_css = donut_html(slices, total, data_through)
    monthly_figure = monthly_html(monthly_commits(args.handoff, data_through))

    def meta(g):
        return f'<p class="ds-meta">{g["first"]} → {g["last"]} · {g["n"]:,} commits since Oct 2025</p>'

    # Card keys: the named groups, plus "claudefolio" (the alias group, slugified from its label).
    card_meta = {}
    for key in named_keys + ["claudefolio"]:
        g = groups.get(key)
        if g is None:
            sys.exit(f"no card group {key}: alias file must map the Claudefolio directory to the label Claudefolio")
        if key == "skills":
            c = skill_counts(rows)
            card_meta[key] = (f'<p class="ds-meta">{g["first"]} → {g["last"]} · {g["n"]:,} commits since Oct 2025 '
                              f'(token-reduce {c[0]}, Devin {c[1]}, Kimi {c[2]}, skill index {c[3]}, Grok {c[4]})</p>')
        else:
            card_meta[key] = meta(g)

    # Same-window figures: Claude = main + subagents (recovered logs excluded); Codex = own tokens.
    def window(key):
        r = ranges[key]
        return (r[0] + r[1]) / 1e9, r[2] / 1e9

    since_claude, since_codex = window("since")
    d30_claude, d30_codex = window("30")
    d7_claude, d7_codex = window("7")
    with open(os.path.join(args.handoff, "codex_daily_corrected.csv"), encoding="utf-8", newline="") as fh:
        codex_days = list(csv.DictReader(fh))
    tokens = "\n".join([
        '<div class="article-grid">',
        f'<article class="card"><h3>Claude</h3><p class="token-n">{since_claude:.1f} billion tokens</p><p>Observed over the same dates for both tools, {SAME_WINDOW_START} to {data_through} (last day partial). Raw, cache reads included; {ranges["since"][3] / 1e9:.1f} billion tokens from recovered logs are left out.</p></article>',
        f'<article class="card"><h3>Codex</h3><p class="token-n">{since_codex:.1f} billion tokens</p><p>Same dates, {SAME_WINDOW_START} to {data_through}. Raw tokens Codex used itself on this server, cached input included.</p></article>',
        '</div>',
        f'<p>Same comparison, shorter windows: last 30 days, Claude {d30_claude:.1f} billion and Codex {d30_codex:.1f} billion; last 7 days, Claude {d7_claude:.1f} billion and Codex {d7_codex:.1f} billion.</p>',
        '<p><a href="../token-usage/">The full token usage study →</a></p>',
        '<p><a href="../../dispatchbench/">DispatchBench: how we pick which model builds what →</a></p>',
    ])
    method = "\n".join([
        f"<li>Commits: <code>git log --all</code> on every local repo, counted once per commit even across branches, from 2025-10-01 to {data_through}. Commits by outside authors are left out. Merge commits and pull-request branch commits both count. Totals can step up between refreshes when a sweep picks up more branches.</li>",
        f"<li>Claude tokens: local session logs, deduplicated per message, taking the larger of the 2026-10-29 audit and the daily ledger for each day.</li>",
        "<li>Codex tokens: every local session log, counting only each session's own use, not the history it inherited from a parent session.</li>",
        "<li>Not counted: ChatGPT chat usage, which has no token meter we can read, and small Grok, Devin and Kimi runs.</li>",
        "<li>No invoice-backed dollar total exists yet. That is why the page shows tokens.</li>",
    ])

    with open(args.page, encoding="utf-8", newline="") as fh:
        text = fh.read()

    text = fill(text, "kicker", f"Lab notes · {data_through}")
    text = fill(text, "hero-bullets", "\n" + hero + "\n")
    text = fill(text, "donut", donut_figure)
    text = fill(text, "donut-css", "\n" + donut_css + "\n")
    text = fill(text, "monthly", monthly_figure)
    for key, line in card_meta.items():
        text = fill(text, f"card-meta-{key}", line)
    text = fill(text, "tokens", tokens)
    text = fill(text, "method", "\n" + method + "\n")
    text = fill(text, "snapshot", f"<li>One snapshot in time: {data_through}.</li>")

    with open(args.page, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    print(f"ok: {len(rows)} rows, {len(groups)} groups, {len(slices)} donut slices, total {total:,}")


if __name__ == "__main__":
    main()
