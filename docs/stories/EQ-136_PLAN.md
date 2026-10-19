# EQ136 proposed intraday contract and pre-code plan

## Current concrete contract proposal

EQ136 is now the active specification story in [draft PR499](https://github.com/atulsrivas1/equity-features/pull/499). GOV030/GOV031 planning deliveries and R16 prerequisites are accepted. The [working math](../features/INTRADAY_FOUNDATIONS.md), [exact API/codec/status/precision proposal](../api/INTRADAY.md), [optional package decision](../decisions/R17_INTRADAY_PACKAGE.md), [independent fixture README](../../tests/fixtures/intraday_math/README.md) and [frozen measurement plan](../R17_TEST_STRATEGY.md) make the original remaining choices concrete for separate review. They supersede the older draft's rounded-band operands and unspecified capability/tolerance choices; original fixture arithmetic remains retained and checked. No production kernel, package artifact or accepted final API is claimed before review/publication/readback. Earlier proposal follows as history.

Owner-selected R17, [issue470](https://github.com/atulsrivas1/equity-features/issues/470). Status: pre-code proposal under GOV031 preparation, not accepted math, a registry change or implementation. Prerequisites: accepted GOV030/GOV031 publication/readback, accepted R16 baseline, applicable separate review and concrete Ready evidence. [Handoff](../R17_AUTONOMOUS_HANDOFF.md), [fixtures](EQ-136_FIXTURES.json), [test strategy](../R17_TEST_STRATEGY.md).

## Deliverable and first actions

Freeze original finalized-bar/grid/availability/math/output/capability identities and independent reference expectations for EQ137–140. Inspect actual normalized bar contracts and affected callers in core/I/O/workers; record whether a new context type/API is needed instead of forcing daily HistoryContext onto intraday slots. Produce reviewed math/API/discovery/state proposals, fixture verifier and compatibility/no-impact decisions; publish and read back those documents before EQ136 Done. Specification-only: no production kernel, package version change, numerical speed result or install matrix is claimed by this draft.

## Proposed data and temporal contract

Inputs are caller-supplied ordered governed bar slots with UTC int64 nanosecond bounds, instrument/source/revision/grid/calendar identities, currency/decimal price scale, compatible action basis, completion and known-at coverage. Slot intervals are half-open [start,end), positive and nonoverlapping; no silent sorting, resampling, inferred holiday calendar, deduplication or forward fill. A finalized slot is eligible only when end <= feature cutoff and its supplied evidence is available under the declared knowledge policy. Forming/future/revised-after-cutoff values cannot enter an origin-time result. Expected absent slots remain absent, not compressed away.

Close prices are positive scaled integers in compatible units; H/L validity is required only for outputs that read them. Identity/grid mismatch, duplicate slot, malformed precision/bounds and incompatible action basis are typed admission errors. Missing/empty/incomplete inputs retain distinct coverage/availability evidence. Missing H/L does not invalidate an otherwise admitted close-only branch; invalid supplied metadata is not ignored simply because another branch does not use a value.

Use an explicit initialization anchor. Proposed session-reset mode anchors at the first admitted session bar and excludes overnight changes from its seed. Proposed carry mode requires a caller-supplied earlier anchor and complete governed predecessor slots; transitions between supplied sessions include the resulting overnight close change/true range and must be labeled accordingly. Do not silently choose or switch modes. Sessions closed by calendar policy are not missing expected bars. Candidate period constraints retain existing history conventions: EMA/ATR >=1, RSI >=2; bands >=2; all periods are integer, not booleans. Window membership counts governed slots, not calendar minutes or only observed rows.

An unresolved missing observation within an anchored recursive chain makes downstream recurrence unavailable until a valid explicit reinitialization/replay; never resume by skipping the gap. Rolling bands may recover after the selected window again has complete required observations even if an older, out-of-window slot was missing. Caller updates/corrections create new source/revision evidence; old cutoff results are immutable.

## Proposed mathematical definitions

Let C,H,L be admitted bar prices, close anchor a and period N. Price outputs use currency/share; RSI uses points 0–100. These proposals preserve the existing daily definitions where appropriate while changing the governed input grid explicitly; they are not an assertion that today's daily API accepts intraday inputs.

| Output | Proposed mathematics and first eligible index | Actual direct operands |
| --- | --- | --- |
| EMA | E[a+N-1] = mean(C[a:a+N]); E[t] = alpha*C[t] + (1-alpha)*E[t-1], alpha=2/(N+1) | Complete anchored close chain and EMA state/config |
| RSI | Gains=max(delta,0), losses=max(-delta,0); seed mean of first N changes; Wilder update ((N-1)*average + current)/N; 100*G/(G+D), both zero ->50; first a+N | N+1 close seed observations, then ordered gains/losses state |
| ATR | TR[t]=max(H[t]-L[t], abs(H[t]-C[t-1]), abs(L[t]-C[t-1])); seed first N TRs beginning a+1; Wilder update; first a+N | H/L for those TR slots, predecessor closes, compatible TR state; not RSI or EMA |
| Band middle | Mean of selected last N complete closes | Supplied compatible rolling mean or closes/config |
| Band upper/lower | middle +/- k*sqrt(population price variance), k finite positive; variance=sum((C-mean)^2)/N | Compatible mean and price variance; not return volatility or ATR |
| Band width ratio | (upper-lower)/middle; zero denominator unavailable | Selected compatible band bounds and middle |
| Band position | (C[t]-lower)/(upper-lower); zero width unavailable for this cell only | Selected compatible close and band bounds |

Population price variance and k are explicit versioned choices, not inferred library defaults. Zero variance yields valid equal upper/middle/lower and zero width ratio; only band position is unavailable. A direct centered high-precision reference qualifies numerical stability; the production approach must not silently clamp a material negative variance. Propose exact price accumulation with guarded integer bounds and Float64 output tolerance frozen against the independent oracle before implementing optimized recurrences. Float tolerance must cover the selected scale/history, not excuse unstable large-offset cancellation.

Candidate IDs: intraday.ema, intraday.rsi, intraday.atr, intraday.band_middle, intraday.band_upper, intraday.band_lower, intraday.band_width_ratio and intraday.band_position. Eight output identities, not eight processes or one ID per period. They are reserved proposals only; EQ136 must reconcile registry/discovery/versioning and affected consumers before allocation. No change to the accepted existing 39 built-ins in this packet.

## Dependency and capability contract

Closes independently feed EMA, RSI and rolling price moments; H/L plus predecessor close feed TR/ATR. Mean/variance feed band bounds; compatible band bounds feed width and position cells with their own availability. A supplied compatible intermediate can satisfy a phase input without recomputing upstream leaves. Preparation identity includes instrument/population, interval/grid, action/unit basis, selected membership/anchor, cutoff, configuration/algorithm and source revision. Equivalent names alone are insufficient for reuse.

Batch is required for every selected R17 output. Ordered update/restore are candidate capabilities, requiring independent parity, duplicate/order/correction and compatibility contracts per feature; unsupported capabilities must be explicitly frozen as such before implementation Ready. No arbitrary recurrence merge is claimed. Keep caller-owned state pure; persistent service/job scheduling belongs outside this package. Immutable inputs and separately owned states allow cross-symbol/family work without locks on a global feature chain. Shared mutable aliases remain a qualification concern, not permission to remove ordering.

## Independent expected cases and acceptance

The supplied tiny fixture uses rational prices to expose seeds and first-eligible indices. Additional required cases: flat and monotone closes; period boundaries; large offset/small variation; complete closes but missing H/L; band zero width; end=cutoff versus forming bars; late known-at revision; missing expected slot versus nontrading session; reset versus explicit carry; warm-up and replay after gap. Review expected arithmetic independently of any shared optimized kernel.

Before dependent implementation stories EQ137–140 become Ready, reconcile exact normalized input/result APIs, all eight selected ID/version decisions, per-cell error/availability precedence, numeric tolerances, session/anchor mode schemas and unsupported capability dispositions. These are explicit remaining design decisions for this specification story, not questions silently delegated to implementation. First actions: source/caller audit, original complete contract, independent synthetic verifier, separate review and applicable docs checks. End state: accepted source-independent per-output contract and evidence, published through review/Test/release/readback; dependent kernels remain separate stories.
