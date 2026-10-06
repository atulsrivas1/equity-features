# EQ035 declared-universe breadth pre-code plan

Issue40/E05#31/R2,8provisional points;028/034 supplied references prerequisites.
Prepared during032/034 gates; final034 ReturnReference(result,config,context) API
reviewed at source9a89cf8. No035 implementation before034 verified Done. One active implementation story, batch only.

Declared immutable unique U preserves expected M even when members lack data.
Direction counts A(r>0),D(r<0),Z(exact0) from available compatible supplied returns;
E=A+D+Z, coverage E/M. No epsilon or zero fill. Above-SMA K(close>exact SMA), Eeligible,
fraction K/E, coverage E/M. Equality not above; compare exactC*N-sum using existing
SMAReference witness, never rounded Float64 means or hidden recalculation. Partial
U retains explicitly partial structured counts/fractions with incomplete_coverage;
E0null/quality0ofM, emptyU not_applicable, absentU missing_input.

Define DeclaredUniverseSpec(namespace,session_id,universe_id,membership_identity,effective_ns,
members:tuple[str,...]), schema1, owned unique opaque IDs in declared namespace.
Caller declaration binds membership selection and evaluation point, not provider
truth; derived metadata is a supplied definition, not an observed market frame.
Effective point inside target [open,close),<=C, explicit identity. Reject duplicate/
extra supplied members and mismatched namespace/session. Do not infer universe from
available values. Source classification admission may be retained when explicitly
supplied, but declared U does not require hidden membership lookup.

Define CompletedClose(entity,coefficient,known_at_ns,source,row_index,interval,
coverage), schema1: positive int64 coefficient orNone, original DAILY/BAR source
binding/count/index/PriceUnit/adjustment, exact full actual target session bounds;
completion<=C, known-at policy, complete selected certificate. No fake one-row
metadata. Define SMAInput(reference:SMAReference,config,context:HistoryContext),
schema1, validating exact original SMA result/config/context/period/units/basis/
source/availability/current consumer backend compatibility. Existing exact witness
provides numerator/count; no dependency computation.

Define MemberFeatures(entity,return_reference=None,sma=None,close=None), schema1,
owning supplied034 ReturnReference/current SMAInput/CompletedClose. Requests only
consume corresponding family; unavailable optional fields remain distinct.
Define BreadthSpec(entity) explicit aggregate output entity/session, and typed
MemberExclusion(entity,feature_id,status,reasons). Return BreadthResult(result,
exclusions), schema1, retaining standard FeatureResult plus exclusions for absent
members without manufacturing EvidenceRow price observations.

Separate compute_direction_breadth and compute_above_sma_breadth calls accept owned
member tuple|None,ConfigSpec,*,universe|None,spec. Parent explicit period/window is
return h+1completed_eod versus SMA Ncompleted_eod respectively; no mixed config
pretending one horizon fits both. Align requested child selected grid/target/period/
price scale/currency/adjustment/algorithm/C-K-E with parent, preserving distinct
actual child config identities/evidence bounds. Output standard existing structured
BreadthCounts/BreadthFraction cells, no new output dtype. Quality expectedM/observedE.
Provided empty member tuple for nonempty U yields incomplete E0; absent dataset
None yields missing_input; empty U yields not_applicable, extras still errors.
Malformed requested dependencies are typed errors; unavailable compatible member
values exclude only that member with retained reasons. Above-SMA requires both
admitted completed close and SMA. Use exact comparisons including int64-limit
half-tick case where Float64 price/mean round equal.

Retain original member source/derived context/reference/certificate identities,
role-prefix by explicit member/component, exact inputID/kind/metadata dedup only;
conflicting reused IDs fail. Different-instrument normalized daily frames require
distinct frame IDs under current history ownership. Parent evidence maps to aggregate
output entity/feature but keeps original input/index/event/known-at/bounds; child
reference identities retain original member association. Exact original-row proof
deduplicates, conflicting collision fails even with output evidence limit zero/full;
a separate transient validation map checks every supplied proof. Global retained
output evidence limit enforced. Member
exclusions are typed companion data, never fake observed rows. Source truth remains
caller-asserted. Preserve original known-at in reconstruction.

Independent fixtures Uabcd returns+.1,-.05,0,missing =>(1,1,1),E3/M4,3/4partial;
all available/zero/all unready/absent/empty U; duplicate/extra/membernamespace;
above closes11,9,10,missing vsSMA10=>K1/E3/fraction1/3/coverage3/4; exact int64
half-tick comparison despite Float64 equality; missing close/SMA and independent
per-member exclusions; unit/basis/period/grid/version/C-K-E/source conflicts,
future/unrelated mutation and admitted revision identity, reconstruction/bounded
original indices/ownership/malformed witnesses; truthful two batch flags/allstatefalse.
Preserve prior unit/123formula suites, no throughput claim.

Pair0.0.3a8 completes39batch IDs (all16R2numerical) while session23update/restore22merge
and existing schemas/39equations unchanged. New companions schema1; version-bound
caller state/registry replay/rebuild explicit. Public API/math/contracts/design/
example/changelog/lesson/continuity and issue evidence with source. Author self-review
+CI only; all local/head/repeatarchives/freshpairs/SIXchecks/guarded merge/main tree/
docs/bothOS actual bundles/FOURfreshpairs/final receipt/byte equality before Done.
No source/provider/private copy/performance/state/stable/tag/PyPI; R3paused.

Concrete035 contract review against034/028: SMAInput validates single v1 SMA cell/entity, actual config digest/evidence limit/availability/namespace/session/backendID, explicit periodN>=1/windowcountN/completed_eod, exact governed target/selected certificates, source price/adjustment metadata, exact history_context binding, available daily observed>=N/historycomplete/targetclose<=C/available action proof. Available SMA witness denominator==N and Float64 projection are already owned SMAReference guards. Unit/witness alignment does not authenticate coefficients. ReturnReference requires h+1 window. Both consumers align exact selected SessionSpecs/grid versions across members, allowing per-instrument action snapshot identity only under common supported policy/anchor. CompletedClose absent coefficient remains distinct from unknown knowledge and incomplete source certificate, preserving requested exclusion precedence. Avoid importing calculation helpers into contracts.
