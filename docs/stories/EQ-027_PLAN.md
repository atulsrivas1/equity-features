# EQ-027 horizon returns and prior extrema — pre-code draft

Issue #32; E05/R2; estimate 8 provisional effort points. Local preparation only;
requires accepted repairs, GOV010 publication and delivered EQ033 before pull.

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
