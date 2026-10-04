# Session, bar and trade mathematical contract

Definition version: 1. Owner: EQ-002. Applies to the20IDs below from V1_SCOPE.md.
This is a specification and synthetic reference evidence, not production calculation code.

Consumers may use supported parameters or derive their own equations. A materially changed equation is a distinct namespaced custom feature, not this built-in ID. See the [customization design](../PACKAGE_DESIGN.md#consumer-customization-eq-093) and planned EQ-093 extension story; no registration API is implemented yet.

## Shared input, timing and quality rules

Caller supplies instrument/session identity, currency/price scale, integer share units, adjustment basis, eligibility-policy identity, session open/close, requested cutoff, auction inclusion and coverage evidence. Nothing is fetched. Fractional share quantities require a future explicit quantity-scale extension; v1 quantities are integer shares.

Ordinary trade timestamps are in [open, cutoff), with cutoff<=session close. A separately identified closing-auction record at exactly session close is admitted only when cutoff=close and closing-auction inclusion is explicitly true. Opening-auction records at open require explicit inclusion; ordinary records at open are admissible. Invalid/future/out-of-target admitted records raise validation errors rather than silently disappear. Provider conditions/cancels/corrections must already be normalized by the caller; eligibility=false records within the target may be excluded with counts/evidence. No vendor condition-list default is implied.

Bars represent nonoverlapping intervals [start,end), start>=open and end<=cutoff. They are ordered by start/end and uniquely identified. Caller certifies the same target/auction/eligibility policy for all bar constituents; OHLC bars cannot have auctions or individual trades removed afterward. A completed bar ending at close may represent a included closing auction only with declared compatible construction policy. Opaque, incompatible policy is rejected when the required guarantee is absent. Requested subwindows must align to whole bars; no OHLC/volume proration is permitted.

All eligible price-bearing bars have volume>0 and finite positive prices satisfying low<=open,close<=high. An observed zero-volume interval is admissible only with null OHLC and zero or absent actual notional; it contributes zero to volume, not invented prices. Provider bars with stale nonnull prices at zero volume need explicit caller normalization, not guessed price observations. Bars with positive volume and null prices are invalid for this contract. Eligible trades have finite price>0 and size>0. Zero/negative sizes, nonfinite prices, malformed identities and overlapping bars are errors. Duplicate admitted event IDs or ambiguous trade tie order are errors; no automatic sort/dedup. Trade order is the total key(event_ns, caller order key); top-K ties use this ascending key and then unique event ID if needed.

Prices use exact scaled integers at the mathematical boundary (p=price_ticks/10^scale); amounts are currency*shares. Aggregated notional must be real traded notional, compatible with quantity/price adjustment and eligibility. For a positive-volume bar, low*volume<=actual_notional<=high*volume when notional is supplied on this exact compatible basis. No guessed close*volume notional. Arbitrary-precision exact reference arithmetic checks examples; production kernels must use checked sufficiently wide accumulation, raising on unrepresentable counts/products/sums rather than wrapping. Contract details are finalized in EQ-011/014.

Ratio outputs are dimensionless fractions, not percentages:0.03 means3%. Price outputs are currency/share; share totals integer; count integer; mean size shares/trade; amount currency. Final float64 ratios/prices use rtol1e-12 and atol1e-12 in their declared units against exact rational expectations. Integer totals and retained exact notional representations compare exactly. No implicit rounding before ratios. Broader backend tolerance changes need an algorithm-version decision.

Missing input produces null values with missing_input, not zeros. For an observed, fully covered target containing no eligible events, counts/volume/notional totals are zero; undefined prices/ratios are null with not_applicable and reason no_eligible_observations/zero_denominator. Actual bar notional is null/missing_input when any positive-volume constituent lacks it; other independent features are unaffected. Flat range makes close-location undefined, not0.5 or0.

Coverage is per field/window: a missing expected interval or unproved complete event delivery yields incomplete_coverage and null published feature value. Optional evidence can retain observed arithmetic; it is not a complete feature. A caller-requested cutoff before close can have complete coverage of that shorter range and valid cutoff features, but metadata must mark scope=cutoff, not completed EOD. For EOD, cutoff=close plus declared complete policy/coverage is required. Computable values do not imply causal availability; actual known-at and simulation eligibility remain explicit supplied metadata. No feature uses a later bar, event or future prior-close revision.

Prior close P must be positive, known under supplied availability policy, and bound to the governed immediately preceding session and compatible instrument/currency/adjustment basis. If absent, gap/close-close are missing_input; if incompatible/unavailable, they are null with an explicit reason. Other session values remain independent. EQ-006 owns action/availability policy; this contract does not execute adjustment or invent historical trust.

## Notation and worked fixture

B+ is the ordered price-bearing eligible bars; B includes observed zero-volume intervals. T is the eligible normalized trades. O,H,L,C are aggregated price-bearing OHLC, V=sum bar volume, N=actual bar notional sum, P=compatible prior close. For configured window W, B_W contains whole bars inside W; V_W is their volume. All definitions inherit validation/coverage above.

Fixture b1:O100,H103,L99,C102,V200,N20300; b2:O102,H104,L101,C103,V300,N30900. Both are complete, compatible, consecutive intervals. Prior close P98. First/last windows select b1/b2 respectively. Prices are currency/share and quantities shares, with illustrative scale0.

Fixture t1:p100,q2; t2:p102,q3; t3:p101,q5, in that order with unique IDs. K2 selects t3 then t2. Independent rational expected results are stored in tests/fixtures/session_math/golden.json and explained in its README.

## Exact definitions

| Feature ID | Equation / selection | Units | Worked expectation |
| --- | --- | --- | --- |
| session.bar.open | O=open of first B+ | currency/share | 100 |
| session.bar.high | H=max(high over B+) | currency/share | 104 |
| session.bar.low | L=min(low over B+) | currency/share | 99 |
| session.bar.close | C=close of last B+ | currency/share | 103 |
| session.bar.volume | V=sum(volume over B) | shares | 500 |
| session.bar.notional | N=sum(actual_notional over B), only if all positive-volume entries supply it | currency | 51200 |
| session.bar.close_weighted_price | sum(close_i*volume_i over B+)/V; undefined if V=0 | currency/share, proxy | 513/5 =102.6 |
| session.price.open_close_return | C/O-1 | fraction | 3/100 |
| session.price.range_fraction | (H-L)/C | fraction | 5/103 |
| session.price.close_location | (C-L)/(H-L); null if H=L | fraction | 4/5 |
| session.price.overnight_gap | O/P-1, compatible P required | fraction | 1/49 |
| session.price.close_close_return | C/P-1, compatible P required | fraction | 5/98 |
| session.structure.interval_ohlcv | Same first/max/min/last/sum rules within B_W; full window coverage required | structured prices/shares | First W:(100,103,99,102,200); last W:(102,104,101,103,300) |
| session.structure.interval_volume_share | V_W/V, window and target coverage required; null if V=0 | fraction | First2/5, last3/5 |
| session.trade.count | n=len(T) | trades | 3 |
| session.trade.volume | Q=sum(q_j over T) | shares | 10 |
| session.trade.notional | A=sum(p_j*q_j over T) | currency | 1011 |
| session.trade.vwap | A/Q, null if Q=0 | currency/share | 1011/10 |
| session.trade.mean_size | Q/n, null if n=0 | shares/trade | 10/3 |
| session.trade.top_k | First min(K,n) sorted by(-size, event_ns, order_key, event_id), K integer>=1 | bounded trade rows | K2:[t3(size5),t2(size3)] |

If B+ is empty, bar OHLC and all price-based functions are null. Interval OHLCV still returns observed volume0 with null prices for a covered empty window. Top-K on a covered empty trade set is an empty list, not null; missing/incomplete trade input produces null evidence. No use of prices from previous sessions to fill empty intervals. A trade count is a normalized effective-record count; a provider event already aggregating multiple trades must declare that semantic and cannot pretend to represent individual trades without an appropriate contract.

## Batch/state and reduction semantics

Volume/notional/count use associative exact sums until checked representation limits. Bar open/close merge needs ordered disjoint ranges and earliest/latest bounds; highs/lows combine only price-bearing observations. Interval accumulators maintain separate whole-window aggregates. Mean/proxy/VWAP are computed from totals, never averages of partition ratios. Top-K merges by a stable global key over disjoint compatible event sets. Overlapping or duplicate partitions are invalid; row-conservation/identity evidence is caller-validated. Missing coverage/notional propagates independently across partitions.

Snapshots only cover consumed events and declared coverage at the requested cutoff. A state that consumed a later event cannot retrospectively snapshot an earlier cutoff. Corrections require explicit replay/rebuild. State version/schema/config/policy identity and bounds are required for restore compatibility; actual APIs/tests are EQ-023–025. No arbitrary time-state merge is promised beyond explicitly compatible bar/trade reductions.

## Acceptance evidence and ownership boundaries

The example checker validates exact golden arithmetic, feature-ID coverage, boundary scenarios and predicate policies using synthetic inputs. It is a reference verifier, not the production API or evidence that package kernels, performance or provider data are correct. Fixture coverage and command are documented alongside fixtures. EQ-006 must provide trustworthy compatible prior-close/action/availability inputs; until then these two formulas are mathematically defined but reference readiness may remain unavailable. EQ-011–016 implement contract encodings without changing this mathematics silently.
