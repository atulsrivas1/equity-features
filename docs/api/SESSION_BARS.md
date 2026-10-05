# Session bars — experimental 0.0.2a0

`from equity_features.session import compute_bars`

`compute_bars(batch, config, *, entity, prior_close=None) -> FeatureResult` implements
the twelve bar/price IDs in [the accepted formulas](../features/SESSION_FORMULAS.md).
The batch is a CanonicalBatch of BAR kind or None for missing input; entity is one
EntityKey. Inputs and configuration are owned in-memory contracts. Nothing is fetched.
See [the runnable synthetic example](../../examples/session_bars.py).

ConfigSpec requires algorithm v1, explicit price unit and precisely one Parameter:
eligibility_policy (nonempty string). Other parameters fail. Its SessionSpec supplies
actual open/close and auction choices; C must satisfy open<C<=close. Its WindowSpec
supplies the governed predecessor for prior-close returns. C/K/E and reconstruction
remain the existing timing contract; input known-at is never inferred from bar end.

Executable batch metadata needs InputScope(open,C,eligibility_policy,opening,closing),
matching target auctions. This is the caller's assertion of construction/delivery
scope, not certification of source truth. Coverage.expected/observed/complete describe
that population; observed must equal this batch's row count. Missing intervals or
unproved completeness require incomplete coverage. Empty complete targets produce
volume/notional zero and null undefined prices/ratios. All supplied rows must have
the requested entity. Invalid order/overlap/bounds/OHLC/unit/basis raises ContractError.
No sorting, filling, proration, bar constituent filtering or adjustment occurs.

Each result has independent quality. Missing notional does not erase OHLC/volume
or close-weighted proxy; absent prior affects only gap/close-close. Missing volume
prevents defining the price-bearing population. Positive-volume supplied prices
must be positive/non-null/coherent; zero volume requires null OHLC. Missing fields
remain missing, while null malformed positive-volume supplied prices are errors.
Unavailable knowledge/coverage nulls affected published values; no observed subtotal
is mislabeled a complete feature. Full supplied input bindings retain original
scope/source/snapshot/known-at via caller-owned canonical batches; bounded result
evidence is empty in this family. Result metadata C distinguishes cutoff from EOD.

Prior close is exactly one DAILY observation in the immediately preceding governed
session, same instrument/namespace/price unit/adjustment evidence/eligibility and
auction construction. Its InputScope equals its completed daily interval and ends
at or before target open. Positive supplied close and complete coverage are required.
Unknown/future/null prior facts leave only dependent returns unavailable. A source
revision remains bound in its input metadata. Missing prior does not trigger a lookup.

OHLC and proxy outputs are float64 currency/share, ratios dimensionless fractions,
volume exact checked int64 shares. Actual notional is an exact decimal128 coefficient
in currency/10^price_scale; scale and currency are in the bound PriceUnit. It is never
close*volume. Exact Python integer reductions and Fraction arithmetic precede one
float conversion (absolute/relative tolerance 1e-12). Counts/sums check representation
bounds before publication; no int64 product wrapping. The Python backend materializes
column dictionaries and O(number of bars) index/value tuples; inputs already own
tuples. This is a checked reference implementation with no throughput or zero-copy
claim. Bounded incremental state and qualified numerical acceleration are separate
stories. Only batch capability is advertised for these twelve IDs.

Schema1 scalar results remain unchanged. InputScope is an additive schema1 envelope
field; R0 batches lacking it still construct/round-trip, but cannot be executed by
this API. Capability/registry digest and OHLC output dtype change intentionally in
0.0.2a0. Old registry snapshots fail the existing digest guard. Custom/R2 execution
and the SessionAccumulator API qualifies update/restore and conditional legal merge for these IDs. See [incremental modes](INCREMENTAL.md).
