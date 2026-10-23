# EF3 delivery evidence (EF3 package)

October 23, 2026. Evidence summary for the EF3 release (relative statistics and realized variance, robust history and volume pace, breadth and adaptive volume). This is delivery evidence, not acceptance: **EF3 is not accepted.** EQ-153, EQ-154, EQ-155, EQ-156, EQ-157 and EQ-241 acceptance is not done, and every decision recorded here is a coordinator decision, pending owner review. Merge facts below were read from GitHub and git on this date; verdicts, fixture counts and timings are taken from the documents named in each section and were not re-run for this package.

## Scope delivered

| Contract | Stories | Producers | Frozen contract |
| --- | --- | --- | --- |
| D: relative statistics, daily log volatility, realized variance | EQ-153, EQ-154 | `ef3.relative_stats` (3 headers), `ef3.daily_log_volatility` (1), `ef3.intraday_realized_variance` (2) | `docs/ef3/RELATIVE_RV_CONTRACT_PROPOSAL.*` (#689) with Amendment 1 (#693) |
| E: robust history, volume pace, mean ratio | EQ-155, EQ-156, EQ-241 | `ef3.robust_history` (6), `ef3.volume_pace_robust` (4), `ef3.volume_ratio_mean` (3) | `docs/ef3/ROBUST_PACE_CONTRACT_PROPOSAL.*` (#690) |
| F: session breadth, observed breadth, adaptive volume | EQ-220, EQ-242, EQ-237 (as named in the library PR title) | `ef3.session_breadth` (16), `ef3.observed_breadth` (7), `ef3.adaptive_volume` (10) | `docs/ef3/BREADTH_ADAPTIVE_CONTRACT_PROPOSAL.*` (#691) |

52 new headers in total (source: `docs/ef3/EF3_SHARED_AMENDMENT.md`, section a). The frozen `docs/ef1/CONTRACT.json` is unchanged. The shared amendment is `docs/ef3/EF3_SHARED_AMENDMENT.*` (#696); nothing in it is accepted.

## Layers merged (merge commits read from GitHub)

| Layer | Contract D | Contract E | Contract F |
| --- | --- | --- | --- |
| Contract (core) | #689 `75ece6a`, Amendment 1 #693 `29d360a` | #690 `5471a2a` | #691 `cfb4ce1` |
| Library (core) | #692 `d8ed913` | #694 `6adf840` | #695 `ee92759` |
| I/O (equity-feature-io) | #36 `b8e09f4` | #37 `01295be` | #38 `86cbff2` |
| Workers (equity-feature-workers) | #80 `bd65fe5` | #82 `f92fd6a` | #81 `1317428` |

Other core PRs: shared amendment #696 `82c1c8a`; retrospective #697 `778b608` and #698 `af7250d`; tools (contract layer pack, quiet batch runner) #699 `4cb50ef`. All core PRs #689 to #699 are merged (10:49 to 17:15 UTC on October 23, 2026). Windows installed qualification is core PR #700, **still open and not merged** at the time of writing; it is cited below as open.

## How each part was verified

Independent review verdicts are not recorded on the PRs. They come from the sources named here.

- Contracts (#689 to #691, #693): the recomputation is described in the contract documents; reviewer verdicts for the contract PRs were not located in the sources read for this package.
- Libraries (verdict source: `docs/knowledge/RETRO_EF2_EF3.md` section 1 and the Review notes in `docs/ef3/*_IMPLEMENTATION.md`): D #692 approved earlier, with a documented reconstruction-mode exception; E #694 approve, six contract nits; F #695 approve, one contract ambiguity needing a ruling (roster rows of other groups).
- I/O (checkpoint docs `EF3_*_IO.md` in equity-feature-io; verdicts from the retrospective): D #36 approve with fixes (return types, doc wording; a stale sha256 later found by the D worker author); E #37 approve with fixes (real defect: instrument id "X" hardcoded in builders); F #38 BLOCK at first review (declared sha256 stale because of a CRLF working copy, overstated doc, silent sort) and merged afterwards. The post-fix re-review is not recorded in detail in the sources read.
- Workers (worker docs in equity-feature-workers; verdicts from the retrospective): D #80 approve (limits added at review); F #81 approve with fixes (view mislabel, leaked library error). E #82: the retrospective records only the failed Haiku run (98 of 124 passed) and the Sonnet takeover; **no reviewer verdict for E workers #82 was found in the sources read**.
- Shared amendment #696: approve with fixes (retrospective); its own text says R3, R7 and the worker-layer claims of R9 were not re-verified by the reviewer.

## What was matched, at which layer

Fixture counts (author-reported in the implementation docs, not independently confirmed in this package): D 62 results, 3 prefix-property, 48 refusals; E 124 results (44 history, 24 cohort, 37 pace, 19 mean), 48 refusals; F 99 results (49 declared, 20 observed, 30 adaptive), 62 refusals (73 variants).

| Layer | D | E | F |
| --- | --- | --- | --- |
| Library (implementation docs, author) | 62, 3 prefix, 48 refusals matched | 124 matched (P18 through an alternate construction), 48 refusals | 99 matched (1224 cells), AD06 prefix 7 of 7, 62 refusals |
| I/O adapter (checkpoint docs) | 62 of 62 matched, 48 of 48 refusals | all result fixtures matched, 48 of 48 refusals | 1224 of 1224 output cells matched |
| Worker (worker docs) | 62 of 62 results plus 2 of 2 prefix cases; 180 of 180 runs read back, replayed, reopened | 124 cases built and run, full results demo in 4 shards; an explicit pass count was not found in the doc | 99 of 99 matched, readback, replay, reopen; the reviewer ran 76 of the 99 through the sink path |

### What was NOT driven (worker-layer refusal coverage)

- D workers: 24 of 48 refusal fixtures driven (by the reviewer), 5 of those failed at compute; the other 24 were not run. PX03 is not a separate case. Invalid-admission controls were reviewed by reading, not exercised.
- E workers: all 48 refusals driven with `--refusals`: 14 refused at adapter build (worker never reached), 16 at worker admission, 17 at compute, 1 (RF31) is not a worker path. Contract code matched via the library code in all 48.
- F workers: 59 of 62 refusals driven (by the reviewer); 3 not driven. The 99-case results demo is registered but was not run end to end by the reviewer (about 45 minutes).
- Refusal codes collapse to `INVALID_COMMAND` at the workers (ruling R9, pending owner review); identity refusals map to `RESULT_IDENTITY_MISMATCH` in the E and F workers.
- Not exercised: independent mypy (author-reported clean only), unit suites (none by policy), real or observed data.

## Installed qualification (Windows)

Core PR #700 (`docs/ef3/EF3_INSTALLED_QUALIFICATION.md`) is **open and not merged**. Its description states: 8 packages as wheel and sdist, 4 install forms, pip check clean, 346 demos per form (287 EF3 worker contract result fixtures plus the 59-demo EF1/EF2 regression sample), identical content hashes across forms. These are the PR's own claims and are not part of this package until that PR is reviewed and merged. Linux was not run.

## Code performance (author or reviewer observed, one machine, not reproduced by the coordinator, no performance claim)

- Relative statistics, 4096-return window: about 0.2 s (4-digit closes), 2.5 s (10-digit), 10.5 s (16-digit); daily log volatility and realized variance about 0.7 s on 4096 slots (author).
- Robust history, 4096-session window: about 0.23 s (author), 0.25 s (reviewer).
- Breadth declared, 4096 members, 16 outputs: about 0.8 s (author and reviewer). Adaptive volume, 4096 random rationals: about 2 s (author), 1.7 s (reviewer); the 13 s float-equal near-tie case was author-observed and not reproduced by the reviewer.
- Workers: about 25 s per fixture for F (author); roughly 30 to 60 s per case estimated across layers; E reviewer saw about 10 s per case run alone. Not profiled.

## Known limits and release-gate items

- Reconstruction-mode exception (R1): for `ef3.relative_stats`, excluded `unknown_availability` and `future_knowledge` evidence rows are omitted in reconstruction mode because the unchanged shared validator rejects them there.
- Shared amendment rulings R1 to R9 are pending owner review. R4 (observed breadth roster) is a known divergence: the proposed ruling and merged behavior differ, and either the contract or the code must change. R5 (gating of fact `known_at`) is undecided.
- Output ownership manifest: two EF3 manifest entries have no header (`relative.session.primary.beta_residual_fraction`, `relative.session.secondary.beta_residual_fraction`) and 36 EF3 headers have no manifest entry.
- Refusal codes collapse to `INVALID_COMMAND` at the workers (R9). D workers: spawn mode unsupported for the relative and log-volatility routes; the grid registry never evicts.
- Package versions were not bumped (a bump changes the R17 digest); a version bump and release publication are owed and need the owner.
- New unit strings (`members`, `observations` and others listed in the amendment) are recorded as additive but not applied to the frozen shared contract file.
- Exact zeros: `+0.0` is guaranteed only where fixtures mark it; no snapping.
- Batch API holds data in memory (O(n)); no incremental state; reset epoch mode only for adaptive volume.

## Not done (not claimed)

- Acceptance of EQ-153, EQ-154, EQ-155, EQ-156, EQ-157 and EQ-241. EF3 is not accepted.
- Linux installed qualification (owner action); merge and review of Windows qualification #700.
- A real-source demo, source-rights and parity, benchmarks, an owner demo of the EF3 results, the owner's review of all coordinator decisions, and the final EF3 retrospective update.

## Owner items

Review rulings R1 to R9; decide the R4 and R5 divergences; confirm the manifest follow-up; approve the version bump and release publication; Linux qualification; owner demo; decide acceptance.
