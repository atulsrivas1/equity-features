# Development continuity

Updated2026-10-05 (Eastern). Read AGENTS.md, PUBLIC_DEVELOPMENT.md and R1_AUTONOMOUS_HANDOFF.md for the next mission. GitHub Project remains the status authority.

## R1 handoff preparation and R0 follow-up review

Owner requested a handoff package for a new R1 development chat under GOV-008 #143.
[R1_AUTONOMOUS_HANDOFF.md](R1_AUTONOMOUS_HANDOFF.md) contains the bounded mission,
two prerequisite fixes, ten story plans (76 provisional points plus 8 prerequisite
points), architecture/contract evolution, tests, documentation, delivery/stop gates
and copyable kickoff prompt. This chat prepares documentation; it does not start
R1 kernels or a new chat. Existing R0 evidence remains historical and PR120 deferred.

Follow-up review of main 8f363cbccc91ae32363b856701888f855467aea4 reran 170 unit
tests, 123 references, strict typing on 14 files, policy/compatibility/import/registry
checks, repeat artifact builds and clean wheel/sdist installs with both examples.
Local Windows hashes matched delivery evidence; live main Windows/Linux CI was
green and both bundles unexpired. All R0 EQ stories were closed/Done and R0 closed.
Review found two subsequent P2 defects, now tracked as BUG-001 #144 (exact-cutoff
ordinary market exclusion evidence) and BUG-002 #145 (backend I/O checker bypass).
The original R0 chat was observed actively repairing both findings in its own
branch ([PR146](https://github.com/atulsrivas1/equity-features/pull/146)) during
preparation; the handoff was isolated to avoid interfering. Both
remain verification prerequisites: reuse actually delivered repairs, do not duplicate
active work, and record acceptance on the bug issues. No fix is claimed here.
Resolve them before EQ-017, whose
dependency readiness must be reassessed. Do not erase accepted R0 history.

Resume in the execution chat: inspect live issues/Project/checkout, read the R1
package, baseline checks, inspect the R0 repair delivery; reuse accepted fixes or
complete available prerequisite work under its issue/plan, then
EQ-017–026 sequentially. No public registry, later-release implementation, concrete
adapters/workers or external-product integration. Preparation publication and exact
head/main checks must be verified under GOV-008 before its Done status.

## Active R0 review rework

Owner requested two independently reproduced P2 fixes before R1 on2026-10-05.
EQ009#11/EQ013#16 and R0 reopened; EQ017#21 returned Backlog with these blockers;
E02 reopened, E03 stays open. Original alpha6 delivery evidence below remains factual.
Pre-code plan: stories/R0_REVIEW_FIX_PLAN.md. One bounded two-story repair PR/author
shares package gates; this is the recorded temporary work-in-progress exception.
No R1 implementation, deferred reviewer activation or later scope is authorized.

Alpha0.0.1a6.post1 corrects exact-cutoff ordinary trade/quote FUTURE_MARKET exclusions
using the same boundary predicate as consumption; completed/auction endpoint rules
are preserved and incompatible markers rejected. Six new/176total units pass, with
strict typing14sourcefiles. Purity guard admits an explicit reviewed backend surface,
tracks simple aliases and rejects namespace escapes/unreviewed backend access;
38negative/10positive scanner-only fixtures pass. Current packages have no backend I/O.
123math references remain unchanged. Draft review/head/main/build/artifact acceptance
is pending. After actual corrected delivery reaccept both stories/E02/R0, restore
EQ017 Ready and stop before R1. Keep E03 open for R3 EQ093 and PR120 unchanged.

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

EQ-011 Done via PR135, final head08f4a9b5e4bdadf93288179722c383053c1e78c8,
main98098f17a235dd4997dd89a6b7ec4ba69a3f7130. All six exact-head and main checks
passed;19published Git blobs matched. Immutable schema1 five-kind core and explicit
Arrow/NumPy bridges,28unit cases, generator/mapping/ndarray-subclass negatives,
strict typing/boundary/core isolation, four repeat-build hashes, fresh wheel/sdist
installs and runnable example passed. Downloaded/hashed/inspected both actual main
OS bundles; four independent fresh installations each passed28cases and example.
- [foundation-98098f17a235dd4997dd89a6b7ec4ba69a3f7130-ubuntu-24.04](https://github.com/atulsrivas1/equity-features/actions/runs/37259573665/artifacts/11324335042), expires2026-11-04T03:28:55Z; four SHA256 hashes recorded on issue14.
- [foundation-98098f17a235dd4997dd89a6b7ec4ba69a3f7130-windows-latest](https://github.com/atulsrivas1/equity-features/actions/runs/37259573665/artifacts/11323938312), expires2026-11-04T03:29:42Z; four SHA256 hashes recorded on issue14.

EQ-012 Done via PR136, final headaf16dd0ad9107d3aa18ea79503c4e3cb9c370bb1,
mainc2e799bc39743f97f2b46391317d80f0458c3eaf. Six exact-head and main checks
passed;13Git blobs matched. Supplied sessions/early-close/auctions, governed windows,
C/K/E/reconstruction and schema1 canonical configuration/digests implemented at0.0.1a2.
55unit cases/123references/strict types/isolation/boundary, repeat-build hashes,
fresh wheel/sdist installs/examples passed. Both actual main OS bundles downloaded,
hashed/inspected and four independent fresh installs passed55cases/examples.
- [foundation-c2e799bc39743f97f2b46391317d80f0458c3eaf-windows-latest](https://github.com/atulsrivas1/equity-features/actions/runs/37260231384/artifacts/11324158674), expires2026-11-04T03:39:44Z; hashes on issue15.
- [foundation-c2e799bc39743f97f2b46391317d80f0458c3eaf-ubuntu-24.04](https://github.com/atulsrivas1/equity-features/actions/runs/37260231384/artifacts/11323989517), expires2026-11-04T03:38:59Z; hashes on issue15.

EQ-013 Done via PR137, final head6be599c08c586154a92d8aa2e5607eaceac8d8b5,
mainb93cdc6c7d1541e0316662ec82cee3ecda30d1e1. Six exact-head/main checks passed;
16Git blobs matched. Typed value/quality/identity/evidence/error and copied Arrow
result tables at0.0.1a3.87units/123references/strict types/isolation/boundary,
repeat hashes and installed examples passed. Both actual main bundles verified and
four fresh wheel/sdist installs each passed87cases and extended example.
- [foundation-b93cdc6c7d1541e0316662ec82cee3ecda30d1e1-windows-latest](https://github.com/atulsrivas1/equity-features/actions/runs/37261152850/artifacts/11325290781), expires2026-11-04T03:53:57Z; hashes on issue16.
- [foundation-b93cdc6c7d1541e0316662ec82cee3ecda30d1e1-ubuntu-24.04](https://github.com/atulsrivas1/equity-features/actions/runs/37261152850/artifacts/11324881569), expires2026-11-04T03:53:03Z; hashes on issue16.

EQ-014 Done after focused rework PR139/head ebb95f4a42b25933e6e174c47f181a6adcffaf38,
main12d7fea0b6f218963a8569c18665bd6a258cb0fe, alpha4.post1. Close-only supplied
OHLC positivity/coherence now independent of volume, with three regressions and
123total unit tests. Six head/main checks,10published blobs and both actual main
OS bundles passed; four fresh installs each passed123tests/examples. Evidence on
issue17; prior PR138 acceptance and its discovered gap remain recorded.

EQ-015 Done via PR140/head84bb632810eb3b0fd7e06e6143a800b4ad4ef6c2,
mainfa6eb51f08065e4855a592a3a01c64ba2fc7c6bd, alpha5.39-ID immutable metadata and
scoped custom registration;22new/145total unit cases,123references, catalog parity,
strict typing/isolation/boundary, repeat builds and installed registry example pass.
All six head/main checks and18published blobs verified; both actual main bundles
hashed/inspected; four fresh installs each passed145tests/example. Evidence on issue18.

EQ-016 Done via PR141/head67be802cf30177e4b6958cdd9ac0d4cc199b23ed,
main8a857f1270a1b9a976ed8404ed70de9facd5636a, alpha6.25new/170total unit cases/123references,
strict types14sourcefiles/registry parity/isolation/boundary, repeat builds and both
installed examples pass. Six exact-head/main checks,15published blobs and both actual
main bundles verified; four fresh pair installs passed170cases/both examples.
Evidence on issue19 and [final R0 acceptance](R0_ACCEPTANCE.md).

All16R0 EQ stories are Done. The final acceptance delivery procedure verifies this
report publication/main gates, closes R0 and prepares EQ-017 Ready. See live milestone/
Project and R0_ACCEPTANCE.md for the completed decision. No active implementation remains. E03 remains open/
In progress, already milestone null, for R3 EQ-093. Deferred GOV-005/PR120 unchanged.

## Failures and corrections

- Final acceptance audit stopped when a scratch first-page Project cache omitted
  the R3/deferred issue IDs. Refreshed all112items using REST pagination, then
  verified the actual open/Backlog/deferred states; no acceptance gate was skipped.

- EQ-012 Project PATCH returned truncated JSON after applying Ready to release.
  Checked merge stopped. Verified live state, used unique per-call request files,
  retried the idempotent status step; actual merge/main checks and artifacts then
  verified. Main watcher now asserts actual main/origin-main identity, so a feature
  branch check cannot stand in for main acceptance.
- EQ-013 malformed-float fixture initially used "bad", a valid hexadecimal number.
  Corrected the negative input to "not-hex"; valid hex normalization remains allowed.


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
2. Complete codex/r0-review-repairs PR review,176unit/123reference/type/boundary/
repeat build/example and exact-head/main/publication gates. Actually download/hash/
inspect both post1 main bundles and four fresh pair installs before Released/Done.
3. Publish corrected delivery/acceptance evidence, reaccept EQ009/EQ013/E02/R0 and
restore EQ017 Ready. Stop; no R1 code or deferred reviewer setup. Prior evidence stays.
4. Run the planning block from .github/workflows/docs.yml; python tools/verify_session_examples.py, verify_quote_examples.py, verify_history_examples.py, verify_context_examples.py, verify_timing_examples.py; import/license checks; pinned venv compatibility, strict mypy, boundary/unit/build checks as applicable. Stop on failures.
5. Each implementation delivery requires actual successful main artifact download, commit/hash/content/clean-install verification before Released/Done. Record issue/epic/Project and this continuity alongside every story; attach every created PR to execution chat. Stop at verified R0 acceptance and report next-story readiness.

## Historical governance evidence

GOV-006 PR123 published scope correction4a0dda1bb440e7a78750c39d60f2e3f36042a0ae; current generic boundaries preserved. Deferred PR120 synchronized66def0e7bdc708ac82ce3ffeedaf0764f79cbcfe and remains untouched. GOV-007 PR126/127 delivered the autonomous handoff; initial verified main0cf343e14863e41e39ad142ac0977a9731101346. CRLF-vs-LF publication-tool mismatch was corrected by comparing committed Git blob bytes. Preserve prior history/evidence; documentation delivery alone never completes a package milestone.

Existing BUG001#144 (3points) and BUG002#145 (5points), created by separate R1
handoff preparation, now link PR146 and track these same two defects. Confirmed
points and In progress states; no duplicate implementation scope. GOV008#143 and
its handoff preparation remain untouched.
