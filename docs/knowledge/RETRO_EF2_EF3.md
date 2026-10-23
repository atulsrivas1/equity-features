# Retrospective: EF2 and EF3 (draft, October 23, 2026)

Status: EF3 close update added as section 9 (EF3 built, qualification run and evidence merged; owner demo and acceptance pending). EF2 had no retrospective when it merged; this covers it from its evidence doc and from the EF3 record only, with no per-agent EF2 numbers (the EF2 coordinator session is not available). Nothing here is an acceptance claim.

## 1. Quality

Measured on EF3 (D, E, F; library, I/O, workers; plus the shared amendment). Every PR got a fresh independent reviewer with its own harness.

| Unit | Author | Reviewer verdict | What review found |
|---|---|---|---|
| D library #692 | Sonnet | approved earlier | documented reconstruction-mode exception |
| D I/O #36 | Haiku | approve with fixes | return types, doc wording; later a stale sha256 in the source-evolution file (found by the D worker author, not by review) |
| D workers #80 | Haiku | approve | spawn mode and grid registry limits undocumented; refusal fixtures half unrun |
| E library #694 | Sonnet | approve | six contract nits (result-wide evidence limit, `ordinary` boundary, invented coverage names, unvalidated `known_at` on facts) |
| E I/O #37 | Haiku | approve with fixes | real defect: instrument id "X" hardcoded in builders; doc cited the wrong checkout |
| F library #695 | Sonnet | approve | one contract ambiguity needing a ruling (roster rows of other groups) |
| F I/O #38 | Haiku | BLOCK | declared sha256 stale (CRLF working copy hashed differently from the LF blob); doc overstated "every builder takes ids explicitly"; silent sort hides the shared order check |
| F workers #81 | Haiku | approve with fixes | readable view mislabelled per-output runs as prefix runs; `required_roles` leaked a raw library error |
| Amendment #696 | Sonnet | approve with fixes | "accepted" wording; manifest comparison skipped by the author |
| E workers | Haiku then Sonnet | open | Haiku run: 98 of 124 passed, 26 failed (all cohort cases, H25, R16), cause undiagnosed |

Findings:
- Every author claim about fixture values held up under an independent harness (D 62, E 124, F 99 results; 48/48 and 62/62 refusals at the I/O layer). The defects were in dimensions the author's harness never varied: non-default entity ids, refusal coverage at the worker layer, display labels, error translation, hashes.
- The author harness used the same inputs as the author's own builder. A reviewer that re-derives inputs from the contract JSON and varies ids finds more than one that re-runs the author's fixtures.
- Two coordinator errors: I reported a source-evolution sha as matching when the declared value was stale after a later edit; and I let a Haiku agent's "setup done, shall I continue?" stop go unnoticed for one cycle. Both were caught, none shipped.
- Refusal coverage is thin above the library. D workers: 24 of 48 driven (by the reviewer). F workers: 59 of 62 driven (by the reviewer). Worker-layer refusal codes collapse to `INVALID_COMMAND`.
- Open contract items carried to the owner: reconstruction-mode evidence exception, roster/`known_at` rulings (R4, R5), two manifest entries with no header, 36 headers with no manifest entry.

## 2. Token usage

Source: the per-agent usage lines reported on completion (cumulative context tokens, tool uses, wall time). They overstate billed tokens (a resumed agent re-counts its context) and say nothing about price, so treat them as a relative measure.

| Unit | Build | Review | Fix/merge round | Total (k) |
|---|---|---|---|---|
| D I/O | 247 (56 tools, 8 min) | 144 (29 tools, 5 min) | +3 | 394 |
| D workers | 270 (81 tools, 26 min) | 113 (23 tools, 12 min) | +7 | 390 |
| E library | 358 (86 tools, 19 min) | 259 (60 tools, 11 min) | +1 | 618 |
| E I/O | 319 (65 tools, 13 min) | 164 (38 tools, 7 min) | +21 | 504 |
| F library | 372 (72 tools, 21 min) | 219 (37 tools, 9 min) | +1 | 592 |
| F I/O | 292 (60 tools, 10 min) | 137 (26 tools, 5 min) | +7 | 436 |
| F workers | 215 (76 tools, 44 min) | 195 (58 tools, 24 min) | +8 | 418 |
| Amendment | 123 (25 tools, 3 min) | 86 (9 tools, 1 min) | +2 | 211 |
| E workers (Haiku, failed) | 276 (67 tools, 42 min) | not reached | | 276 |

