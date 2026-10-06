# R4 DuckDB qualification strategy

Owner direction on October 6, 2026: begin DuckDB adapter work, using synthetic
conformance tests followed by representative real-data integration tests. Both
are required; synthetic success alone cannot establish actual-source readiness.
R2 and R3 milestones are accepted. R4 remains unimplemented and unaccepted.

Scope: [R4](https://github.com/atulsrivas1/equity-features/milestone/5),
[E07](https://github.com/atulsrivas1/equity-features/issues/55), EQ049–056.
Pull EQ049 first, then dependency-ready mapping/reads/calendar/provenance work.
EQ054 owns adapter conformance; EQ055 owns representative actual-data evidence;
EQ056 requires both. No worker, provider download or full historical build.

## Two complementary test populations

Public synthetic fixtures use fictional instruments, hand-authored values and
temporary DuckDB/Parquet files. They require no provider credentials or licensed
data. Expected results come from explicit source rows, contract rules and
hand-derived mathematics, not another copy of the adapter implementation.

Private real-data validation uses a frozen, bounded instrument/session/source
scope selected after inspection. Record actual catalog and selected file hashes,
mapping and package versions, source/optimized identities, normalization policy,
calendar/reference versions and C/K/E. Do not publish private paths, paid rows,
provider identifiers or source artifacts without established publication rights.
Public summaries may describe methodology and limitations without exposing data.
No real slice or mathematical result has been selected or verified by this plan.

| Required case | Synthetic evidence | Real-data evidence |
| --- | --- | --- |
| Source resolution | Distinct generations, overlapping curated/prepared dates, missing/ambiguous selections, explicitly recorded substitutions and failed pins | Pin one selected generation and reconcile original/optimized lineage without double counting |
| Precision and nulls | UTC nanoseconds beyond float precision; scaled prices; overflow; absent/null/zero; invalid types | Verify original timestamp parsing and declared price/quantity representation, with source support where retained floating fields are insufficient |
| Ordering and multiplicity | Tied timestamps, distinct equal payloads, cross-chunk ordering, stable occurrence identities | Reconcile selected source rows and identities; never treat equal payloads as duplicate executions automatically |
| Coverage and availability | Observed-empty versus missing partition, incomplete intervals, unknown/later known-at, exact boundary cases | Check selected partitions and per-instrument warm-up; retain unverified admission and unknown availability |
| Quote sampling | Trade-snapshot fixtures and explicit rejection of unsupported continuous requests | TBBO remains trade-sampled; no continuous-feed completeness claim |
| Calendars and references | Governed holidays, early closes, DST, action/reference revisions and late knowledge | Supply versioned sessions and validate effective/known-at membership/action evidence; file dates do not prove a calendar or historical membership |
| Bounded reads | Instrument/time predicates, chunks, maximum rows/batches, cancellation, private read-only connections | Measure requested slices, rows/bytes/copy costs, memory and elapsed reads on the actual workload |
| Numerical integration | Admitted adapter batches passed through installed public calculations against hand goldens | Independently check selected computed values, units, quality and evidence; record tolerances and unavailable features |

## Acquisition and calculation are separate checks

Successful SQL reads or physical rewrite hashes do not prove source completeness,
provider truth, historical availability or correct feature mathematics. Adapter
tests first check the canonical delivered population and its metadata, then check
calculation outputs independently. Legacy derived outputs are comparisons with
their own versions/limitations, not unquestioned goldens. Future outcomes remain
separate from feature inputs.

Missing prior sessions may invalidate an EMA prefix while permitting a later
finite SMA window under the existing accepted rules. Exercise both outcomes.
Baselines can be calculated from admitted supplied history through explicit caller
composition; legacy watchlist/context/baseline imports are not prerequisites for
the core adapter. Do not add hidden dependency acquisition to calculations.

## Acceptance and delivery

EQ054 runs the public EQ043 conformance kit against the actual DuckDB adapter,
plus DuckDB/Parquet-specific integration fixtures. An in-memory example alone is
not DuckDB adapter acceptance. EQ055 freezes actual scope before running and
retains successful and blocked cases; no full-corpus conclusion follows from a
few instruments or sessions. Numerical unavailable results must be distinguished
from adapter failures and successful-empty acquisition.

Qualify optional adapter installation, supported Windows/Linux behavior, typing,
dependency/pure-core isolation and reproducible examples. Update relevant issue,
API, mapping, test, limitations and delivery documents alongside each story.
Final-head separate review, CI, installed artifacts and actual publication
readback remain required before Released/Done. Neither private real-data testing
nor provider access is required in public CI. Source/reference limitations may
keep particular features unavailable even when the bounded adapter is accepted.

## Decisions still owned by R4 stories

EQ049 selects a bounded explicit resolver interface and receipt/pin contract.
EQ050 defines actual schema/precision/eligibility mappings and unsupported fields.
EQ051 selects measured connection/batch/cancellation behavior and DuckDB pin.
EQ052 resolves caller-governed calendars, warm-up and reference gaps. EQ053 binds
the actual acquisition evidence. Concrete real instruments/dates, independent
goldens and justified tolerances are frozen under EQ055, not invented now.

The current local-review alternatives in CODE_REVIEW.md explicitly cover R2/R3;
hosted activation remains unverified. Obtain an owner-authorized R4 alternative
or actual hosted final-head review before merging R4 changes. This plan does not
silently extend a bounded earlier authorization.
