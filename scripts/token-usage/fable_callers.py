#!/usr/bin/env python3
"""Who talks to Fable, who invokes it, and how. Read-only; aggregates only (no session names, prompts or paths).
usage: python3 -I fable_callers.py OUT.json [--merge DATA.json] [--snippet SECTION10.html (needs --merge or --mcp-data DATA.json for the headline counts)]
  OUT.json     writes the traffic block
  --merge      also sets DATA.json["traffic"] = block (run after refresh.sh copies data.json into the repo)
env: CLAUDE_TRANSCRIPTS (default agent-memory live/claude-projects mirror), BUS_DB (default agent-host-chat-control state.sqlite), CODEX_SESSIONS (default ~/.codex/sessions)
Method:
 - A Fable invocation = a Claude transcript file with at least one assistant message whose model contains 'fable'.
   Subagent files (…/subagents/*.jsonl) are runs started through the Agent tool; their parent is <session>.jsonl next to the subagents dir.
   Main files are sessions started by a person, launcher or `claude -p`; entrypoint says which (cli, claude-desktop, sdk-cli).
 - The same count for opus-5-5 and sonnet-5-5 gives the comparison.
 - Bus rows come from coordination_messages (sender, recipient). A recipient whose NAME contains 'fable' is not proof it ran Fable:
   the transcript of such a session is checked for its real model (`named_fable_sessions`).
 - Launch paths other than the Agent tool (CLI flag, session-send, bus post, Agent Host MCP call) are counted from command text in
   Claude and Codex logs only where a command or bus summary names Fable as the model; zero is reported as zero with the window."""
import html, os, sys, json, glob, re, sqlite3, collections, datetime

TR = os.environ.get("CLAUDE_TRANSCRIPTS", "/home/agents/agent-memory/agents/claude/private/live/claude-projects")
DB = os.environ.get("BUS_DB", "/home/agents/agent-host-chat-control/state/state.sqlite")
CX = os.environ.get("CODEX_SESSIONS", os.path.expanduser("~/.codex/sessions"))
ENTRY = {"cli": "CLI session", "claude-desktop": "desktop session", "sdk-cli": "headless claude -p"}
SUBTYPE = {"reviewer": "reviewer subagent", "fable-reviewer": "reviewer subagent", "gpt-relay": "other subagent"}


def fam(model):
    m = model or ""
    if "fable" in m: return "fable"
    if "opus-5-5" in m: return "opus-5-5"
    if "sonnet-5-5" in m: return "sonnet-5-5"
    return None


def scan_file(f):
    counts = collections.Counter(); ep = None; win = {}
    for l in open(f, errors="ignore"):
        if '"assistant"' not in l: continue
        try: d = json.loads(l)
        except Exception: continue
        if d.get("type") != "assistant": continue
        m = d.get("message") or {}
        k = fam(m.get("model"))
        if not k: continue
        counts[k] += 1; ep = d.get("entrypoint") or ep
        ts = (d.get("timestamp") or "")[:10]
        if ts:
            a, z = win.get(k, (ts, ts)); win[k] = (min(a, ts), max(z, ts))
    return counts, ep, win


def transcripts():
    runs = []; main_model = {}
    files = glob.glob(TR + "/**/*.jsonl", recursive=True)
    for f in files:
        counts, ep, win = scan_file(f)
        if not counts: continue
        sub = "/subagents/" in f
        meta = {}
        mf = f[:-6] + ".meta.json"
        if os.path.exists(mf):
            try: meta = json.load(open(mf))
            except Exception: pass
        main_model[f] = counts.most_common(1)[0][0]
        runs.append(dict(f=f, sub=sub, counts=counts, ep=ep, win=win, agentType=meta.get("agentType") or ""))
    return runs, main_model, len(files)


