# EQ-052 — R4 pre-code plan

[Issue59](https://github.com/atulsrivas1/equity-features/issues/59), R4/E07.
Estimate: **8 provisional story points**, not a deadline. Prepared plan only;
no implementation, executed tests or delivery claimed.

## Start and dependencies

EQ049–051; accepted timing/history rules. Reinspect live acceptance and accepted public contracts before pulling.
One active implementation story. Follow [execution package](../R4_AUTONOMOUS_HANDOFF.md)
and [test strategy](../R4_TEST_STRATEGY.md); define concrete interfaces and independently
expected fixtures before source implementation.

## Design

Versioned caller-governed sessions, warm-up and effective/known-at references; freeze calendar/reference support without file-date inference.

## Open questions and source issues

Freeze exact API/configuration/backend pins and supported source populations when
pulled. Unknown precision/availability/eligibility/calendar/reference evidence stays
explicit. A consequential canonical schema/capability change needs a versioned
decision, regression evidence and review. Real instruments/dates/goldens must be
selected from inspected source support, not invented in this preparation.

## Required tests

Holidays/DST/early closes, missing EMA prefix versus finite-window recovery, prior-only baselines, action/membership revisions; gap/reference guide.

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

Explicit supported sessions/history/references; unsupported causal references remain unavailable. Neither a prepared plan nor a source merge establishes this outcome.


## Concrete pre-code design after EQ051 acceptance

EQ049/050/051 issues56/57/58 are Closed/ProjectDone, no other open PR. Accepted
mainaaedb7a8 has successful docs37527287259/Foundation37527287306/optional37527287289,
24 actual archive equality/current20native reports and4unexpired channels; source
FOUR actual forms installed62tests/strict4/measured parity/core invariance. EQ051
Released6024998010/postrelease reread passed. Pull dependency-ready052 only;
053-056 remain planned. Optional0.1.0a4 adds external governance utilities; core
contracts/features/math/schema/dependencies stay unchanged. Reuse accepted
SessionSpec/WindowSpec/HistoryContext/AvailabilitySpec/CanonicalBatch rather than
add another mathematical calendar/history/reference contract to pure packages.

### Calendar and bounded history requests

GovernedCalendar(namespace, version, evidence_id, dated_sessions, closed_dates=(),
grid_kind='supplied_sessions', max_sessions=4096) owns exact ISO-date/SessionSpec
pairs. All labels explicit; namespace/unique dates/IDs/increasing nonoverlapping
bounds/positive size validated. Closed dates cannot overlap supplied session dates.
No sorting, timezone conversion, holiday inference or calendar fetching. DST/early
close behavior is exactly caller-supplied SessionSpec UTCns/scheduled bounds.
For grid_kind='utc_daily_intervals', each explicit date matches UTC midnight and
an exact24h interval. UTCdaily cannot be relabeled exchange RTH; DataKind.DAILY
read requests over supplied RTH sessions are unsupported until callers normalize
compatible daily inputs separately. Supplied SessionSpecs can govern event/bar
reads without inventing source timing. Definition identity binds labels, dates,
actual/scheduled bounds, intervals/flags and declared closures.

plan_history(calendar, window, initialization_anchor=None,
anchor_previous_slot=False, max_sessions=4096)->HistoryPlan uses the existing
WindowSpec.selected_sessions/history_complete. Window governed IDs must exactly
match the supplied calendar. Finite requests use exact selected consecutive slots;
prior_only excludes target; completed_eod includes target. Recursive requests use
an explicit anchor-to-target prefix; anchor_previous_slot additionally retains
an explicitly present predecessor for ATR-style previous close. Never skip a
missing source partition, shorten a denominator or restart an anchor. No feature
values are calculated. Insufficient supplied grid remains visible through plan
history_complete/reason; absent required anchor/predecessor fails unavailable.
The whole governed grid remains available for HistoryContext target structure,
while acquisition selects only the required slots. Bound plan digest includes
calendar/window/anchor policy and exact acquisition dates/session/time limits.

HistoryPlan.acquisition_request(request_id,kind,instruments,snapshot_id,price_unit,
availability,max_batch_rows=1024,max_rows=10000,max_batches=100) constructs the
existing typed AcquisitionRequest from explicit selected slots/bounds. Only
historical market kinds supported, existing completed-interval/event selections
and quote sampling declared explicitly. Insufficient/empty required grid fails
unavailable instead of invented rows. DAILY requires UTCdaily calendar mode;
caller composition may derive RTH daily summaries from admitted intraday inputs
outside acquisition. ReadConfig uses the calendar's version, sessions and exact
partition-session pairs; no file-date calendar inference.

Required counts remain accepted mathematics supplied via WindowSpec: return(h)
needs h+1completed closes; SMA(N) needs N; volatility(N) needs N+1; prior extrema
need N prior-only slots. EMA/RSI/ATR require explicit contiguous anchor prefixes
and their accepted seed/predecessor rules. Config periods/algorithms and actual
public pure calculations remain authoritative; request planning is not formula
admission or sufficient warm-up certification.

make_history_context(calendar, entity, daily, slot_coverage,
initialization_anchor=None, action_admission=None)->HistoryContext verifies supplied
DAILY kind/namespace/one instrument/session IDs/exact session intervals and actual
per-session row presence against caller-provided one-row slot certificates, then
uses existing HistoryContext. Missing slots stay observed0/incomplete; null fields
stay present/unavailable for pure calculation admission. Whole-frame unknown
coverage cannot invent per-slot completeness; caller certificates are explicit
assertions, not provider truth. Supplied certificates cannot claim absent rows.
No sorting/filling/aggregation/price conversion occurs in this helper.

### Supplied reference requests and gaps

ReferenceRequest(namespace, snapshot_id, instruments, fact_kinds, availability,
max_rows=10000) is explicit versioned caller intent for canonical reference facts.
resolve_supplied_reference(request, batch=None)->ReferenceResolution preserves
supplied canonical batch and original effective/known-at/reference identities;
requires kind/namespace/snapshot/requested identities/fact kinds/count/structural
validation. None remains unavailable/not_supplied; incomplete coverage and
unknown/later known-at are visible evidence gaps. These whole-supplied-population
gaps do not replace relevant-fact selection or certify a feature unavailable.
Accepted pure action/classification admission performs effective/C/K/E selection,
revision checks and actual quality. No vendor/FMP file inference, reference SQL,
provider facts, automatic adjusted data or PIT fabrication. Retained DOUBLE action
ratios and present sector files are not silently admitted as exact historical facts.

### Independent expectations before implementation

Temporary actual DuckDB/Parquet fixtures join supplied calendar plans with052 read
requests, preserving known missing slots. Fictional versioned calendar definitions
have a declared closed date, pre/post DST UTC open shifts and an early close with
explicit scheduled close; test exact bounds and exclusion without exchange-truth
claim. Independent integer time expected populations enforce completed UTCdaily
versus unsupported RTH daily distinction.

Five governed daily slots with closes(10,missing,30,40,50), explicit per-slot
certificates and reconstruction reason: target SMA3=40 from slots3/4/5 while
anchored EMA3 remains null/incomplete_coverage. Prior-only two-slot baseline is
(30+40)/2=35 and target mutation cannot enter its request. Return/volatility count
requirements stay documented. Wrong anchor/predecessor, compressed grid, mismatched
slot certificates, duplicate IDs/date/namespace/UTCday, limits and unknown source
partitions fail or remain unavailable explicitly.

Supplied synthetic split/membership revisions retain different snapshot IDs,
effective boundaries and known-at. Use existing pure admission APIs to verify
causal later/unknown evidence unavailable versus explicit reconstruction identity;
no source reference acquisition or fabricated provider completeness. Native bothOS
installed source-form tests, strict typing, existing core invariance, docs and
separate final-head review/CI/actual artifact/main/readback remain before Done.
Real source calendar/reference limitations stay private-explicit and are qualified
under EQ055; no actual slice/golden is frozen by this plan.
