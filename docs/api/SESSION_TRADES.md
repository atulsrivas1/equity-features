# Trade aggregates — experimental0.0.2a2

`from equity_features.session import compute_trades`

`compute_trades(batch, config, *, entity) -> FeatureResult` implements count, volume,
notional, vwap and mean_size from the [accepted formulas](../features/SESSION_FORMULAS.md).
Supply one CanonicalBatch of TRADE kind (or None for absent source), ConfigSpec and
EntityKey. [The runnable example](../../examples/session_trades.py) uses synthetic
prices100/102/101 and sizes2/3/5: count3, volume10, notional1011, VWAP101.1 and
mean size10/3. No bar-derived proxy enters trade notional/VWAP.

The target is InputScope(open,C,eligibility_policy,opening,closing), with a matching
nonempty eligibility_policy Parameter and actual session auction choices. Only that
parameter is supported here. Namespace, instrument/session, currency/scale and exact
adjustment evidence must match configuration. Coverage.observed equals this batch's
raw delivered rows; complete requires known matching expected count. Caller certifies
source truth/completeness, normalized eligibility and original known-at/revision.
The API checks declarations, representations, order/IDs, bounds and policy, without
sorting, deduplication, fetching, adjustment or guessing vendor conditions.

Eligible=True rows define the arithmetic population. Ineligible records within target
are excluded from counts/size/products, while raw delivery coverage remains explicit.
Ordinary trades use open<=event<C. Only explicitly identified closing auction at
actual close with C=close and configured inclusion has the endpoint exception.
Out-of-target records, even ineligible ones, raise typed errors. Supplied eligible
prices/sizes must be positive/non-null; malformed payloads are errors. Absent payload
fields are distinct: missing size leaves count available, missing price leaves count,
volume and mean_size available. Count never requires an invented price.

Unknown/future knowledge in supplied facts prevents causal published aggregates; it
is not silently filtered into a complete population. Partial coverage gives null
affected values/incomplete_coverage. Reconstruction permits later/unknown knowledge
with the existing separate configuration identity. Observed fully covered empty or
all-ineligible populations give count/volume/notional0; undefined VWAP/mean_size are
null/not_applicable. Missing source gives null/missing_input, not zeros. Quality
expected/observed counts measure raw delivery, while count values measure eligible
trades. Result input bindings retain exact supplied source/snapshot/mapping/input,
scope, units, adjustment, sampling and coverage identities; C/K/E/config are bound.
Row evidence is empty in this aggregate API, rather than unbounded retained input.

Counts and volume are checked int64. Notional is a checked decimal128 coefficient
in currency/10^price_scale; the bound PriceUnit supplies currency and scale. Exact
Python integer products/sums precede Fraction to float64 conversion for VWAP and
mean_size, with rtol/atol1e-12. No int64 wrapping or price rounding. Overflow is a
typed failure, not a null/zero result. This checked backend materializes column/index
tuples proportional to batch size; it has no measured throughput or zero-copy claim.

Only five trade batch flags are added (19 total implemented bar/structure/trade IDs).
Top-K, quotes, update/restore/merge and custom/R2 execution remain unsupported.
Notional registry unit/type metadata migrates explicitly to the scaled coefficient;
registry digest and both distribution versions advance to0.0.2a2. State APIs and
bounded merge/restore evidence belong to later R1 stories. Delivery uses successful
main artifacts plus actual downloaded/install verification, never source merge alone.
