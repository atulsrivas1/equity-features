# Session interval structure — experimental0.0.2a1

`compute_structure(batch, config, *, entity) -> FeatureResult` in equity_features.session
implements interval_ohlcv and interval_volume_share. Supply the EQ017 bar target,
ConfigSpec and one entity, plus named SessionSpec.intervals. See
[the runnable example](../../examples/session_structure.py). Each interval is within
actual session bounds; overlapping windows remain independent. A supplied bar crossing
either requested boundary raises bounds; there is no proration or silent clipping.

BatchMetadata.interval_coverage is an owned tuple of typed IntervalCoverage(name,
start_ns,end_ns,Coverage). Declaration bounds must equal the requested window and
lie within InputScope; observed equals the count of selected whole bars. Complete
target coverage never substitutes for absent window evidence. Missing windows are
incomplete; future configured windows are unready until their end<=C. Window-specific
knowledge is checked on its selected bars, without later unavailable rows poisoning
an independently complete earlier OHLCV. Volume share also requires a complete,
available full-target volume denominator; V=0 makes it not_applicable.

Result cells are immutable IntervalOHLCV and IntervalVolumeShares tables. Rows carry
IntervalSpec and nested QualityRow with the original EntityKey/feature ID and
window expected/observed counts, status and reasons. OHLCV row fields open_price,
high_price,low_price,close_price use float64 currency/share; volume is checked int64.
Covered empty windows have volume0 and null prices with available row quality.
Unavailable rows have null numerical fields. A missing source gives null table cells
and missing_input, distinct from observed empty windows.

Global available means every requested row is available. Global incomplete_coverage
retains a typed partial table, counts ready windows and exposes the distinct row
reasons (including knowledge/missing-field/zero-denominator readiness). Consumers
must inspect row quality; a partial table is not an all-window scalar value. Registry
metadata deliberately changes to the two concrete structured ValueTypes. The existing
breadth/scalar contracts remain intact; structured consistency/key checks reject
misleading aggregate quality. No JSON strings, invented feature IDs or untyped public
dictionary payloads represent results.

Arrow output is a copied list-of-struct value with nested interval UTCns, typed price/
volume/share fields and quality. Input interval declarations survive Arrow round trips
and result identity. For exact time inspection use the nested timestamp array cast
to int64, as existing input/evidence bridges do; converting UTC timestamps to Python
datetime can require host timezone data and loses nanoseconds. Tests check integer
nanoseconds, avoiding that conversion. No additional timezone/database dependency.

Reductions reuse the checked EQ017 arithmetic under derived interval bounds and
preserve original target construction/adjustment identity in the root result. This
reference path copies selected columns and performs one reduction per interval;
cost is O(windows*bars) plus materialization. No throughput claim. Precision remains
rtol/atol1e-12; counts compare exactly. Only these two batch flags are added; streaming,
restore and merge qualification remain separate stories. See [migration](../contracts/RESULTS.md)
and [delivery procedure](../BUILD_DELIVERY.md).

BUG003/0.0.2a10 preserves known closed-window omissions in incremental state,
rejects contradictory complete re-certification atomically and retains unaffected
window readiness. See [coverage/state policy](../api/INCREMENTAL.md).
