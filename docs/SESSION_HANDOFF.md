# Development continuity

Updated2026-10-04 (Eastern). Read AGENTS.md, PUBLIC_DEVELOPMENT.md and R0_AUTONOMOUS_HANDOFF.md. GitHub Project remains the status authority.

## Verified delivery and current work

EQ-001–004 Done: PR106/112/121/124 established39IDs and74exact design references. EQ-005 Done via PR128, squash b3a39a4209580e95ebe7f953d63b81f839901dfe;26context references. EQ-006 Done via PR129, squash5c8edf56392ac319483669c7f8890597b489ff68;23timing cases. E01 Done. These123references establish mathematics/policy, not production kernels or provider readiness.

EQ-007 Done: PR130 source a333fa7af53fc8f33e2b95368a99716bee6658d5, then actual foundation delivery under EQ-009. Source merge alone correctly remained Ready to release. EQ-008 Done via PR131,86321207b2ce8557a64a58782cfea28de4003a56: CPython3.12 x64, Windows/Linux; exact optional NumPy2.2.6/PyArrow20.0.0 pins and development tool lock. Local Windows3.12.10; CI Linux3.12.14 and Windows3.12.10 recorded in artifact manifests. Other environments unqualified.

EQ-009 Done via PR132 and follow-up PR133. Final head18866d7f96f78516e27ed95787a9432c276c5050; main0e130ca2a759ff13a35ca44da05382056a4b4768. All six exact-head checks and main workflows passed.14negative boundary fixtures, declared runtime dependency allowlist, strict typing,123references, source/import/licensing-content checks, repeat four-artifact SHA256 parity and fresh wheel/sdist installs passed. All story-changed Git blobs matched GitHub bytes (full squash diff, not just last commit). Both final main bundles were actually downloaded/hashed/inspected; their four distribution hashes matched previously fresh-installed PR132 main bundles, so install evidence was reused on identical bytes. No independent review claimed.

## Foundation delivery channel

