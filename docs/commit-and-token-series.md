# Why the commit and line series were spiky, and the fix

Measured 3 November 2026 on the host sweep (window 2026-05-24 to 2026-11-03, 164 UTC days). Numbers come from `scripts/token-usage/commit_sweep.py` and `build_daily.py`; the old figures from the previous sweep files.

## What was wrong

The commit series on the page was 16,415 commits. The table now says 8,285 landed commits (13,234 on any branch). The lines series was dominated by a handful of commits.

| Cause | Effect | Fix |
|---|---|---|
| Multi-actor commits counted once per actor. A commit with both a Claude and a Codex trailer was a Claude commit and a Codex commit, and `total` summed them. | +3,074 commits (13,341 real commits shown as 16,415) | One column per actor combination (`claude_codex`), total counted once |
| `git log --all` reads refs nobody works on: `refs/archive/codex-worktree-maintenance/*` and `refs/codex/snapshots` (admin snapshots), `refs/rewritten/*` (pre-rewrite backups) | 47 "Recovery of missing worktree administrative state" commits on 24 Oct added 78.8M lines (71% of all lines added in the window) in six commits of 11 to 15M each. They also made 24 Oct the biggest line day by a factor of 19 | Sweep walks `--branches --remotes --tags` plus each worktree's HEAD |
| Per-worktree refs depend on which checkout you ask. `refs/rewritten/*` is visible from the main checkout, not from a linked worktree. | the monorepo: 2,859 commits from the main checkout, 2,172 from a worktree (687 apart; 646 refs) | Same ref set from any checkout (tested) |
| Branch commits and the squash commit that lands them are both commits | 3,781 non-merge commits are not on main; 747 of them repeat a change that did land | `commits_landed` counts non-merge commits on main/master only; `commits_all_refs` is kept for reconciling |
| Rebase, cherry-pick and amend give the same change a new hash | 94 more copies among landed commits | Copies with the same project, author, UTC day, subject, file count and lines added/removed count once (a fingerprint, not a patch comparison: two different changes with the same message, size and day would merge) |
| Merge commits | 1,074 in the window | Excluded from landed, counted in `commits_merge` |
| Bulk imports, lockfiles, data dumps | Of 31.6M lines added, 28.0M (88%) are "noise" (data files, lockfiles, vendored, generated); 63 commits touching more than 100 files add 6.2M lines but 0.3M of code | Code basis = `src` + `test` lines, bulk commits (over 100 files) left out. All-lines kept as `all_added_raw` |
| Three sweeps (commit, scope, lines) read the repos at different times | 27,671 / 28,776 / 28,780 commit counts for the "same" history | One sweep, one file |

`commit_sweep.py` stops on a repo git cannot read (it skips it with a warning, or exits 1 with `--strict`); the old sweeps returned nothing for it without saying so. One scratch repo with a bad ref is skipped today.

After the fix the daily series is still uneven, which is real. Landed commits per day: median 40, top days 233 (9 Oct), 212 (28 Sep), 211 (12 Sep). Coefficient of variation 0.86 landed, 0.87 all-branch: the unevenness is the workflow, not an artefact. Code lines touched per day: median 6.6k, top 127k (22 Oct) and 120k (21 Oct), both research-note commits in the private research repo plus one DispatchBench report. Raw all-lines added had a coefficient of variation of 3.0; the code basis has 1.5.

## Commits against tokens

Over the 163 complete days, daily correlation with total tokens: landed commits 0.53, all-branch commits 0.49, code lines touched 0.42, raw lines added 0.09. On the 47 days where Claude tokens are measured the landed-commit correlation is 0.69. The raw lines series has almost no relation to token use (0.09, with the maintenance job already removed) because data dumps and lockfiles drown the code.

Where tokens and commits still do not line up, by cause:

