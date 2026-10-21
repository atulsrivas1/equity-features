# R26 original mathematical and independent-fixture proposal

Status: source-only planning under GOV038. These are original proposed contracts and hand-derived synthetic arithmetic witnesses, not frozen semantics, executed fixtures, implementation tests or private-source parity. [Admission](PREPARATION.md) remains pending. Exact source-derived binding details stay private. The six named matrix outputs allocated to R26 and additional typed measures must receive individual formula/profile/producer bindings under EQ188; different source variants cannot be counted as one qualified behavior.

## Numeric and population contracts to freeze

For execution i, supplied exact price p is currency per underlying payoff unit, q is positive integer contracts and m is positive underlying units per contract. Premium P_i=p*q*m is currency; q*m is an explicitly named underlying-equivalent quantity, not delta exposure or traded equity shares. Never assume multiplier 100. Require compatible currency/action/definition identity, positive/eligible inputs and explicit fixed decimal scale/digit/magnitude limits. Additive totals are exact; ratio results preserve exact numerator/denominator and need a frozen rendering policy. Reject overflow/resource admission before partial publication. R25 IV tolerances are unrelated to these arithmetic contracts.

Complete empty populations have count/premium 0 and undefined zero-denominator shares/concentration. Incomplete/unknown populations are unavailable for complete-population metrics; partial diagnostics must be separately labelled. Unknown sign is an explicit category, not an omitted trade. Capture witnesses are supplied evidence whose shape/binding can be checked; the kernel cannot prove provider completeness.

## Causality, signs and windows

Propose explicit half-open [start,end) windows, integer event and known-at instants, source/partition order witnesses and a signing-availability boundary per execution. Quote admission requires compatible identity, quote event no later than trade, known-at no later than signing boundary, eligible age and causally admissible order for ties. A deterministic ID sort is not a cross-feed causal witness. Late-known quotes cannot improve an origin-time result; restatements have separate identities.

Distinguish observed direction, quote proxy and tick proxy. Proposed exact midpoint quote profile: strictly uncrossed two-sided quote, compare 2p with bid+ask; greater gives+1, less gives-1, equality unknown. Locked/crossed/stale/missing/future quotes remain unknown with reasons. A separately named exact tick profile uses prior per-contract/session/basis price and carries only its own last nonzero tick sign; absent seed/unchanged initial prices remain unknown. Hybrid precedence and shared equity-kernel reuse require explicit contracts. These profiles do not claim equivalence to every historical source convention. Generic equity signing/bucket/correlation implementations retain equity ownership.

Cancels/replacements are immutable as-of revisions. Only revisions known by the request cutoff affect that generation. Recompute the affected ordered suffix where a correction changes later signs or clusters; do not only subtract a premium. Preserve earlier stored origin-time generations. Exact disjoint sum/group merge does not authorize unordered sign-state merge, averaging HHIs or averaging medians.

## Proposed outputs