About 3.84M subagent tokens for EF3 including the failed Haiku E workers run (276k) and excluding the Sonnet takeover still running. Coordinator tokens are not measurable here (the session counter reset); the coordinator carried a short handoff instead of a 550-turn history, which was the point of the restart.

Observations:
- Haiku was not much cheaper in tokens than Sonnet on the same kind of layer (250-320k vs 360k). Any saving is price per token, not volume, and was not measured.
- Review cost 42-91% of build cost (median about 60%). It found the defects above, so it earned its place, but reviewers re-derived data the build already had. Giving reviewers the author's input derivation to audit (not repeat) may cut cost without losing the independent recompute.
- Largest avoidable waste in the coordinator thread: the E workers agent ended its turn on every progress poll, which produced about 90 "run is at N of 124" notifications, each re-reading the context. Cost scales with notification count, not with work done.
- Idle round trips: two agents stopped to ask "continue?" after finishing setup.

## 3. Worker performance (agents)

- Parallelism worked: three layers ran at once (E I/O with F library; D workers with E library; F workers with the amendment), with predicted merge hotspots communicated up front. Merge conflicts: none so far, the E workers branch still has to rebase.
- Sequential constraints were real: F library waited for E library (shared files), each workers layer waited for its I/O merge.
- Haiku by layer: I/O 3 of 3 acceptable after one fix round; workers 2 of 3 acceptable after fixes and 1 failed (E workers: 26 failures, stopped without diagnosing). The skill's rule (Haiku first, Sonnet after one miss) held; the E workers handoff to Sonnet is the first use.
- Longest agent wall times were the workers layers (26-44 min), dominated by the demo and fixture runs, not by writing code.
- Reviewers returned in 1-24 min. The long ones (F workers 24 min, D workers 12 min) were again fixture runs.

## 4. Code performance

Author-observed timings on one machine, copied from the implementation docs and PR reports; the coordinator did not reproduce them and no performance claim follows.

- Relative statistics (exact rationals), 4096-return window: about 0.2 s with 4-digit closes, 2.5 s with 10-digit, 10.5 s with 16-digit closes. Cost grows with close magnitude.
- Daily log volatility and realized variance: about 0.7 s on 4096 slots.
- Robust history/pace/mean (E): a 4096-session window in about 0.25 s (reviewer-measured).
- Breadth declared (F), 4096 members, all 16 outputs: 0.7-0.8 s (reviewer and author). Adaptive volume, 4096 random rationals: 1.7 s (reviewer); author reported 2 s typical and 13 s for a float-equal near-tie stream, which the reviewer did not reproduce. A Fraction-based baseline took about 29 s for 4096 rows, so the library keeps integer pairs.
- Worker layer: roughly 30-60 s per fixture case end to end (estimated from agent wall times and monitor progress, not measured per case) (build task, run, publish to DuckDB, replay, reopen, HTML view). A 124-case run takes about 2 hours sequentially. Time was not profiled; the likely cost is per-case process, database and view setup rather than the maths (library times above are sub-second). Memory is O(window), batch only; the contract's O(1) incremental state is not delivered.

## 5. Other

- Review of the review: reviewer scratch harnesses are not kept (scratch folders, no tests by policy), so a later reviewer cannot re-run the earlier independent check. Keeping reviewer harnesses in the shared notes folder would make re-verification cheap.
- Shared checkouts drifted under agents (core moved by another process, io left detached). Isolated worktrees prevented damage; leftover `wt-*` worktrees pile up and need a cleanup pass.
- Line endings: a CRLF working copy produced a different sha256 than the committed LF blob and broke the source-evolution check, twice. Hash the committed blob (`git show HEAD:path | sha256sum`).
- Contract fixtures that cannot be built literally (P18) and refusal fixtures stored without inputs (F) force each layer to invent constructions; the contract should ship refusal inputs.
- Not done yet for EF2 and EF3: Linux qualification (owner action), installed Windows qualification of EF3, browser demo, real-source demo, owner demo, release acceptance.

## 6. What we change (also written into the release-coordinator skill)

