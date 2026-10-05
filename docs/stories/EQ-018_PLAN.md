# EQ-018 — interval bar structure plan

Prepared2026-10-05 before coding; issue22/epic20/R1. Confirm5Fibonacci points.
EQ017 is Done at PR149/main674194de7cc0ecb33b0569768572f4c89a1b354c,
0.0.2a0 with205units/123references, both OS CI and actual bundles/fourfresh
installs accepted. Receipt EQ-017_DELIVERY.md. Live EQ018 Ready; other R1 work
remains Backlog. One active story; author review+CI; PR120 remains deferred.

## Design and API

`compute_structure(batch: CanonicalBatch | None, config: ConfigSpec, *,
entity: EntityKey) -> FeatureResult` in session.bars supports exactly the two
session.structure IDs. Config session.intervals supplies named whole-bar windows;
eligibility_policy and all target admission remain EQ017. Intervals may overlap
as independent windows. Any bar straddling a requested window boundary is an error;
no proration or inferred coverage. A future/incomplete configured window produces
unavailable window status; no future bar is consumed.

Add typed IntervalCoverage(name,start_ns,end_ns,coverage) rows to optional owned
BatchMetadata.interval_coverage. Names unique, bounds within supplied scope, counts
matching selected whole bars. Each requested fully observed window needs an exact
matching declaration; absence gives incomplete coverage. Window evidence is distinct
from full-target delivery: a complete opening interval can yield OHLCV even if later
delivery is incomplete, while volume share needs both interval and target volume.
Scope, window delivery and policy survive Arrow and result input identity.

Add typed immutable IntervalOHLCV and IntervalVolumeShares table cells, containing
named interval rows with UTCns bounds, typed nullable prices/volume/share and
independent status/reasons/expected/observed. Null prices on a covered empty window
coexist with available observed volume0. Global FeatureResult quality aggregates
window readiness, but retains explicit typed partial tables (a documented analogue
of structured breadth). It cannot present a partial row as available. Arrow uses
list-of-struct values with exact ns and nested quality, not JSON/object dictionaries.
Registry output metadata migrates to these concrete types and both IDs gain batch;
all unimplemented modes remain false. Both distributions advance to0.0.2a1.

Reuse checked bar reductions under explicitly derived interval configuration;
preserve original construction/adjustment/price policy and root result identity.
No invented whole-session denominator, gaps, auctions or end-of-day completion.

## Tests, documentation and exit

Independent b1/b2 first/last expectations (100,103,99,102,200)/(102,104,101,103,300),
volume shares2/5 and3/5. Test overlapping windows, exact boundaries, earlyclose and
auction construction, missing/null/empty/zero, incomplete target with complete
window, missing window declaration, after-cutoff windows, straddling rejection,
knowledge exclusions restricted to relevant windows, type/ownership/Arrow output
and prior R0/EQ017 regression preservation. Precision remains1e-12 float64.

Publish API/example, contract/registry migration, changelog and continuity, including
EQ017 receipt/recovery. DraftPR, author review, formal Test, strict typing/purity/
reference/compatibility/licensing/repeat-build/clean-install and six exact-head
checks; squash merge then published bytes/main OS CI and actual downloaded bundles
with fourfresh installations before Released/Done. Both IDs callable with truthful
per-window readiness and no leakage. Pull EQ019 only after this exit.
