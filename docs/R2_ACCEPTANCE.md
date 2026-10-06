# R2 historical and contextual qualification

EQ037 [issue42](https://github.com/atulsrivas1/equity-features/issues/42),
[plan](stories/EQ-037_PLAN.md), [PR234](https://github.com/atulsrivas1/equity-features/pull/234).
Final acceptance is pending review, immutable builds, published-main CI and actual
installed artifacts. This qualification document does not close R2.

## Mathematical and capability coverage

All sixteen R2 IDs are actual batch implementations; session capabilities remain
23 update/restore and 22 conditional merges. Supplied C/K/E, governed session grids,
completion, initialization, action/reference identity, quantity and unit policies remain
explicit. Missing dependencies are typed unavailable results; no fetching or hidden
calculation occurs. Source-independent calculations use synthetic fixtures.

| R2 ID | Individual delivery | Causality/admission fixtures | Capability |
| --- | --- | --- | --- |
| `history.return` | [EQ027](stories/EQ-027_DELIVERY.md) | [actual fixtures](../tests/unit/test_history.py) | Batch only; update/restore/merge rejected |
| `history.prior_high` | [EQ027](stories/EQ-027_DELIVERY.md) | [actual fixtures](../tests/unit/test_history.py) | Batch only; update/restore/merge rejected |
| `history.prior_low` | [EQ027](stories/EQ-027_DELIVERY.md) | [actual fixtures](../tests/unit/test_history.py) | Batch only; update/restore/merge rejected |
| `history.sma` | [EQ028](stories/EQ-028_DELIVERY.md) | [actual fixtures](../tests/unit/test_history.py) | Batch only; update/restore/merge rejected |
| `history.ema` | [EQ028](stories/EQ-028_DELIVERY.md) | [actual fixtures](../tests/unit/test_history.py) | Batch only; update/restore/merge rejected |
| `history.rsi` | [EQ029](stories/EQ-029_DELIVERY.md) | [actual fixtures](../tests/unit/test_history.py) | Batch only; update/restore/merge rejected |
| `history.atr` | [EQ029](stories/EQ-029_DELIVERY.md) | [actual fixtures](../tests/unit/test_history.py) | Batch only; update/restore/merge rejected |
| `history.return_volatility` | [EQ030](stories/EQ-030_DELIVERY.md) | [actual fixtures](../tests/unit/test_history.py) | Batch only; update/restore/merge rejected |
| `baseline.daily_volume` | [EQ031](stories/EQ-031_DELIVERY.md) | [actual fixtures](../tests/unit/test_daily_volume.py) | Batch only; update/restore/merge rejected |
| `baseline.relative_volume` | [EQ031](stories/EQ-031_DELIVERY.md) | [actual fixtures](../tests/unit/test_daily_volume.py) | Batch only; update/restore/merge rejected |
| `baseline.interval_volume` | [EQ032](stories/EQ-032_DELIVERY.md) | [actual fixtures](../tests/unit/test_bucket_volume.py) | Batch only; update/restore/merge rejected |
| `baseline.interval_relative_volume` | [EQ032](stories/EQ-032_DELIVERY.md) | [actual fixtures](../tests/unit/test_bucket_volume.py) | Batch only; update/restore/merge rejected |
| `relative.market_return` | [EQ034](stories/EQ-034_DELIVERY.md) | [actual fixtures](../tests/unit/test_relative.py) | Batch only; update/restore/merge rejected |
| `relative.sector_return` | [EQ034](stories/EQ-034_DELIVERY.md) | [actual fixtures](../tests/unit/test_relative.py) | Batch only; update/restore/merge rejected |
| `breadth.direction_counts` | [EQ035](stories/EQ-035_DELIVERY.md) | [actual fixtures](../tests/unit/test_breadth.py) | Batch only; update/restore/merge rejected |
| `breadth.above_sma_fraction` | [EQ035](stories/EQ-035_DELIVERY.md) | [actual fixtures](../tests/unit/test_breadth.py) | Batch only; update/restore/merge rejected |

[Integrated actual API tests](../tests/unit/test_r2_integration.py) combine all eight
history goldens on one seven-slot frame: 5/21, 122, 103, 365/3, 975/8, 4700/57,
122/9 and sqrt(476449/44791488). Future S6 mutations preserve whole results; extrema
also exclude the target. Missing S1 invalidates recursive prefixes but complete later
finite windows recover. Existing suites independently cover cutoff/known-at/action
admission, exact reference/baseline witnesses, partial bucket coverage and expected
universe exclusions. [Composition regressions](../tests/unit/test_composition.py)
retain configured currencies, source ownership and zero-evidence consistency.

## Prerequisites, review and compatibility

[BUG003](stories/BUG-003_DELIVERY.md) and [BUG004](stories/BUG-004_DELIVERY.md)
are accepted repaired prerequisites. Actual [equivalence fixtures](../tests/unit/test_equivalence.py),
[incremental fixtures](../tests/unit/test_incremental.py),
[state fixtures](../tests/unit/test_state.py),
[overflow fixtures](../tests/unit/test_state_float_overflow.py) and
[omission fixtures](../tests/unit/test_interval_omissions.py) requalify supported session
batch/update/restore/partition replay. R2 state modes remain unsupported.

All twelve stories EQ027–038 require their actual delivery receipts. EQ033's
[supplied-policy receipt](stories/EQ-033_DELIVERY.md), EQ036's
[composition receipt](stories/EQ-036_DELIVERY.md) and EQ038's
[comparison receipt](stories/EQ-038_DELIVERY.md) complement the numerical matrix.
EQ038 distinguishes five actually executed private Go EMA/ATR synthetic vectors from
source-only definitions; its public CI replays captured observations and public APIs.
No universal legacy parity or private source publication is claimed.

Pair 0.0.3a13 corrects two discovery dtypes and two breadth wire units to existing
producer representations. No math/algorithm/input/result/state schema change. Rebuild
cached registry definitions; replay exact-version state/caller contexts. The selected
separate local Codex reviewer must cover all sixteen kernels and the frozen final head;
review identity, execution and limitations will be recorded in the final delivery receipt.
Old stories retain original review provenance. Hosted activation remains unverified.

## Remaining acceptance gates

Full unit/reference/typing/boundary/import/registry/compatibility/license/documentation
checks; six exact-head CI checks; repeated four archives and both fresh local pairs;
guarded main merge with tree equality and both OS CI; both actual manifests and four
fresh installed Windows wheel/sdist pairs using both OS universal archives. Native Linux
execution is CI evidence. Final independently reviewed receipt and published archive
byte equality precede issue42 Done, all twelve Project Done records, E05 and milestone3
closure. R3 remains paused. The declared channel is experimental CI artifacts, with
retention/expiry in receipts; no stable release, tag, PyPI, provider readiness, source
authentication or throughput claim.

## EQ037 supplied proof validation correction

Daily and interval relative-volume consumers validate every supplied baseline proof
and target original-row event/known-at/completed interval before clipping output evidence.
Explicit contradictory claims for the same source ID/row reject consistently regardless
of retention. Coherent same-frame different-row reuse remains allowed. Output retention
bounds do not expand; absent proof is not reconstructed or source-authenticated.
Pair0.0.3a13 records this admission correction; formulas/schemas/capabilities unchanged.
