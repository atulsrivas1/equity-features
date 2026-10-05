# EQ-019 — trade aggregates plan

Prepared 2026-10-05 before coding; issue23, epic20, R1. Confirmed8points.
Prerequisites EQ017/018 are Done, latest mainc3faac1ae34c5c3470313c6064210e37ce1cd90d
(0.0.2a1),223units/123references and actual OS bundle/fourfresh install receipts.
Live EQ019 Ready; deferred PR120 is the only open unrelated PR. Preserve PR151's
R3 EQ095 roadmap and94-story planning. One active story; author self-review plus CI.

## Interface and mathematics

`equity_features.session.trades.compute_trades(batch: CanonicalBatch | None,
config: ConfigSpec, *, entity: EntityKey) -> FeatureResult` implements exactly five
session.trade aggregate IDs. Reuse supplied configuration/price units, target
InputScope, eligibility-policy/auction construction and C/K/E admission from EQ017.
Only eligibility_policy Parameter is supported. One requested instrument/session;
do not silently sort, deduplicate, filter invalid bounds or normalize conditions.
The existing semantic validator checks order/IDs, auctions and supplied payloads.

Eligible=True rows define T. Count=len(T), Q=sum(size), A=sum(price*size),
VWAP=A/(Q*10^price_scale), mean_size=Q/count. Count and volume are checked int64;
notional is checked decimal128 price-scale coefficient; Fraction precedes float64
ratio conversion, tolerance1e-12. Actual trades, never bar close*volume, determine
notional/VWAP. Python wide products avoid int64 wrapping; no throughput claim.

Independent readiness: count needs identity/time/eligibility only; absent size blocks
volume/notional/VWAP/mean_size, absent price blocks only notional/VWAP. Supplied
null/nonpositive eligible payloads remain malformed per the existing contract.
Ineligible normalized records within target contribute no arithmetic; preserve raw
delivery coverage. Unknown/future knowledge in supplied records blocks causal
published metrics rather than silently produce a complete filtered population.
Partial delivery nulls all affected outputs. Quality expected/observed counts refer
to delivered raw rows; feature values count eligible observations separately.
Observed fully covered empty/all-ineligible populations have count/Q/A0, undefined
VWAP/mean_size null/not_applicable. Absent batch gives missing_input, never zeros.

Advertise only these five new batch flags (19 total implemented IDs), evolve notional
unit metadata explicitly, and release both distributions as0.0.2a2. Other execution
modes/top-K/quotes/R2/custom remain false. Accumulator-ready exact reductions use
fixed totals/availability flags; bounded update/restore/merge implementation belongs
to later R1 stories, not an untested promise in this change.

## Independent verification and documentation

Hand fixture prices100/102/101 and sizes2/3/5: count3, volume10, notional1011,
VWAP101.1, mean_size10/3. Test scaled prices, wide products, volume overflow,
ineligible/empty/missing/null, independent absent payloads, duplicate IDs/equal-time
order, out-of-target and auction boundaries, coverage/source/unit/basis/identity,
C/K/E/reconstruction and provenance. Preserve all R0/bar/structure regressions
and123formula references; installed wheels/sdists execute tests and new example.

Update API/example, registry/unit migration, package docs/changelog and continuity,
including EQ018 receipt. Draft PR, actual author review, Test, typing/purity/import/
license/compatibility/reference/repeat-build/clean-install gates, six exact-head
checks, squash merge, published bytes/main OS CI and actual bundles/fourfresh
installations before Released/Done. Exit: all five callable with truthful quality
and exact source/version delivery evidence; only then pull EQ020.