Successful main Foundation package checks retained artifacts,30day requested retention, manifest source commit/clean flag/SHA256/OS/runtime. No PyPI or stable production release. Build/rebuild instructions: BUILD_DELIVERY.md; compatibility: COMPATIBILITY.md. Artifact evidence/expiry/hashes are recorded on issues9/11.
- [foundation-0e130ca2a759ff13a35ca44da05382056a4b4768-windows-latest](https://github.com/atulsrivas1/equity-features/actions/runs/37258142835/artifacts/11323726340), expires2026-11-04T03:08:49Z; prior byte-identical install evidence: https://github.com/atulsrivas1/equity-features/actions/runs/37257622066/artifacts/11323481301.
- [foundation-0e130ca2a759ff13a35ca44da05382056a4b4768-ubuntu-24.04](https://github.com/atulsrivas1/equity-features/actions/runs/37258142835/artifacts/11323307342), expires2026-11-04T03:08:14Z; prior byte-identical install evidence: https://github.com/atulsrivas1/equity-features/actions/runs/37257622066/artifacts/11323042505.

EQ-010 Done via PR134, final head74b672ff49370959c24c0469273efcac992580f5,
mainbebe4138d234138a51a98fe659923f6217e05f68. Exact-head/main checks and six
published blobs verified; public owner/Apache metadata and read-only PyPI404
snapshot recorded. E02 Done with all native children accepted. This neither reserves
registry names nor authorizes publication.

EQ-011 In progress,8points confirmed before code. Plan: stories/EQ-011_PLAN.md.
Immutable canonical core for five kinds, source/unit/coverage/adjustment/sampling
metadata, explicit Arrow/NumPy materializing bridges and27independent unit cases
implemented. Core imports exclude optional backends. Experimental version0.0.1a1.
Strict typing passed with PyArrow missing-stub override only; boundary passed.
Current tests cover exact ns/int64/decimal128 endpoints and null/ownership behavior.
Author review added concrete-container guards before source freeze. A development
build had already produced earlier bytes; its installed sdist correctly failed the
new27case tests. Those stale bytes are rejected; final source is rebuilt with the
source/tests frozen throughout build/install verification. Synthetic installed
example: examples/canonical_inputs.py.
Semantic validation remains EQ-014. Source review, all references, repeat build,
clean install, exact-head/main CI and actual artifact delivery remain mandatory.
E03 now active and remains open through EQ-093/R3.

## Failures and corrections

- EQ-011 review found Windows default text decoding damaged punctuation in two
  edited documents. Restored original Unicode and used explicit UTF-8; no source
  semantics or evidence identities changed.

- PR128 merge-commit request rejected: repository permits squash only. Checked command stopped; allowed squash used on the same green head.
- Windows console UTF-8 print failed after an issue close; live closure verified, console reconfigured; no failed command counted as validation.
- Whole-roadmap GraphQL queries consumed quota, then targeted queries also hit exhaustion. Switched to documented REST Projects endpoints and verified actual returned fields. CLI GraphQL quota reset03:25:33UTC. Connector draft conversion lacked write access; signed-in GitHub UI performed readiness transitions. No gate waived.
- Copied licenses inherited a trailing blank line; staged diff check stopped before commit. Trimmed whitespace only, preserved license text/root license.
- EQ-008 close assertion stopped while main matrix still ran; closure waited for successful workflows.
- EQ-009 imported-function alias loophole found during artifact acceptance. Acceptance metadata finished before process stop reached it; EQ-009 explicitly reopened/In progress and EQ-010 returned Backlog. EQ-007 actual artifact acceptance remained valid. PR133 fixed imported names/wildcard bypass with three negatives; new final-head/main/artifact verification preceded reacceptance. Earlier build/hash/install evidence remains factual.

## Boundaries and durable authorization

Owner authorizes remaining EQ-011–016 one at a time through verified R0 acceptance. Create each full story plan before implementation, inspect live issue/Project/prerequisites, confirm points, preserve unrelated work and obey eight stages. Author self-review/CI are approved; GOV-005 issue119/PR120 stays explicitly owner-deferred. No independent bot/human review, account/profile changes, paid/source access, private data, external-product integration, public registry or recurring automation. Calculation packages have no source/clock/job I/O. R1/R2 kernels and R3 custom execution remain unimplemented. EQ-093 stays R3; EQ-094 retired.

E03 includes R3 EQ-093 and must remain open. Reconcile its spanning R0 milestone assignment before closing R0, with explicit rationale; do not implement R3 or close the epic to clear a milestone. R0 acceptance still requires EQ-011–016 typed in-memory foundation, tests/docs and final versioned artifact delivery. Original chat stopped implementation; this chat owns the sequence.

## Exact resume steps

1. Work in the existing equity-feature-project checkout, not this chat output directory; inspect status/branch/HEAD/origin/main and concurrent PRs. Public documentation intentionally excludes private local paths.
2. Active EQ-011: finish author review of inputs/columnar/27unit tests and docs/contracts/INPUTS.md. Run all gates, open linked draft PR, exact-head CI, squash publication, committed blob verification and main CI; deliver/verify0.0.1a1 artifacts before Done.
3. After EQ-011 Done, pull EQ-012 issue15 with live prerequisite/Project inspection and full pre-code plan. Then EQ-013/014/015/016 in dependency order, no later-release calculators.
4. Run the planning block from .github/workflows/docs.yml; python tools/verify_session_examples.py, verify_quote_examples.py, verify_history_examples.py, verify_context_examples.py, verify_timing_examples.py; import/license checks; pinned venv compatibility, strict mypy, boundary/unit/build checks as applicable. Stop on failures.
5. Each implementation delivery requires actual successful main artifact download, commit/hash/content/clean-install verification before Released/Done. Record issue/epic/Project and this continuity alongside every story; attach every created PR to execution chat. Stop at verified R0 acceptance and report next-story readiness.

## Historical governance evidence

GOV-006 PR123 published scope correction4a0dda1bb440e7a78750c39d60f2e3f36042a0ae; current generic boundaries preserved. Deferred PR120 synchronized66def0e7bdc708ac82ce3ffeedaf0764f79cbcfe and remains untouched. GOV-007 PR126/127 delivered the autonomous handoff; initial verified main0cf343e14863e41e39ad142ac0977a9731101346. CRLF-vs-LF publication-tool mismatch was corrected by comparing committed Git blob bytes. Preserve prior history/evidence; documentation delivery alone never completes a package milestone.
