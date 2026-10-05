# EQ031 daily volume baseline and supplied relative volume pre-code plan

Issue36/E05#31/R2;5 provisional complexity points. Pre-code design prepared while final EQ030 receipt gates run; EQ027 prerequisite Done. No calculation implementation starts until EQ030 is Done.

Prior N>=1/default20 governed complete daily volumes exclude target and use exact
sum/N, shares. Every selected slot is required; no skip/observed denominator.
Covered zeros yield available0baseline. Target volume divided by that matching
baseline gives dimensionless relative volume, including explicitly supplied
intraday observed prefix. Zero baseline yields not_applicable/zero_denominator
even0/0; missing baseline/target remains unavailable, never0/forecast.

Define owned VolumeBaseline(result,config,context,numerator,denominator,quantity_basis)
schema1: single baseline.daily_volume Float64 FeatureResult, exact nonnegative
decimal128 volume sum/positive int64 count, matching result projection/quality/
configuration/context binding. Unavailable exact operands None. This is structural
supplied dependency admission, not authenticated data. compute_daily_baseline
produces this reference from a canonical daily volume-only history/ConfigSpec/
HistoryContext. No price data required, though provided price unit/basis must agree.
WindowSpec.count=N/prior_only; explicit period and quantity_basis(raw_shares or
split_shares) plus optional evidence_limit. Raw policy permits raw_shares only;
adjusted history requires compatible action admission with the same quantity basis,
config digest/C/K/E/output adjustment. Dividends never scale quantities implicitly.

Define owned TargetVolume(entity,volume,known_at_ns,source,row_index,interval,
coverage,endpoint_mode,quantity_basis), with supplied InputBinding, original row
index and selected-row InputScope/Coverage. Volume is
nonnegative int64 or None; kind BAR/DAILY, observed/source count bounds and typed
scope proof retained. The selected certificate expects one actual observed row;
complete=False marks uncertified target coverage, while a null field stays distinct.
Mode completed_eod or observed_prefix is explicit. Producer
caller supplies an already aggregated volume fact, never a hidden aggregation.
Observed-prefix facts use BAR-kind normalized source rows; DAILY-kind rows cannot
be relabeled as a partial-day fact. EOD facts may use a full-session BAR or DAILY.
Target selected interval starts at target open, ends at its consumed cutoff;
completed_eod reaches session close, prefix ends at evaluation market cutoff and
is complete for that observed prefix. If original source-frame scope is supplied,
it must contain that interval; original frame counts/bounds/revision remain rather
than being rewritten to a fake one-row source. Original known-at follows C/K/E policy.
Missing/uncovered target yields null with reason. This is not a forecast of final
volume and does not assert a forming day is completed. No source authentication.

compute_relative_volume(target,baseline,config,*,context) consumes supplied
VolumeBaseline only; never calculates a missing dependency. Match target/entity/
namespace/grid/N/window/quantity basis/adjustment/C/K/E/exact config/context identity and
retained data/reference revisions. Scalar ratio uses exact target*count/sum before
Float64. Retain original baseline/source/context/action/target bindings, deduplicating
only exactly identical source identities/metadata; conflicting reused identity
is an error. Evidence binds original selected rows/target index with bounded totals.
Absent dependency or optional target never erases an independent baseline result.
Add a derived baseline_reference binding whose identity hashes the supplied result, config, context and exact operands; it is a dependency identity, not an observed source row. Target certificate identity similarly binds the supplied target fact and selected scope. Source binding roles are retained unless an identical input ID/kind/metadata is already present; differing roles alone do not create a second observation. Reject conflicting reused source IDs.
Ratio quality counts two supplied dependencies; unavailable target/dependency
propagates first, while an admitted zero baseline gives not_applicable. The retained
baseline quality continues to expose its Nrequired/observed prior-slot counts.

Actual API fixtures: [100,200,300] mean200/target500 gives5/2, target/future mutation
leaves baseline unchanged; defaults20/N1/wide sums/finite recovery/missing/null rows;
coveredzero baseline/zero target/no0fill; intraday partial versus complete-prefix
and EOD bounds; known-at equality/unknown/future/reconstruction; revision/namespace/
entity/grid/quantity/basis/unit/config conflicts; unavailable baseline/target;
original row bounds/evidence and immutable/malformed exact witness; false modes.
Independent expected rational values, preserve previous485units/123references.

Pair0.0.3a5 adds two batch flags (33total), existing schemas/session23update/
restore22merge and39equations unchanged; exact-version state/registry rules require
replay/rebuild. Batch-only, no public volume accumulator. No hidden dependency,
fetching/provider/performance/private copy/stable/tag/PyPI. Public math/API/contracts/
version/registry/example/changelog/lesson/continuity with pre-code commit; author
self-review+CI accurately labeled. Full local/exact-head/repeated archives/fresh
pairs/SIXchecks/guarded merge/main exact source/docs/bothOS actual bundles/FOURfresh
pairs/final receipt/main byte equality before eight-stage Done. R3 paused.

Configuration admission defaults period20 only when absent, quantity_basis raw_shares only when absent; reject unknown parameters and require WindowSpec.count equal effective period/prior_only and exact governed grid/session. Evidence_limit defaults0. PriceUnit may be None for volume-only input, but a supplied one must match all original data bindings. Action-admission quantity_basis must equal selected basis even for raw policy. Exact witness binds result entity, namespace, session, availability, configuration digest and derived history-context identity; available daily input binding must exist. The numerator is nonnegative decimal128 and <=N*int64max; denominator equals configured period and quality expected/observed. Unavailable witness carries no operands. Single-result algorithm/backend compatibility is checked; schema1 does not authenticate provenance.
