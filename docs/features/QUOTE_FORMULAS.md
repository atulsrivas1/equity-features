# Quote mathematical and sampling contract

Definition version1; owner EQ-003. Applies to the3quote IDs in V1_SCOPE.md. This is a specification with synthetic reference evidence, not a production package or admitted provider feed. Source I/O is outside calculations.

## Supplied inputs and observation admission

Caller supplies instrument/session identity, currency/share price scale, compatible adjustment basis, open and requested cutoff, source/sampling identity, eligibility-policy identity, input delivery coverage and availability evidence. Target is [open,cutoff), open<cutoff<=session close and duration must fit int64 nanoseconds; no quote closing-auction endpoint exception. Session/early-close calendar and reference availability are supplied, not discovered. Use exact int64 UTC nanoseconds, stable unique event IDs and total order(event_ns,caller order key); duplicate/ambiguous/unordered or out-of-target rows are validation errors, not silently sorted/deduplicated.

Every admitted quote row is a normalized full current bid/ask state or sample, not a raw one-side delta. Caller reconstructs deltas, withdrawals and cancellations before calculation. Missing sides are explicit nulls; absent price is not carried from the previous row. Excluded updates are not observations, do not enter counts and do not refresh continuous state/age. Their exclusion/delivery evidence remains caller-owned. Structural fields and admitted price representations must be validated; malformed/nonfinite/noninteger/out-of-range price coefficients raise errors. Exact scaled nonpositive prices are representable invalid market states, counted rather than treated as valid quotes. Quote sizes are optional and are not used by these definitions; zero displayed size is not independently a price-validity rule. Caller normalization must represent a withdrawn side as null when required by its declared source policy.

Qs is trade-associated snapshot sampling, with one observation per admitted snapshot. Repeated identical prices at different admitted events remain distinct observations; trade-associated frequency bias is explicitly retained. Qc is continuous quote-state updates with declared complete normalized delivery. Qc event-weighted summaries are still update-weighted, not duration-weighted. Qs and Qc cannot be pooled as equivalent populations without a new declared sampling specification.

## State classification and per-observation values

Let b,a be bid/ask in exact common price units. A null or nonpositive side is invalid. Otherwise d=a-b and m=(a+b)/2. If d>0 the state is normal; d=0 locked; d<0 crossed. Valid means normal OR locked. Positive crossed quotes have optional signed diagnostics d and10000*d/m, but are excluded from published spread means. Missing/nonpositive sides have null spread/midpoint diagnostics. The field called absolute spread means spread in price units for valid observations; it does not mean abs(a-b), which would hide a crossed book.

For valid observation i, s_i=a_i-b_i (currency/share) and z_i=10000*s_i/m_i (basis points). Locked contributes0 to both. Midpoint is a mathematical half-sum; do not round it to a price tick before dividing. Wider checked arithmetic is required for a+b, differences and weighted products. Final float64 outputs use rtol1e-12/atol1e-12 in stated units; counts/durations compare exactly. No implicit percent or price rounding. Quote scale/schema details are EQ-011/014.

Counts: n_total = n_normal+n_locked+n_crossed+n_invalid. n_valid=n_normal+n_locked. Locked is a subset of valid, so total is NOT valid+locked+crossed+invalid. Count row eligibility before classification; do not silently drop invalid observations from total. Diagnostics retain the declared population and source sampling label.

## Exact feature definitions

| Feature ID | Equation / selection | Units | Worked expectation |
| --- | --- | --- | --- |
| session.quote.sampled_spread | Optional per-observation s_i,z_i; equal-observation summaries mean_s=sum(s_i)/n_valid and mean_z=sum(z_i)/n_valid, over normal/locked only | currency/share and bps | q1spread2,bps20000/101; q2locked0; valid means1 and10000/101 |
| session.quote.state_counts | n_total, n_valid, n_locked, n_crossed, n_invalid, with n_normal optionally exposed as diagnostic; count invariants above | observations | total4,valid2,locked1,crossed1,invalid1 |
| session.quote.time_weighted_spread | Qc only: mean_s_time=sum(s_j*dt_j)/D_valid; mean_z_time=sum(z_j*dt_j)/D_valid; D_valid=sum(dt_j valid); expose duration diagnostics and D_valid/(cutoff-open) | currency/share,bps,int64 nanoseconds,fraction | D_valid7ns; mean_s6/7; mean_z60000/707; valid fraction7/12 |

No quantiles, variance, trade-size weighting or ratio of mean spread to mean midpoint is part of these3IDs. More statistics require their own mathematical specification. Mean bps is the mean of individual bps, not10000*mean_spread/mean_midpoint.

## Continuous carry, expiry and initial state