def summarize(runs, main_model):
    by_model = collections.defaultdict(lambda: dict(runs=0, messages=0, subagent_runs=0, main_sessions=0))
    inv = collections.Counter(); path = collections.Counter(); sub_type = collections.Counter(); weekly = collections.defaultdict(collections.Counter)
    for r in runs:
        for k, n in r["counts"].items():
            b = by_model[k]; b["runs"] += 1; b["messages"] += n; b["subagent_runs" if r["sub"] else "main_sessions"] += 1
            a0 = r["win"][k][0]
            wk = (datetime.date.fromisoformat(a0) - datetime.timedelta(days=datetime.date.fromisoformat(a0).weekday())).isoformat()
            weekly[wk][k] += 1
        if "fable" not in r["counts"]: continue
        if r["sub"]:
            pm = main_model.get(r["f"].split("/subagents/")[0] + ".jsonl")
            inv["Claude %s session, via Agent tool" % (pm or "parent not mirrored")] += 1
            path["Agent tool (subagent)"] += 1
            sub_type[SUBTYPE.get(r["agentType"], "model override on %s" % (r["agentType"] if r["agentType"] in ("general-purpose", "workflow-subagent") else "other agent type"))] += 1
        else:
            label = ENTRY.get(r["ep"], "other entrypoint")
            inv["Claude %s started on Fable" % label] += 1
            path[label] += 1
    return by_model, inv, path, sub_type, weekly


def window(runs, k=None):
    d = [r["win"][m][0] for r in runs for m in r["win"] if k in (None, m)]; e = [r["win"][m][1] for r in runs for m in r["win"] if k in (None, m)]
    return (min(d), max(e)) if d else (None, None)


def klass(name):
    n = name.lower()
    for key, label in (("chatgpt", "ChatGPT"), ("kepler", "Kepler"), ("codex", "Codex"), ("wren", "Orchestrator agent"), ("bus-follower", "Bus followers"), ("workflow-checkpoint", "Scheduled jobs"),
                       ("ack-hygiene", "Scheduled jobs"), ("crypto-hype-watch", "Scheduled jobs"), ("bus-stall-watcher", "Scheduled jobs"), ("bus-router", "Bus followers"),
                       ("launcher", "Claude launchers"), ("claude", "Claude sessions"), ("agent-host", "Agent Host"), ("sharpe", "ChatGPT/Codex research roles")):
        if key in n: return label
    return "Other"


def bus():
    c = sqlite3.connect("file:%s?mode=ro" % DB, uri=True)
    rng = c.execute("select min(substr(created_at,1,10)), max(substr(created_at,1,10)), count(*) from coordination_messages").fetchone()
    sent = collections.Counter(); recv = collections.Counter(); to_fable = collections.Counter(); to_fable_sender = collections.Counter()
    fable_rng = [None, None]
    for s, r, d in c.execute("select sender, recipient, substr(created_at,1,10) from coordination_messages"):
        sent[klass(s)] += 1; recv[klass(r)] += 1
        if "fable" in r.lower():
            to_fable[r] += 1; to_fable_sender[klass(s)] += 1
            fable_rng = [min(filter(None, [fable_rng[0], d])), max(filter(None, [fable_rng[1], d]))]
    named = c.execute("select count(*) from coordination_messages where lower(summary) like '%--model fable%' or lower(summary) like '%model: fable%' or lower(summary) like '%model fable%'").fetchone()[0]
    kep = collections.Counter(klass(r) for (r,) in c.execute("select recipient from coordination_messages where sender like '%kepler%'"))
    kep_in = collections.Counter(klass(s) for (s,) in c.execute("select sender from coordination_messages where recipient like '%kepler%'"))
    kep_f = c.execute("select count(*) from coordination_messages where sender like '%kepler%' and lower(recipient) like '%fable%'").fetchone()[0]
    mcp = c.execute("select min(substr(created_at,1,10)), max(substr(created_at,1,10)) from usage_events").fetchone()
    mcp_posts = c.execute("select count(*) from usage_events where tool='coordination_post' and event_type='request_completed'").fetchone()[0]
    return dict(range=rng[:2], messages=rng[2], sent=sent, received=recv, to_fable_named=sum(to_fable.values()), to_fable_named_recipients=len(to_fable),
                to_fable_named_by_sender=to_fable_sender, to_fable_named_range=fable_rng, summaries_naming_fable_model=named,
                kepler_sent_to=kep, kepler_received_from=kep_in, kepler_to_fable_named=kep_f, mcp_range=mcp, mcp_coordination_post_calls=mcp_posts), set(to_fable)


