# Retrospective: EF2 and EF3 (draft, October 23, 2026)

Status: draft written while EF3 is open. Finalize at EF3 close with the E worker, installed Windows qualification, browser demo and owner demo. EF2 had no retrospective when it merged; this covers it from its evidence doc and from the EF3 record only, with no per-agent EF2 numbers (the EF2 coordinator session is not available). Nothing here is an acceptance claim.

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
| E I/O | 319 (65 tools, 13 min) | 164 (38 tools, 7 min) | +21 | 503 |
| F library | 372 (72 tools, 21 min) | 219 (37 tools, 9 min) | +1 | 591 |
| F I/O | 292 (60 tools, 10 min) | 137 (26 tools, 5 min) | +7 | 436 |
| F workers | 215 (76 tools, 44 min) | 195 (58 tools, 24 min) | +8 | 418 |
| Amendment | 123 (25 tools, 3 min) | 86 (9 tools, 1 min) | +2 | 211 |
| E workers (Haiku, failed) | 276 (67 tools, 42 min) | not reached | | 276 |

About 3.8M subagent tokens for EF3 before the E workers rework, excluding the Sonnet takeover still running. Coordinator tokens are not measurable here (the session counter reset); the coordinator carried a short handoff instead of a 550-turn history, which was the point of the restart.

Observations:
- Haiku was not much cheaper in tokens than Sonnet on the same kind of layer (250-320k vs 360k). Any saving is price per token, not volume, and was not measured.
- Review cost 40-70% of build cost. It found the defects above, so it earned its place, but reviewers re-derived data the build already had. Giving reviewers the author's input derivation to audit (not repeat) may cut cost without losing the independent recompute.
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
- Breadth declared (F), 4096 members, all 16 outputs: 0.7 s (reviewer). Adaptive volume, 4096 random rationals: 1.7 s (reviewer); author reported 2 s typical and 13 s for a float-equal near-tie stream, which the reviewer did not reproduce. A Fraction-based baseline took about 29 s for 4096 rows, so the library keeps integer pairs.
- Worker layer: roughly 30-60 s per fixture case end to end (build task, run, publish to DuckDB, replay, reopen, HTML view). A 124-case run takes about 2 hours sequentially. Time was not profiled; the likely cost is per-case process, database and view setup rather than the maths (library times above are sub-second). Memory is O(window), batch only; the contract's O(1) incremental state is not delivered.

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

After every retrospective we improve the working agreement and the way we work. Done here: items 1-9 above are written into the release-coordinator skill (layer brief checklist) and a new step 8 makes the improvement step part of every release close. Next retrospective (EF3 close) must report, per item 1-9, whether it was applied and whether it helped (token use, defects found at review, rounds per PR, idle notifications), and propose the next set of changes.
