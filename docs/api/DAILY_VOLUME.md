# Daily volume and supplied relative volume

EQ031 / experimental0.0.3a5 / batch only. [Plan](../stories/EQ-031_PLAN.md),
[frozen mathematics](../features/CONTEXT_FORMULAS.md),
[synthetic installed example](../../examples/daily_volume.py).

`equity_features.volume.compute_daily_baseline(batch, config, *, context)` returns
an owned `VolumeBaseline`. Supply canonical DAILY rows and `HistoryContext` with
one certificate per governed slot. Prices are not required or used, but existing
canonical market `PriceUnit` metadata remains required and must match configuration.
Each selected prior slot needs a complete admitted volume, including valid zero.
Target volume never enters the exact checked decimal128 sum. Divide by required N,
not observed count. Output is Float64 shares plus exact numerator/count, single
typed result/quality and original source/revision/coverage/context/action bindings.

Config v1 accepts `period` default20, `quantity_basis` default `raw_shares`, and
`evidence_limit` default0. Reject unknown parameters. Window count equals period,
anchor is `prior_only`, and exact target/grid must match context. Too few governed
slots gives insufficient_history; a missing/incomplete selected slot gives
incomplete_coverage; absent input/fields or unavailable knowledge gives missing_input.
Null volume stays null; no gap compression or zero fill. Original known-at is kept
in reconstruction. Raw policy requires raw shares; adjusted volume needs matching
supplied action admission, including quantity basis. Dividends do not change shares
implicitly. Unsupported algorithms and incompatible units/revisions are typed errors.

`VolumeBaseline(result, config, context, numerator, denominator, quantity_basis)`
schema1 validates the single v1 shares projection, typed config/context/result
identity, daily source, exact nonnegative decimal128 sum/count and coverage. Available
count equals period/expected/observed, sum is within N*int64max. Unavailable operands
are both None. Available witness cannot contradict governed coverage/action readiness.
This validates supplied structure; it does not authenticate source truth.

`TargetVolume(entity, volume, known_at_ns, source, row_index, interval, coverage,
endpoint_mode, quantity_basis)` schema1 is a caller-supplied already aggregated
fact. Volume is nonnegative int64 or None; `source` is an original InputBinding;
`row_index` remains within its delivered count. Selected InputScope/Coverage certify
one actual row and retain original frame metadata/counts. Original frame scope,
if supplied, must contain and agree with the selected construction policy. An
uncertified selected row has complete=False; a missing fact is None.

`compute_relative_volume(target, baseline, config, *, context)` consumes the matching
supplied reference and target only. It never computes a missing baseline or aggregates
raw target events. Entity/grid/N/quantity basis/price metadata/adjustment/C/K/E/exact
config/context/current qualified backend version must agree. Target selected interval
starts at actual open. `completed_eod` reaches actual close and must be admitted at C;
`observed_prefix` ends exactly at C within session bounds and uses BAR source kind.
A DAILY row cannot be relabeled as a partial day. Coverage concerns this observed
prefix; the ratio is not a prediction of final daily volume. Auction policy remains
explicit and matches supplied session/source construction.

Available ratio is exact V*N/sum projected once to Float64 fraction. An admitted
zero baseline gives not_applicable/zero_denominator even0/0. Missing target/dependency
or unready dependency takes precedence over zero denominator; independent baseline
readiness remains in its retained result. Ratio quality counts two dependencies;
baseline quality separately counts N required slots. Target null/knowledge unavailable
gives missing_input; target incomplete/future completion gives incomplete_coverage.

Result metadata retains original source identities/revisions and typed derived
history context, baseline dependency and target certificate identities. Derived
bindings are assertions about dependencies, not observed market rows. Exactly equal
input ID/kind/metadata is retained once, allowing prior and target rows from the same
original daily frame; conflicting reused identity or role fails. Bounded evidence
keeps original row indices/known-at/bounds without changing source-frame counts.

Examples: prior [100,200,300] gives600/3=200shares; target500 gives5/2. Prior zero
volumes give available0; ratio is undefined. Finite-window recovery requires every
new selected slot to be admitted. No public history/volume accumulator, update,
restore or merge mode is supported. Session modes remain23update/restore22conditional
merge. Pair version changes require existing caller state replay/registry rebuilding.
No provider access, hidden normalization, performance, source authentication or
stable publication claim. Float64 results use declared rtol/atol1e-12; witnesses
retain exact sums/counts. Batch loops/transient input/evidence costs are explicit.