def named_fable_models(names):
    """Real model of sessions whose bus name contains 'fable': match transcript project dirs by name."""
    out = collections.Counter()
    for n in names:
        tail = n.replace("claude-", "", 1)
        for d in glob.glob(TR + "/*%s*" % tail):
            for f in glob.glob(d + "/*.jsonl"):
                counts, _, _ = scan_file(f)
                for k, v in counts.items(): out[k] += v
    return out


import shlex


class CMD:
    @staticmethod
    def search(cmd):
        """True when a shell segment starts `claude` (or new-session) and passes --model/-m fable."""
        for seg in re.split(r"[;&|\n]+", cmd):
            try: t = shlex.split(seg)
            except ValueError: continue
            if not t or os.path.basename(t[0]) not in ("claude", "new-session"): continue
            for i, w in enumerate(t):
                v = w.split("=", 1)[1] if w.startswith("--model=") else (t[i + 1] if w in ("--model", "-m") and i + 1 < len(t) else "")
                if re.fullmatch(r"(claude-)?fable(-[\w.-]+)?", v): return True
        return False


def commands(d):
    """Shell command strings from one log line: Claude tool_use Bash input, Codex function_call arguments."""
    out = []
    m = d.get("message")
    if d.get("type") == "assistant" and isinstance(m, dict) and isinstance(m.get("content"), list):
        for blk in m["content"]:
            if isinstance(blk, dict) and blk.get("type") == "tool_use" and isinstance(blk.get("input"), dict): out.append(str(blk["input"].get("command") or ""))
    p = d.get("payload")
    if isinstance(p, dict) and p.get("type") == "function_call":
        try: a = json.loads(p.get("arguments") or "{}")
        except Exception: a = {}
        c = a.get("cmd") or a.get("command") or ""
        out.append(" ".join(c) if isinstance(c, list) else str(c))
    return out


def launch_commands():
    """Shell commands that start Claude with Fable as the model, by log source."""
    res = collections.Counter()
    for src, root in (("claude", TR), ("codex", CX)):
        for f in glob.glob(root + "/**/*.jsonl", recursive=True):
            for l in open(f, errors="ignore"):
                if "fable" not in l: continue
                try: d = json.loads(l)
                except Exception: continue
                res[src] += sum(1 for c in commands(d) if CMD.search(c))
    return {k: v for k, v in res.items() if v}


def donut(id_, title, rows, note):
    """Inline SVG donut + table fallback. rows: [[label, n], ...]; slices below 2% fold into Other."""
    tot = sum(n for _, n in rows) or 1
    keep = [r for r in rows if r[1] / tot >= 0.02 or len(rows) <= 7]; rest = tot - sum(n for _, n in keep)
    if rest: keep.append(["Other (small)", rest])
    R, C, acc, arcs, tr = 40, 2 * 3.14159265 * 40, 0.0, [], []
    for i, (lab, n) in enumerate(keep):
        L = C * n / tot
        arcs.append('<circle r="%d" cx="60" cy="60" fill="none" stroke="var(--data-model-%d)" stroke-width="22" stroke-dasharray="%.2f %.2f" stroke-dashoffset="%.2f" transform="rotate(-90 60 60)"/>' % (R, i % 8, L, C - L, -acc))
        acc += L
        tr.append('<tr><td><i style="background:var(--data-model-%d)"></i>%s</td><td class="numeric">%s</td><td class="numeric">%.1f%%</td></tr>' % (i % 8, html.escape(lab), format(n, ","), 100 * n / tot))
    return ('<figure class="tr-donut" id="%s"><svg viewBox="0 0 120 120" role="img" aria-label="%s: %s"><title>%s</title>%s</svg>'
            '<figcaption><b>%s</b><table><thead><tr><th>Group</th><th>Count</th><th>Share</th></tr></thead><tbody>%s</tbody></table><small>%s</small></figcaption></figure>'
            % (id_, title, html.escape(", ".join("%s %d" % (l, n) for l, n in keep), quote=True), title, "".join(arcs), title, "".join(tr), note))


