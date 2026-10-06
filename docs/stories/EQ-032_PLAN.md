# EQ032 individual bucket volume baseline and supplied ratio pre-code plan

Issue37/E05#31/R2,8provisional points; depends031. Pre-code preparation while final EQ031 receipt gates run. No implementation until EQ031 is verified Done; one active implementation story.

For a caller-defined half-open bucket b with offsets0<=start<end relative to open,
prior N>=1/default20 entire buckets yield exact sum(V_j,b)/Nshares, target excluded.
Every required prior slot remains in N. An actual early close before bucket end
has absent eligible observation, incomplete_coverage/INELIGIBLE rather than0 or a
smaller denominator. Other independently supplied buckets remain usable. Covered
zero volumes are valid; missing/null/source/knowledge states stay explicit.

Use single-bucket calls returning standard FeatureResult/quality plus exact typed
reference. Bucket identity is part of owned context/config-derived input identity;
call each bucket independently. This preserves existing Float64 shares/fraction
catalog output/schema instead of inventing an untyped parallel dictionary or new
aggregate output dtype. A caller can retain a tuple of typed bucket results; no
hidden cross-bucket aggregation/composition. Existing typed session-structure
results remain distinct. No cumulative time-of-day substitution.

Define VolumeBucket(name,start_offset_ns,end_offset_ns,grid_version), schema1.
Nonnegative int64 start/end and positive bounded duration; grid version and name
explicit. Define BucketContext(entity,grid_version,sessions,bucket,slot_coverage,
action_admission=None), schema1, immutable owned grid with exact namespaced ordered
sessions/target and one certificate per required bucket slot. Daily HistoryContext
certificates are not repurposed as bar coverage. Bucket identity/grids agree;
early-close-excluded slots must have observed0 and incomplete certificate.

compute_interval_baseline(batch|None,config,*,context)->IntervalBaseline with
standard single baseline.interval_volume Float64 shares result, exact nonnegative
checked decimal128 sum/count, config/context/quantity basis. Canonical BAR rows
represent already supplied individual bucket volume, never a hidden sum of smaller
bars. One original row per instrument/session/bucket at exact open+offset bounds,
chronological supplied grid order, namespace/price metadata/adjustment/actual row
count/per-bucket presence certificates checked for all structural source rows.
Rows for ineligible early-close buckets are rejected; absence is retained. Context
metadata binds declared bucket/grid definitions, not market prices. Only selected
prior buckets consumed at C/K/E; original index/known-at/coverage/revision retained.
Source scope if present contains actual bounds. Volume-only still needs canonical
PriceUnit metadata. Config v1 period(default20),quantity_basis(defaultraw_shares),
evidence_limit(default0), matching prior_only count/exact session/grid/adjustment.
Compatible supplied action admission required for adjusted shares; dividends never
scale quantities implicitly. No price arithmetic, calendars, fetching or sorting.

Define BucketVolume(entity,volume,known_at_ns,source,row_index,interval,coverage,
bucket,quantity_basis), schema1. BAR source only, original row bounds/counts retained,
selected certificate expects one actual row. compute_interval_relative_volume
(target|None,baseline|None,config,*,context)->standard single
baseline.interval_relative_volume Float64 fraction result. Consume supplied matching
IntervalBaseline only; no dependency calculation. Exact config/context/bucket/grid/
unit/basis/versions/C/K/E/revisions matched. Target interval must equal exact bucket
bounds and fit actual target session. A wholly elapsed bucket ending<=C with complete
coverage can be ready; a partial supplied selected interval never reinterpreted as
whole bucket. Explicit incomplete target yields incomplete_coverage. Full interval
ending>C yields future_market; target bucket excluded by actual early close is incomplete with
ineligible reason even when no fact is supplied. Missing target for an otherwise eligible bucket remains missing_input, not0. Exact V*N/sum projected
once; admitted zero baseline not_applicable/zero_denominator even0/0; unready
dependencies/target precede zero handling. Ratio quality two dependencies, baseline
N-slot quality retained. Derived dependency/certificate identities and original
source/evidence deduplication follow031; structural proof is not source authentication.

Independent API fixtures: historical10/20/30mean20, target50ratio5/2; future/target
mutations; default20/N1/exactwide/zeros/missing/null/finite recovery; early-close
last bucket observed2/expected3null while another full bucket ready; variable actual
open and offset alignment/half-open boundaries; duplicate/order/malformed bounds/
conflicting grid/quantity/namespace/unit/revision/config; missing/incomplete/forming
versus elapsed target; equalityatC/known-at/reconstruction; bounded original row
indices/source scopes/malformed witnesses/immutable inputs/false state modes.
Preserve accepted031 units and all123formula references; no measured performance claim.

Pair0.0.3a6 adds two batch flags (35total),39mathematical definitions, existing
canonical/result/state schemas and session23update/restore22merge remain unchanged.
New bucket companions schema1; all historical/context state modes remain false.
Exact-version caller state/registry replay/rebuild explicit. Public API/spec/math/
example/design/changelog/lesson/continuity and issue evidence accompany source.
Author Codex self-review+CI accurately labeled. Full local/exact-head/repeatarchives/
freshpairs/SIXchecks/guarded merge/main exact tree/docs/bothOS actual bundles/FOURfresh
pairs/final receipt and byte equality before eight-stageDone. R3paused. No stable/
registry/provider/private code publication or future deadline.

Partial target certificate distinction: BucketVolume selected interval may be a positive prefix of its declared bucket solely to report incomplete_coverage; it cannot count as admitted whole-bucket volume even if its prefix certificate is complete. Bounds must begin at exact bucket start and end<=bucket end; complete bucket proof requires equality at end. A malformed shifted start/extended end is a typed bounds error. Full bucket with end>C is future_market. No phantom source row/evidence for absent early-close bucket.

Acceptance wording reconciliation: issue37/backlog retains original observed-day denominators wording. Frozen EQ005 CONTEXT_FORMULAS is explicit that missing/early-close slots do not shrink N; preserve observed/expected counts as evidence, use required N for the mean, and return unavailable on gaps. Document this interpretation in issue/PR/API without substituting a median/cumulative or observed-only estimator. No change to frozen mathematics.
