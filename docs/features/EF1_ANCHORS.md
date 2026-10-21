# Exact supplied anchored totals — EQ167

Definitionv1, frozen ef1-contract1 anchor slice. This is the original supplied-anchor formula; it is not a copied breakout policy. [API and source-authoring status](../api/EF1_ANCHORS.md), [reviewed release contract](../ef1/CONTRACT.json).

Anchor start A and cutoff C define a positive-duration[A,C)scope; **A<C**. A=C is ContractError BOUNDS, distinct from a completely observed positive-duration interval containing zero eligible observations. Actual source REFERENCE evidence must bind the requested anchor definition/revision and be available under supplied known-at mode K; no current clock or source lookup occurs.

For eligible canonical trades, p is the positive integer price coefficient, q positive integer shares. Exact coefficient notional N=sum(p*q) and V=sum(q). In admitted BAR mode, N=sum(actual_notional), V=sum(volume), using actual compatible traded notional, never close*volume or typical price. Every positive-volume constituent must supply actual notional for N/V readiness. Declared zero-volume bars have null prices and zero/absent actual notional and contribute0. No averaging partition VWAPs.

For positive-volume bars, a supplied actual_notional must be positive independently of OHLC presence. Optional absent OHLC cannot turn a supplied nonpositive amount into valid traded notional. Missing amount still gives independent volume readiness; positive amount with absent OHLC remains a supported operand-only shape. LIB01 source-review correction and its original negative/zero/positive controls remain unexecuted at this stage.

Outputs are N as checked decimal128 coefficient at PriceUnit.scale, V as checked int64 shares, and VWAP=N/(V*10**scale) in full currency/share. Sums/products use wide exact integer arithmetic; reference division uses Fraction and converts once to float64. Exact totals compare exactly; float tolerance atol=rtol=1e-12. Overflow is a typed error, never wrapped arithmetic. N is not silently rounded or given a second scale.

Independent A01 fixture: scale2USD, eligible trades(1000,2) and(1300,1). N3300 represents USD33, V3shares, VWAP11USD/share. A compatible whole bar(open1000,high1300,low1000,close1300,V3,N3300) has the same result. Close*volume3900 would be wrong. If actual_notional is missing, V3 stays available while N/VWAP stay null.

Independent A02: actual complete scope[10,20), zero delivered eligible rows, actual available anchor proof. N0 and V0 are available, VWAPnull/not_applicable/zero_denominator. Absent delivery instead gives missing_input. Independent A03: A=C=20 always raises BOUNDS before any zero-width InputScope could be constructed.

Readiness is field-specific. Supplied proof knowledge/coverage and original market coverage/knowledge gate consuming outputs; missing quantity blocks price-bearing-population totals, missing trade price affects only notional/VWAP. Malformed order, unit, basis, wrong anchor hash or straddling bar boundaries is an error, not missingness. Ordinary trade timestamps t<C; completed bars end<=C. Explicit accepted regular-close auction construction remains distinct. No missing prices/observations are filled and no constituent is inferred from bar extrema.

Batch and full supplied replay only. No persistent recurrence, arbitrary partition merge, automatic reset, threshold-derived anchor, scanner/episode, provider capability or performance claim is delivered. Pure kernels retain requested/source identities and leave I/O, orchestration and publication outside this module. Independent authored tests are currently **unexecuted** under the resource reservation.
