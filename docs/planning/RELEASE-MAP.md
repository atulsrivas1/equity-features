# Release map: what exists and what is next

> Working document, not a decision. PO, 2026-10-30. Internal, synthetic, pre-release. Sources are existing and not repeated: `STATUS.md`, `DECISIONS.md`, `docs/EQUITY_DELIVERY_REPLAN.md` (EF1-EF8 goals), `docs/plans/design-coverage-map.json` and `docs/plans/records/` (CV), `docs/dv1/`, `docs/ef5/`. Hand-kept table (under 20 stories; no generator yet).

## What exists

| Item | State | Open |
|---|---|---|
| EF1-EF4 | Delivered in all three layers, Windows-qualified, not accepted | Linux, real-source demo, rights/parity, acceptance (owner publish gate) |
| EF5 | Contract frozen internally (ef5-price-structures-1); library, io, workers bumped | PO-1..PO-7 ratification (owner); service/MCP exposure not built |
| DV1 | DV1-0..DV1-6 libraries merged; C1/C2 bump merged in all three repos | Closeout C4 (RL1-01..08), CAT-DV1 |
| CV0 | Merged (166-item map, validator) | CV1-CV6 |
| Replan EF6-EF8 | Not started | After RL1 |
| Label clash | Replan EF6 is events/fundamentals; the PO parity reconciliation (local `work/`) used EF6..EF14 for later stories (EF6 = DV1, EF12 = real-data enablement incl. service/MCP exposure, EF14 = named patterns) | Architect/coordinator ruling |

## Next release: RL1 "DV1 closeout, catalogue and coverage"

Working id RL1 because `docs/releases/R1` is historical. `docs/releases/RL1/` is created when its SCOPE and READINESS are written (one release ahead, never empty).

In flight, not buffer (coordinator): workers re-pin PR (commit pins to 6c3123c plus the two #110 notes), then core re-pin PR (SIBLINGS and commits; run conformance, r10, r9, evidence_pilot), then merge core #761. Team meeting before any new feature work.

| ID | Story | Lane | Size | Status | Blocker / closer |
|---|---|---|---|---|---|
| RL1-01 | DV1 contract wording: RO fixtures expected=observed; input says interval bars | core | S | Ready | none |
| RL1-02 | DV1 second-author recompute incl. DV1-1 re-run (author is not the original) | core | M | Ready | none |
| RL1-03 | DV1 reviewer-verdict rows into `docs/qa` | core | S | Ready | none |
| RL1-04 | core_spread policy-label order | core | S | Blocked | Architect options, then PO ruling |
| RL1-05 | Joint-call `evidence_limit` ratification | PO | S | PO acts after RL1-02 | PO |
| RL1-06 | Freeze text "Frozen as ..." | core | S | Blocked | RL1-01..05 |
| RL1-07 | Independent docs review and Tester pass of DV1 | Tester | M | Blocked | RL1-06 |
| RL1-08 | Ownership manifest 10-row flip | core | S | Blocked | RL1-07 |
| RL1-09 | Catalogue S2-S8, whichever are unmerged (S3, S6, S8 serial on the io writer) | io/workers/core | M each | Ready if unmerged (state unconfirmed) | Architect confirms state |
| RL1-10 | CV1 generator and gate (CV6 folded in) | io | L, split | Blocked | RL1-09 (S3, S6, S8) |
| RL1-11 | CV2 (own io-contracts bump), CV3 (gate demo PR per repo), CV4 (after S2) | io, core, workers | M | Blocked | RL1-10 |
| RL1-12 | CAT-DV1 catalogue pages (io-contracts a5 to a6), then CV5 flip | io | M | Blocked | RL1-08 |
| RL1-13 | Bars job specs need 13 headers | workers | S | Blocked | Architect: header list |
| RL1-14 | 39-feature cap vs 40 built-ins | core/workers | S | Blocked | Architect ruling |
| RL1-15 | E9 unit-spelling migration (three repos) | all | L, split | Blocked | Owner E9 ratification; PO orders it last on the provisional reading |
| RL1-16 | ef5.* service/MCP exposure | workers | L | Blocked | Architect design; owner item only if it goes beyond primitives |

Later: four other intraday shared-admission families, controlled-machine benchmarks, README-gate gaps, Researcher ideas, then replan EF6-EF8 and the parity stories.

### Ready buffer (honest)

Ready now: core 3 (RL1-01..03); io and workers 0 certain, up to 7 more if the Architect confirms RL1-09 unmerged. The playbook target of 10 is not met. The PO starts RL1 short, because everything else waits on DV1 closeout or an Architect ruling. Growth plan: Architect rulings on RL1-04, -13, -14, -16 and the RL1-09 state convert 5 to 8 stories to Ready; the PO then writes story files (`TEMPLATES/story.md`) for the Ready set. Tester has no work until RL1-07.

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
| Line-ending rule; version bump at release | Existing behaviour |

## Rulings needed from the Architect

1. State of catalogue S2-S8 across io, workers and core.
2. core_spread policy-label order options.
3. Header list for bars job specs; where the 39 cap lives.
4. Design for ef5 service/MCP exposure and E9 migration sequencing.
5. Release id and EF label scheme (RL1 vs parity EF6..EF14).
