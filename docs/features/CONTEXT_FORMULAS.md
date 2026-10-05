# Baseline, relative and breadth formulas

EQ-005, formula version 1. Eight IDs from V1_SCOPE.md. EQ031 daily baseline/relative volume implementation is in source qualification; remaining contextual kernels are planned. [Daily API](../api/DAILY_VOLUME.md).
Inputs are synthetic or caller-supplied in memory. Apply HISTORICAL_FORMULAS.md's
governed session grid and EQ-006 admission policy. Prices are compatible positive
scaled integers; volumes are nonnegative integers, summed in overflow-safe wide
arithmetic. Missing observations are null, never zero. No sorting or gap compression.

## Baselines

For target governed session t and positive integer N (default 20), W={t-N,…,t-1}.
`baseline.daily_volume` is B=sum(V[j] for j in W)/N, in shares. Target is excluded;
future sessions cannot change B. Every slot must have complete, admitted volume.
Fewer than N governed prior slots → insufficient_history; an existing missing slot
or incomplete volume → incomplete_coverage; absent dataset → missing_input.
Observed and expected session counts accompany readiness. B=0 is an available value.

`baseline.relative_volume` is V[t]/B, dimensionless, for supplied admitted target
volume and the matching baseline identity (instrument, grid, N, unit/basis, t).
Target may be observed intraday: record its cutoff/completeness explicitly; never
label an intraday/full-day ratio a forecast of closing volume. Null target yields
missing_input; B=0 yields not_applicable with reason zero_denominator, even for 0/0.

`baseline.interval_volume` repeats B independently for each caller-defined bucket
b on W: B[b]=sum(V[j,b])/N. Buckets are half-open [start,end) relative to session
open, identified by grid version and exact offsets. A historical session must
contain the entire bucket, and its supplied observation coverage must be complete.
An early close before bucket end is an absent eligible observation, never volume 0;
it makes that bucket incomplete_coverage. Other fully covered buckets remain usable.
Do not divide by the smaller observed count or mix differing bucket durations.
Record expected N, observed count and excluded-session reasons per bucket.

`baseline.interval_relative_volume` is V[t,b]/B[b]. Exact bucket/grid/unit/basis
identity must match. Target bucket must be fully elapsed and covered at its supplied
cutoff; partial target bucket → incomplete_coverage. Zero denominator and missing
rules follow daily relative volume. These are individual bucket ratios, not a
cumulative time-of-day feature. Supplied volume 0 in a covered bucket is valid.

Example N=3: prior volumes [100,200,300] give B=200; target 500 gives 5/2. Target
9000 still gives B=200. Prior [0,0,0] gives available B=0 and undefined ratio.
Bucket volumes [10,20,30] give 20; losing one bucket on an early close leaves
observed=2/expected=3 and null B rather than 15 or 40/3.

## Relative returns

`relative.market_return` = r_symbol - r_market, dimensionless simple-return
difference (multiply by 100 only for display in percentage points).
`relative.sector_return` = r_symbol - r_sector with supplied admitted membership
effective for the target and appropriate supplied sector benchmark.
Return inputs bind identical start/end governed session IDs, horizon, evaluation
cutoff, completed/intraday endpoint mode, currency, adjustment policy/version and
availability policy. Different instrument identities are expected; their namespace
mapping and benchmark/membership identities must be explicit. No ticker-only join,
interpolation, FX conversion or hidden benchmark calculation. Incompatibility is
a typed validation error; missing benchmark/membership yields missing_input only
for the dependent comparison. Unready returns propagate their status and reasons.
For 100→110 and 200→210, returns are 1/10 and 1/20; relative value is 1/20.
This is an arithmetic spread, not (1+r_symbol)/(1+r_market)-1.

## Declared-universe breadth

U is an immutable unique list of namespaced instrument IDs with membership identity
and evaluation time. Reject extra members, duplicate IDs and incompatible horizons,
cutoffs, currency/basis or feature versions. Preserve supplied expected |U| even
when members lack data. Each member contributes at most once. Only available,
compatible member values count as eligible; retain exclusions by member/reason.

`breadth.direction_counts`: A=count(r>0), D=count(r<0), Z=count(r=0), units members.
Return A,D,Z, eligible E=A+D+Z, expected M=|U| and coverage E/M. Partial U yields
incomplete_coverage with these explicitly partial counts; absent members never enter
Z. Nonempty U with E=0 has null counts and coverage 0. Empty U yields not_applicable,
null counts/coverage; absent U yields missing_input. Zero is exact zero of a supplied
simple return; no arbitrary epsilon threshold. Any future tolerance needs config
and algorithm-version identity.

`breadth.above_sma_fraction`: among members with available compatible completed
close and configured SMA, K=count(close>SMA), E=eligible, fraction K/E. Equality
is not above. Return K,E,M,E/M and member exclusions. Missing close/SMA does not
enter E. E=0 gives null fraction; empty U not_applicable. Partial universe gives
incomplete_coverage with an explicitly partial fraction. SMA period/anchor, price
scale/currency/basis, session and cutoff must match; comparison uses exact compatible
units, never raw integers from different scales. There is no default K/M fraction.

Example U={a,b,c,d}, returns [+1/10,-1/20,0,missing] gives (1,1,1), E=3,M=4,
coverage=3/4, incomplete_coverage. Closes [11,9,10,missing], SMA [10,10,10,10]
give K=1,E=3,fraction=1/3. With all four available, E=M and status available.

## Evidence and limitations

Each result retains required input/config/algorithm identities, target/cutoff,
window/bucket endpoints, expected/observed coverage and unavailable reasons.
Unavailable scalar values are null; partial structured breadth is intentionally
distinguished from unavailable scalar baselines. `not_applicable` zero-denominator
is a mathematical result, not malformed input. Invalid integer representation,
negative volume, duplicate identities or inconsistent alignment raises an error.
Fixtures establish equations and boundaries only; no production API, performance
or actual reference/source availability is qualified by this specification.
