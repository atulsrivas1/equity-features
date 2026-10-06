# Individual bucket volume baselines

EQ032 / experimental0.0.3a6 / batch only. [Pre-code plan](../stories/EQ-032_PLAN.md),
[frozen mathematics](../features/CONTEXT_FORMULAS.md),
[synthetic installed example](../../examples/interval_volume.py).

`VolumeBucket(name, start_offset_ns, end_offset_ns, grid_version)` schema1 supplies
an explicit half-open bucket relative to each actual session open. Offsets are
bounded nonnegative int64, start<end. Exact UTC bounds are checked for int64 overflow.
`BucketContext(entity, grid_version, sessions, bucket, slot_coverage,
action_admission=None)` schema1 owns a unique ordered namespaced grid and one
bucket certificate per slot. Grid versions agree; target belongs to grid. Daily
coverage is not a substitute for per-bucket coverage. An actual session ending
before bucket end must retain observed0/incomplete coverage, including early close.

`equity_features.buckets.compute_interval_baseline(batch, config, *, context)`
returns `IntervalBaseline` for ONE declared bucket. Supply already aggregated
canonical BAR bucket rows, one exact row per eligible session/bucket. No smaller-bar
aggregation, calendar lookup, sorting or gap compression occurs. Original frame
counts, scope, price metadata, adjustment, row index and revision are preserved.
Every structural row must match its exact bucket bounds and declared instrument/
grid/order. Reject rows for ineligible early-close buckets and contradicting
presence certificates. Canonical PriceUnit metadata is required without price
fields; volume alone enters arithmetic.

Config v1 accepts period(default20), quantity_basis(defaultraw_shares), evidence_limit
(default0). Window is prior_only/countN with exact target/grid. Each of N required
prior slots must have admitted complete volume; denominator remains N. Too few
governed slots gives insufficient_history; missing/incomplete/null/early-close
selected bucket gives incomplete_coverage; absent dataset/field or unavailable
knowledge gives missing_input. Early-close exclusion reason is ineligible; no
phantom source row is created. Covered zero is valid. Missing outside the selected
window does not block finite recovery. Original known-at is retained in reconstruction.
Adjusted shares require compatible supplied action admission; no factor is applied
again and no dividend quantity convention is inferred.

`IntervalBaseline(result, config, context, numerator, denominator, quantity_basis)`
schema1 pairs a single standard Float64 shares result with exact checked nonnegative
decimal128 sum/count. Available count matches required N/expected/observed and mean
projection; unavailable operands are None. Contradictory coverage/action claims
are rejected. Source/context/config/availability and qualified consumer version
are checked. This is structural admission, not source authentication.

`BucketVolume(entity, volume, known_at_ns, source, row_index, interval, coverage,
bucket, quantity_basis)` schema1 supplies target volume, nonnegative int64 or None.
Source is an original BAR InputBinding; selected row index stays within original
delivered count, certificate expects one actual row. Selected InputScope must
agree with original scope/construction policy if supplied. A partial positive
prefix may be represented explicitly for unready coverage; it never counts as a
complete bucket. Bounds start at exact bucket start and end<=bucket end/actual
session close; shifted/extended bounds are errors.

`compute_interval_relative_volume(target, baseline, config, *, context)` consumes
the matching supplied reference without computing a missing mean. Exact bucket/
grid/entity/config/unit/quantity/adjustment/C/K/E/context/current qualified backend
must agree. Full target bucket ending<=C and completely covered can be ready, even
before whole-session close. Partial target gives incomplete_coverage; a full
bucket ending>C gives future_market/incomplete_coverage. Target bucket excluded
by early close gives ineligible/incomplete_coverage without fabricating a row;
missing target for an eligible bucket gives missing_input. Unknown/future knowledge
or null volume gives missing_input. Independent baseline readiness is preserved.

Available ratio is exact V*N/sum projected once to Float64 fraction. Admitted zero
baseline gives not_applicable/zero_denominator even0/0; unready target/dependency
precedes zero handling. Ratio quality counts two dependencies; baseline retains
N-slot quality. Derived context/reference/certificate bindings identify supplied
assertions, not observed market data. Identical original ID/kind/metadata is retained
once; conflicting reused identities or roles fail. Bounded evidence keeps original
row indices/known-at/bounds.

Call each bucket independently and retain typed results separately. Existing
FeatureResult Float64 schemas/units remain; there is no untyped parallel output
dictionary or cumulative time-of-day reinterpretation. Example prior10/20/30 gives
20shares; target50 gives5/2. A missing late bucket after early close gives observed2/
expected3 and null mean, while the fully covered morning bucket stays ready.
Original story wording about observed-day denominators refers to retained coverage
evidence: frozen EQ005 forbids reducing N to observed count.

Pair0.0.3a6 adds two batch IDs (35total), with false bucket/history update/restore/
merge modes. Session modes remain23update/restore22conditional merge. Existing
canonical/result/state schemas and39equations remain; new bucket companions are
schema1. Exact-version caller state/registry replay/rebuild applies. No provider,
hidden normalization, source truth, performance/public accumulator or stable
publication claim. Float64 tolerances rtol/atol1e-12; witnesses keep exact sums.
Batch loops/transient input/identity/evidence costs are explicit.
