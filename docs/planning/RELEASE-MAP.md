# Release map: what exists and what is next

> Working document, not a decision. PO, 2026-10-30. Internal, synthetic, pre-release. Sources are existing and not repeated: `STATUS.md`, `DECISIONS.md`, `docs/EQUITY_DELIVERY_REPLAN.md` (EF1-EF8 goals), `docs/plans/design-coverage-map.json` and `docs/plans/records/` (CV), `docs/dv1/`, `docs/ef5/`. Hand-kept table. Commit 6c3123c and workers #110 come from HANDOFF-2026-10-30 (local, not re-verified here); "Windows-qualified" is from STATUS.md (under 20 stories; no generator yet).

## What exists

| Item | State | Open |
|---|---|---|
| EF1-EF4 | Delivered in all three layers, Windows-qualified, not accepted | Linux, real-source demo, rights/parity, acceptance (owner publish gate) |
| EF5 | Contract frozen internally (ef5-price-structures-1); library, io, workers bumped | PO-1..PO-7 ratification (owner); service/MCP exposure not built |
| DV1 | DV1-0..DV1-6 libraries merged; C1/C2 bump merged in all three repos | Closeout C4 (RL-01-01..06), CAT-DV1 |
| CV0 | Merged (166-item map, validator) | CV1-CV6 |
| Replan EF6-EF8 | Not started | After RL-01 |
| Labels | Replan EF6 = events/fundamentals again; DV1 is its own family; parity stories are PX-09..PX-14 | Scheme ruled (below) |

## Next release: RL-01 "DV1 closeout, catalogue and coverage"

Naming (PO decision, pending owner review): `R<n>` is historical and never reused; `EF1`-`EF8` keep the replan meaning; named families keep their own id (DV1 is not EF6; the parity label EF6=DV1 is retired); parity stories EF9-EF14 become `PX-09`..`PX-14`; releases are `RL-<nn>` with folder `docs/releases/RL-01/`, created when SCOPE and READINESS are written, and stories `RL-01-<nn>`.

In flight, not buffer (coordinator, status 2026-10-30): the workers re-pin PR is in progress (it moves the workers pin for the merged core and io changes); then the core re-pin PR (SIBLINGS and commits; run conformance, r10, r9, evidence_pilot), then merge core #761. Team meeting before any new feature work.

| ID | Story | Lane | Size | Status | Blocker / closer |
|---|---|---|---|---|---|
| RL-01-01 | DV1 contract wording: RO fixtures expected=observed; input says interval bars; core_spread names the common first "parameters" stage (option A) with one gate case per adjacent stage pair | core | S | Blocked | After core #761 (shared DV1 markdown files) |
| RL-01-02 | DV1 second-author recompute incl. DV1-1 re-run (not the original author) | core | M | Blocked | After core #761 |
| RL-01-03 | DV1 reviewer-verdict rows into `docs/qa` | core | S | Ready | none |
| RL-01-04 | core_spread policy-label order | PO | - | Ruled: option A (docs only), folded into RL-01-01 | none |
| RL-01-05 | Joint-call `evidence_limit` ratification | PO | S | PO acts after RL-01-02 | PO |
| RL-01-06 | C4 PR: "Frozen as" text and 10-row manifest flip in ONE PR; evidence = independent docs review and Tester pass | core + Tester | M | Blocked | RL-01-01, -02, -03, -05 |
| RL-01-07 | S6 part 2 (Python lookups, io-contracts bump 1) | io | M | Merged | io #68 (3410402); bump #69 (927372a) to 0.1.0a6 |
| RL-01-08 | S8 `check_input`/`check_output` | io | M | Merged | io #70 (3409c7a) |
| RL-01-09 | S2 EF2+EF1 catalogue families | io | M | Merged (partial EF1) | io #71 (e47b0c5); follow-up RL-01-20 |
| RL-01-10 | S4 link layer (io docs, workers docs) | io, workers | S | Io half merged | io #72 (0dbe5f5); workers half open as "RL-01-10 workers lane" |
| RL-01-11 | S5 header cross-check + IO_V1 one-line reference | io | S | Merged | io #73 (f1251ce) |
| RL-01-12 | S3 remainder: workers gate and core advisory hook (rulings: parallel, single-repo; no order) | workers, core | S | Workers part merged | workers #111 (1df482e); core hook open |
| RL-01-13 | S7 core pointer README note | core | S | Merged | core #774 (f43434b) |
| RL-01-14 | Bars job spec lists the closed 13-id `BAR_IDS` set: core exports it publicly first, then workers import it after the re-pin | core, then workers | S+S | Core part merged | core #773 (e646fe7); workers part open, needs the workers re-pin |
| RL-01-15 | CV1 generator and gate (CV6 folded in) | io | L, split | Blocked | RL-01-07, -08 (S3 io part merged) |
| RL-01-16 | CV2 (own bump), CV3 (gate demo PR per repo), CV4 (after S2) | io, core, workers | M | Blocked | RL-01-15, -09 |
| RL-01-17 | CAT-DV1 catalogue pages, then CV5 flip | io | M | Blocked | RL-01-06 ("Frozen as" text merged); RL-01-16 (bump order S6, CV2, CAT-DV1) |
| RL-01-20 | EF1 proposed core contracts: catalogue pages once frozen | io | S | Blocked | Core freeze of EF1 proposed contracts; origin PO ruling on io #71 |
| RL-01-21 | check_input/check_output hardening (non-hashable feature_id, bare-string reasons, roles=None TypeError; document) | io | S | Ready | none |
| RL-01-22 | Header cross-check v2: feature ids, dtype, unit, schema_version; resolve 34 NOT_DECLARED pairs | io | M | Ready | none |
| RL-01-18 | E9 unit-spelling migration (three repos) | all | L, split | Blocked | Owner E9 ratification; ordered last |
| RL-01-19 | ef5.* service/MCP exposure, primitives only, per Architect design (closed command table from the catalogue, remote schema v1.2) | workers | L | Blocked | RL-01-07 (lookups); Architect confirms notional-cell remote decode status; owner item only beyond primitives |

