# Sampled quote summaries — experimental0.0.2a4

`equity_features.session.compute_quotes(batch, config, *, entity)` returns
`session.quote.sampled_spread` and `session.quote.state_counts`. Use explicit
eligibility_policy and observation_limit integer0..10000 parameters. Input is a
caller-owned normalized full quote state; caller reconstructs deltas/withdrawals
and excludes observations before canonical admission. Quote schema has no
eligibility column. Optional sizes do not enter these equations.

Supply exact unit/basis, one entity, scope[open,C), known delivery coverage,
source snapshot/mapping, unique ordered events and C/K/E availability evidence.
No quote endpoint/closing-auction exception. Absent side fields on nonempty input
are missing_input; supplied null or nonpositive sides are representable invalid
market states. Missing/incomplete/unavailable-knowledge publications are null.

A positive bid below ask is normal; equality locked; bid above ask crossed.
Valid=normal+locked. Invalid means null/nonpositive side. Counts satisfy
total=normal+locked+crossed+invalid exactly and use checked int64. Covered empty
counts are available0. Qs (`trade_snapshot`) means are snapshot weighted; Qc
(`continuous`) means are update weighted. Sampling remains in metadata and the
sampled cell; neither summary implies time coverage or pooling equivalence.

For valid rows, spread=(ask-bid)/10^scale and bps=20000*(ask-bid)/(ask+bid).
Midpoint is never rounded. Checked wide coefficient sums and Fraction convert
mean spread once. Individual bps use exact wide fractions before float64;
compensated summation then divides by valid count. Final means use absolute and
relative tolerance1e-12. Bps is a mean of individual ratios, never a ratio of
means. Crossed signed diagnostics are excluded from means; locked contributes0.
No quantiles, variance or size weighting belongs to these frozen feature IDs.

`QuoteStateCounts(normal,locked,crossed,invalid)` exposes derived total/valid.
`SampledSpread(sampling,total,valid,mean_spread,mean_bps,observation_limit,rows)`
contains immutable typed first min(limit,total) `QuoteObservation` diagnostics
(input/event IDs, UTCns/order/known-at, original bid/ask, state and signed spread/
bps). Invalid diagnostics are null. `truncated` explicitly says rows were omitted;
limit0 retains none. Means always use the whole admitted valid population.
Matching bounded EvidenceRows bind every retained observation. If valid=0,
means are null/not_applicable while the typed diagnostic cell remains present;
counts remain independently available. This is a narrow structured-result
exception checked against valid denominator and complete population quality.

Schema1 envelopes remain; new quote_state_counts/sampled_spread dtypes and
registry digest require consumer handling. Arrow copies typed struct/list cells,
int64 original prices and UTCns timestamps with separate quality/evidence tables.
Summary retention is fixed counters, checked exact spread sum and compensated
bps pair plus bounded diagnostics. Input canonical ownership/validation and Arrow
copies scale with supplied rows. R1 qualifies batch/update/restore and conditional legal merge through
[SessionAccumulator](INCREMENTAL.md). Event-weighted summaries do not claim
duration coverage or measured throughput. [Example](../../examples/session_quotes.py).
