# EQ-054 — R4 pre-code plan

[Issue61](https://github.com/atulsrivas1/equity-features/issues/61), R4/E07.
Estimate: **5 provisional story points**, not a deadline. Prepared plan only;
no implementation, executed tests or delivery claimed.

## Start and dependencies

EQ043 plus EQ049–053. Reinspect live acceptance and accepted public contracts before pulling.
One active implementation story. Follow [execution package](../R4_AUTONOMOUS_HANDOFF.md)
and [test strategy](../R4_TEST_STRATEGY.md); define concrete interfaces and independently
expected fixtures before source implementation.

## Design

Existing SDK against actual installed DuckDB adapter, public synthetic DuckDB/Parquet fixtures; independent expectations.

## Open questions and source issues

Freeze exact API/configuration/backend pins and supported source populations when
pulled. Unknown precision/availability/eligibility/calendar/reference evidence stays
explicit. A consequential canonical schema/capability change needs a versioned
decision, regression evidence and review. Real instruments/dates/goldens must be
selected from inspected source support, not invented in this preparation.

## Required tests

[Test matrix](../R4_TEST_STRATEGY.md), bothOS clean wheel/sdist conformance, limits/cancellation, core isolation; executable fixture guide.

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

Actual DuckDB conformance and synthetic integration, not an in-memory substitute. Neither a prepared plan nor a source merge establishes this outcome.
