# BUG-004 delivery receipt

PR171 implements typed saved-state float overflow rejection in pair0.0.2a11.
State schema2/formulas unchanged; exact implementation matching/no migration.
[Pre-code plan](BUG-004_PLAN.md), [public state errors](../api/INCREMENTAL.md).

Three independent cases cover rehashed positive/negative/very large exponents,
inf/nan/malformed text, unchanged caller state, original OverflowError cause and
nonzero finite exact roundtrip/continuation. Author self-review+CI; full validation,
exact-head/main/publication/actual-artifact/fresh-install gates pending. Live issue163
owns actual evidence; no delivery claimed yet. Owner then stops this repair session.
