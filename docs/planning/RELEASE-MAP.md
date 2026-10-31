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

In flight, not buffer (coordinator, status 2026-10-31): the workers re-pin (workers #112, 474f79d) and the core-side workers pin (core #777, df80995) are merged; core #761 is not yet merged. Team meeting before any new feature work.

| ID | Story | Lane | Size | Status | Blocker / closer |
|---|---|---|---|---|---|
| RL-01-01 | DV1 contract wording: RO fixtures expected=observed; input says interval bars; core_spread names the common first "parameters" stage (option A) with one gate case per adjacent stage pair | core | S | Blocked | After core #761 (shared DV1 markdown files) |
| RL-01-02 | DV1 second-author recompute incl. DV1-1 re-run (not the original author) | core | M | Blocked | After core #761 |
| RL-01-03 | DV1 reviewer-verdict rows into `docs/qa` | core | S | Merged | core #778 (3ea6efc) |
| RL-01-04 | core_spread policy-label order | PO | - | Ruled: option A (docs only), folded into RL-01-01 | none |
| RL-01-05 | Joint-call `evidence_limit` ratification | PO | S | PO acts after RL-01-02 | PO |
| RL-01-06 | C4 PR: "Frozen as" text and 10-row manifest flip in ONE PR; evidence = independent docs review and Tester pass | core + Tester | M | Blocked | RL-01-01, -02, -03, -05 |
| RL-01-07 | S6 part 2 (Python lookups, io-contracts bump 1) | io | M | Merged | io #68 (3410402); bump #69 (927372a) to 0.1.0a6 |
| RL-01-08 | S8 `check_input`/`check_output` | io | M | Merged | io #70 (3409c7a) |
| RL-01-09 | S2 EF2+EF1 catalogue families | io | M | Merged (partial EF1) | io #71 (e47b0c5); follow-up RL-01-20 |
| RL-01-10 | S4 link layer (io docs, workers docs) | io, workers | S | Done | io #72 (0dbe5f5); workers lane workers #114 (570d14c) |
| RL-01-11 | S5 header cross-check + IO_V1 one-line reference | io | S | Merged | io #73 (f1251ce) |
| RL-01-12 | S3 remainder: workers gate and core advisory hook (rulings: parallel, single-repo; no order) | workers, core | S | Done | workers #111 (1df482e); core hook core #776 (203445a) |
| RL-01-13 | S7 core pointer README note | core | S | Merged | core #774 (f43434b) |
| RL-01-14 | Bars job spec lists the closed 13-id `BAR_IDS` set: core exports it publicly first, then workers import it after the re-pin | core, then workers | S+S | Done | core #773 (e646fe7); workers re-pin workers #112 (474f79d), core-side pin core #777 (df80995); workers part workers #113 (e9e5f5b) |
| RL-01-15 | CV1 generator and gate (CV6 folded in) | io | L, split | Ready | none (RL-01-07, -08 merged) |
| RL-01-16 | CV2 (own bump), CV3 (gate demo PR per repo), CV4 (after S2) | io, core, workers | M | Blocked | RL-01-15 |
| RL-01-17 | CAT-DV1 catalogue pages, then CV5 flip | io | M | Blocked | RL-01-06 and RL-01-16 (bump order S6, CV2, CAT-DV1) |
| RL-01-20 | EF1 proposed core contracts: catalogue pages once frozen | io | S | Blocked | Core freeze of EF1 proposed contracts; origin PO ruling on io #71 |
| RL-01-21 | check_input/check_output hardening (non-hashable feature_id, bare-string reasons, roles=None TypeError; document) | io | S | Merged | io #74 (cc2cf31) |
| RL-01-22 | Header cross-check v2: feature ids, dtype, unit, schema_version; resolve 34 NOT_DECLARED pairs | io | M | Merged | io #75 (39a5f97); 34 pairs recorded in `tools/header_crosscheck_accepted.json` |
| RL-01-18 | E9 unit-spelling migration (three repos) | all | L, split | Blocked | Owner E9 ratification; ordered last |
| RL-01-19 | ef5.* service/MCP exposure, primitives only, per Architect design (closed command table from the catalogue, remote schema v1.2) | workers | L | Blocked | Architect's notional-cell decode confirmation |

Closed by ruling: 39-feature cap stays 39 (per-job policy limit, not a built-in count); "no change, documented" (former cap story). Any change to it is decided once with RL-01-19.

io-contracts bump order (one order; version strings assigned by the coordinator): S6 (RL-01-07), then CV2, then CAT-DV1 last.

Later: four other intraday shared-admission families, controlled-machine benchmarks, README-gate gaps, Researcher ideas, then replan EF6-EF8 and the parity stories.

### Ready buffer

Story files: `docs/releases/RL-01/STORIES.md`. Status 2026-10-31: done are RL-01-03, -07, -08, -09 (partial EF1), -10, -11, -12, -13, -14, -21 and -22. Waiting: RL-01-01 and -02 wait on core #761; RL-01-06 waits on -01, -02, -05. Blocked: RL-01-16 (on -15), RL-01-17 (on -06 and -16), RL-01-18 (owner E9 ratification), RL-01-19 (Architect's notional-cell decode confirmation) and RL-01-20 (core freeze of the EF1 proposed contracts). Ready: RL-01-15. Lanes: core Developer -01/-02 after core #761; io Developer takes RL-01-15; workers Developer has no Ready story. Tester: nothing until -06.

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
