# Validation and explicit normalization

EQ-014, experimental0.0.1a4. These stdlib helpers inspect owned caller input;
no source retrieval, calendars, corporate-action application or feature calculator.
They are a reference admission/transform boundary, not a throughput claim.

## Checked admission

`validate_batch(batch, session=None, availability=None, required_fields=None)`
never sorts, deduplicates or removes rows. It checks unique canonical event/interval/
reference identity and per-partition order. Trades/quotes use strictly increasing
(event_ns,order_key) within instrument/session; equal-time distinct order keys are
allowed, ambiguous ties fail. Interleaved instruments are allowed. Bars are ordered,
nonoverlapping per instrument/session; daily slots are unique per instrument/session
and chronological/nonoverlapping per instrument regardless of opaque session labels.
Reference facts are ordered by effective start/reference ID per instrument/session.
Declared preserve/unsorted metadata does not waive the checked calculation path.

Eligible trades with supplied price/size require positive nonnull coefficients;
ineligible rows remain and may retain missing prices. Quantities/counts cannot be
negative. Positive-volume bars require positive nonnull supplied OHLC and coherence
low<=open/close<=high. Exact supplied actual notional must lie between low*volume
and high*volume. Zero-volume bars require null OHLC and zero/absent notional;
stale prices require explicit caller normalization. Forming/out-of-session intervals,
negative/nonpositive rational factors and invalid effective bounds fail.
Quotes retain normal/locked/crossed/invalid classifications; nonpositive/null sides
are invalid observations, not schema errors or rows silently excluded from counts.
Negative supplied quote sizes are malformed. No quote expiry/weighted kernel exists.

Supplied SessionSpec enforces matching namespace/session and actual bounds/auction
rules. Market cutoff must be within actual session bounds even for zero-row batches;
this tightens the earlier SessionSpec helper to the accepted EQ-002 C<=close rule.
Known-at checks return typed row exclusions; they do not overwrite timestamps or
filter records. Reconstruction preserves its distinct identity. Without a SessionSpec,
ordinary trade/quote timestamps must be strictly below supplied C; auction exceptions
need explicit supplied session evidence. No reference effective-time lookup occurs.

`ValidationReport` returns row count, missing fields, null counts, knowledge exclusions
and every quote state. Default field requirements are trade price/size, quote bid/ask,
bar/daily OHLC/volume; references have no universal payload requirement. Explicit
`required_fields` replaces that default, allowing independent volume checks on valid
zero-volume/null-OHLC bars. Unknown schema fields fail. Absent optional fields remain
missing for dependent readiness rather than becoming zero. Present malformed eligible
fields fail. `supplied_fields_ready` concerns these requested fields/knowledge only;
it does not certify coverage, source truth, full feature warm-up or numerical results.
Legitimate zero-volume OHLC nulls may be reported while independent volume is ready.

`checked_int64`, `checked_decimal128`, `checked_sum` and `checked_product` perform
exact wide Python arithmetic, then check output representation. Sum validates each
input representation, so out-of-range operands cannot hide through cancellation.
Product operands are int64, output defaults to decimal128; explicit int64 product
raises when necessary. No wrapping. Coverage counts also have int64 bounds.
`require_compatible_inputs` checks namespace, exact unit/scale, quantity unit and
adjustment basis/policy/anchor. Instrument-specific action snapshots may differ and
remain bound separately. Actual identity/horizon/source admission belongs to the
caller and future calculators; this is not a general ticker join or basis conversion.

## Owned opt-in transformations

`normalize_batch(batch, sort=False, deduplicate="reject", price_unit=None,
rounding="exact")` returns `NormalizedBatch(batch,report)` with new immutable columns.
Sort is explicit, using supplied full order keys and deterministic partition grouping.
Deduplication supports only explicitly requested identical rows with matching canonical
identity; conflicting revisions/values fail. No default keep-first/drop correction.
The output is semantically rechecked. Original objects and known-at remain unchanged.

Same-currency scale changes apply to price/bid/ask/OHLC and actual-notional
coefficients; quantities stay unchanged. Upscaling is exact with overflow checks.
Downscaling needs exact divisibility unless caller selects half_even; ties resolve
exactly for either sign. Rounding that creates invalid admitted market values fails.
No FX, action/basis conversion, gap filling or bar proration. Source coverage is
preserved as original delivery evidence, never automatically repaired by dedup;
output row count and original/discarded row indices are separately explicit.

Report records original/output input IDs, row mapping, discarded indices, actual
sorting, original/output price units, dedup/rounding policy and rounded cell count.
A real data/order/scale change binds a SHA256 transform digest into input/mapping
identity while preserving source snapshot. The digest covers columns, metadata,
row mapping and transform policies. A no-op preserves input identity; repeated
normalization is idempotent. Ordered/reject declarations reflect the checked output.
Immutable metadata may be shared safely; this is no zero-copy backend promise.

`quantize_float_prices(values, unit=..., interpretation=..., rounding=...)` requires
concrete float64/None values and explicit policy. binary64_exact uses the exact binary
value; decimal_repr uses its shortest decimal representation. For0.1 at scale2,
decimal_repr/exact gives10 while binary64_exact/exact rejects the binary remainder.
Half-even handles finite nonexact values and records rounding count; NaN/infinity,
Boolean/integer impostors and int64 overflow fail. Result retains unit/interpretation/
rounding; caller must bind this evidence when creating a new canonical source input.

33new/120total unit cases and123existing mathematical references cover independent
order, tie, bar/quote/reference, session/knowledge, missing/null, arithmetic, copy,
identity/dedup, exact/half-even and float interpretation fixtures. Strict typing,
core isolation/boundary, repeat builds, installed tests/examples, exact-head/main CI
and actual main artifact checks precede Done. Author self-review only. The algorithms
here validate/normalize; numerical feature kernels remain R1/R2.
