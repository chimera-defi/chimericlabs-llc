#!/usr/bin/env python3
"""Refresh the generated regions of research/building/index.html.

Reads from --handoff DIR:
  commits_by_project.csv        per-project commit counts and first/last dates
  headline_counts.json          data_through date, Codex own tokens and Claude best measured tokens

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
        first = row["first_commit_all_history"][:10]
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


def donut_html(slices, total, data_through):
    circles, legend, css = [], [], []
    cum = 0
    for i, s in enumerate(slices, start=1):
        start = round(1000 * cum / total)
        cum += s["n"]
        end = round(1000 * cum / total)
        length = max(end - start - GAP_UNITS, 1)
        circles.append(
            f'<circle cx="100" cy="100" r="70" fill="none" stroke-width="36" class="slice slice-{i}" '
            f'pathLength="1000" stroke-dasharray="{length} {1000 - length}" stroke-dashoffset="{-start}"></circle>'
        )
        pct = 100.0 * s["n"] / total
        legend.append(
            f'<li><i class="swatch slice-bg-{i}" aria-hidden="true"></i><span>{html.escape(s["label"])}</span>'
            f'<span class="donut-n">{s["n"]:,} · {pct:.1f}%</span></li>'
        )
        css.append(f".slice-{i} {{ stroke: {s['colour']}; }} .slice-bg-{i} {{ background: {s['colour']}; }}")
    top = [f'{html.escape(s["label"])} {100.0 * s["n"] / total:.1f}%' for s in slices[:3]]
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
        rx = re.compile(re.escape(open_m) + r".*?" + re.escape(close_m), re.S)
        found = len(rx.findall(text))
        if found:
            hits += found
            text = rx.sub(lambda m, o=open_m, c=close_m: o + body + c, text)
    if hits != 1:
        sys.exit(f"marker gen:{name} found {hits} times, expected 1")
    return text


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--handoff", required=True, help="directory with the three handoff inputs")
    ap.add_argument("--aliases", help="JSON file {directory_name: display_label}, kept outside the repo")
    ap.add_argument("--page", default=DEFAULT_PAGE, help="page to rewrite (default: research/building/index.html)")
    args = ap.parse_args()

    rows, headline, aliases = read_inputs(args.handoff, args.aliases)
    data_through = headline["data_through"][:10]
    groups = build_groups(rows, aliases)
    total = sum(int(r[COMMITS_COL]) for r in rows)
    named_keys = [k for k, _, _ in GROUPS]
    n_projects = len(named_keys) + sum(1 for g in groups.values() if g["aliased"])

    # Biggest project: largest group that is not an "Other" catch-all.
    projects = [g for g in groups.values() if g["key"] in named_keys or g["aliased"]]
    biggest = max(projects, key=lambda g: g["n"])
    if biggest["label"] == "Claudefolio":
        biggest_line = f"Claudefolio, a portfolio research platform for AI agents, is the biggest: {biggest['n']:,} commits."
    else:
        biggest_line = f"{html.escape(biggest['label'])} is the biggest: {biggest['n']:,} commits."

    claude_total = int(headline["claude_tokens_best_measured"])
    codex_total = int(headline["codex_own_tokens_lifetime_on_host"])

    hero = "\n".join([
        f"<li>{total:,} commits across {n_projects} projects since October 2025.</li>",
        f"<li>{biggest_line}</li>",
        "<li>Most AI tokens are re-reads of saved context, not new writing.</li>",
    ])
    slices = donut_slices(groups, total)
    donut_figure, donut_css = donut_html(slices, total, data_through)

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

    tokens = "\n".join([
        '<div class="article-grid">',
        f'<article class="card"><h3>Claude</h3><p class="token-n">{claude_total / 1e9:.1f} billion tokens</p><p>Measured from 2026-07-10 to {data_through}, raw, cache reads included. Earlier logs are gone, so this is a floor, not a lifetime total.</p></article>',
        f'<article class="card"><h3>Codex</h3><p class="token-n">{codex_total / 1e9:.1f} billion tokens</p><p>Raw tokens Codex used itself on this server, cached input included, 2026-05-24 to {data_through}.</p></article>',
        '</div>',
        '<p class="ds-meta">Estimates, not a bill. The two tools count differently, so the totals are not added together.</p>',
    ])
    method = "\n".join([
        f"<li>Commits: <code>git log --all</code> on every local repo, counted once per commit even across branches, from 2025-10-01 to {data_through}. Commits by outside authors are left out. Merge commits and pull-request branch commits both count.</li>",
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
