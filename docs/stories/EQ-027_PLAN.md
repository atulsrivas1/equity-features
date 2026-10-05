# EQ-027 horizon returns and prior extrema — pre-code plan

Issue #32; E05/R2; estimate 8 provisional effort points. Pulled after verified GOV010/BUG003/BUG004 and EQ033 Done. Accepted baseline
main d3e9fc9c2c2f4d5b7892cd96ffefc3d1f15badad, pair0.0.3a0. Eight points confirmed
as complexity; next experimental pair0.0.3a1.

## Frozen mathematics and live acceptance

Three existing IDs: history.return uses h+1 complete governed closes including
target, even though only endpoints enter C[t]/C[t-h]-1. Prior high/low use N slots
before target; target/future values cannot influence them. Defaults h=1/5/20/60/252
and extrema N=20/60/252. Missing slots stay in the grid; no inferred calendars,
sorting, duplicate removal, zero filling, gap compression or source lookup.

## Concrete contract and callable

Add immutable HistoryContext(schema_version=1, entity, grid_version,
sessions: tuple[SessionSpec,...], slot_coverage: tuple[Coverage,...],
initialization_anchor: str | None, action_admission: PolicyAdmission | None).
This extends governed context rather than replacing canonical rows/config/results
with dictionaries. Owned tuples require unique increasing nonoverlapping sessions,
one coverage certificate per slot and namespace/target consistency. Daily batch
may omit a governed slot; coverage then reports unavailable for that slot. Future
rows may be present structurally but only selected dependencies enter arithmetic,
knowledge readiness and consumed evidence. Row/session/bounds/grid mismatches and
duplicate IDs raise typed errors. Context identity binds exact session bounds,
coverage/anchor/grid/action identities and source/config revisions.

`compute_history(batch: CanonicalBatch | None, config: ConfigSpec, *,
context: HistoryContext, feature_ids: tuple[str,...]) -> FeatureResult` initially
accepts these three implemented IDs only. Parameters are a single explicit positive
integer period per invocation; callers request distinct period configurations.
No duplicate feature/entity keys are created for multiple horizons. WindowSpec
and parameter count/anchor must agree: return completed_eod count=h+1; extrema
prior_only count=N. Required target mode is explicit. Config policy/price unit/
namespace/basis and supplied EQ033 admission bind all dependencies.

Output FeatureResult Float64 in stated units with expected/observed/reasons and
bounded consumed/excluded evidence. Absent batch/column=missing_input; too few
governed slots=insufficient_history; null/missing/uncompleted selected slot or
incomplete certificate=incomplete_coverage; unknown/future knowledge=missing_input.
Independent high/low readiness does not require close. Use exact integer extrema
and rational endpoint arithmetic; convert only final values. Wide sums/products
must not wrap. No update/restore/merge advertised by this first story; later
indicator plans own qualified bounded state, if supported.

## Independent tests and documentation

Actual API tests: golden h3=5/21 and prior high122/low103; defaults on sufficiently
long synthetic grids; period1; valid endpoints with a missing middle close;
target/future mutation invariance for prior extrema; selected/future knowledge;
prior extrema before target close; minimum/empty/absent history; absent high/low
independence; wide int64 endpoints; duplicate/unordered/bounds/unit/basis/config
errors; ownership and identity changes. Expected values derive from exact fractions
and hand computations, not production helpers. Preserve repaired session tests
and123 formula references. Extend registry only for delivered modes/IDs.

Public HISTORY API/context schema guide, installed synthetic example, changelog,
version decision, package scope and continuity accompany implementation. Commit
this plan before code after actual dependencies pass. Self-review plus exact-head
CI, repeat archive/installed gates, published main bytes/main bothOS CI, actual
bundle manifests/hashes/content and four fresh pair installations precede receipt,
Released and Done. Plan publication or source merge alone does not complete #32.


Contract refinement completed during EQ033 gates and frozen before EQ027 source code.
ResultMetadata's existing typed InputBinding can bind caller-owned grid context
with role history_context, source_id caller-history-context, snapshot_id=grid_version,
mapping_version=history-context-v1 and input_id=context identity digest. This
represents the supplied context, not a fetched/provider reference. Exact sessions,
slot certificates, initialization anchor and action admission are hashed; existing
ResultMetadata schema1 stays unchanged. Price metadata/inputs additionally bind
actual data revisions, quantity policy and C/K/E through config/action evidence.

HistoryContext checks one expected row per slot (Coverage.expected=1, observed0/1),
unique increasing nonoverlapping SessionSpecs and typed optional ActionPolicyAdmission.
Context certificates bind actual row presence: absent slot cannot be certified
observed1. Present close=null in an observed row is still unavailable. All batch
rows must map to governed sessions/exact session bounds in grid order; future
valid rows are structurally checked but outside selected windows do not affect
arithmetic/knowledge readiness. Never apply whole-frame incomplete coverage to a
fully certified selected window; actual batch observed count must still match.

Config parameters: period explicit positive int, evidence_limit optional int>=0
(default0). Window count=h+1 completed_eod for return, count=N prior_only for
extrema. Return and extrema must be separate invocations because their frozen
membership/anchor differs; prior_high/prior_low may share a call. Selected high/low
readiness remains independent. Output evidence stays bounded and uses original
completed_interval row/event_ns=end_ns with original known_at. Selected unavailable
knowledge rows are excluded diagnostics; no future rows become consumed evidence.

Registry must separate session batch IDs from all batch IDs before adding history:
existing UPDATE_IDS=BATCH_IDS alias would otherwise falsely advertise new update/
restore capability. History batch additions do not change session-only update,
restore or22 conditional merge inventory. Independent registry tests verify this.


API/config compatibility: the existing exact-version session state rule remains;
EQ027 pair0.0.3a1 does not migrate saved0.0.3a0 accumulators despite schema2 being
unchanged. Price outputs are final Float64 values from exact scaled coefficients;
return endpoints use transient Fraction with rtol/atol1e-12. Include explicit
ActionPolicyAdmission compatibility (entity/config digest/availability/basis) in
history validation, and include its reference binding in result metadata. Raw
history may use None policy admission because no adjustment is required; supplied
raw action context remains source binding, not neutral-return certification.

Policy readiness must remain independent from invalidation: mismatched admitted
identities are typed errors; unavailable but compatible action evidence produces
unavailable dependent historical results, with original reasons retained. Readiness
for future/nonselected slots is not propagated. Metadata's history_context hash
binds every supplied session/certificate; whole-context identity changes are honest
source differences even when a selected mathematical result is invariant.
