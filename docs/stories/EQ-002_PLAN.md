# EQ-002 — story execution plan

Story: [Specify session, bar and trade formulas](https://github.com/atulsrivas1/equity-features/issues/3).
Epic: E01. Release: R0 design/foundation. Estimate: **5 story points, provisional**.
Status: plan drafted; exact formula specification, fixture validation and story acceptance are not completed by this plan.

Execution evidence: SESSION_FORMULAS.md and decisions/session-semantics.md are drafted; golden fixtures and tools/verify_session_examples.py cover all20IDs and17reference cases. Final-head CI, publication and issue acceptance must be verified before completion. This plan remains the rationale; live issue/Project owns status.

## Purpose and estimate

Turn the 20 session/bar/trade IDs owned by EQ-002 in V1_SCOPE.md into unambiguous mathematical specifications that independent implementers can follow. Resolve units, eligible inputs, boundaries, ordering, ties, denominators and quality states before numerical package code.

Points measure relative effort/complexity/uncertainty, not hours. Use the Fibonacci scale1/2/3/5/8. This is the first provisional five-point reference: twenty related definitions, shared semantics and independent boundary fixtures. Re-estimate if new scope is added or research changes the assumptions; do not equate points to a release date. All other story estimates remain unset until individually planned.

## How to start

1. Confirm EQ-001 scope and issue acceptance; inventory every EQ-002-owned ID (including joint EQ-006 gap/close-return ownership).
2. Create a definition template and proposed shared policies before filling individual formulas.
3. Resolve local formula decisions, recording defaults and rejected alternatives; bind EQ-006-dependent adjustment semantics explicitly rather than implementing adjustment logic here.
4. Write equations and independently worked synthetic examples for all20IDs. Map shared fixtures and edge cases to each definition.
5. Verify arithmetic using exact rational/decimal reference calculations and coverage/link checks. Review consistency against source-independent contracts and batch/stream requirements.
6. Publish the reviewed/tested specification and fixture evidence, verify public contents, then mark the documentation story Released and Done. Do not claim package implementation or R0 completion.

Pull this story from Ready to In progress while planning/specifying. A plan-only PR is not the story's final Code review/Test/release gate; keep the story In progress until the complete specification is reviewable.

## Design and deliverables

The deliverable is a mathematical contract, not a provider adapter or numerical implementation. Each definition records feature ID, equation, input columns, input basis, output units, target/cutoff semantics, eligibility, empty/missing/invalid cases, denominator handling, ordering, precision, coverage/evidence, supported state/reduction behavior, worked example and related implementation stories.

Planned artifacts:

- docs/features/SESSION_FORMULAS.md: shared policy plus all20definition entries.
- docs/decisions/session-semantics.md: consequential choices and reasons.
- tests/fixtures/session_math/: small synthetic inputs and independently derived expected results with precision/units/policy metadata; not production code or proprietary samples.
- Validation record in the issue/PR: feature coverage, arithmetic checks, edge cases and remaining cross-story contracts.

Later implementations consume these definitions: EQ-017/018 bars/structure, EQ-019/020 trades/top-K, EQ-023–026 state/parity/edge cases. Exact public API/schema work remains EQ-011–016. No premature dependency installation, DuckDB reads, performance claims or calculation-library skeleton is required for this story.

## Proposed numerical definitions to settle

| Group | Proposed design |
| --- | --- |
| Bar OHLC | First eligible completed bar open, maximum high, minimum low, last eligible close in validated interval order |
| Bar volume/notional | Sum eligible bar volume; sum actual notional only when supplied with compatible units/basis; no invented notional from close*volume |
| Bar close-weighted proxy | Sum(close*volume)/sum(volume); distinct ID and approximation label, never advertised as actual trade VWAP |
| Session returns | (close/open)-1; gap=(open/prior_close)-1; close return=(close/prior_close)-1; ratios are fractions rather than percentage-point numbers |
| Range and close location | (high-low)/close; (close-low)/(high-low), with an explicit undefined state for zero range |
| Interval structure | Aggregate fully covered eligible bars in caller-defined opening/closing windows; reject unsupported bar/window straddling instead of prorating OHLC |
| Interval volume share | Interval eligible volume/session eligible volume; observed coverage remains explicit, not automatically a full-session result |
| Trade aggregates | Count eligible records, sum quantities and exact price*quantity notional; VWAP=notional/volume; mean size=volume/count |
| Top-K | Largest eligible quantities descending; stable caller-supplied order breaks ties; return row identities and bounded evidence |

These are recommendations, not approved completed formulas. Shared definition must specify per-field readiness: a computable observed aggregate may have incomplete-session coverage. Do not silently treat partial history as a completed EOD feature. Final field/error representation is coordinated with EQ-013.

## Open questions and proposed answers

| Question | Proposed resolution / owner |
| --- | --- |
| Who decides provider trade conditions? | Caller/adapter supplies validated eligibility and policy identity; formulas do not hard-code vendor condition lists. EQ-002 defines required guarantees; mapping is later adapter scope. |
| Are open/close auctions included? | Explicit caller session/auction policy, with no hidden default. Define supported boundaries and endpoint inclusion in EQ-002; use separate synthetic tests for inclusion/exclusion. |
| How are corrections/cancellations handled? | Caller supplies the normalized effective event set. V1 accumulators rebuild/replay corrected data; no exchange recovery protocol in this story. |
| Can a bar crossing a requested interval be split? | No implied OHLC proration; require compatible aligned bars or declare unsupported/incomplete interval. |
| What happens with a zero denominator? | Null/unavailable ratio plus reason; never infinity or a fabricated zero. Distinguish valid zero counts/volume from missing input. |
| Are prices adjusted internally? | No silent adjustment. Require a declared compatible basis for comparisons; EQ-006 owns precise action/availability policy. Gap formulas can be specified conditionally on compatible inputs. |
| Who supplies prior close and previous session? | Caller supplies price, governed session identity, basis and availability. No calendar or historical fetch inside formulas. |
| How do equal timestamps and top-K ties resolve? | Stable supplied ordering/sequence; no incidental file row order. Specify duplicates and unsupported ambiguous ordering explicitly. |
| How do partial sessions affect values? | Separate observed arithmetic from completeness/readiness; require cutoff and coverage metadata, no false complete-EOD claim. |
| What precision is required? | Exact scaled price/quantity arithmetic and overflow policy at boundaries; ratio outputs use documented floating tolerance. Exact rational fixture values retained. |

There is no external data dependency for this story. Cross-story timing/adjustment/schema decisions must be tracked with explicit contracts and owners; if a necessary decision cannot be expressed conditionally, record the blockage rather than invent a policy. The human owner need only resolve product changes or competing semantics that cannot be settled within the agreed scope.

## Validation and tests

This story validates definitions and expected examples, not an unimplemented production package. Reuse the resulting fixtures in implementation tests later.

| Case | What must be established |
| --- | --- |
| Normal two-bar session | Every OHLC/volume/actual-notional/proxy/return/range/location field has an independently checked result |
| Known trade prices and unequal quantities | Trade notional/VWAP/mean size/top-K match exact arithmetic, not a simple price average |
| Bar proxy versus actual notional | Deliberately different values remain correctly named and distinguishable |
| Missing actual bar notional | Bar notional unavailable while other independent fields remain usable |
| Empty versus absent input | Observed-empty counts/volume distinguished from missing data; prices/ratios not invented |
| Zero quantity/denominator and flat range | Invalid versus valid-zero cases defined; undefined ratios never silently become zero or infinity |
| Ties, duplicate identities and unordered input | Deterministic ordering/tie policy or explicit validation error; no silent dedup/sort |
| Invalid price, size and bar OHLC | Per-definition validation policy, including non-finite values and inconsistent OHLC |
| Session open/close, auctions and early close | Exact endpoint/boundary examples under each supported supplied policy |
| Opening/closing window alignment | Volume conservation; straddling bars and missing intervals identified |
| Partial cutoff and missing intervals | No future data in snapshot; incomplete coverage retained even if arithmetic computable |
| Prior close missing/incompatible/unavailable | Gap/close-close affected independently; basis/availability mismatch not ignored |
| Precision and integer extremes | Rational golden values, declared rounding and overflow rejection requirements |
| Batch partitions | Definitions independent of batch boundaries; legitimate sums/top-K reductions preserve rows and stable order |

Example seeds to expand, with actual final fixture schemas defined later:

- Two bars: (O100,H103,L99,C102,V200,N20300), (O102,H104,L101,C103,V300,N30900). Proposed session O100/H104/L99/C103/V500/N51200; close-weighted proxy102.6; open-close return0.03; close location0.8; range fraction5/103. First interval volume share0.4, second0.6. Prior compatible close98 gives gap2/98 and close-close5/98.
- Trades: prices100/102/101 with sizes2/3/5. Count3, volume10, notional1011, VWAP101.1, mean size10/3; largest trade is the size5 record. Prices/quantities in these examples have explicitly compatible illustrative units.

Expected results are derived independently of the eventual library. If a formula changes during specification, update equations and fixture rationale together. Documentation checks must ensure every20scopedID has a definition, example and owner mapping; don't add implementation-mirroring tests or speed benchmarks for this documentation story.

## Documentation and GitHub updates

Update this plan, formula document, decisions, fixtures/readme, V1 scope links when needed, issue acceptance/evidence, linked PR and SESSION_HANDOFF alongside the story. Add Story points=5 to the Project as a provisional estimate. Keep status accurate. Record substantive open-question resolutions and failures; review tooling is not an independent human reviewer.

## End state

EQ-002 is Done only when:

1. All20session/bar/trade IDs have exact documented equations, units, eligibility, denominator/order/boundary/quality rules and independently worked examples.
2. Synthetic fixture expectations and edge-case coverage are checked and evidence is recorded.
3. Cross-story dependencies are explicitly resolved or bounded by compatible-input contracts; no unresolved ambiguity that prevents implementation is hidden.
4. Applicable review and documentation checks pass on the actual final commit.
5. Specification/fixtures are published and verified, GitHub acceptance is updated, and continuity names the next Ready work.

No numerical package functions, DuckDB/provider adapter, worker, package release or production backtest acceptance is implied. R0 remains open. The completed specification becomes the implementation contract for later session-feature stories.
