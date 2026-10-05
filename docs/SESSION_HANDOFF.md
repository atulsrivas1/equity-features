# Development continuity

Updated 2026-10-04. Public repository: atulsrivas1/equity-features; Apache-2.0. Read AGENTS.md and PUBLIC_DEVELOPMENT.md. GitHub Project is the actual status authority.

## Completed work and current scope

EQ-001 Done via PR106: 39 builtin IDs. EQ-002 Done via PR112: 20 session/bar/trade definitions and 17 reference cases. EQ-003 Done via PR121 (merge af0dbb8552a3667c242bd46756bf6cb2292d4a5d): 3 quote definitions and 26 reference cases. EQ-004 Done via PR124 (merge 4fbe9e00d278a7bb70ca024c094b63b8e83dbebb): 8 historical definitions and 31 reference cases. Their final-head CI, default-branch publication and post-publication checks are recorded on their issues. These 74 mathematical reference cases do not qualify production kernels, performance or provider inputs. No production package or public registry release exists yet.

EQ-004 established SMA-seeded EMA, Wilder RSI/ATR, explicit anchors, strict recursive gap behavior, prior-only extrema and sample simple-return volatility with explicit scaling. Preserve these recorded decisions. EQ-005 is Ready; EQ-006–016 remain Backlog at this snapshot. Verify live Project before reporting status.

## Autonomous R0 handoff

Owner requested a separate chat to complete bounded R0 work. [R0_AUTONOMOUS_HANDOFF.md](R0_AUTONOMOUS_HANDOFF.md), tracked by GOV-007 issue125, contains the mission, kickoff prompt, remaining EQ-005–016 story plans, provisional points, tests/docs and delivery gates. The new execution chat owns R0 after this document is published; the original chat stops implementation to avoid concurrent writes. Resume by reading that package and the live EQ-005 issue6, preparing its full story plan and using the agreed workflow. Continue one story at a time through R0 acceptance; do not start R1 automatically.

Both source-independent distributions are planned: equity-feature-contracts and equity-features. R0 includes actual contracts/validation/registry foundation, not only documents. Establish and verify a declared internal foundation-artifact channel under EQ-009 before declaring implementation delivery; merging source alone is insufficient. No public registry publication or stable release version/date is authorized. E03 spans R0 and R3 EQ-093: retain the later child and reconcile epic milestone tracking honestly before closing R0.

## Product and review boundaries

Calculations receive in-memory inputs and perform no fetching/database/file/credential/job/output/clock work. Adapters/workers/remote access remain later releases. Other applications are separate products; see decisions/product-boundaries.md. GOV-006 issue122/PR123 delivered scope cleanup (merge 4a0dda1bb440e7a78750c39d60f2e3f36042a0ae). EQ-094 is retired not_planned with no active Project/milestone/parent scope; never reuse it. 93 active EQ stories remain. GOV-004/PR118 is a superseded proposal; historical diffs remain visible. EQ-093 custom calculators remains Backlog/R3, with no implementation or sandbox claim.

GOV-005 issue119/PR120 remains open and explicitly owner-deferred. Do not activate or merge it as part of R0. Deferred branch synchronized at 66def0e7bdc708ac82ce3ffeedaf0764f79cbcfe with passing checks. Existing author self-review, CI, acceptance/documentation and publication checks apply. Record actual reviewers/limitations; no separate hosted bot or independent human review is claimed. Administrator merges do not imply human review.

## Verification and recovery

EQ-005 delivered via PR128 (squash b3a39a4209580e95ebe7f953d63b81f839901dfe).
Final head fee6be4c20581567c28b4ef6e79b7b960dc004b0 passed both CI checks;
100 reference cases/planning passed before and after delivery, all eight Git blobs
matched GitHub bytes, main CI passed. Issue6 Done/closed and E01 checklist verified.
Merge-commit attempt was rejected (repository allows squash only); checked commands
stopped, then allowed squash on the same head succeeded. A Windows console Unicode
print failed after the successful issue close; live closure was independently
verified and UTF-8 stdout fixed. No failed command counts as validation.

EQ-006 In progress on codex/eq-006-timing-policy, confirmed8points. Plan and timing
policy separate market C, reference knowledge K and evaluation E with C,K<=E;
delayed EOD knowledge is not instantly available at close. Split/dividend basis
and reconstruction are explicit.23design fixtures added. Broad full-roadmap Project
query hit rate-cost rejection; stopped, switched to targeted cached-ID query,
verified live transition. PR120 stays deferred; author self-review only.
Resume: run all five tools/verify_*_examples.py and planning block in docs workflow;
inspect diff, linked PR, Code review/Test, exact final-head CI, allowed squash merge,
GitHub bytes vs committed blobs and main checks before Released/Done. Update E01,
then EQ-007 planning. No production kernels/source admission claimed.


Documentation CI verifies 93 active EQ IDs, 39 feature IDs and all eight lifecycle states. Run the planning code in .github/workflows/docs.yml, python tools/verify_session_examples.py, python tools/verify_quote_examples.py, python tools/verify_history_examples.py and git diff --check; add relevant story-specific checks as contracts/code grow. Final-head CI and default-branch delivery verification remain required.

Use explicit UTF-8 and fail-fast checked subprocesses. GOV-002 recorded a local encoding failure and a shell sequence that wrongly continued to merge; corrected post-merge checks passed. GOV-006 recorded an unsupported Project CLI flag, corrected before publication; no failed command counts as validation. Public fixtures are synthetic or explicitly licensed. Never publish private data, credentials or internal paths. Documentation delivery is not parent milestone/package delivery. Preserve unrelated work and update this file after meaningful decisions, failures, validation and completed work.

GOV-007 handoff PR126 merged 508fd81d0021aea44162b26e1e1c261449c28038 with both final-head CI checks passing. A post-publication byte assertion stopped on local CRLF versus GitHub LF; normalized text matched. Corrected verification compares GitHub content bytes with `git show HEAD:path` bytes, not checkout bytes; all four changed files matched committed blobs and all 74 references/planning checks passed. This verification-tool mismatch did not change published content. Use committed-blob comparison for exact publication checks on Windows.

## Package foundation execution

EQ-006 delivered via PR129, final head31101d0f25630b0b117d3e1f65f16ae0b5c120aa,
squash5c8edf56392ac319483669c7f8890597b489ff68.123references, exact final-head
and main CI, eight changed blobs verified. Issue7/E01 Done. CLI GraphQL quota later
exhausted until03:25:33UTC; REST Project API checked against official GitHub docs,
status updates verified through returned field values. Draft conversion connector
lacked repository write access; signed-in GitHub UI converted PR129 instead.
No quota/review/release gate was bypassed. Local checks use explicit UTF-8.

EQ-007 In progress: confirmed5points; two src distributions, py.typed/license,
inward dependency and isolated import smoke. No numerical APIs. All123references
and import/planning checks pass locally. Review/exact-head CI/main publication
pending; after source merge retain Ready to release awaiting EQ-009 artifacts.
EQ-008 may be pulled after source gates; no second active implementation. Resume:
inspect diff/open linked PR, formal lifecycle and final-head CI; squash merge,
verify committed blobs/main CI. Do not mark EQ-007 Released/Done on merged source.

EQ-007 staged diff check stopped on inherited trailing blank lines in copied LICENSE
files; removed trailing whitespace only, kept root license and all license text.
Import smoke compares normalized license text. No commit/push occurred on failure.
