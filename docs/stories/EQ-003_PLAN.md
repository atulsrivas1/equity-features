# EQ-003 — story execution plan

Story: [Specify quote formulas and sampling](https://github.com/atulsrivas1/equity-features/issues/4). Epic E01; release R0. Estimate: **5 points, provisional relative complexity**, not hours or a delivery date.

## Purpose and start

Define the three EQ-003-owned IDs from V1_SCOPE.md before package implementation. Confirm EQ-001 scope and EQ-002 timing/precision/coverage conventions; inventory quote sampling kinds, then settle state classification, denominator and continuous validity policies. The complexity is in temporal carry, gaps, eligibility and independent examples rather than the number of formulas.

Write the formula contract and consequential decisions first, derive synthetic rational expectations independently, then validate edge cases and partition arithmetic. Open a linked draft PR, self-review the full specification, execute final-head CI and verify publication before Done. The owner explicitly deferred Codex reviewer setup; label self-review accurately and retain all existing test/documentation/release gates.

## Design and deliverables

- docs/features/QUOTE_FORMULAS.md:3definitions, input/sampling contract, state/count/summary equations, continuous validity and quality rules.
- docs/decisions/quote-semantics.md: locked/crossed handling, observation versus duration weighting, initial state and expiry choices with rationale.
- tests/fixtures/quote_math/: synthetic inputs, hand-derived expected results and explanation.
- tools/verify_quote_examples.py: exact rational reference arithmetic and boundary checks, not production functions.
- Documentation CI, V1 scope navigation, issue/PR evidence and SESSION_HANDOFF updates.

## Decisions and open questions

| Question | Story decision or owner |
| --- | --- |
| How are quotes sampled? | Caller declares trade-associated samples or complete continuous normalized state updates; no inferred continuous book from samples |
| What is valid? | Positive two-sided normal or locked price; crossed/one-sided/nonpositive observations excluded from valid spread means but counted |
| What weights a sampled mean? | One equal weight per admitted observation; trade-associated bias is visible; no size weighting |
| What weights continuous spread? | Duration of valid state clipped to window, next update and explicit positive max_age; locked0 included |
| What is initial state? | Prior admitted seed with original age, explicitly known inactive, or unknown left boundary; unknown duration prevents complete published time-weighted results |
| What do invalid/expired states mean? | Known excluded duration, not invented0spread; expose valid duration/fraction and state diagnostics |
| What default quote age? | No market-wide default; caller must supply max_age and its policy identity |
| What is still open? | EQ-011–016 settle typed encoding; EQ-006 owns availability/adjustment admission; EQ-021/023–026 implement/parity-test kernels and carry. No dependency is hidden as an implicit provider default |

## Validation

Check every3ID has units, equations, examples and boundary rules. Independent golden cases establish sampled means/counts and continuous integrals. Edge checks cover locked0, signed crossed evidence, missing/nonpositive versus malformed fields, empty/absent/incomplete input, equal timestamps, duplicates/order, half-open bounds, seed age, unknown/inactive left boundary, invalid resets, excluded updates, expiry configuration, precision/overflow-safe intermediates, partial cutoff and duration conservation. Partition checks use boundary carry and numerator/denominator totals rather than means of means.

No performance benchmark or backend/package build is required for this mathematical documentation story. Preserve existing session reference cases; CI adds quote checks. Publication evidence records actual final commit/checks and verifies public documents/fixtures.

## End state

All3quote feature IDs have implementation-ready mathematical/temporal definitions and independently checked examples, questions are resolved or explicitly bounded, linked documentation and final-head checks pass, and published artifacts are verified. Only then mark documentation Released/Done. No calculation package, continuous provider feed, chart adapter, accepted real dataset or R0 release is implied. Next EQ-004 historical formulas becomes Ready when its inputs/acceptance are confirmed.
