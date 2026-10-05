# BUG-004 delivery receipt

PR171 implements typed saved-state float overflow rejection in pair0.0.2a11.
State schema2/formulas unchanged; exact implementation matching/no migration.
[Pre-code plan](BUG-004_PLAN.md), [public state errors](../api/INCREMENTAL.md).

Three independent cases cover rehashed positive/negative/very large exponents,
inf/nan/malformed text, unchanged caller state, original OverflowError cause and
nonzero finite exact roundtrip/continuation. Author self-review+CI; full validation,
exact-head/main/publication/actual-artifact/fresh-install gates pending. Live issue163
owns actual evidence; no delivery claimed yet. Owner then stops this repair session.

## Integrated local qualification —2026-10-05

The owner transferred remaining repair delivery to the R2 execution session.
Existing production repair and tests were reused unchanged. PR171 was integrated
with main65e66fd as exact head `9e78e14a8fe2572a262083af4bd207af8f84199c`,
without force-pushing or dropping repair/owner-pause/knowledge histories.

380units/123references/strict26files/purity38negative10positive/import/registry/
compatibility/license/UTF8 pass on pinned Windows CPython3.12.10,NumPy2.2.6/
PyArrow20.0.0. Four archives reproduce and pass content/license/typing inspection;
fresh local wheel/sdist pairs each380tests/eleven examples pass. Build manifest
identifies exact head with source_dirty=false. Author self-review+CI policy;
hosted activation remains explicitly deferred despite merged guidance.

Three final-head package jobs have passed; the remaining Linux package job and
two documentation jobs are queued without runners. No Ready to release/merge/
main/artifact/installed-main/Done claim. GOV010 also waits for queued main docs.
The external Actions gate is explicit on issue163; actual final-head/main/bothOS
bundle/four installed-pair and receipt publication checks remain. Calculation
implementation waits for genuine BUG003/004 Done and GOV010 acceptance.
