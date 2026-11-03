#!/usr/bin/env python3 -I
"""Build case studies from local benchmark results and handoff data."""
import csv, html, json, os, sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from statistics import mean, median

H = Path(sys.argv[1]) if len(sys.argv) == 2 else sys.exit('usage: case_studies.py HANDOFF_DIR')
SRC = Path(os.environ.get('TOKEN_USAGE_SRC', '~/claude-usage-audit')).expanduser()
BENCH = Path(os.environ.get('DISPATCHBENCH', '~/workspace/dispatchbench/results')).expanduser()
PROJECTS = Path(os.environ.get('CLAUDE_PROJECTS', '~/.claude/projects')).expanduser()
OUT = Path(__file__).resolve().parents[2]/'research/token-usage'


def rows(name):
    with (BENCH/name).open() as f: return [json.loads(line) for line in f if line.strip()]


def select(data, config, **filters):
    return [r for r in data if r['config'] == config and all(r.get(k) == v for k, v in filters.items())]


def stats(data):
    return dict(n=len(data), passed=sum(r['passed'] for r in data), median_wall_s=round(median(r['wall_s'] for r in data), 2))


def check(label, value, expected):
    if value != expected: raise ValueError(f'{label}: expected {expected}, got {value}')


def study(id, title, story, setup, happened, number, lesson, sources, caveat, numbers):
    return dict(id=id, title=title, story=story, setup=setup, happened=happened, number=number, lesson=lesson, sources=sources, caveat=caveat, numbers=numbers)


