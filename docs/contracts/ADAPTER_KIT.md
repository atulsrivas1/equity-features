# Public adapter conformance development kit

## R4.1 ownership clarification

Existing pure input protocol/SDK contracts remain compatible in `equity-feature-contracts`. New storage publication and explicit factory interfaces are planned in companion I/O packages; concrete adapters/sinks stay outside calculations. [Architecture](../IO_WORKER_ARCHITECTURE.md) specifies responsibilities and consumer extension paths. Do not interpret a historical absence-of-DuckDB statement below as current R4 delivery status. No contract/runtime change occurs in this planning story.


EQ043 adds `equity_feature_contracts.adapter_kit` in experimental pair0.0.4a4. It reuses the accepted [adapter protocols and delivery validator](ADAPTERS.md). Source acquisition and concrete adapters stay outside both numerical distributions. Implementation review, CI and actual publication gates are recorded on [issue49](https://github.com/atulsrivas1/equity-features/issues/49).

## Pure reusable checks

ConformanceCase(case_id, request, capabilities, batches, expected_error=None, acquisition_error=None, live=False) owns a concrete finite envelope tuple. Request/capabilities are the existing schema1 types. Each case names either successful supplied delivery or the expected stable SourceErrorCode. `run_conformance(cases, max_cases=128)` checks finite nonempty unique cases (explicit bound1..10000), calls public validate_delivery and returns ConformanceReport.outcomes. Each ConformanceOutcome identifies expected/observed codes and derived passed status; report.passed requires all actual cases to pass. Unexpected source errors become failed outcomes, never success. Invalid case containers/fields/bounds raise typed SourceError.

A supplied acquisition_error qualifies captured error classification only. It cannot accompany any delivered prefix, never validates prefix completeness, and contains no arbitrary exception message/credentials. The kit does not invoke adapters, consume lazy iterators, authenticate claims or prove error occurrence. Users collect actual outcomes outside core. `validate_delivery` may concatenate up to request.max_rows for semantic order/duplicate admission; that is bounded supplied-input checking, not streaming/source scheduling. Directly constructing an empty report is unqualified; run_conformance rejects an empty suite.

## External synthetic adapter and reproduction

The separately built equity-feature-demo0.3.0 consumer has py.typed and InMemoryBarAdapter in `equity_feature_demo.adapter`. Its fixed synthetic raw BAR fixture supports explicit historical namespace/unit/snapshot/range and max chunk sizes. Whole bars must fit requested bounds; it never fabricates partial bars or filters unknown/future knowledge. Complete-source coverage is preserved separately from selected-chunk delivery coverage. Deterministic request/ordinal source input IDs remain distinct. Missing data yields one terminal missing envelope with unknown incomplete zero delivery; an observed empty selection yields a real zero-row canonical batch. It checks total rows/chunks and cancellation before/between chunks; already yielded chunks cannot be retracted. No live/provider/file/DuckDB/retry/cache/worker support.

Build/install both core wheels (or sdists) into a fresh environment, build the external consumer wheel with the pinned build tools, and install it with `--no-index --no-deps`. Run `python -I -c "from equity_feature_demo import main; main()"` outside repository imports. tools/build_foundation.py performs these steps for each fresh core pair, checks public consumer imports/installed locations and unchanged core bytes. The actual adapter passes the public reusable suite, binds its delivered source to the custom calculation and independently verifies range/open5/100 versus built-in range/close5/103. The framework/consumer versions identify implementation, not provider truth.

## Mapping checklist and errors

- Map source instruments/session identity explicitly; preserve snapshot/mapping/input and row ordering. No ticker-only source joins.
- Preserve exact signed int64 UTCns and integer scaled-price units/currency; reject float time/price coercion, overflow and undeclared rounding. Use public quantization/normalization reports where conversion is required.
- Declare canonical kind/schema1, raw/adjusted policy/snapshot/anchor, sampled/continuous quote semantics and original known_at. Acquisition selection differs from calculation C/K/E readiness; future/null knowledge remains present for calculation admission.
- Preserve original source coverage versus each chunk's actual delivered count and final marker. Empty, missing, unavailable and partial interruption remain distinct. Source declarations are not authenticated evidence.
- Honor explicit row/chunk bounds before yielding misleading complete data. For an unqualified adapter, caller-owned bounded collection checks count/rows after each yield and cancels/stops at the declared limits; it cannot guarantee responsiveness inside arbitrary source code.
- Distinguish unsupported, authentication, entitlement, rate limit, transport, schema, unavailable, cancellation and resource-limit SourceErrorCode. The synthetic adapter translates its owned contract construction/validation failures to SourceError(SCHEMA) with a safe fixed message and original cause. Translate source/mapping failures into safe typed errors without secrets. Generic supplied error-code fixtures do not claim a real provider failure was executed.

Public installed tests cover actual valid chunks/boundaries, exact units/precision/schema errors, order/duplicate/final/ordinal negatives, unknown/future availability, empty/missing/unavailable, declared errors and actual synthetic cancellation/bounds. Conformance establishes the checked contracts only; no source truth, rights, entitlements, financial correctness, sandbox, custom purity or resource certification of arbitrary adapters. EQ039/040/095 and final R3 acceptance further qualify the full consumer guide/integration.
