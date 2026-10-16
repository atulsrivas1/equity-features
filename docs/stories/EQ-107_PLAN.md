# EQ107 — optional tamper-evident local event ledger

[Story207](https://github.com/atulsrivas1/equity-features/issues/207), [E15#195](https://github.com/atulsrivas1/equity-features/issues/195), [R11milestone12](https://github.com/atulsrivas1/equity-features/milestone/12); eight provisional complexity points, not days. This is a pre-code packet. EQ107 remains Backlog/unassigned until separate exact readiness review; there is no ledger implementation or database/process qualification.

## Accepted prerequisites

EQ106 is [accepted Closed/Done](https://github.com/atulsrivas1/equity-features/issues/206#issuecomment-6205931841) at main2462ded4742ff5ff7c28578b6fc30126c8a47a53/PR408, all46finalcandidate/23main checks. Separate source/API/security/builder/finaldocs, fresh bothOS archive/installed-map and actualmain/closure reviews approved, findings[]. EachOS8repeatarchives/4freshforms/89pins/6prioracceptedidentities,26declaration methods each plus combined1producer31accepted and8outer archive controls; full original producer bytes preserved. Independent captured-map/archive audit is not independent reinstall or native qualification. EQ097 is also Closed/Done. No acceptance rerun is needed.

## Concrete proposed design

Implement external stdlib SQLite storage, separate from calculations and the pure event package. [Contract](EQ-107_CONTRACT.md) and [exact profile/SQL/API](EQ-107_PROFILE.json) define one chain/store, immutable canonical events, indexed global uniqueness/references, explicit expected-head CAS, transaction acknowledgment/unknown reconciliation, full verification and contiguous recording-sequence pages. Expected anchors remain caller-retained trust; valid shortened/replaced histories are not authenticated by internal consistency. No signing/witness/R13 service, deletion/erasure policy, caller SQL, model API, hosted service or physical quota/deadline is introduced.

Creation and opening are separate: no overwriting or silent missing-file creation. Open queries journal mode without converting unsupported WAL. Actual hot-journal recovery is distinguished from application repair. Append checks <=16 indexed targets and logical reservations, not every old row; explicit verify/open scans a consistent full snapshot. Unknown COMMIT/rollback outcome poisons/closes and never replays automatically; read-only reconcile handles exact proposal identity even after later appends. Fixed through checkpoints and explicit caller start/terminal prevent arbitrary filtered/truncated pages being called a complete history. Prior page context matches content, not membership/authenticity.

## Independent pre-code expectations

[Oracle](EQ-107_ORACLE.json):12unchanged accepted linked events/10kinds/13references/9667bytes,4checkpoint goldens,10anchor and6reconciliation cases. [Literal cases](EQ-107_CASES.json):21checkpoint wire errors/precedence,17stored-state mutations,7append refusals,valid whole replacement and real count/byte-limit recipes. [Pages](EQ-107_PAGES.json):5positive/10negative continuation/coverage cases. [Boundary descriptions](EQ-107_BOUNDARIES.json) additionally freeze exact type/limit/error ordering. None is a runtime pass; future tests must use these expectations without regenerating goldens through the ledger.

Real limits use actual independently generated rows:4096events/2217818bytes, or2241events/33551262bytes before14979byte overflow. Logical32MiB excludes SQLite pages/journals/indexes/old backing; no physical storage/nodes/security promise. <=64events*16384bytes makes1MiB page aggregate overflow unreachable for valid individual events; test the reachable count/per-event limits rather than claiming impossible independent coverage.

## Qualification and documentation

[Qualification plan](EQ-107_QUALIFICATION_PLAN.md) defines39planned new methods,4actual process-death transaction cut points, fixed bounded platform owners derived from reviewed historical source patterns, with no inherited Linux execution proof,10repeatarchives/8acceptedarchiveidentities and4fresh store-light/actual-producer wheel-sdist forms on bothOS. Freeze/review exact new builder/entry/controller before execution. Current finalhead and independently verified publicmain/artifacts/lifecycle remain mandatory. [Accepted archive inputs](EQ-107_ACCEPTED_ARCHIVES.json) bind actual EQ106 main, not a new requalification receipt.

Same-story API/README/examples, anchor/recovery/privacy/retention/migration/security/compatibility/roadmap/changelog, decisions/lesson, handoff and issue/PR evidence are required before delivery. Public schema/equations/result/content/receipt identities stay unchanged; no fetching/files/SQLite/model/scheduling/publication enters calculation functions. First publish/review this packet, resolve actionable findings, then actual Ready/Atul/In progress, one runtime story at a time. Owner's all-R11 local review grant already applies; no repeat permission question. EQ108–110 remain Backlog and R11 is unfinished.
