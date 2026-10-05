# EQ-011 execution plan

Story #14, E03/R0; **8 points**, confirmed when pulled after EQ-010/E02 acceptance.
Prerequisites: all EQ-001–006 formulas/timing, verified two-distribution foundation,
tested optional columnar versions and declared artifact channel. First action: map
each canonical input field to accepted precision, identity and nullability rules.

Problem: caller data must preserve its meaning across packages and columnar backends.
Acceptance maps trades/quotes/bars/daily/reference → typed immutable schema/batch
values; namespace/time/unit/scale → explicit metadata and int64 admission; sampling,
eligibility/coverage/adjustment/availability → retained metadata/columns; evidence →
independent schema/precision/identity/null tests and Arrow/NumPy round trips.

Design: stdlib core owns detached immutable column tuples and frozen metadata;
explicit columnar module accepts only concrete in-memory Arrow/NumPy objects and
copies into owned core tuples. No lazy dataframe/source execution. int64 UTCns and
prices/counts, explicit decimal scale/currency, nullable values and exact rational
adjustment identity; immutable caller input/snapshot/mapping bindings. Reference
schema holds effective/known-at facts, not discovered references. Unknown availability
remains null. Schema/type/precision admission is here; semantic ordering/duplicates,
OHLC/coherence, overflow accumulation and opt-in normalization are EQ-014.

Decisions: nullable price fields preserve invalid/missing quote observations; eligible
trades need positive prices under EQ-014. Volume/count representations stay integers.
Actual bar notional uses decimal128 coefficient for wide exact products, with a
declared bound; calculations must raise outside representable output. No inferred
eligibility, corporate-action conversion or provider readiness.

Tests: every kind/field schema, required/optional/null columns, namespace/source binding,
int64/time bounds, Boolean-vs-int rejection, exact nanosecond endpoints, price scales,
Arrow metadata/decimal and NumPy mask/int64 round trips, unsupported sampling/basis,
defensive ownership. All123references plus strict typing/boundary/import/build tests
and exact Linux/Windows final-head/main CI. Docs: input contract tables, API/copy
examples, plan, compatibility/dependency policy and continuity alongside code.
End: experimental0.0.1a1 foundation artifacts actually delivered/verified; source
alone remains Ready to release. E03 starts but stays open through R3 EQ-093.
