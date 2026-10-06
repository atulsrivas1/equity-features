# Declared-universe breadth, schema1

Pair0.0.3a9 / EQ035. This is pure aggregation of supplied member facts and results.
Frozen mathematics: [context formulas](../features/CONTEXT_FORMULAS.md);
[pre-code plan](../stories/EQ-035_PLAN.md). No dependency is calculated or fetched.

`DeclaredUniverseSpec(namespace,session_id,universe_id,membership_identity,effective_ns,members)`
owns an immutable unique list U of opaque instrument IDs. Its explicit membership
revision and evaluation point bind the caller declaration, not source authentication.
The point is inside actual target [open,close) and <=C. Expected M is always |U|;
missing members cannot reduce M. Duplicate/extra members or namespace/target conflicts
are typed errors. `BreadthSpec(entity)` names the aggregate output explicitly.

`MemberFeatures(entity,return_reference=None,sma=None,close=None)` carries optional
owned dependencies. `ReturnReference` is the qualified EQ034 result/config/context.
`SMAInput(reference,config,context)` binds the exact owned SMA witness to its actual
configuration/history grid/source/action/timing proof. `CompletedClose` retains a
positive scaled int64 coefficient or null, original known-at, original DAILY/BAR
source frame metadata and row index, full actual target interval and one selected
coverage certificate. Selected certificates do not replace original frame counts.
Auction inclusion must agree with SessionSpec. New companions and exclusions schema1;
existing result/input/state schemas are unchanged.

`compute_direction_breadth(members,config,*,universe,spec)` consumes only returns:
A=count(r>0), D=count(r<0), Z=count(r==0) with exact zero and no epsilon.
Its explicit parent period h uses h+1 completed-close slots. Available compatible
members contribute once; no absent member enters Z. `compute_above_sma_breadth`
consumes only completed closes and supplied SMAInput, with a separate parent period
N/window N completed-close configuration. K=count(close>SMA), fraction K/E;
equality is not above. The comparison uses SMAReference.compare_price, exact sign
of close_coefficient*N-sum, preserving a half-tick near int64 limits even if Float64
close and mean round equal. It never recomputes the SMA or uses K/M.

Both return `BreadthResult(result,exclusions)`: standard FeatureResult with one
existing structured BreadthCounts/BreadthFraction cell, plus typed MemberExclusion
records. Quality expected M/observed E, coverage E/M. For E>0 incomplete U retains
explicitly partial counts/fraction with incomplete_coverage and partial_universe;
E0 gives null structured value and quality0/M. Empty U is not_applicable/empty_universe;
absent U is missing_input with expected unknown. Dataset None is missing_input;
provided empty members for nonempty U is known incomplete coverage, not missing data.
Absent-member exclusions are companion records, never fake EvidenceRow observations.
Malformed requested dependencies are typed errors; compatible unready dependencies
exclude only the affected member, preserving status priority and all unavailable
SMA/close/absent dependency reasons (deduplicated), even with output evidence limit0. Unrequested fields do
not affect values/readiness or consumed identity.

Requested members align exact governed/selected session grid, period/anchor,
currency/price scale, supported adjustment policy/anchor/algorithm/backend and C/K/E.
Per-instrument action snapshots and actual child configuration/evidence bounds stay
separate. A completed close must agree with its supplied SMA's actual adjustment.
Unavailable/future/unknown closes cannot enter E. Reconstruction is explicit and
retains original known-at values; it does not certify historical availability.

Derived aggregate-spec/universe/dependency/certificate bindings retain actual identities and are
supplied definitions, not market observations. Exact original inputID/kind/metadata
deduplicates; conflicting reuse is rejected. Different-instrument normalized DAILY
frames require distinct IDs. Borrowed evidence maps to aggregate entity/feature
while retaining original source row/event/known-at/bounds/completed boundary and full
child association. Identical proof deduplicates. All supplied proof conflicts are
validated even if output evidence limit is zero/full; transient proof validation and
identity/aggregation work is not bounded by retained output evidence size.

Synthetic U={a,b,c,d}, returns[1/10,-1/20,0,missing] yields(1,1,1),E3/M4,coverage3/4.
Closes[11,9,10,missing] against SMA10 yieldK1/E3,fraction1/3. The
[installed example](../../examples/declared_breadth.py) constructs dependencies using
public producers and preserves the missing d exclusion. Actual API fixtures cover
these independent goldens, int64 exact comparison, empty/absent/all-unready/zero,
original/revised evidence, source/config/typed-proof guards, knowledge/reconstruction,
auction/partial/future boundaries, unrequested isolation, instrument-specific actions,
future-history invariance and unsupported modes.

39batch IDs now include all16R2 numerical IDs. Session remains23update/restore and
22conditional merge; history/context/breadth state modes are false. Exact-version
caller state replay/registry rebuilding applies. No source truth/private copy/provider/
performance/public accumulator/stable/PyPI claim. Actual delivery remains subject to
[story receipt](../stories/EQ-035_DELIVERY.md); R3paused.
