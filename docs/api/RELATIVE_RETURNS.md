# Supplied benchmark and sector comparisons

EQ034 / experimental0.0.3a7 / batch only. [Plan](../stories/EQ-034_PLAN.md),
[mathematics](../features/CONTEXT_FORMULAS.md),
[synthetic installed example](../../examples/relative_returns.py).

`ReturnReference(result, config, context)` schema1 owns a single v1 `history.return`
Float64 fraction result and its actual ConfigSpec/HistoryContext. Constructor
checks entity/target/namespace/horizon/grid/config/context/availability/price metadata/
basis/source/algorithm/coverage/completion/action proof. Available source frame must
contain at least h+1 closes; required slots and completed target are certified. An
unavailable reference preserves its typed status/reasons. Available scalar projection is within positive-int64-price bounds [-1,float(int64max-1)]; lower -1 permits legitimate Float64 rounding near total loss. This validates structure,
not source truth. Producer is the existing supplied history API; the relative API
never recomputes a missing return. Consumer requires current qualified backend version.

`SectorBenchmark(sector_id, entity)` schema1 explicitly maps a sector label to its
benchmark instrument/target. `RelativeSpec(entity, market_benchmark=None,
sector_benchmark=None, membership_effective_ns=None)` schema1 owns output symbol
and expected benchmarks. Benchmark targets agree. Sector membership point is
explicit within target [open,close), <=C; no inferred opening/closing timestamp.
Sector label is not assumed to equal benchmark ticker. Versioned identity retains
the declaration, including optional fields.

`equity_features.relative.compute_relative(symbol, market, sector, membership,
config, *, spec, feature_ids)` consumes requested `relative.market_return` and/or
`relative.sector_return` only. Inputs are ReturnReference or None and supplied
ClassificationAdmission or None. Parent Config v1 requires positive explicit period
and optional evidence_limit(default0), count h+1/completed_eod, actual target/cutoff,
canonical PriceUnit and supported adjustment policy. Child configs retain their
actual identities/evidence bounds; parent does not forge a common child digest.
Align horizon/governed IDs/exact selected sessions/grid version/endpoint mode/
price scale/currency/basis/policy/anchor/C-K-E. Parent adjustment snapshot binds the
symbol; benchmark action snapshots may differ by instrument under the same policy/
anchor, and remain separately retained. No FX, interpolation or namespace mapping:
v1 uses the same explicitly supplied namespaced grid. Incompatibility is a typed error.

Sector ClassificationAdmission binds symbol, sector_membership kind, exact selected
point, parent config digest and availability. Available text equals explicit
SectorBenchmark.sector_id; sector return entity equals its mapped benchmark entity.
Missing/unready membership affects sector quality only; missing market can coexist
with ready sector. Requested malformed dependencies are typed errors. Unrequested
optional dependencies are not consumed and cannot change another result's value/
readiness; declared specification identity may change. Requesting a configured sector
comparison requires its explicit valid point. An absent benchmark configuration with
no supplied benchmark stays missing, while supplying an undeclared benchmark fails.

Available values are `r_symbol-r_market` and `r_symbol-r_sector`, Float64 fractions,
with rtol/atol1e-12 in fraction units. They are arithmetic spreads of supplied
scalars, not gross-return ratios or stored percentage points. Market quality counts
two dependencies; sector counts three including membership. Unready supplied
operands retain status/reasons before arithmetic; no hidden acquisition or fallback.

Metadata keeps parent config plus actual component source/revision/context/return/
membership identities. Derived dependency declarations are not market observations.
Roles are prefixed; exact ID/kind/metadata deduplicates once, conflicting reused
identity fails. Current history producer owns one instrument per normalized DAILY
frame, so different instruments need distinct frame IDs. Shared reference tables
can retain the same original metadata. Bounded evidence maps to output symbol/
comparison while preserving original source row/event/known-at/bounds; full child
reference identity retains original instrument association. Identical original-row
proof deduplicates, conflicting supplied proof fails even when the output evidence
limit is zero or already full. The transient validation map examines all supplied
proof; the declared bound limits retained output evidence, not validation work. No fictitious benchmark price row or
evidence attached to a nonexistent output entity. Reconstruction keeps original
known-at timestamps.

Example100->110 versus200->210 gives1/10-1/20=1/20; mapped sector300->321 gives
1/10-7/100=3/100. Membership absence leaves the market spread ready. Horizons
1/5/20/60/252, missing/null/warm-up/cutoffs/membership intervals/adjustment snapshots/
source revisions/ownership/malformed proofs and evidence are independently tested.
Future/unrequested data cannot change an admitted value.

Pair0.0.3a7 adds two batch IDs (37total), with false relative/history/bucket state
modes. Session remains23update/restore22conditional merge. Existing schemas and
39equations unchanged; new companions schema1. Caller exact-version state replay/
registry rebuilding applies. No source authentication, hidden calculation, provider,
private copy, performance/public accumulator or stable publication claim.