Closed by ruling: 39-feature cap stays 39 (per-job policy limit, not a built-in count); "no change, documented" (former cap story). Any change to it is decided once with RL-01-19.

io-contracts bump order (one order; version strings assigned by the coordinator): S6 (RL-01-07), then CV2, then CAT-DV1 last.

Later: four other intraday shared-admission families, controlled-machine benchmarks, README-gate gaps, Researcher ideas, then replan EF6-EF8 and the parity stories.

### Ready buffer

Story files: `docs/releases/RL-01/STORIES.md`. Status 2026-10-30: merged are RL-01-07, -08, -09 (partial EF1), -11, -13, the io half of -10, the workers part of -12 and the core part of -14. Ready now: RL-01-03, the core hook of -12, the RL-01-10 workers lane, RL-01-21 and -22; the workers part of -14 becomes Ready when the workers re-pin merges; RL-01-01 and -02 join when core #761 merges. Honest limit: the io catalogue chain (-07, -08, -09, -11) is serial on one writer, so only one io story is in build at a time. Lanes: core Developer -03, -13, then -01/-02; io Developer -07 -> -08 -> -09 -> -10 -> -11; workers Developer -14, -12, -10 workers docs. Tester: nothing until -06; meanwhile reads -07/-08 outputs on the installed io-contracts. A fourth Developer is not warranted (fewer than 20 independent Ready stories).

## Owner-level items (listed, not decided; provisional reading in force)

| Item | Provisional reading |
|---|---|
| E1-E9 ratification | Coordinator rulings in `docs/ef4/EF4_SHARED_AMENDMENT.md` in force; E9 slash-style spelling |
| PO-1..PO-7 ratification | Accepted and applied to the EF5 contract |
| Linux machine and qualification (incl. EQ-139 rerun) | Windows-only qualification; no Linux claim |
| Owner demo | Browser-demo evidence only; none held |
| Publish, tag, sign-off | None; all stays internal, synthetic, pre-release |
| EF5 "stop at primitives" reversal (EF14) | Stop at primitives; no named formations |
| Design owner's 252-vs-253 period number | Contract leaves it to the consumer; no default added |
| Line-ending rule (.gitattributes); package version bump at release | Existing behaviour |

## Rulings from the Architect (PR 767) and PO decisions

Answered in `docs/architecture/RELEASE-0-RULINGS.md`. PO decisions: core_spread option A; keep the 39 cap and close the cap story; bars spec is the closed 13-id set; naming scheme as above; EF6=DV1 retired; ADR-2 range pins deferred; ADR-3 after CV1, ADR-4 after RL-01. Still open for the Architect: confirm the notional-cell remote decode status before RL-01-19.