def snippet(b, mcp):
    cv = b["coverage"]; fm = b["invocations_by_model"]
    inv = [[l.replace("Claude ", "", 1).replace(" session, via Agent tool", " session, Agent tool").replace(" started on Fable", ", started on Fable"), n] for l, n in b["fable_invokers"]]
    paths = b["fable_paths"]; tf = b["bus_to_fable_named"]
    css = ("<style>.tr-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:20px;margin:10px 0}.tr-donut{margin:0;min-width:0}"
           ".tr-donut svg{width:min(100%,180px);display:block;margin:0 auto 8px}.tr-donut table{width:100%;font-size:13px;border-collapse:collapse}.tr-donut th,.tr-donut td{padding:2px 4px;text-align:left}"
           ".tr-donut td.numeric,.tr-donut th:nth-child(n+2){text-align:right}.tr-donut i{display:inline-block;width:10px;height:10px;margin-right:6px;border-radius:2px}.tr-donut small{display:block;margin-top:6px}</style>")
    n = mcp["calls_completed"]
    head = (f'<p id="mcp-headline"><span class="numeric" data-exact="{n}" data-kind="count" title="{n:,}">{n / 1000:.1f}K</span> completed calls, {mcp["tools"]} tools, '
            f'{mcp["first"]}..{mcp["last"]}, three MCPs. {mcp["request_failed"]:,} failed; {mcp["transport_failed"]:,} never reached the tool (connection or timeout). Activity, not tokens.</p>')
    fb = fm.get("fable", {}); ob = fm.get("opus-5-5", {})
    real = dict(tf["real_model_of_those_sessions_messages"])
    real_txt = ", ".join("%s (%s)" % (format(v, ","), {"sonnet-5-5": "Sonnet 5.5", "opus-5-5": "Opus 5.5"}.get(k, k)) for k, v in real.items()) or "no matching transcript"
    # Short sentences: the page rules allow 15 words and two numbers each. Message totals live in the coverage note.
    find = ('<p id="traffic-finding">Fable ran in %d Claude transcripts. Opus 5.5 ran in %d. %d of the Fable runs (%d%%) were subagents spawned by Claude sessions. '
            '%d%% of those came from sessions whose main model is Opus 5.5. The logs show no Fable run started directly by ChatGPT, Codex or Kepler. '
            'They message Claude sessions over the bus. What those sessions spawn is the visible start. '
            '%s bus messages went to sessions with “fable” in the name. Those transcripts hold %s assistant messages%s.</p>'
            % (fb.get("runs", 0), ob.get("runs", 0), fb.get("subagent_runs", 0),
               round(100 * fb.get("subagent_runs", 0) / max(fb.get("runs", 1), 1)), round(100 * dict(b["fable_invokers"]).get("Claude opus-5-5 session, via Agent tool", 0) / max(fb.get("subagent_runs", 1), 1)), format(tf["messages"], ","), real_txt, ", none from Fable" if not real.get("fable") else ""))
    cov = ('<p id="traffic-coverage"><small>Coverage: Claude transcripts %s..%s (Fable seen %s..%s); bus messages %s..%s; MCP calls %s..%s. Assistant messages: Fable %s, Opus 5.5 %s. '
           'Not counted: Fable as advisor (no separate transcript), laptop Claude. A bus name containing “fable” does not mean the session ran Fable.</small></p>'
           % (cv["transcripts"]["first"], cv["transcripts"]["last"], cv["transcripts"]["fable_first"], cv["transcripts"]["fable_last"], cv["bus"]["first"], cv["bus"]["last"], cv["mcp"]["first"], cv["mcp"]["last"], format(fb.get("messages", 0), ","), format(ob.get("messages", 0), ",")))
    grid = '<div class="tr-grid">%s%s%s%s</div>' % (
        donut("tr-sent", "Bus messages sent, by sender", b["bus"]["sent"], "%s messages in the window." % format(cv["bus"]["messages"], ",")),
        donut("tr-received", "Bus messages received, by recipient", b["bus"]["received"], "Same messages, by recipient group."),
        donut("tr-fable-who", "Fable runs, by who started them", inv, "Parent = the Claude session that spawned the run, by its main model."),
        donut("tr-fable-how", "Fable runs, by path", paths, "No Fable run traced to a bus post, MCP call or session-send. %d shell commands name Fable as the model." % b["other_paths"]["launch_commands_naming_fable"].get("claude", 0)))
    return ('<!-- section 10 snippet; built by scripts/token-usage/fable_callers.py; replace the existing <section id=\"mcp\"> element with this one -->\n'
            + css + '<section class="chart-card" id="mcp">' + head + find + grid + cov + '</section>')


