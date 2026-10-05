# Governed historical windows

EQ027/pair0.0.3a1 introduces batch `history.return`, `history.prior_high` and
`history.prior_low`. [Frozen mathematics](../features/HISTORICAL_FORMULAS.md),
[pre-code plan](../stories/EQ-027_PLAN.md), [delivery](../stories/EQ-027_DELIVERY.md).
No history update/restore/merge capability is advertised. Existing session modes
remain23 batch/update/restore and22 conditional merge; total batch inventory is26.

## Owned context and calls

`HistoryContext(entity, grid_version, sessions, slot_coverage,
initialization_anchor=None, action_admission=None, schema_version="1")` owns typed
tuples. Each `SessionSpec` gives exact supplied UTCns bounds and calendar identity.
Sessions are unique, increasing, nonoverlapping and share a namespace; target must
exist. Each `Coverage` expects one normalized daily row, observed0or1. A missing
row has observed0/incomplete; an observed row with null close stays unavailable.
Certificates must match actual row presence, including future structural slots.
No calendar lookup, sorting, holiday inference, gap compression or zero filling.

```python
from equity_features.history import compute_history
result = compute_history(batch, config, context=context,
                         feature_ids=("history.return",))
```

The canonical DAILY batch belongs to one instrument; rows follow the supplied
grid and match exact session bounds. Metadata namespace, price unit, adjustment
and actual observed row count must agree. Structural validation checks all rows;
only selected windows enter arithmetic and knowledge readiness. Future valid
rows/knowledge cannot change selected values. Whole-frame incomplete coverage
does not override complete compatible per-slot certificates for a selected window.

ConfigSpec carries explicit positive integer `period`, optional nonnegative
`evidence_limit` (default0), v1 algorithm, target SessionSpec, grid and price unit.
For horizon h, WindowSpec.count=h+1 and anchor=completed_eod. For extrema N,
count=N and anchor=prior_only. Return and extrema use separate invocations because
their membership differs; high/low can share one invocation with independent
quality. Defaults1/5/20/60/252 and20/60/252 are supported as explicit period configs,
not multiple ambiguous value rows under one identity.

## Membership, precision and readiness

Return requires all h+1consecutive governed closes including target, even though
arithmetic is Ctarget/Cstart-1. Missing middle close is unavailable despite valid
endpoints. Prior high/low use exactly Nprior slots and exclude target; they can be
ready before target close. Missing high does not erase available low or close.
Finite windows recover only when their own exact selected slots recover.

Return uses transient exact rational endpoint arithmetic and converts only the
final fraction to Float64. Extrema compare exact int64 coefficients, then convert
coefficient/10^scale to currency/share. Price-bearing values must be positive;
nulls remain null. Wide near-equal endpoints preserve small nonzero returns.
Qualification tolerance is rtol1e-12/atol1e-12; no throughput/backend claim.

`FeatureResult` carries Float64 keyed columns and independent quality. Missing
batch/field gives missing_input; too few governed slots gives insufficient_history;
selected missing/null/uncompleted/incompletely certified slots give
incomplete_coverage. Unknown/later knowledge gives missing_input. Expected count
is the exact required window count; observed counts field-ready completed/known/
certified slots. Values remain null when unavailable. There is no denominator
shrinking or manufactured zero. Reconstruction permits later/unknown knowledge
with original known-at preserved and a distinct C/K/E/mode/reason identity.

## Adjustment, identity and evidence

Adjusted history requires compatible [EQ033 policy admission](ACTION_POLICIES.md)
in context, with exact entity/config digest/availability/output basis. A mismatched
policy is an identity error; compatible unavailable action evidence keeps dependent
history unavailable. No hidden factor application occurs here. Raw history may
omit action admission only under raw-v1; it represents raw price change, not
split-neutral or shareholder return. Declare the same quantity/price policy for
later consumers; an admission does not authenticate vendor facts.

ResultMetadata retains actual daily/reference InputBindings and one derived typed
history_context binding. Its source_id=caller-history-context and
mapping_version=history-context-v1 distinguish a caller-owned context from an
acquired provider reference. Its coverage counts supplied grid definitions, not
available price slots. Snapshot ID is grid_version; input_id hashes exact
sessions/certificates/initialization/action identities. Config digest and actual
data bindings retain cutoffs/units/revisions. Changing supplied context/source
changes identity even when a selected mathematical value stays equal.

Optional evidence is globally bounded by evidence_limit and deterministic requested
feature/window order. It retains original daily row index, session bounds and
known-at, with completed_interval end-time consumption or typed exclusion reasons.
No future row is consumed. Original action evidence remains in HistoryContext
and its reference binding; neither hashes nor certificates authenticate source truth.

The new package version preserves state schema2 but exact-version session restore
requires matching implementation versions. Replay/rebuild older saved accumulators;
no migration or history state API. Registry snapshot builtin_digest changes when
batch capabilities change; reconstruct discovery from the matching package rather
than silently loading a prior incompatible snapshot. Input/config/result schema1
remains unchanged; HistoryContext is a new schema1 owned contract.

Run [history_windows.py](../../examples/history_windows.py) against installed packages.