Qc requires explicit positive integer max_age_ns and policy/config identity; there is no universal market default. An admitted state at t_j begins at that event, and is fresh on [t_j,t_j+max_age). Its interval ends at the earliest next admitted update, expiry or cutoff, clipped to open. Arithmetic for expiry must be wide/checked or bounded safely; addition cannot wrap near int64 limits. At exact expiry, state is expired. Known expired time is excluded from valid duration, not assigned zero spread.

Invalid and crossed updates replace the previous state immediately and prevent carrying the previous valid quote through them. Locked is valid0. Equal-time ordered updates all enter observation counts; earlier tied states have0duration and the last admitted tied state governs positive time. Timestamp/order IDs and original expiry anchor survive batch boundaries.

Initial state must be one of: a separately supplied admitted pre-open quote seed (event_ns<open, known/admissible under supplied availability policy); explicitly known inactive (no quote); or unknown. A row at open belongs in target events, not the seed. Seed never enters target observation counts; its original timestamp anchors expiry, never restarted at open. A seed already expired contributes expired time until the next update. Unknown initial state contributes unknown duration until the first admitted update; do not fill backward from that future update. A known inactive initial state contributes invalid/no-quote duration until updated. Seed ID cannot duplicate a target event; source row identity, knowledge and state basis must be compatible.

Duration categories normal, locked, crossed, invalid, expired and unknown are disjoint and sum to cutoff-open; D_valid=normal+locked. Invalid time includes explicitly known inactive state. Duration statistics are based on the full canonical update stream, never visual aggregates or trade snapshots. Qs is rejected for time-weighting even if timestamps appear dense. Input completeness/initial-state evidence is required; event count alone cannot prove continuous delivery.

## Quality, empty inputs and known gaps

Sample counts over an observed fully delivered empty target are0; sampled spreads with n_valid=0 are null/not_applicable. All-invalid or all-crossed covered observations have available counts but no valid spread denominator. Absent data is missing_input, not empty. Incomplete delivery nulls affected published summaries/counts with incomplete_coverage; observed arithmetic may be retained separately as evidence.

Continuous source completeness and valid quote duration are distinct. If delivery is unproved/incomplete or any left-boundary duration is unknown, published time-weighted results are null/incomplete_coverage, even if observed valid-time evidence is computable. Caller must not bridge a known feed outage merely by carrying an old quote: declare incomplete delivery, or supply verified normalized no-quote state where that is what actually occurred. Expiry is a declared freshness limit, not proof of complete feed delivery.

For completely delivered and initialized targets, crossed/invalid/expired durations are known excluded intervals. Mean is over D_valid only and remains available when D_valid>0; valid-duration/fraction and excluded durations must accompany it so it cannot be presented as an all-session spread. D_valid=0 gives null means/not_applicable, with known duration diagnostics. Explicit inactive initial state plus no updates is a covered no-quote target; no seed/unknown initialization plus no updates is incomplete temporal coverage. Counts remain independent of continuous initial-state readiness. Partial cutoff can be complete for its requested target but metadata marks cutoff scope, never EOD. Known-at/simulation eligibility are explicit supplied evidence, not inferred from event time or generation time; EQ-006 owns those admission policies.

## State and partition requirements

Sample reductions retain valid count and two sums plus state counts; combine numerators/denominators, never averages of averages. Per-observation evidence need not be retained in bounded state. Complete disjoint source/identity/policy-compatible populations are required for merge; duplicate delivery is caller-normalized and validated.

Continuous state retains last admitted full quote, its original timestamp/order, initialization classification, sums/durations, current bound and policy/version bindings. Advancing to a cutoff accounts for expiry even without a new event. Arbitrary continuous chunk aggregates cannot be merged without ordered boundary carry and conservation; last-quote seed context contributes time, never sample counts. Snapshot cannot report an earlier cutoff after later data/state was consumed. Corrections require explicit replay/rebuild. No production restore/merge API is established by this spec; EQ-023–025 must implement/qualify supported capabilities.

## Independent worked fixture

Window[0,12) in illustrative nanosecond offsets, scale0, max_age6ns. q1 at0:b100/a102; q2 at3:b102/a102; q3 at7:b105/a104; q4 at9:bnull/a102. Sample counts4/valid2/locked1/crossed1/invalid1. Continuous valid q1[0,3),q2[3,7): duration7; crossed[7,9):2; invalid[9,12):3. Weighted numerator s=2*3+0*4=6; bps=(20000/101)*3; divide by7. Fixture README derives expected fractions independently. These tiny times are for arithmetic, not a provider validity recommendation.

Run `python tools/verify_quote_examples.py`. Existing session references remain required. Fixtures verify3ID coverage, exact expectations and sampling/temporal/precision/partition cases; they do not certify package kernels, realtime behavior, source admission or performance. Changed equations need distinct custom identities under planned EQ-093; consumer configuration cannot silently change built-in sampling/denominator meaning.
