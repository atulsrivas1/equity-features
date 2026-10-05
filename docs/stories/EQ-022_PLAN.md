# EQ-022 — continuous time-weighted quotes plan

Prepared before code, issue26/epic20/R1; confirm13points. Pull only after EQ021
verified Done. Preserve EQ095/PR120 and one active story; author review+CI.

## Interface/admission

`compute_time_weighted(batch: CanonicalBatch | None, config: ConfigSpec, *,
entity: EntityKey, seed: CanonicalBatch | None = None) -> FeatureResult` implements
only session.quote.time_weighted_spread. Parameters eligibility_policy,
max_age_ns (exact integer1..int64max), initial_state enum seed/inactive/unknown.
No observed-row retention parameter needed; source rows are caller-owned.
Require continuous sampling, EQ021 canonical source/unit/basis/order/target/coverage/
C/K/E checks; trade snapshots reject. Window duration C-open must fit int64.

Seed mode accepts separately supplied one-row continuous canonical quote with
full bid/ask fields (explicit null permitted), original event<open inside declared
preopen InputScope ending<=open, complete coverage1, matching namespace/entity/
unit/basis/policy and compatible source_id/mapping. Snapshot IDs remain bound
separately; input_id must differ from target, seed eventID must not duplicate any
target ID. Original event anchors expiry; no reset at open. Target quote at open
is an update, never seed. Seed unknown/future knowledge or absent seed contributes
unknown left-boundary time, without consuming its state; exclusion evidence/reason
records unavailable seed. Inactive/unknown modes reject extraneous seed. No fetch.

## Integration and result

Maintain last full state, original event/expiry, integration cursor and six exact
durations: normal/locked/crossed/invalid/expired/unknown. Split every interval at
min(next admitted update, original_event+max_age,C), clipped to open. Use wide
Python expiry arithmetic and clipped checked durations; no int64 addition wrap.
At exact expiry state expired. Invalid/crossed replace previous valid; no carry
through them. Equal-time rows all have observation identity but earlier state has
zero duration and last ordered update governs positive time. Excluded/unknown
knowledge target rows make published result unavailable; no causal filtering into
false complete coverage. Known feed gaps declare incomplete source, never bridged.

Typed QuoteDurations enforces category sum C-open and Dvalid=normal+locked.
TimeWeightedSpread contains durations, null-or-finite valid means, max_age_ns,
initial_state, and derived valid fraction. Mean spread exact checked decimal128
sum((ask-bid)*dt)/(Dvalid*10^scale); bps individual exact Fraction conversion with
compensated sum(z*dt)/Dvalid. rtol/atol1e-12; counts/durations exact. Complete
initialized Dvalid>0 available even with known crossed/invalid/expired time;
Dvalid0 means null/not_applicable with known diagnostic cell. Complete source but
unknown left duration ->null means/incomplete_coverage with typed durations.
Absent source ->null/missing_input; incomplete delivery ->null/incomplete_coverage
because unknown gap positions cannot certify observed category durations.

FeatureResult evolves narrowly for typed NA/initial-unknown cells, checking source
continuous sampling, complete target coverage, scope duration and status/denominator.
Arrow typed nested structs with duration int64. Root metadata binds target/optional
seed separately and config choices. At most one seed evidence row (consumed or
excluded); no unbounded per-update evidence or fake full-source proof. Reusable
integration state retains fixed counters, exact numerator, compensated pair and
one current state; canonical batch validation/copy cost remains input proportional.

## Independent verification/delivery

Offset window[100,112), updates100 normal100/102,103 locked102/102,107 crossed
105/104,109 invalidnull/102; age6: durations normal3 locked4 crossed2 invalid3,
valid7; mean spread6/7, bps60000/707, validfraction7/12. Test preopen seeds and
original expiry, already-expired/unknown/inactive starts, seed unavailable/duplicate/
incompatible, no updates, equal-time replacement, expiry exactly boundary,
invalid/crossed replacement, C/end/early-close, snapshots rejection, coverage gaps,
near-int64 times/duration/weighted products, wide midpoint and independent exact
integral oracle. Preserve274 units/R0/123references;23 batch IDs and discovery
example23. Version both0.0.2a5; eighth installed synthetic example, API/state diagram,
contracts/registry/release/continuity/EQ021 receipt. Full lifecycle/head/main gates
and actual bundles/four fresh installs before Done; no streaming capability yet.