def main():
    out = sys.argv[1]; merge = sys.argv[sys.argv.index("--merge") + 1] if "--merge" in sys.argv else None
    runs, main_model, nfiles = transcripts()
    by_model, inv, path, sub_type, weekly = summarize(runs, main_model)
    w0, w1 = window(runs)
    f0, f1 = window(runs, "fable")
    b, names = bus()
    named = named_fable_models(names)
    launch = launch_commands()
    ser = lambda c: [[k, v] for k, v in c.most_common()]
    block = dict(
        schema=1, built=datetime.date.today().isoformat(),
        coverage=dict(transcripts=dict(files=nfiles, first=w0, last=w1, fable_first=f0, fable_last=f1,
                                       gaps=["Advisor-tool calls are not separate transcripts, so Fable-as-advisor is not counted.",
                                             "Only transcripts mirrored from this host; laptop Claude not included.",
                                             "Parents of subagents are matched by file layout; unmatched parents are shown as such."]),
                      bus=dict(first=b["range"][0], last=b["range"][1], messages=b["messages"]),
                      mcp=dict(first=b["mcp_range"][0], last=b["mcp_range"][1])),
        invocations_by_model={k: v for k, v in by_model.items()},
        fable_invokers=ser(inv), fable_paths=ser(path), fable_subagent_types=ser(sub_type),
        weekly_runs=[[w] + [weekly[w].get(k, 0) for k in ("fable", "opus-5-5", "sonnet-5-5")] for w in sorted(weekly)],
        bus=dict(sent=ser(b["sent"]), received=ser(b["received"])),
        bus_to_fable_named=dict(messages=b["to_fable_named"], recipients=b["to_fable_named_recipients"], by_sender=ser(b["to_fable_named_by_sender"]),
                                first=b["to_fable_named_range"][0], last=b["to_fable_named_range"][1],
                                real_model_of_those_sessions_messages=ser(named)),
        kepler=dict(sent_to=ser(b["kepler_sent_to"]), received_from=ser(b["kepler_received_from"]),
                    messages_to_fable_named=b["kepler_to_fable_named"]),
        other_paths=dict(bus_posts_naming_fable_model=b["summaries_naming_fable_model"], mcp_coordination_post_calls=b["mcp_coordination_post_calls"],
                         launch_commands_naming_fable=dict(launch)),
    )
    json.dump(block, open(out, "w"), indent=1)
    if "--snippet" in sys.argv:
        m = json.load(open(merge))["mcp"]["summary"] if merge else json.load(open(sys.argv[sys.argv.index("--mcp-data") + 1]))["mcp"]["summary"]
        open(sys.argv[sys.argv.index("--snippet") + 1], "w").write(snippet(block, m))
    if merge:
        d = json.load(open(merge)); d["traffic"] = block
        open(merge, "w").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    print("fable runs", by_model.get("fable", {}).get("runs"), "opus-5-5 runs", by_model.get("opus-5-5", {}).get("runs"), "->", out)


if __name__ == "__main__":
    main()