1. Layer brief checklist: never hardcode entity/instrument/role ids (parameters on every builder); vary ids in the harness; run refusal fixtures through each layer or state which were not.
2. Hash gate: compute declared hashes from the committed blob, enforce LF, rerun the extraction check after the last edit and record the commit it ran against.
3. Agents must not end the turn on progress polls and must not stop to ask "continue?" when the brief says to finish: run long batches in parallel, wait once, report once. Briefs say so.
4. Reviewers audit the author's input derivation and then re-derive from the contract with varied ids; they keep their harness in the shared notes folder.
5. Haiku gets one correction round on a layer; a second miss goes to Sonnet. Workers layers default to Sonnet when the layer needs new runner registration plus cohort/multi-run cases.
6. Refusal fixtures: contracts must carry inputs or an explicit "construct" recipe; worker docs state build-time vs compute-time refusal.
7. Profile one worker case before running a 100+ case demo; batch the demo in parallel.
8. Retrospective is a release gate: EF2 is written here, EF3 is finalized at close, each as a docs PR with an independent reviewer.
9. Reduce `LESSONS.md` reading cost: new lessons go into the skill checklist or a short list at the top of the retrospective, not only into the long log.

Owner items: confirm the changes above (decided, pending owner review), clean up leftover worktrees, decide whether reviewer harnesses should be committed under `tools/` despite the no-tests policy.

## 7. Standing rule (owner, October 23, 2026)

After every retrospective we improve the working agreement and the way we work. Done here: items 1-5, 7 and 8 of section 6 are written into the release-coordinator skill (layer brief checklist, and step 8 for item 8); items 6 and 9 are added to the checklist below. A new step 8 makes the improvement step part of every release close. Next retrospective (EF3 close) must report, per item 1-9, whether it was applied and whether it helped (token use, defects found at review, rounds per PR, idle notifications), and propose the next set of changes.

## 8. Token efficiency: verdict and solutions (owner request, October 23, 2026)

Verdict: partly efficient. Verification quality was high and every defect was caught before release, but the same facts were read and derived several times, and the coordinator thread paid for avoidable notifications. Waste, ranked by size (evidence in sections 2 and 3):

| # | Problem | Evidence | Solution (decided, pending owner review) | Status |
|---|---|---|---|---|
| 1 | Every agent and reviewer re-read the 6500-line frozen contract JSONs and the long implementation docs | each unit read the contract; review cost 42-91% of build | contract layer pack: `tools/contract_pack.py` makes a compact pack (ids, roles, entity ids, fixture lists, acceptance rule kinds) and `--fixture ID` prints one fixture; briefs point at the pack, not the JSON | tool PR in preparation |
| 2 | About 90 "run is at N of 124" notifications from one agent | E workers agent, each re-read the coordinator context | `tools/run_batch.py`: parallel batch, one final summary, heartbeat file for peeking; briefs forbid ending the turn on a poll | tool PR in preparation |
| 3 | Idle "shall I continue?" stops | E and F workers (Haiku) | brief says finish end to end; coordinator answers once with "proceed" | in skill checklist |
| 4 | Failed Haiku workers run (276k) before Sonnet took over | E workers | Sonnet by default for workers layers with new runner registration or multi-run cases; Haiku for I/O layers (3 of 3 acceptable); Haiku workers layers passed on D and F after fixes and failed on E, so use Sonnet when the layer adds runner registration or multi-run cases; one correction round | in skill |
| 5 | Reviewers re-ran the author's input derivation and every fixture, 24 min on workers layers | F workers reviewer | reviewer budget: audit author derivation, independent recompute on a fixed sample (at least 25 results, all refusals, all prefix) plus full run only for pure-library layers; stated in the brief | in skill |
| 6 | Worker cases take about 30-60 s each (estimate), unprofiled | 124-case run took about 2 h | profile one case first, parallel batches via `run_batch.py`; fix the dominant cost before the full run | to do at EF4 |
| 7 | No token ledger; cost was reconstructed from completion lines | section 2 | `docs/knowledge/TOKEN_LEDGER.md`: one row per unit (build, review, fix tokens, tool uses, minutes, model, verdict); coordinator appends in the release's docs batch; EF4 sets a per-unit budget from it | created |
| 8 | Templates re-written by an LLM per contract (I/O and workers differ little between releases) | D, E, F adapters share structure | investigate generating adapter and worker skeletons from the layer pack; decide at EF4 start with a measured trial on one layer | open |
| 9 | Coordinator spot-runs duplicated reviewer runs | this session | coordinator reads the diff and the reviewer's report; spot-runs only when the reviewer could not run something | in skill |

