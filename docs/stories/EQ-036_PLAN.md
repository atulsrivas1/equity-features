# EQ036 pure feature composition: pre-code plan

Issue41/E05#31/R2,5points;035 and all delivered numerical family APIs prerequisites.
No implementation before035 Done. Public pre-code review required.

Define FamilyResult(instance_id,result,config,context=None), schema1. Instance ID
is explicit and unique in a supplied bundle; multiple configurations of the same
feature are allowed as distinct instances (different horizons or bucket scopes).
Results remain whole immutable FeatureResults with their original configuration,
metadata, quality and bounded evidence. Never merge columns into a forged common
config or overwrite by feature ID alone. Optional context must be owned
HistoryContext/BucketContext; exact context digest/source role must agree when
required by that family. Do not accept an untyped dictionary or executable callback.
Use explicit companion: SMAReference|VolumeBaseline|IntervalBaseline|ReturnReference|
BreadthResult|None. Each companion's result must equal this instance's actual result;
where it owns config/context those must match the supplied instance config/context.
This preserves exact witnesses and breadth exclusions, not arbitrary callback/maps.
A ratio's prerequisite baseline can be a separate explicitly supplied instance with
its witness; absent prerequisites are never generated. SMAInput's actual config/
context is retained by the instance and its exact SMAReference companion.

Define CompositionSpec(namespace,session,availability,instance_ids), schema1;
instance_ids declared unique ordered list, missing supplied instances remain explicit.
Define FeatureBundle(spec,components,missing_instances), schema1. Pure compose_features
validates concrete tuple input, duplicate/extra IDs, parent namespace/exact target
session/C-K-E, actual component config digest/availability/namespace/target,
algorithm versions and qualified backend. Existing continuous quote backend
python-exact-compensated is allowed alongside actual python-exact kernels with
matching package version; do not force a fake common backend. Whole result may have
multiple entities within its declared namespace/session. Do not require identical
windows, evidence bounds or action snapshot IDs across independent instances.

Validate each supplied config against its exact component result and typed context;
reject stale/mismatched context, not merely string-equal sessions. Validate per-entity
same-component units/basis against actual original source metadata where owned
contracts require it. Independent families may have distinct supported price/quantity
scopes; do not imply a cross-family arithmetic operation. Mode is explicitly batch;
requesting update/merge/restore via composition is unsupported, not hidden fallback.

Cross-component same inputID/kind/metadata must be consistent. Keep original
component proofs/entities instead of remapping whole bundle evidence; contradictory
same original source row/event/known-at across components rejected. Effective/active
intervals, use/exclusion and output entity/feature are legitimate per-feature derived
proof and remain in their original component, not forced equal globally (e.g. quote
age intervals versus event-sampled evidence). No proof can be fabricated when an
instance's evidence limit0 supplies none. Context guards validate exact owned
HistoryContext/BucketContext bindings when required by their producer; unavailable
optional consumers cannot be forced to invent a context they never consumed.
Source authenticity remains caller-owned; configuration digests are identity.
No source reads/dependency calculation/scheduling/output publication.

Independent fixtures: different h1/h5 returns and distinct buckets survive in order;
missing optional family retained; shared exact source identity accepted; conflicting
source revision rejected; duplicate/extra instances and namespace/session/cutoff/
backend/config/context/schema mismatches typed; immutable bundle preserves all
per-component quality/evidence/exclusions; composed values equal original supplied
results, no hidden acquisition or calculation, unsupported modes rejected.

Pair0.0.3a10 planned;39batch/session23update-restore22merge unchanged,16R2 IDs batch
only. Composition is typed orchestration not a new numerical feature/catalog ID.
Public API/graph/example/contracts/package design/changelog/no-impact math decision/
lesson/handoff and issue/PR with code. Exact local/head/repeated archives/BOTH fresh
pairs/SIX checks/guarded main/full tree/docs/bothOS actual bundles/FOUR fresh pairs/
final receipt publication and byte equality before Done. Separate owner-authorized local Codex review plus CI and actual acceptance gates; R3paused; no performance/publication/provider claim.

Reconciled against accepted035 corrected pair0.0.3a9: BreadthResult.result/exclusions schema1; SMAInput holds reference/config/context; metadata includes explicit aggregate/universe identities. Freeze these exact unions and original-versus-derived proof rules publicly before036 implementation. No036code yet.

Concrete wrapper decisions before publication: CompositionSpec has explicit namespace,
SessionSpec, AvailabilitySpec, ordered unique instance_ids, mode=batch/schema1.
FamilyResult validates own ConfigSpec digest/session/availability and cell v1/catalog
IDs, per-component market source namespace/declared unit/supported adjustment policy
alignment; it does not impose a false shared window/evidence limit/action snapshot.
An explicit collection performs no cross-unit arithmetic: distinct valid instance
units are retained, not silently converted/merged. Owned HistoryContext/BucketContext
is required for producer-level consumed context binding; optional consumer children
remain inside actual metadata/companion identities. An owned companion can retain
its already-supplied context; conflicting explicit context/config is an error.
FeatureBundle is an immutable coherent collection in declared instance order, with
missing instances explicit and its digest binding spec plus whole components and
companions. No merged FeatureResult/shared config/backend is invented. Cross-instance
input IDs require exact kind/metadata consistency and original-row event/known-at
proof agreement; derived evidence use/interval/entity may legitimately differ.
Consumer compose_features checks actual qualified package version and python-exact
or python-exact-compensated backend only, rejecting unknown/unqualified IDs/modes.

035 compound-reason corrective pair0.0.3a9 is a prerequisite; its historical0.0.3a8 qualification does not satisfy Done. Composition planned pair advances0.0.3a10, no036implementation before corrected035 acceptance.

## Prerequisite acceptance and review

EQ035 issue40 is Done after actual published main8454c926a6c5970d5e71e48f577dfa5b52bb299d, all final-head/main checks, completed separate local review and BOTH final bundles byte-equal to FOUR fresh installed pairs each561tests/twenty examples. [Acceptance evidence](https://github.com/atulsrivas1/equity-features/issues/40#issuecomment-6007758004). The owner selected a separate local Codex reviewer here; EQ036 will use separate review and record exact final-head coverage/findings/limitations. Hosted GOV005 remains unverified. This plan is committed before EQ036 source changes.

For declared ordered I and supplied component map F, output order is I filtered to supplied keys, missing list is I minus supplied keys in original order. Each supplied value, original quality/evidence and exact witness/companion is preserved unchanged. Bundle identity binds the full spec and supplied immutable components including companions; missing components never generate values or dependency execution. These are collection semantics; no numerical equation changes. Reject ambiguous instance identity or contradictory original source proof; preserve valid distinct per-feature derived proof.

## Pre-code separate-review refinements

The separate local reviewer found a normalized-frame ownership ambiguity: direct daily_history bindings represent one context instrument, and bucket_history represents one instrument/declared bucket. Global identical input metadata and original event/known-at cannot alone establish compatible ownership, especially with evidence_limit0. Bind each such inputID to its owned context instrument (and normalized VolumeBucket scope for bucket_history); reject cross-instance conflicting owners even when no evidence is retained. Same instrument/frame may be reused across horizons; distinct instruments/buckets use distinct source identities as required by their actual producer. These checks validate declared structure, not source authenticity.

Qualified backend selection is feature-specific: python-exact-compensated belongs to the continuous quote family; other delivered families use python-exact. Check current qualified package version plus exact configured/default evidence_limit for every instance. Optional companions preserve supplied witnesses; composition never invents a missing witness or dependency. Final review must cover these guards and the release receipt, with actual findings disposition.
