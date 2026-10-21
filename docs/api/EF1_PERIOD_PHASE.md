# EF1 period and extended-phase API — EQ166

The opt-in `equity_features.ef1` API now has the bounded `period` and `extended`
producers. Use unchanged `build_ef1_config`, `decode_ef1_context`,
`ef1_definitions` and `compute_ef1(batches, config, entity=...)`. The reviewed
[contract](../ef1/PERIOD_PHASE_CONTRACT_PROPOSAL.md) and
[source freeze](../ef1/PERIOD_PHASE_SOURCE_AUTHORING_FREEZE.json) govern this
subset. Canonical schemas, codec, defaults and package versions are unchanged.

Period returns all nine `calendar.period` headers; extended returns all eight
`session.extended` headers. Discovery describes the complete family, units and
exact dependencies. Execution is batch/full supplied replay only, without
incremental state, provider acquisition, service or storage in calculations.

| Producer | Present-role subsequence passed to pure call |
| --- | --- |
| period | calendar_provenance: REFERENCE, daily_history: DAILY, bars: BAR |
| extended | calendar_provenance: REFERENCE, bars: BAR, prior_close: DAILY |

Pass actual present batches in declared order, omitting unavailable roles.
Observed empty batches remain present; `None` is not a batch. Adapter containers
and worker manifests retain every nullable slot independently. Actual kind
uniquely identifies each role. Reordered/duplicate roles and input IDs reject.

The exact mathematical envelope is `{version,producer,calendar,selection}`,
version `ef1-context1`, encoded as existing `ef1_context_json` Parameter. Period
selection is exactly `{period_id,kind,count,start_date,end_date_exclusive,inclusion}`.
Kinds are week/month/year/rolling_weeks/rolling_months; inclusion is
current_to_cutoff/prior_complete. Declared dates must equal derived civil
boundaries. Extended selection is exactly `{phase}`, premarket/postmarket.
Both require nonnull mathematical calendars and actual causal calendar proof
for available results. Every extended window contains explicit predecessor and
target, including all before-start/empty branches.

Market scopes declare `supplied_period` or `supplied_phase`, exact original
auction flags and interval coverage. DAILY intervals name each required session;
BAR intervals are `period_prefix` or `phase_prefix`. The library preserves full
actual metadata and original rows. It does not manufacture coverage, construct
bars from trades, guess a predecessor or create a zero-width scope. See
[formulas/readiness](../features/EF1_PERIOD_PHASE.md).

```python
from equity_features.ef1 import compute_ef1, ef1_definitions

definitions = ef1_definitions(config)  # complete nine- or eight-header family
result = compute_ef1(present_batches, config, entity=entity)
```

The [frozen synthetic packets](../ef1/PERIOD_PHASE_CONTRACT_PROPOSAL.json) contain
complete configs, original inputs and independently expected results.
PERIOD_BASE gives open10, close13, volume5, notional57, return0.3, scheduled2,
completed1. EXTENDED_BASE gives open8, close10, volume5, notional46,
open-close return0.25 and predecessor-close return1.0. Source tests exercise
the actual API; installed three-layer/browser demonstrations remain separate.

This bounded subset does not implement observed-session counts, fixed-observation
lookbacks, native trade construction, alternate change denominators or periods
beyond existing64-session/4096-byte bounds. Original regular-open and full
inventory/consumer bindings remain release obligations. No original/private
numerical parity or release is claimed.
