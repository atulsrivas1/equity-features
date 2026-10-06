# EQ-051 — R4 pre-code plan

[Issue58](https://github.com/atulsrivas1/equity-features/issues/58), R4/E07.
Estimate: **8 provisional story points**, not a deadline. Prepared plan only;
no implementation, executed tests or delivery claimed.

## Start and dependencies

EQ049/050. Reinspect live acceptance and accepted public contracts before pulling.
One active implementation story. Follow [execution package](../R4_AUTONOMOUS_HANDOFF.md)
and [test strategy](../R4_TEST_STRATEGY.md); define concrete interfaces and independently
expected fixtures before source implementation.

## Design

Private read-only connections, bound filters, owned source populations, bounded batches/cancellation; choose tested DuckDB/backend pins.

## Open questions and source issues

Freeze exact API/configuration/backend pins and supported source populations when
pulled. Unknown precision/availability/eligibility/calendar/reference evidence stays
explicit. A consequential canonical schema/capability change needs a versioned
decision, regression evidence and review. Real instruments/dates/goldens must be
selected from inspected source support, not invented in this preparation.

## Required tests

Predicates, chunks/limits/order/cancellation/errors; measure SQL plus conversion/copy/native memory; optional install/read API.

Apply relevant accepted SDK, mathematical/time/action and package-isolation checks.
Keep synthetic DuckDB conformance and private real-data acceptance separate; record
actual executed results, source/installation identities and limitations. Original
or legacy derived output is not automatically an independent numerical golden.

## Documentation

Update relevant public API/mapping/install/limitations examples, issue/PR, review
and delivery receipt, changelog and SESSION_HANDOFF alongside implementation.
Private actual-source evidence remains outside public files without redistribution
rights. Final installed/artifact/CI/readback evidence precedes Done.

## Done outcome

Bounded historical acquisition; no scheduler/live feed. Neither a prepared plan nor a source merge establishes this outcome.
