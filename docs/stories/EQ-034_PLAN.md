# EQ034 supplied benchmark and sector return comparisons pre-code plan

Issue39/E05#31/R2,5provisional points;027/033 prerequisites Done. Pre-code preparation while final032 receipt gates run; no implementation until032 is verified Done. Publish before code.

Arithmetic simple-return difference r_symbol-r_benchmark, Float64 fraction; no
ratio of gross returns, percentage-point storage, benchmark calculation, FX,
calendar interpolation or source lookup. Market and sector readiness independent.

Define ReturnReference(result,config,context), schema1, owning a single v1
history.return Float64 fraction result and its exact ConfigSpec/HistoryContext.
Validate entity/namespace/target/grid/periodN+1completed_eod window/price metadata/
basis/availability/config/context/source bindings and algorithm. Available proof
requires complete selected closes/target completion and compatible available action
admission, not just scalar presence. Unavailable states retain typed reasons and
identities. Consumer checks current qualified backend version; source truth is not
authenticated. Never recompute endpoints/dependency from missing data.

Define SectorBenchmark(sector_id,entity) and RelativeSpec(entity,market_benchmark=None,
sector_benchmark=None,membership_effective_ns=None), schema1. Explicit benchmark
entities bind instrument and target session; same explicit namespaced governed
calendar/selected endpoints is supported v1, no implicit cross-namespace join.
Sector classification text matches explicit sector_id, NOT assumed equal to benchmark
ticker. Sector supplied return entity matches SectorBenchmark.entity. Membership
point is explicitly caller supplied inside actual target [open,close), <=C, and
retained in spec identity; no default open/close guess. Sector-only requirements do
not prevent market calculation. Missing membership/sector affects sector only.

compute_relative(symbol|None,market|None,sector|None,membership|None,config,*,spec,
feature_ids)->FeatureResult. Config supplies parent target/window/availability/unit/
adjustment/period/evidence limit, independent identity retained. Child configs may
have different identities/evidence bounds but must align period/horizon/exact
selected SessionSpecs/start-end IDs/grid version/window endpoint mode/price scale/
currency/adjustment policy and C/K/E. Child action admissions remain bound to their
actual child configs; parent never fabricates a common child digest. Supplied
ClassificationAdmission binds symbol entity/namespace, sector_membership kind,
exact chosen effective point and parent config digest/availability; unready admission
propagates typed status. Incompatible identities are errors, no ticker-only match.

Retain component source/derived context/reference/dependency identities, preserving
source metadata/count/revision. Role prefixes distinguish components; identical
sourceID/kind/metadata can be retained once, conflicting reused identity fails.
Different-instrument normalized DAILY frames must not reuse one input ID because
current history producer owns one instrument/frame; explicit frame identities are
required. Shared reference tables may retain identical original frame metadata.
Bounded component evidence maps to output symbol entity/relative feature while
retaining original source row/index/event/known-at/bounds and derived full child
reference identity; exactly identical original-row proof deduplicates, conflicting
collision errors. Do not fake benchmark source rows or attach evidence to nonexistent
output entities. Market quality2dependencies; sector quality3including membership.
Missing/unready operands precede arithmetic; retain independent availability.

Independent API fixtures:100->110 versus200->210 gives1/20 difference; direct
gross-return-ratio distinction; sector missing versus ready market; explicit sector
ID->benchmark mapping; unknown/expired/future/reconstruction membership; first/
last and mid-session chosen points; mismatched horizon/start-end/grid/C-K-E/currency/
scale/basis/algorithm/backend/source revisions/entities; null/coverage/warm-up
propagation; immutable/malformed references; no dependency calculation; bounded
original source/evidence identities; future/unrelated memberships cannot change
admitted values; two truthful batch flags, all state modes false. Preserve prior
units/all123reference fixtures, rtol/atol1e-12 in declared fraction units.

Pair0.0.3a7 adds two batch IDs37total, companion schemas1; existing schemas/39math
and session23update/restore22merge unchanged. Exact-version state/registry replay/
rebuild explicit. Full API/math/contracts/design/version/example/changelog/lesson/
continuity and issue evidence with source; author self-review+CI only. All local/
head/repeated archives/freshpairs/SIXchecks/guarded merge/main exact tree/docs/bothOS
actual bundles/FOURfreshpairs/final receipt/byte equality before eight-stageDone.
No provider/private source/performance/state/stable/tag/PyPI claim; R3paused.

Requested comparisons only consume their corresponding optional dependencies. An unrequested market/sector/membership input does not change another result value/readiness; declared parent spec identity can still reflect supplied configuration. Malformed identities for requested dependencies are typed call errors, while missing/unready dependencies remain per-feature quality. Evidence is globally bounded and exact duplicates deduplicate only after mapping to output symbol entity; conflicting original-row assertions fail.

For parent config, parameters are explicit positive period and optional evidence_limit; window count=period+1/completed_eod. Parent availability/unit/adjustment/selected grid must align child references, but parent identity/evidence_limit need not equal child configs. Action admissions validate in each ReturnReference against its child config rather than incorrectly re-binding to parent. Sector ClassificationAdmission is produced against parent config/spec point and retained as a separate dependency. Membership snapshot revision enters identity even when value is unchanged.
