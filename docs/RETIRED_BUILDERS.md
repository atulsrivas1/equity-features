# Retired and deferred builders

PO final status 2026-10-29.

- **tools/build_evidence_evaluation.py: RETIRED.** Historical EQ117 evidence-evaluation qualification over frozen inputs (its package table pins the a4 era and its inputs are recorded receipts).
  It is kept only so that receipts naming it still resolve; `main()` refuses to run. The current evidence line is built and qualified by `build_evidence`, `build_explanations`, `build_diagnostics`,
  `build_agent_evidence`, `build_agent_ledger` and `build_evidence_pilot`.
