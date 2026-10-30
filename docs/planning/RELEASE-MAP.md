# Release map: what exists and what is next

> Working document, not a decision. PO, 2026-10-30. Internal, synthetic, pre-release. Sources are existing and not repeated: `STATUS.md`, `DECISIONS.md`, `docs/EQUITY_DELIVERY_REPLAN.md` (EF1-EF8 goals), `docs/plans/design-coverage-map.json` and `docs/plans/records/` (CV), `docs/dv1/`, `docs/ef5/`. Hand-kept table. Commit 6c3123c and workers #110 come from HANDOFF-2026-10-30 (local, not re-verified here); "Windows-qualified" is from STATUS.md (under 20 stories; no generator yet).

## What exists

| Item | State | Open |
|---|---|---|
| EF1-EF4 | Delivered in all three layers, Windows-qualified, not accepted | Linux, real-source demo, rights/parity, acceptance (owner publish gate) |
| EF5 | Contract frozen internally (ef5-price-structures-1); library, io, workers bumped | PO-1..PO-7 ratification (owner); service/MCP exposure not built |
| DV1 | DV1-0..DV1-6 libraries merged; C1/C2 bump merged in all three repos | Closeout C4 (RL1-01..06), CAT-DV1 |
| CV0 | Merged (166-item map, validator) | CV1-CV6 |
| Replan EF6-EF8 | Not started | After RL1 |
| Label clash | Replan EF6 is events/fundamentals; the PO parity reconciliation (local `work/`) used EF6..EF14 for later stories (EF6 = DV1, EF12 = real-data enablement incl. service/MCP exposure, EF14 = named patterns) | Architect/coordinator ruling |

## Next release: RL1 "DV1 closeout, catalogue and coverage"

Working id RL1 because `docs/releases/R1` is historical. `docs/releases/RL1/` is created when its SCOPE and READINESS are written (one release ahead, never empty).

In flight, not buffer (coordinator): workers re-pin PR (commit pins to 6c3123c plus the two #110 notes), then core re-pin PR (SIBLINGS and commits; run conformance, r10, r9, evidence_pilot), then merge core #761. Team meeting before any new feature work.

| ID | Story | Lane | Size | Status | Blocker / closer |
|---|---|---|---|---|---|
| RL1-01 | DV1 contract wording: RO fixtures expected=observed; input says interval bars | core | S | Blocked | After core #761 (open; conflicts on the two shared DV1 markdown files) |
| RL1-02 | DV1 second-author recompute incl. DV1-1 re-run (author is not the original) | core | M | Blocked | After core #761 (re-run only meaningful after it merges) |
| RL1-03 | DV1 reviewer-verdict rows into `docs/qa` | core | S | Ready | none |
| RL1-04 | core_spread policy-label order | core | S | Blocked | Architect options, then PO ruling |
| RL1-05 | Joint-call `evidence_limit` ratification | PO | S | PO acts after RL1-02 | PO |
| RL1-06 | C4 PR: freeze text "Frozen as ..." and the 10-row ownership manifest flip in ONE PR; its evidence is the independent docs review and the Tester pass (not later steps) | core + Tester | M | Blocked | RL1-01..05 |
| RL1-07 | Catalogue S2-S8, none merged (only S1 is: core #754, io #66; no catalogue PR open). S3, S4, S5, S7 size S; S2, S6, S8 size M. S3, S6, S8 serial on the io writer | io/workers/core | S-M | Ready: S3, S6, S8, S7 (S7 needs only S1); S2 serial with S6/S8; S4, S5 after S3 | none |
| RL1-08 | CV1 generator and gate (CV6 folded in) | io | L, split | Blocked | RL1-07 (S3, S6, S8) |
| RL1-09 | CV2, CV3 (gate demo PR per repo), CV4 (after S2) | io, core, workers | M | Blocked | RL1-08 |
| RL1-10 | CAT-DV1 catalogue pages, then CV5 flip | io | M | Blocked | RL1-06 (merged "Frozen as" text) |
| RL1-11 | Bars job specs need 13 headers | workers | S | Blocked | Architect: header list |
| RL1-12 | 39-feature cap vs 40 built-ins | core/workers | S | Blocked | Architect ruling |
| RL1-13 | E9 unit-spelling migration (three repos) | all | L, split | Blocked | Owner E9 ratification; PO orders it last on the provisional reading |
| RL1-14 | ef5.* service/MCP exposure | workers | L | Blocked | Architect design; owner item only if it goes beyond primitives |

io-contracts bump order (PO, one order; version strings assigned by the coordinator): S6 bump first, then CV2 its own bump (PO ruling D3: it cannot fold into S6 because S6 and S8 precede CV1), then CAT-DV1 last. The earlier "a5 to a6" for CAT-DV1 holds only if it lands first.

Later: four other intraday shared-admission families, controlled-machine benchmarks, README-gate gaps, Researcher ideas, then replan EF6-EF8 and the parity stories.

### Ready buffer (honest)

Ready now: core 1 (RL1-03) and catalogue S3, S6, S8, S7 (io lane, serial on one writer, so about 2 at a time). RL1-01 and -02 become Ready when core #761 merges (3 more). The playbook target of 10 is not met. The PO starts RL1 short, because everything else waits on DV1 closeout or an Architect ruling. Growth plan: merging #761 plus Architect rulings on RL1-04, -11, -12 and -14 convert 5 to 7 stories to Ready; the PO then writes story files (`TEMPLATES/story.md`) for the Ready set. Tester has no work until RL1-07.

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

## Rulings needed from the Architect

1. Confirm the io-contracts bump order above.
2. core_spread policy-label order options.
3. Header list for bars job specs; where the 39 cap lives.
4. Design for ef5 service/MCP exposure and E9 migration sequencing.
5. Release id and EF label scheme (RL1 vs parity EF6..EF14).
