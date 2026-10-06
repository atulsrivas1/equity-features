# EQ-050 — R4 pre-code plan

[Issue57](https://github.com/atulsrivas1/equity-features/issues/57), R4/E07.
Estimate: **8 provisional story points**, not a deadline. Prepared plan only;
no implementation, executed tests or delivery claimed.

## Start and dependencies

EQ049 interface frozen. Reinspect live acceptance and accepted public contracts before pulling.
One active implementation story. Follow [execution package](../R4_AUTONOMOUS_HANDOFF.md)
and [test strategy](../R4_TEST_STRATEGY.md); define concrete interfaces and independently
expected fixtures before source implementation.

## Design

Trades/TBBO/minute/daily mappings; exact UTCns, price/share units, original identities, nulls, eligibility, known-at; freeze precision policies and unsupported fields.

## Open questions and source issues

Freeze exact API/configuration/backend pins and supported source populations when
pulled. Unknown precision/availability/eligibility/calendar/reference evidence stays
explicit. A consequential canonical schema/capability change needs a versioned
decision, regression evidence and review. Real instruments/dates/goldens must be
selected from inspected source support, not invented in this preparation.

## Required tests

Independent row expectations, overflow, ties, absent/null/zero, invalid clock/scale and sampling; mapping/normalization guide.

Apply relevant accepted SDK, mathematical/time/action and package-isolation checks.
Keep synthetic DuckDB conformance and private real-data acceptance separate; record
actual executed results, source/installation identities and limitations. Original
or legacy derived output is not automatically an independent numerical golden.

## Documentation

Update relevant public API/mapping/install/limitations examples, issue/PR, review
and delivery receipt, changelog and SESSION_HANDOFF alongside implementation.
Private actual-source evidence remains outside public files without redistribution
rights. Final installed/artifact/CI/readback evidence precedes Done.

## Done outcome

Qualified canonical mappings; no invented source fields. Neither a prepared plan nor a source merge establishes this outcome.

## Concrete EQ050 mapping decisions (pre-code draft)

Use accepted contracts schema1/corepair0.0.4a4 without changes. Optional adapter adds mapping1 APIs; no acquisition yet. Inspection of retained source types and primary provider clock definitions governs supported representations; private identifiers/rows remain excluded.

- MappingPolicy declares source schema, PriceUnit, binary64_exact or decimal_repr interpretation, exact or half_even rounding, explicit source-to-canonical instrument pairs, eligibility policy and optional governed default eligibility. No inferred currency, scale, eligibility or permanent ticker identity. Reuse accepted quantize_float_prices; report rounded cell counts and bind policy/report to source input identity.
- RowOccurrence(source_token, original_row, order_key) binds retained occurrence to caller-supplied source identity. Exact nonnegative int64 row and order key; duplicate occurrence IDs rejected. Tied/equal payloads with distinct occurrences preserved. Physical order keys are not provider sequence or execution-uniqueness certification.
- map_columns(policy, columns, *, metadata, occurrences, sessions) returns immutable MappedSource(batch, report). Concrete dictionary of tuple/list columns with equal bounded lengths, owned output; explicit exact session labels per row; metadata source/snapshot/coverage/scope remain caller assertions. Instrument pairs must match requested actual source integers. Metadata units and namespace/source required; output binding includes deterministic mapping policy/report/occurrence digest. Unknown fields are named as unmapped rather than guessed.
- Parse ts_utc lexical UTC ISO dates/times up to9 fractional digits using integer day arithmetic (no float epoch or microsecond truncation); accept exact int64 UTCns only when explicitly present. Reject offsetless/invalid/leap seconds/overflow. Optional known_at remains absent/null; supplied values use exact UTC conversion, never event time or bar end.
- Trades map price/size and require Boolean eligible source column with policy or explicit caller-owned default policy. TBBO maps top bid/ask and sizes as quote/trade_snapshot only; no continuous completeness promise. Optional condition retained if supplied.
- OHLCV maps minute start/end+60s or UTC daily start/end+24h, checks boundary alignment and int64 overflow. Source OHLCV interval clock is receive aggregation, not silently exchange-event causal or RTH daily. Sessions come from caller; calendar governs only later story. Map volume as checked shares/int64; don't infer actual_notional/trade_count. Zero-volume nonnull OHLC rejects under accepted validation; explicit normalization belongs caller.
- Preserve missing column versus present null versus zero. validate_batch checks mapped semantic order/identity/OHLC/quantity; no sorting, deduplication, fill or adjustment. Fixed safe SourceError messages suppress raw source paths/values/exception contexts. No source-truth/PIT guarantee or numerical formula change.

Independent fixtures before implementation: exact1700000000000000001 time; epoch negative and int64 limits; valid UTC fractions/calendar date versus invalid leap/offsetless/too-long;10.125 scale2 half_even1012 and10.375=>1038;0.1 binary64 exact reject versus decimal_repr10; nonfinite/bool/overflow; all four schemas; huge shares overflow; null/missing/zero; explicit absent eligibility unavailable and true/false; tied distinct occurrences; duplicate occurrence/ambiguous order rejection; trade-snapshot only; minute/UTCdaily boundaries; zero-volume staleprice reject and nullOHLC preserved; known-at absent/null/later retained; owned detach; source binding/report policy changes; unknown instrument/scope/coverage constraints and pure core unchanged.

Update public mapping/API/normalization examples, plan/changelog/install/build qualifications and story evidence/handoff. Add actual optional installed fixture/strict typing coverage, increment experimental optional version for expanded API, preserve both core archives. Separate final-head local review, nativebothOS CI, clean repeat-build/wheel/sdist and actual main artifact qualification/readback precede Done. No real numerical acceptance claimed; EQ051–056 remain dependency-scoped.

Implementation refinement: MappingPolicy also requires source_clock=event for
trades/TBBO or receive_aggregation for OHLCV. This is an explicit caller declaration
of retained clock provenance, not inferred certification from ts_utc spelling.
Unknown clock evidence is unsupported. max_rows defaults10000 with exact positive
int64 bounds. Expanded optional API version0.1.0a2; core unchanged.
