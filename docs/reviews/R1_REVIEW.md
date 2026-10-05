# Independent R1 review — 2026-10-05

Reviewed `atulsrivas1/equity-features` main commit `176f20f7d292603adb63d89e9cbc39cb795e2ab6`, experimental version `0.0.2a9`. Review only: no source fixes or GitHub lifecycle changes were made.

Disposition: delivery evidence is consistent, but repair the coverage defect before relying on the incremental structure API. Two reproducible findings remain.

## P2 — Persist known missing delivery for closed intervals

Location: `packages/features/src/equity_features/incremental.py:213` and `:264`.

Snapshot remembers expected > observed only for the whole-prefix certificate. `_structure` consults each newly supplied interval certificate without retaining a previously declared missing fact for that interval. A closed interval can therefore be re-certified complete with a smaller expected count, despite receiving no replacement facts or replay. Export/restore preserves the absence of a gap flag.

Reproduction using existing synthetic fixtures:

1. Declare a structure population with final expected count unknown and no fixed interval coverage. Supply the bar for interval `first=[100,150)`.
2. Snapshot at 150 with whole-prefix `Coverage(None,1,False)` and first-interval `Coverage(2,1,False)`.
3. Result reports first interval incomplete, expected 2 / observed 1. Accumulator `known_gap` remains false.
4. Export/restore; supply only the bar for the different interval `last=[150,200)`.
5. Finalize with whole-prefix `Coverage(2,2,True)` and first interval `Coverage(1,1,True)`.
6. First interval becomes Available with volume 200, expected 1 / observed 1; both whole structure outputs are Available. No missing first-interval bar was supplied.

This violates the documented permanent known-missing-delivery/replay rule. Caller certificates are trusted assertions, but the calculator already has a concrete contradictory earlier assertion; this is not a request to authenticate discarded source history.

Repair: retain bounded per-window known-gap state, reject contradictory complete re-certification, and propagate known interval omissions to whole-target completeness. Preserve independent readiness of unaffected windows. Include these flags in state validation/export/restore and legal merge. Add regression coverage for the sequence above, direct execution and restored execution, unaffected-window readiness, and atomic rejection.

## P3 — Normalize overflow during saved-state float decoding

Location: `packages/features/src/equity_features/state.py:53` and `:220`.

An otherwise well-formed, correctly rehashed quote state with `bps_sum={"binary64":"0x1.0000000000000p+1024"}` causes `float.fromhex` to raise `OverflowError`. Restore's exception normalization omits that type, so callers catching the documented `ContractError` receive an unexpected exception. No calculator is returned and no existing state is mutated; this is an error-contract defect, not evidence of accepted corrupt arithmetic.

Repair: translate this conversion overflow to `ContractError(INVALID_SCHEMA)` and add a regression alongside the existing inf/nan and malformed-state cases. A rehashed envelope is necessary to exercise structural admission rather than only checksum rejection.

## Independent verification completed

- 370 unit tests pass.
- All 123 independent formula references pass: session 17, quote 26, history 31, context 26, timing 23.
- Strict mypy passes for 26 source/example files.
- Boundary policy gate passes: 38 negative and 10 positive fixtures.
- 300 deterministic continuous-quote cases pass an independent per-nanosecond duration/exact-rational oracle, using randomized states, equal-time events, initialization and expiry. Each case also passes four update/export/restore steps and batch parity.
- Repeated four-archive build, archive inspection, reproducibility hashes and fresh wheel/sdist pair installations pass. Each clean pair runs the 370 unit tests and eleven examples. Local environment is Windows CPython 3.12.10.
- Latest-main Documentation and Foundation GitHub Actions runs `37349389845` and `37349389926` succeed; Foundation includes Linux and Windows. Local review does not claim independent Linux execution.
- Live project: all ten EQ-017–026 stories and both prerequisite bugs are Done. R1 milestone is closed with 12 closed / zero open issues. E04 is closed. EQ-027 remains open; R2 implementation was not started by this review.
- Documentation and acceptance receipts describe the experimental artifact channel, bounded retention, source-independent API, deferred reviewer integration and unsupported continuous merge consistently.

## Rebuilt artifact SHA256

The independent clean-source build manifest identifies the reviewed main commit and `source_dirty=false`.

| Artifact | SHA256 |
| --- | --- |
| equity_feature_contracts-0.0.2a9-py3-none-any.whl | 773a35a13edb557ae35b2a995fec587d9e7052b9122b852d63aa846e539f2d28 |
| equity_feature_contracts-0.0.2a9.tar.gz | 9eb93fe85d8728e157ebb9725f040c67a9742ad303e6b6b488dd95daea381f4c |
| equity_features-0.0.2a9-py3-none-any.whl | f177b27d0f922da7f42fcbebcb9533b49e36456f264b7d1c7571eb77bda75e96 |
| equity_features-0.0.2a9.tar.gz | 3a8935594ae5c4ce0b548149c40a7ca37ea8b933dd0643a19caaf86b4d6c851e |

These checks establish the tested cases and delivery receipts, not universal correctness or throughput. No live financial source data, adapter or worker is part of this review.