def main():
    through = (H/'data_through.txt').read_text().strip(); day = date.fromisoformat(through[:10])
    copies = list(SRC.glob('dashboard-v5-*/case09_copy.md'))
    if not copies: raise FileNotFoundError('no dashboard-v5-*/case09_copy.md in TOKEN_USAGE_SRC')
    paras = max(copies, key=lambda p: p.stat().st_mtime).read_text().strip().split('\n\n')
    check('case09 paragraphs', len(paras), 6)
    studies = [study('pr218', 'A change to session instructions', paras[0], '', paras[1]+'\n\n'+paras[2], paras[3], '', ['Codex rollout counters and Claude session transcripts for the change'], paras[4]+'\n\n'+paras[5], {})]
    if not PROJECTS.is_dir(): raise FileNotFoundError('CLAUDE_PROJECTS directory is missing')
    boundaries = defaultdict(list); seen = set()
    files = list(PROJECTS.glob('*/*.jsonl'))
    if not files: raise ValueError('no Claude project transcripts found')
    for path in files:
        with path.open() as f:
            for line in f:
                if 'compactMetadata' not in line: continue
                obj = json.loads(line); meta = obj.get('compactMetadata'); stamp = obj.get('timestamp')
                if not isinstance(meta, dict) or not stamp or stamp[:10] > day.isoformat(): continue
                if meta.get('preTokens') is None or meta.get('postTokens') is None: continue
                key = obj.get('uuid') or (str(path), stamp)
                if key in seen: continue
                seen.add(key); boundaries[path].append((stamp, meta))
    all_b = [b for group in boundaries.values() for b in group]
    if not all_b: raise ValueError('no compaction boundaries with token counts')
    busy = max(boundaries.values(), key=len); stamps = sorted(b[0] for b in busy)
    span = (datetime.fromisoformat(stamps[-1].replace('Z', '+00:00')) - datetime.fromisoformat(stamps[0].replace('Z', '+00:00'))).total_seconds()/3600
    pre = sum(b[1]['preTokens'] for b in all_b); post = sum(b[1]['postTokens'] for b in all_b)
    ratio = round(median(b[1]['postTokens']/b[1]['preTokens'] for b in all_b)*100, 2)
    n = dict(boundaries=len(all_b), triggers=dict(Counter(b[1].get('trigger', 'unknown') for b in all_b)), pre_tokens=pre, post_tokens=post, freed_tokens=pre-post, median_post_pre_pct=ratio, busiest_count=len(busy), first_timestamp=stamps[0], last_timestamp=stamps[-1], span_hours=round(span, 2), average_minutes_between=round(span*60/(len(busy)-1), 2) if len(busy)>1 else None)
    studies.append(study('compaction', 'Compaction cuts context to a tenth', f"Compaction cut a long session's carried text to a median {ratio:.0f}% of its size, and one session did it {len(busy)} times in {span:.0f} hours.", "When a session's text gets too long, Claude Code summarizes it into a shorter one (compaction) so the work can go on.", f"Across {len(all_b):,} compactions still on disk, {pre:,} tokens became {post:,}, freeing {pre-post:,}. The busiest session compacted {len(busy)} times, about once every {n['average_minutes_between']:.0f} minutes.", f"Median size after compaction: {ratio:.1f}% of before.", 'Compaction frees space but does not stop the text growing back.', ['Claude session transcripts (compaction records)'], 'Claude deletes transcripts after about 30 days, so this counts only transcripts still on disk and shrinks with each refresh unless retention is raised. Duplicate records from resumed sessions are removed.', n))
    standard = rows('2026-10-28-terra-function.jsonl'); fast = rows('2026-11-02-terra-priority-function.jsonl'); ladder = rows('2026-10-22b-function.jsonl'); noise = rows('2026-11-02-terra-noise-function.jsonl'); rescue = rows('appendix/luna_rescue.jsonl'); devin = rows('2026-10-28-devin-function.jsonl')
    a, b = select(standard, 'terra61-low'), select(fast, 'terra61-low-fast')
    x, y = stats(a), stats(b)
    for label, v in [('standard', x), ('priority', y)]: check(label+' counts', (v['n'], v['passed']), (60, 60))
    for v, data in [(x,a),(y,b)]: v['mean_out_tok'] = round(mean(r['out_tok'] for r in data))
    change = round((median(r['wall_s'] for r in b)/median(r['wall_s'] for r in a)-1)*100, 2)
    studies.append(study('priority', 'Priority tier: faster, same tokens', f"Moving Codex 6.1 terra (low effort) to the priority speed tier cut the median task time {abs(change):.0f}%, from {x['median_wall_s']:.2f} to {y['median_wall_s']:.2f} seconds.", 'DispatchBench is our benchmark of small coding problems. The same model and effort ran the 60-run main ladder once on the standard tier and once on the priority tier.', f"Both runs passed {x['passed']} of {x['n']}.", f"Mean output was {x['mean_out_tok']:,} tokens on standard and {y['mean_out_tok']:,} on priority.", 'The faster tier changed the time, not the work: same passes, same output size.', ['DispatchBench results/2026-10-28-terra-function.jsonl', 'DispatchBench results/2026-11-02-terra-priority-function.jsonl'], 'Small problems only. The priority tier is billed at a different rate, which this page does not cover. The two runs were made on different days.', dict(standard=x, priority=y, median_change_pct=change)))
    a, b = select(ladder, 'haiku-high', phase='exploratory'), select(ladder, 'sol61-high', phase='exploratory'); x, y = stats(a), stats(b)
    for label,v in [('haiku',x),('sol',y)]: check(label+' rows',v['n'],60)
    for v,data in [(x,a),(y,b)]:
        v['mean_in_tok'] = round(mean(r['in_tok'] for r in data)); v['mean_out_tok'] = round(mean(r['out_tok'] for r in data))
    ir = round(mean(r['in_tok'] for r in b)/mean(r['in_tok'] for r in a),2); oratio = round(mean(r['out_tok'] for r in a)/mean(r['out_tok'] for r in b),2)
    studies.append(study('haiku', 'Same passes, different token mix', f"Claude Haiku and Codex 6.1 sol, both at high effort, passed all {x['n']} problems; sol read {ir:.1f}x more input tokens per call.", 'Two models ran the same 60 DispatchBench problems.', f"Haiku took a median {x['median_wall_s']:.2f} seconds per problem, sol {y['median_wall_s']:.2f}. Per call, Haiku read {x['mean_in_tok']:,} input tokens and wrote {x['mean_out_tok']:,}; sol read {y['mean_in_tok']:,} and wrote {y['mean_out_tok']:,}.", f"Haiku wrote {oratio:.1f}x as many output tokens; sol read {ir:.1f}x as many input tokens.", 'Output size alone does not show token use: the model that wrote more also read far less.', ['DispatchBench results/2026-10-22b-function.jsonl'], 'The Haiku high-effort arm was exploratory, not pre-registered. Different vendors count tokens differently.', dict(haiku=x, sol=y, input_ratio=ir, output_ratio=oratio)))
    problems = {r['problem'] for r in rescue}; check('repair problems', len(problems),7)
    base = [r for r in select(ladder,'luna-low',phase='main') if r['problem'] in problems]
    x = stats(base); full = stats(select(rescue,'luna-low+haiku-low-repair')); conditional = stats(select(rescue,'luna-low+haiku-on-fail'))
    for label,v,expected in [('baseline',x,(35,21)),('review every answer',full,(35,35)),('on failure',conditional,(35,34))]: check(label+' counts',(v['n'],v['passed']),expected)
    low = stats(select(ladder,'luna-low',phase='main')); sol = stats(select(ladder,'sol61-medium',phase='main'))
    check('main luna counts',(low['n'],low['passed']),(60,46)); check('main sol counts',(sol['n'],sol['passed']),(60,58))
    studies.append(study('repair','A cheap model plus a targeted repair',f"A small Codex model (luna, low effort) passed {x['passed']} of {x['n']} hard runs alone and {conditional['passed']} of {conditional['n']} when Claude Haiku repaired only the answers that failed the problem's own examples.", 'Seven harder problems, five runs each. Luna is fast but misses some; Haiku (low effort) was added as the repairer.', f"Haiku reviewing every answer passed {full['passed']} of {full['n']} but the median time rose from {x['median_wall_s']:.1f} to {full['median_wall_s']:.1f} seconds. Repairing only on failure passed {conditional['passed']} of {conditional['n']} at a median {conditional['median_wall_s']:.1f} seconds.", f"Passed {x['passed']} of {x['n']} alone, {conditional['passed']} of {conditional['n']} with repair on failure; median time {x['median_wall_s']:.1f} to {conditional['median_wall_s']:.1f} seconds.", 'Run the cheap check first and call the second model only when the check fails.', ['DispatchBench results/2026-10-22b-function.jsonl','DispatchBench results/appendix/luna_rescue.jsonl'], 'The seven problems are the ones luna missed most, so the gap is larger than on the whole ladder (luna passed 46 of 60 there). The median barely moves because the repair ran only on the failing runs.', dict(baseline=x, review_all=full, on_fail=conditional, main_luna=low, main_sol=sol)))
    groups = {}
    for label,data in [('initial',standard),('additional',noise)]:
        for config in ('terra61-low','terra61-high'):
            subset = [r for r in select(data,config) if r['problem'] < 'p13']; groups[label+'_'+config] = stats(subset)
            expected = (60,60 if config.endswith('low') else 58) if label == 'initial' else (120,119)
            check(label+' '+config+' counts',(len(subset),sum(r['passed'] for r in subset)),expected)
    misses = [dict(config=r['config'],problem=r['problem'],repeat=r['repeat']) for data in (standard,noise) for r in data if r['config'] in ('terra61-low','terra61-high') and r['problem'] < 'p13' and not r['passed']]
    distinct = len({r['problem'] for r in misses}); check('noise misses', (len(misses),distinct), (4,1))
    pooled = {c:dict(n=sum(groups[k]['n'] for k in groups if k.endswith(c)),passed=sum(groups[k]['passed'] for k in groups if k.endswith(c))) for c in ('terra61-low','terra61-high')}
    studies.append(study('noise','A gap that was noise',f"Two effort levels of Codex 6.1 terra differed by 2 of 60 problems at first; after 15 repeats the gap was {pooled['terra61-low']['n']-pooled['terra61-high']['n']+pooled['terra61-low']['passed']-pooled['terra61-high']['passed']} of {pooled['terra61-low']['n']}, and all {len(misses)} misses were on {distinct} problem.", 'We compared two effort levels of Codex 6.1 terra on 12 problems: 5 repeats first, then 10 more.', f"In the first 5 repeats low passed {groups['initial_terra61-low']['passed']} of {groups['initial_terra61-low']['n']} and high {groups['initial_terra61-high']['passed']}. In the next 10 repeats both passed {groups['additional_terra61-low']['passed']} of {groups['additional_terra61-low']['n']}.", f"Pooled over 15 repeats: low {pooled['terra61-low']['passed']} of {pooled['terra61-low']['n']}, high {pooled['terra61-high']['passed']} of {pooled['terra61-high']['n']}; {len(misses)} misses on {distinct} problem.", 'One small run can overstate a gap. Repeat it before choosing on a miss.', ['DispatchBench results/2026-10-28-terra-function.jsonl','DispatchBench results/2026-11-02-terra-noise-function.jsonl'], "The benchmark report's confidence interval for the pooled difference includes zero.", dict(groups=groups, pooled=pooled, misses=misses, distinct_miss_problems=distinct)))
    x = stats(devin); y = stats(select(ladder,'haiku-low',phase='main')); check('devin counts',(x['n'],x['passed']),(12,6)); check('devin configuration',{r['config'] for r in devin},{'devin16slow-default'}); check('haiku low counts',(y['n'],y['passed']),(60,57))
    studies.append(study('devin','A delegate that missed half',f"Devin's delegate tool passed {x['passed']} of {x['n']} benchmark problems; Claude Haiku (low effort) passed {y['passed']} of {y['n']}.", 'Devin is one of the tools the host can hand coding tasks to. We ran it once through the 12-problem ladder with its stock setup.', f"Devin took a median {x['median_wall_s']:.2f} seconds and Haiku {y['median_wall_s']:.2f}.", f"{100*x['passed']/x['n']:.0f}% passed against {100*y['passed']/y['n']:.0f}%.", 'The time was the same; the passes were not. Check a lane before routing work to it.', ['DispatchBench results/2026-10-28-devin-function.jsonl','DispatchBench results/2026-10-22b-function.jsonl'], 'Only 12 Devin runs, one per problem, exploratory and not pre-registered.', dict(devin=x,haiku=y)))
    weeks = defaultdict(Counter)
    with (H/'claude_model_weekly.csv').open() as f:
        for r in csv.DictReader(f):
            if date.fromisoformat(r['week_start']) + timedelta(days=7) <= day: weeks[r['week_start']][r['family'].lower()] += int(r['raw_tokens'])
    keys = sorted(weeks)[-4:]; check('complete weeks available',len(keys),4)
    shares = [dict(week_start=k,haiku_pct=round(100*weeks[k]['haiku']/sum(weeks[k].values()),2)) for k in keys]
    old,new = weeks[keys[-2]]['opus'],weeks[keys[-1]]['opus']; delta = new-old
    facts = [dict(id='haiku_share',text="Haiku's share of Claude raw tokens by week: "+', '.join(f"{v['haiku_pct']:.1f}% ({v['week_start']})" for v in shares)+f'. Opus raw tokens fell {abs(delta)/old*100:.0f}% between the last two complete weeks ({old:,} to {new:,}). Which model a session used is not logged, so the cause is not established.',numbers=dict(weeks=shares,opus_previous=old,opus_latest=new,opus_change=delta),sources=['Handoff claude_model_weekly.csv'])]
    last = json.loads((H/'last7.json').read_text()); cr = round(last['claude']['cache_read']/last['claude']['output'],1); xr = round(last['codex']['cached_input']/last['codex']['output'],1)
    facts.append(dict(id='ratio',text=f"In {last['window']}, Claude read {cr:.0f} cached tokens for each token it wrote; Codex read {xr:.0f}.",numbers=dict(claude_ratio=cr,codex_ratio=xr,window=last['window']),sources=['Handoff last7.json']))
    sources = list(dict.fromkeys(s for item in studies+facts for s in item['sources']))
    doc = dict(schema='token-usage-case-studies-v1',data_through=through,studies=studies,facts=facts,sources=sources)
    OUT.mkdir(parents=True,exist_ok=True); (OUT/'case_studies.json').write_text(json.dumps(doc,indent=2)+'\n')
    doc = json.loads((OUT/'case_studies.json').read_text()); esc = html.escape
    parts = ['<section class="chart-card" id="case-study">','<h2>Case studies</h2>']
    for s in doc['studies']:
        parts += ['<article class="case">',f"<h3>{esc(s['title'])}</h3>",f"<p class=\"story\">{esc(s['story'])}</p>"]
        parts += [f'<p>{esc(s[k])}</p>' for k in ('setup','happened','number','lesson') if s[k]]
        parts += ['<details><summary>Sources and caveat</summary>',f"<p>{esc(s['caveat'])}</p>",'<ul>'] + [f'<li>{esc(source)}</li>' for source in s['sources']] + ['</ul></details>','</article>']
    parts += ['<h3>Quick facts</h3>','<ul>'] + [f"<li>{esc(f['text'])}</li>" for f in doc['facts']] + ['</ul>','</section>']
    (OUT/'case_studies.html').write_text('\n'.join(parts)+'\n')
    for s in doc['studies']: print(s['id']+': '+s['story'])
    for f in doc['facts']: print(f['id']+': '+f['text'])


try: main()
except (OSError, ValueError, KeyError, ZeroDivisionError, json.JSONDecodeError) as e: sys.exit(f'case_studies: {e}')