- Eligible counts/contracts, exact premium and signed/unknown premium summaries over declared groups/windows. Keep execution sign separate from right-adjusted direction: for call d=s, for put d=-s. This is a labelled arithmetic proxy, not customer intent, position, multi-leg strategy direction or dealer inventory.
- For group premiums g_j and total T>0, HHI=sum(g_j^2)/T^2 and top share=max(g_j)/T. Distinguish contract and expiry partitions. Put/call premium ratio has call-premium denominator; zero is undefined. Known-sign imbalance uses known signed premium as denominator, whereas total imbalance includes unknown premium; names/evidence must distinguish them.
- Prior-only relative contracts/trade-count use a compatible completed prior-session median. For sorted history, median is the middle value or exact mean of the middle two; MAD is the median absolute deviation from that median. Candidate robust score=(current-median)/(c*MAD) with an explicitly declared positive exact scale c. A proposed profile uses exact c=7413/5000; MAD 0 is undefined, with diagnostics retained. Freeze history slot identity/completeness, minimum sample count, cutoff and zero-denominator policy; product screen thresholds are not mathematical minima.
- Temporal execution clusters require explicit contract/basis, quote witness, sign and inclusive adjacent-gap rule; a quote/sign/session change breaks a cluster. Repeated exact-print grouping and maximum-total-span clustering are different profiles, not interchangeable implementations of a temporal cluster. EQ188 must resolve every selected source binding before release, with gaps owned visibly rather than silently dropped.
- DTE uses supplied civil-date/calendar/expiry evidence. Short-DTE boundary is a request/profile parameter. OTM requires causal compatible spot and explicit call K>S / put K<S convention; ATM equality is not OTM. DTE-only admission need not depend on spot. Distinguish full-population shares, known-reference conditional shares and reference coverage; never use a conditional denominator under a full-population label.
- EQ190 participation joins compatible complete window/basis/cutoff operands. Share-equivalent participation=sum(q*m)/equity shares; premium-to-turnover=sum(P)/equity dollar turnover. Ratios can exceed 1; they do not describe one common population fraction. Signed equity buckets and generic Pearson arithmetic require accepted compatible equity producers EQ158/EQ153, with no duplicated implementation in options.
- For lag k, descriptive correlation pairs option x(t) with equity y(t+k). Positive lag needs later equity buckets and cannot be available at an earlier origin. Bind exact grid, finite pair membership/count, sign profiles and max operand availability. Require sufficient pairs and positive variance under the frozen policy; missing buckets are not observed zero. Source-to-result EQ190 acceptance waits for actual equity producer integration, even if supplied synthetic vectors can test a consumer boundary.

## Independent hand-derived arithmetic examples

These original examples assume explicitly admitted synthetic identities/clocks/populations solely to show arithmetic. They are not complete wire fixtures or run evidence.

| Execution | Right/group | Price | Contracts | Multiplier | Supplied proxy sign | Premium |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| a | call/A | 2 | 3 | 100 | +1 | 600 |
| b | call/A | 1.5 | 2 | 100 | -1 | 300 |
| c | put/B | 4 | 1 | 100 | +1 | 400 |
| d | put/C | 2 | 1 | 50 | unknown | 100 |

Complete totals: 4 executions, 7 contracts, 650 underlying-equivalent units and premium 1400. Calls 900, puts 500, put/call 5/9. Buyer-proxy premium 1000, seller-proxy 300, unknown 100; signed execution premium 700; known-sign imbalance 7/13; total-premium imbalance 1/2; unknown share 1/14. Right-adjusted net premium is600-300-400=-100. Group premiums 900/400/100 give HHI 1/2 and top share 9/14. A compatible equity fixture of 100 shares and dollar turnover 2000 gives participation 13/2 and 7/10 respectively.

History 2,4,6,8 has median 5 and MAD 2; current 11 gives median-relative 11/5 and, under c=7413/5000, robust score 5000/2471. A constant history has MAD 0 and an undefined robust score. This four-value arithmetic fixture does not establish any eventual production minimum history length.

For complete paired buckets x=[1,2,3,4], y=[8,2,4,6], lag +1 pairs [1,2,3] with [2,4,6] and gives r=1 with 3 pairs. Lag 0 gives r=-1/5. Missing a paired bucket reduces count rather than filling zero; a constant vector has undefined correlation. These are hand expectations for independent consumer qualification, not evidence an equity producer is implemented.

## Before freeze and execution

Resolve every policy/variant/profile and selected output binding; freeze exact records/wire/errors/limits and independent full metadata fixtures. Review numerical and causal expectations independently from the implementation author. Include boundaries, future-known input, unknown/partial/empty, mixed multipliers, precision extremes, stale/locked/tied quotes, suffix correction, legal merge/restore and producer compatibility. Actual both-platform artifacts, measured bounded workloads, direct/worker/stored parity and browser evidence remain later executed gates. No arithmetic example here substitutes for them.
