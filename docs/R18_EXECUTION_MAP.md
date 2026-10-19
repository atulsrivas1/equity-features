# R18 current execution and dependency map

Source inspection of public worker main `231349aaf2bf1b9ec21f45807382ca9c6522520c`, tree-identical to the accepted b7 candidate. These are source facts and prospective qualification boundaries, not measured exclusive costs or an adopted scheduler design. [EQ142 plan](stories/EQ-142_PLAN.md) owns implementation qualification.

## Separate the kinds of edge

| Layer | Real prerequisite or ownership | Refinement boundary |
| --- | --- | --- |
| Supplied source admission | Valid exact task/batch/manifest, population, units, source/revision, C/K/E, configuration and input budget | Common structural validity is not the same as each output's field readiness |
| Selected preparation | Already computes the union of selected anchored closes, true ranges and/or price moments once | Do not recreate independent preparation per scalar or describe existing sharing as missing |
| Output readiness | EMA/RSI use their own anchored closes/changes; ATR uses accepted predecessor closes/successor H/L; bands use their last N scheduled closes | No EMA→RSI→ATR→band chain; preserve seed/window-specific availability |
| Numerical state | Chronological recurrence inside exact instrument/grid/anchor/config/revision; immutable compatible moments/witnesses | Batch replay does not imply update/restore/merge or persistent state |
| Current partition policy | Connected components of intersecting instrument populations, including transitive intersections; ordered tasks inside each component | Same-symbol grouping is coarse, but generic callbacks and ownership are not proven independent by their labels |
| Result joining | Full selected task FeatureResult, headers, identity, values/nulls/quality/evidence and once-global cap | Family splitting cannot independently cap and concatenate evidence or publish partial headers |
| Resource admission | Task/result/transport limits plus job-wide parent/children/queue/publication budgets | Repeated validation at different boundaries is not automatically redundant |
| Publication | Current coordinator validates and publishes after pure completion, under actual generation/task/commit authority | Prove cancellation/retry/partial-commit/replay semantics before relaxing a barrier or overlapping publication |

## Exact public source anchors

- [supervisor.py partition_tasks, line152](https://github.com/atulsrivas1/equity-feature-workers/blob/231349aaf2bf1b9ec21f45807382ca9c6522520c/packages/workers/src/equity_feature_workers/supervisor.py#L152): population connected components, chronological/hash ordering and row-weight allocation. More workers cannot split a single existing component. Current source accepts at most32 workers; the former inspected host's48 logical slots is not a new supported degree.
- [intraday.py compute_intraday_inputs, line105](https://github.com/atulsrivas1/equity-feature-workers/blob/231349aaf2bf1b9ec21f45807382ca9c6522520c/packages/workers/src/equity_feature_workers/intraday.py#L105): actual admission, selected context/history/header verification, one selected-union preparation, compute and identity check.
- [supervisor.py _validate_results, line193](https://github.com/atulsrivas1/equity-feature-workers/blob/231349aaf2bf1b9ec21f45807382ca9c6522520c/packages/workers/src/equity_feature_workers/supervisor.py#L193), [child line361](https://github.com/atulsrivas1/equity-feature-workers/blob/231349aaf2bf1b9ec21f45807382ca9c6522520c/packages/workers/src/equity_feature_workers/supervisor.py#L361) and [coordinator line563](https://github.com/atulsrivas1/equity-feature-workers/blob/231349aaf2bf1b9ec21f45807382ca9c6522520c/packages/workers/src/equity_feature_workers/supervisor.py#L563): publication preparation, entity admission and OutputManifest checks recur at distinct execution/ownership boundaries. Optional spill and publisher paths add their own obligations.
- [manifests.py task/reuse properties, line220](https://github.com/atulsrivas1/equity-feature-workers/blob/231349aaf2bf1b9ec21f45807382ca9c6522520c/packages/workers/src/equity_feature_workers/manifests.py#L220): task hash re-encodes the record on each property access; reuse hash separately canonicalizes its exact scope. Repeated calls are visible, but their cost fraction and safe reuse design are unmeasured.
- [_supplied.py admit, line49](https://github.com/atulsrivas1/equity-feature-workers/blob/231349aaf2bf1b9ec21f45807382ca9c6522520c/packages/workers/src/equity_feature_workers/_supplied.py#L49): supplied admission includes transport-size and metadata/value checks. Count actual traversals/bytes before deciding what can be reused.

Existing CALCULATION diagnostics include nested callback admission/context/preparation/producer checks; SERIALIZATION includes result validation. Those composite spans overlap or nest. Their sums cannot be subtracted from wall time as an exclusive ledger. EQ142 must qualify clock/process/thread boundaries, nesting and overhead before attributing a bottleneck. Source observations remain hypotheses until the current executable baseline measures them.

## Independent counterexamples

Close-only EMA/RSI must survive missing unrelated H/L; legitimate malformed common input must still reject. Missing closes outside a band's scheduled N-slot window must not block it, but required missing slots cannot be compacted. Constant bands keep available middle/bounds/width0 while position is unavailable. Preserve ATR single-anchor warm-up and target-close independence where applicable; exact large-offset band witnesses; different seeds/anchors/revisions/cutoffs; whole-call overflow; complete global evidence capping; same-symbol independent qualified built-ins versus unknown callbacks; transitive population overlaps and actual universe joins; stale/cancelled/retried work and real commit ownership. Expected mathematics comes from accepted independent fixtures, not two calls to the optimized implementation.