- Claude has no transcripts before 7 Sep 2026 (79 days are Codex-only, 16 have a recovered split, 12 have no token row at all). Do not compare commits with tokens before 7 Sep as if both sides were complete.
- Codex had a very large token spike in July and August (the page has an "Exclude Jul-Aug Codex spike" range) that is not matched by commits.
- Most tokens are cache reads (about 98%). They move with how long a session re-reads its context, not with output.
- The last day is partial for both sides.
- Commit day = author date in UTC; token day = UTC timestamp of the record. They agree. A local (+02:00) day would split a few late-evening commits into the next day; we use UTC everywhere. The size of that shift was not measured.
- A commit is dated when it was authored. Work spread over hours lands at the end (squash, rebase) with the author date of each change, so a session does not equal a day of commits.

## The PR 67 jump (15,691 to 16,792, +1,101)

- the monorepo is +684 of it. The 3 November sweep ran `git log --all` from the main checkout, which sees 646 `refs/rewritten/*` refs (created 24 Oct 09:21) holding 687 commits dated Nov 2025 to Mar 2026. A linked worktree cannot see them.
- The other +417 is mostly new work between the 1 and 3 November sweeps (DispatchBench +154, chimericlabs-llc +97, portfolio +56, one new Claudefolio clone +34, claude-remote-session-skill +33).
- Not proven: why the 1 November sweep did not see the rewritten refs, since they existed from 24 Oct. The sweep keeps the first directory it finds for each repo, and the set of directories differed between runs (221, 222). The likely reading is that it opened a linked worktree. The old hash list was overwritten, so this cannot be replayed. With the new sweep the answer no longer depends on the directory.
- Neither number was the right one. Rewritten refs are not work (they are the same changes before a history rewrite) and the page also counted multi-actor commits twice. On the new rules the monorepo and the rest give 13,234 commits in the window, 8,285 landed.

## Consolidated daily table

`research/token-usage/daily.csv`: one row per UTC day from 2025-10-01 (the start of the commit history the page quotes) to the data_through day, 399 rows. `monthly.csv` has one row per month, each the exact sum of its daily rows (`days` shows partial months). `data.json` must carry the same rows under `"daily"`, and the page's commit, line and token series must read from it.

| Column | Meaning |
|---|---|
| `date` | UTC day. Author date for commits, record timestamp for tokens |
| `day_status` | `complete`, or `partial` (the last row only) |
| `commits_landed` | non-merge commits on main/master, copies collapsed, third-party authors out |
| `commits_landed_{claude,codex,claude_codex,other,human}` | the same, by actor from trailers or author name; the five add to `commits_landed` |
| `commits_all_refs` | every non-merge and merge commit on any branch, remote or tag |
| `commits_merge` | merge commits (inside `commits_all_refs`) |
| `code_added`, `code_removed`, `code_touched` | landed commits, `src` + `test` files only, bulk commits (over 100 files) left out. touched = added + removed; this is churn, not size |
| `all_added_raw`, `all_removed_raw` | every category, every commit on any branch (not collapsed). Merge commits carry 0 lines. Reference only |
| `tokens_claude`, `tokens_codex`, `tokens_other`, `tokens_total` | raw tokens incl. cache. Codex uses the corrected total |
| `claude_token_status`, `codex_token_status` | `measured`, `recovered` (Claude: pruned days, audit totals only), `unmeasured` (no row; token columns are 0, not "zero use"), `before_start` (before 2026-05-24, when token records begin; 0 means no data) |

Line categories (`commit_sweep.py`): noise = `node_modules vendor third_party dist build out .next coverage __snapshots__ .terraform broadcast artifacts cache deployments generated .venv site-packages` directories, `*.lock *.min.js *.min.css *.map *.snap *.tfstate *.pb.go *_pb2.py *.csv *.tsv *.jsonl *.ndjson *.parquet *.svg *.ipynb *.log *.sqlite *.db *.wasm *.abi`, the usual lockfiles, and any `.json` that is not a tool config. Then test, doc, src (code extensions), cfg, other. Binary files are 0 lines. Renames are not followed.