Measures for the next retrospective: subagent tokens per unit (target: at least 20% below the EF3 median of about 429k per build-plus-review unit), notifications per agent (target: at most 3), review fix rounds per PR, defects found by review versus defects found after merge, wall minutes per worker layer.


## 9. EF3 close update (October 23, 2026)

Delivered: all three contracts in library, I/O and workers; shared amendment #696; installed Windows qualification run #700 (346 of 346 demos in each of 4 forms, hashes identical); evidence package #701; browser walkthrough of 24 runs, 0 failed. Not accepted; Linux, real-source demo, owner demo and acceptance are open.

Did the changes from sections 6-8 work? (applied, and evidence)

| # | Change | Applied | Effect seen |
|---|---|---|---|
| 1 | no hardcoded ids, vary ids, run refusals | yes, from F I/O on | F I/O reviewer found no id defect (E I/O had one); refusals driven: E workers 48 of 48, F workers 59 of 62 by the reviewer, D 24 of 48 |
| 2 | hash gate from committed blobs | partly | the F I/O stale-hash block happened before the rule; qualification explained CRLF vs LF differences and normalised them |
| 3 | no progress polls, no "continue?" stops | yes for the Sonnet E workers rework, the qualification, evidence and demo agents | notifications per agent 0-2 after the change, against about 90 before |
| 4 | Sonnet for workers layers with new registration | yes (E workers rework) | the 26 failures were example bugs, found and fixed in one pass; Sonnet total for E workers was about 145k after the failed Haiku 276k |
| 5 | reviewer sample budget | yes from E workers on | reviews 133k (E workers), 109k (qualification), 90k (evidence) against 113-259k for earlier layer reviews |
| 6 | contract pack and quiet batch | merged late (#699), used by later reviewers and the qualification | the tool review itself cost 201k (two rounds) and found the first pack dropped role text; token savings from the pack are not yet proven |
| 7 | token ledger | created, extended | works; still reconstructed by hand |

New findings at EF3 close:
- Per-case worker time: the reviewer measured about 10 s per case alone; the author's 4-shard run took about 1.5 min per case under load. The "30-60 s" estimate in section 4 is superseded: do not size runs from it; profile first.
- The D readable-view labels still call ordinary relative-stats runs "prefix length N, series ..." (RS01, RS02): a D worker display defect found only at the browser demo, values correct. Display review needs generated pages for non-prefix cases, not only prefix ones.
- Merge friction: "Base branch was modified" on two squash merges because parallel PRs landed; retry after fetch works.
- Doc line endings are mixed in the repo (STATUS, HANDOFF, EF2 and EF3 docs are CRLF in the index while reviews reported both). Pick one rule.
- Leftover worktrees and a demo server need cleanup at release close.

Token ledger additions since the first draft (k): E workers Sonnet rework 145 (reviewer 133); tools builder 172 (reviewers 96 + 105, re-check 105); qualification 131 (reviewer 109); evidence 110 (reviewer 90); demo preparation 90; docs reviewers 74 + 71. Coordinator turns are not measured.

Changes for EF4 (decided, pending owner review; each is checked at the EF4 retrospective):
1. Reviewer scope and harness reuse: authors save fixture-expansion code to the shared notes folder; reviewers write only the independent comparator and a sample.
2. Run the full worker demo once at qualification, not per layer; per-layer runs use a sample plus all refusals.
3. Display check: generate readable pages for at least one non-prefix case per example and text-check labels before approval.
4. Profile one worker case before any run over 50 cases; size by the measured time.
5. Pick a line-ending rule (.gitattributes) for docs; owner decision.
6. Trial generating adapter and worker skeletons from the contract pack on one EF4 layer; compare tokens with the template-copy approach.
7. Start EF4 in a fresh coordinator session from HANDOFF.md (this session is long).
8. Release close cleans leftover worktrees, servers and scratch.
