# Supplied sessions, windows and deterministic configuration

EQ-012 implements these experimental0.0.1a2 contracts. No calendar/timezone
lookup or wall clock is consulted. Callers supply UTCns boundaries and govern
calendar order; labels identify that supplied interpretation without discovering it.

`IntervalSpec(name,start_ns,end_ns)` is half-open with positive duration.
`SessionSpec(namespace,session_id,open_ns,close_ns,timezone_label,intervals,...)`
holds actual bounds, optional scheduled close, explicit early-close and Boolean
opening/closing auction policies. Named intervals must be within actual bounds;
no synthetic buckets after an early close. Supplied intervals may overlap for
independent feature windows. Early close requires a later scheduled close;
contradictory declarations fail. Lists become owned tuples; generators are rejected.

`session.admits_event(event_ns,cutoff_ns,auction="none",quote=False)` admits ordinary
open<=event<min(C,close). An explicitly labeled opening auction needs inclusion,
event=open and event<C. An explicitly labeled closing auction needs inclusion,
event=close and C=close. Quotes have no auction exception. This predicate checks
bounds/policy only; EQ-014 now rejects C outside actual open/close bounds; caller eligibility, coverage and semantic batch validation
remain separate. It does not turn a forming bar into completed EOD evidence.

`AvailabilitySpec(market_cutoff_ns,knowledge_cutoff_ns,evaluation_ns,mode,reason)`
preserves C/K/E. Known-at mode requires C<=E and K<=E and cannot carry a
reconstruction reason. `knowledge_reason(known_at)` returns None when knowledge
is admitted, unknown_availability for null, future_knowledge for known_at>K.
Equality is admitted. Market bounds are checked separately; known-at admission
alone never grants market eligibility. Reconstruction requires an explicit nonempty
reason and permits later/unknown knowledge while preserving actual supplied times.
It is a different configuration identity and carries no causal availability claim.
A later E admits delayed EOD knowledge; close alone does not establish delivery.

`WindowSpec(count,target_session_id,governed_sessions,anchor)` uses unique supplied
ordered session IDs, including target. Prior-only selects up to count slots before
target; completed_eod includes target. Future IDs do not enter selection. Missing
market data does not remove a governed ID. `history_complete` means enough governed
slots exist, not that their inputs are observed/available; coverage and readiness
remain separate. The library neither infers holidays nor sorts session labels.

## Canonical configuration

`Parameter(name,value)` admits only exact str/int/float/bool/None types; floats
must be finite. No containers/callables or mutable custom scalar objects.
`ConfigSpec(identity,algorithm_version,parameters,session,window,availability,
adjustment,price_unit,schema_version="1")` owns parameters sorted by unique name
and rejects target mismatch. Semantic meaning must be expressed by algorithm
version/parameters; digest alone does not certify a formula or provider input.

`to_json()` uses ASCII-escaped sorted keys, compact separators and schema1.
Float parameters are tagged with Python's exact finite binary64 hex representation,
preserving signed zero rather than depending on decimal rounding. Other scalar
types retain JSON type distinctions. `from_json(text)` parses in-memory text,
rejects duplicate/unknown keys, unsupported versions and nonfinite/malformed
values, and revalidates all components. It never loads executable objects. Parsed
noncanonical whitespace/order normalizes through `to_json()`. This is a versioned
configuration convention, not a remote authorization or general state wire protocol.

`digest` is SHA256 of the canonical UTF-8 JSON. It binds algorithm/config identities,
parameters, actual/scheduled session bounds, timezone label, intervals/auction rules,
window/governed IDs, C/K/E/mode/reason, price units and adjustment snapshot/anchor.
Result contracts separately bind source inputs/backend identities in EQ-013.
Parameter insertion order is irrelevant to object equality, JSON and digest.

```python
from equity_feature_contracts import (
    AvailabilitySpec, ConfigSpec, Parameter, SessionSpec, WindowSpec,
)
config = ConfigSpec("demo:volume-baseline", "v1", (Parameter("window", 2),),
    SessionSpec("demo", "S3", 100, 200, "caller-zone"),
    WindowSpec(2, "S3", ("S1", "missing", "S3", "future")),
    AvailabilitySpec(200, 210, 210))
assert config.window.selected_sessions() == ("S1", "missing")
assert config.availability.knowledge_reason(None) == "unknown_availability"
assert ConfigSpec.from_json(config.to_json()) == config
assert len(config.digest) == 64
```

27new unit cases plus28canonical input cases verify exact UTCns bounds, auctions,
early closes, causal equality/future/unknown knowledge, explicit reconstruction,
governed gaps, deep ownership, scalar/version/JSON negatives, parameter order,
round trips and a fixed schema1 digest compatibility fixture. Numerical calculators,
result errors/statuses and semantic normalization remain later stories. Source merge
alone is not delivery; exact-head/main CI and verified installed main artifacts gate
Done. Author self-review only; no independent review or throughput claim.


EQ033 adds immutable schema1 ActionPolicy/ReferenceFact/PolicyAdmission/AdjustmentApplication/ClassificationAdmission; ConfigSpec/AvailabilitySpec/AdjustmentSpec schema1 remains unchanged. [Signatures, versions and readiness](../api/ACTION_POLICIES.md) bind original factors/revisions/known-at and explicit quantity basis.


EQ027 adds owned HistoryContext schema1: exact SessionSpecs, per-slot certificates, target/grid/anchor/action identities. Existing ConfigSpec schema1 is retained; [history API](../api/HISTORY.md).


EQ028 adds immutable SMAReference schema1 alongside an unchanged FeatureResult; exact sum/count projection, unit/quality and price comparison guards are documented in the [history API](../api/HISTORY.md). ConfigSpec/HistoryContext schema1 stays unchanged.


EQ029 retains HistoryContext/ConfigSpec schema1; the initialization anchor is a close anchor for RSI and TR anchor for ATR, in separate calls/configurations. [Membership/precision](../api/HISTORY.md).


EQ030 retains schema1 and uses optional positive int64 annualization_factor default1 only for volatility, with N+1close WindowSpec. Config identity records supplied conventions; [API](../api/HISTORY.md).

EQ031 supplies owned schema1 VolumeBaseline and TargetVolume, exported from contracts. Exact baseline witness/config/context and original target source/row/selected scope preserve dependency identity, complete EOD versus explicitly observed BAR prefix and quantity basis. Existing PriceUnit metadata requirement is retained for volume-only market rows. [Detailed API](../api/DAILY_VOLUME.md).

EQ032 exports immutable VolumeBucket, BucketContext, IntervalBaseline and BucketVolume schema1. Exact open-relative bucket grids, per-bucket presence/coverage, original source-row proof, early-close ineligibility and full elapsed versus partial target bounds are explicit. Daily coverage is not bucket coverage. [API](../api/INTERVAL_VOLUME.md).