`scripts/token-usage/validate_daily.py` fails when: dates are not contiguous from 2025-10-01 to the data_through day, a definition does not add up, `data.json["daily"]` is missing or differs from the table, the page's commit series covers different days, or a token row disagrees with the table, or `monthly.csv` is not the sum of the daily rows. Token rows covering fewer days than the table is a warning (gaps are real and flagged `unmeasured`). `--legacy` demotes the "not built from the table" failure while the page is being switched.

## Why the page showed three totals, and May 715 against 568

| Figure | What it is | Verdict |
|---|---|---|
| `commit_log.total` 19,979 | monthly commit_log from 2025-10: an older sweep (scope and dedupe not the daily rule) up to May, then the daily per-actor sums from June | retire |
| `project_total` 15,691 | 1 Nov sweep, all refs, summed by project; includes the 684 backup-ref commits | retire |
| `commit_totals` sum 16,415 | the daily series from 2026-05-24, summed per actor, so a Claude+Codex commit counts twice (+3,074) | retire |

From June on `commit_log.months` and the daily `commits` agree (June 1,999) because they are the same per-actor sums. Before that they are different sweeps: May is 715 in `commit_log` (a month that starts 1 May) and 568 in the daily series (starts 24 May), so 147 are May 1 to 23 and not a disagreement of the definition. On the new rules all non-third-party commits on any ref in May are 703 and landed ones are 457; October 2025 is 378 on both sweeps.

"Other: 242" in the week of 2026-05-25 is not an import. It is Devin: 212 commits (plus 5 Devin+other-agent) in one repo on 28 to 30 May (64 on the 28th, 94 on the 29th plus 33 on branches), and 20 commits from another agent in a UI repo on the 30th and 31st. That is 237 in the new sweep; the old one gave 242. May's whole "other" month count is this one burst.

**Headline: landed commits** (non-merge, on main, copies collapsed): 9,180 since 2025-10-01 and 8,285 since 2026-05-24. The wider figure, every commit on any branch, third-party out, is 16,011 (2025-10-01 on) and 13,234 (2026-05-24 on). Pick one and label it; do not add actors.

## What this says about the workflow

- Agents commit often and small, and several lanes share a repo: 33% of landed commits fall on Saturday and Sunday. Daily commit counts measure commit granularity and fan-out as much as output. Use landed code lines and the token series together.
- Work is committed on branches and then squashed or rebased: 3,781 of 13,234 commits (29%) never reach main, and 747 repeat a change that did. Count what lands.
- Large dumps go straight into repos: a 2.4M-line research record, a 2.1M-line `artifacts crap` commit, 6.2M lines across 63 bulk commits. They belong in object storage or `.gitignore`, with a manifest committed instead.
- Maintenance jobs write into the history they are measuring. The worktree recovery job committed 80M lines of admin state. Give such jobs their own non-branch ref namespace (it worked: the new sweep skips it) and keep them out of counts.
- Rewriting history leaves backup refs. They double count unless the sweep excludes them.

## Things to do

1. Switch `build_v5.py` (outside this repo, owned by the usage page work) to read `daily.csv` and write `data.json["daily"]`; run `validate_daily.py` without `--legacy` as the last step of `refresh.sh`.
2. Point `commits_by_project.py` and the building page at `commits_unified.csv` so the by-project totals use the same commit set. Until then the building page total (16,792) follows the old rules.
3. Retire `commit_sweep.py`, `commit_scope.py` and `loc_sweep.py` in the generator checkout.
4. Add a Claude transcript backup before the 30-day cleanup, so the pre-7-Sep gap does not widen.
5. Measure the local-time day shift if a local-day view is ever wanted.

## Things to fix

- The `loc` weekly and daily series on the page still come from `loc_sweep.py` (`--all`, on_main flag) and differ from the table.
- Repos with no main/master ref have no landed commits (two private repos, 365 commits in the old sweep). They show only in `commits_all_refs`.
- The old sweep recorded the the monorepo main checkout only; record the directory used per repo in the sweep log.
