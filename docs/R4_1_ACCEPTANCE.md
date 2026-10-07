# R4.1 release audit and evidence

Canonical [EQ130#287](https://github.com/atulsrivas1/equity-features/issues/287), [E18#276](https://github.com/atulsrivas1/equity-features/issues/276), [E19#277](https://github.com/atulsrivas1/equity-features/issues/277), [milestone15](https://github.com/atulsrivas1/equity-features/milestone/15). This audit follows verified EQ121–129 acceptance. EQ130's completed separate final-head review, successful current checks, published documentation/source/artifacts and postrelease readback are required before its Done/epic/milestone closure. The [live Project](https://github.com/users/atulsrivas1/projects/2) and canonical issue record the actual final outcome; this document does not infer completion from an open PR.

## Story gates and historical evidence

| Canonical story | Delivered scope | Actual acceptance authority |
| --- | --- | --- |
| [EQ-121 #278](https://github.com/atulsrivas1/equity-features/issues/278) | Repository foundations | [Released/Done evidence](https://github.com/atulsrivas1/equity-features/issues/278#issuecomment-6028666231); acceptance checklist checked |
| [EQ-122 #279](https://github.com/atulsrivas1/equity-features/issues/279) | Compatible standalone source extraction | [Released/Done evidence](https://github.com/atulsrivas1/equity-features/issues/279#issuecomment-6029211426); acceptance checklist checked |
| [EQ-123 #280](https://github.com/atulsrivas1/equity-features/issues/280) | Source/sink/factory specification | [Released/Done evidence](https://github.com/atulsrivas1/equity-features/issues/280#issuecomment-6029469345); acceptance checklist checked |
| [EQ-124 #281](https://github.com/atulsrivas1/equity-features/issues/281) | Explicit factories and capability admission | [Released/Done evidence](https://github.com/atulsrivas1/equity-features/issues/281#issuecomment-6029784487); acceptance checklist checked |
| [EQ-125 #282](https://github.com/atulsrivas1/equity-features/issues/282) | Publication lifecycle and independent conformance | [Released/Done evidence](https://github.com/atulsrivas1/equity-features/issues/282#issuecomment-6030216151); acceptance checklist checked |
| [EQ-126 #283](https://github.com/atulsrivas1/equity-features/issues/283) | Immutable Parquet generations | [Released/Done evidence](https://github.com/atulsrivas1/equity-features/issues/283#issuecomment-6030782648); acceptance checklist checked |
| [EQ-127 #284](https://github.com/atulsrivas1/equity-features/issues/284) | Transactional DuckDB output sink | [Released/Done evidence](https://github.com/atulsrivas1/equity-features/issues/284#issuecomment-6031394363); acceptance checklist checked |
| [EQ-128 #285](https://github.com/atulsrivas1/equity-features/issues/285) | Independent custom source/sink extensions | [Released/Done evidence](https://github.com/atulsrivas1/equity-features/issues/285#issuecomment-6031899095); acceptance checklist checked |
| [EQ-129 #286](https://github.com/atulsrivas1/equity-features/issues/286) | Nine-package composition and repository independence | [Released/Done evidence](https://github.com/atulsrivas1/equity-features/issues/286#issuecomment-6032694854); acceptance checklist checked |
| [EQ-130 #287](https://github.com/atulsrivas1/equity-features/issues/287) | Release audit, continuity and R5 readiness reconciliation | This documentation change; completed review, publication/readback and final lifecycle evidence recorded on the canonical issue before completion |

Each canonical acceptance links contributing PRs, actual separate reviewer/head/findings disposition, native/source/installed evidence, same-story documentation and Released/postreadDone. The reviewer is /root/eq121_component_review: separate local automated review, not hosted activation or human review. GOV005 remains separate. Original R4.1 pre-code plans and [R4 acceptance](R4_ACCEPTANCE.md), historical versions/retired IDs/source/private receipts remain preserved. Architecture planning and GOV014/GOV015 do not substitute for delivered story gates. Milestone counts include governance and epics; ten stories is not a claim that the milestone contains only ten issues.

## Actual qualified versions and publication

| Distribution | Qualified version | Role |
| --- | --- | --- |
| equity-feature-contracts | 0.0.4a4 | Canonical inputs/results and pure acquisition protocols |
| equity-features | 0.0.4a4 | Pure supplied-data calculations |
| equity-feature-io-contracts | 0.1.0a2 | Separate I/O publication/factory contracts |
| equity-feature-io-sdk | 0.1.0a2 | Explicit registries, codecs, publication/conformance |
| equity-feature-duckdb | 0.1.0a8 | Standalone bounded source adapter |
| equity-feature-parquet | 0.1.0a0 | Immutable Parquet result generations |
| equity-feature-duckdb-sink | 0.1.0a0 | Serialized transactional output sink |
| equity-feature-example-extensions | 0.1.0a0 | Public synthetic custom source/single-instance memory sink |
| equity-feature-workers | 0.1.0a1 | Typed/buildable version marker skeleton; no commands |


CPython3.12 x64 native Windows/Linux. Optional engines are DuckDB1.5.6, NumPy2.2.6 and PyArrow20.0.0 for their declared components/full composition; pure and lightweight installs omit them. Versions are the tested combinations, not a guarantee about arbitrary releases/platforms. Workers.a0 requires historical SDK.a0; forcing it with SDK.a2, or IOcontracts.a1 with SDK.a2, was rejected by actual complete-candidate offline resolution and independent forced-install pipcheck. Current workers.a1 -> SDK.a2 -> IOcontracts.a2 -> canonicalcontracts.a4 is qualified; worker exports version only, no entrypoints/jobs/claims/scheduler/catalog/generation.

Accepted EQ129 [public UTF8 LF release receipt](stories/EQ-129_RELEASE_RECEIPT.json) SHA256 `dc260d38857d864c0fa87287c2f236896405e4994d539024f57ad4671ca9a745` records these actual releases:

- `equity-feature-io` actual accepted main `d28eddf28d15b4667e25eee92bf7d375c3a445eb`, reviewed `2750f71fd9ca7c5cbabad51ae50fa8850bb170ed`; 165 public blobs equal the reviewed tree.
- `equity-feature-workers` actual accepted main `97fdc096dff8498b6d231cd00fd2cdfc3b8d3a7a`, reviewed `d72788a49e7453637f958939068f32fe29a6b0fc`; 29 public blobs equal the reviewed tree.
- `equity-features` actual accepted main `c45311b59e3df8c601225578bb7a2d3f329ed4bd`, reviewed `0714afa81cd3c3add172c169806c329fff044a77`; 390 public blobs equal the reviewed tree.

All146 archive files (repeated dependencies and16 historical candidate archives included), sixteen actual server ZIP SHA256 digests and all202 downloaded files were checked against manifests/public source inventories/native reports/harnesses/probes/Atul ownership/expiry. Every actual-main archive equals final-qualified metadata by native platform. Current source/SDK/optional/factory/publication/backend/extension/matrix/worker/core qualification stays separately scoped. Actual EQ129 main producer reports: matrix: Linux CPython3.12.14, Windows CPython3.12.10; worker: Linux CPython3.12.14, Windows CPython3.12.10; core: Linux CPython3.12.14, Windows CPython3.12.10. Later EQ130 documentation-head reports retain their own runtimes/source identities; do not extrapolate patch versions between runs.

The declared channel is successful public main CI artifacts with30-day retention. The receipt records exact run/artifact names, IDs, hashes and expiry. Download the native bundle from its named successful run using `gh run download RUN --repo atulsrivas1/REPOSITORY --dir DOWNLOAD_DIRECTORY`, verify manifest/archive/ZIP identities, and follow [installation](INSTALLING.md), [build delivery](BUILD_DELIVERY.md) and companion installation docs. Current composed matrix bundles contain nine current distributions at top level plus separately labeled historical test candidates: install the current supported combination, never the historical directory. No registry or stable tag was published. Expired/missing channels require fresh qualification; source alone is not proof that an artifact is still available.

## Independent behavior and boundaries

Four fresh native matrix wheel/sdist forms each exercise six meaningful methods/nine complete routes: direct and factory synthetic custom source into memory/Parquet/DuckDB sinks, plus accepted standalone minute DuckDB source into all three. Custom500shares/51200notional/102.6close-weighted proxy remains distinct from actual-notional VWAP102.4 and the minute source8shares/11.625weighted/notionalnull MISSING_INPUT. Full twelve result facts, quality/status/reasons/units/nulls/UTCns/source/availability/algorithm/schema/config/evidence bytes are independently checked and replayed/read back. Source catalog/original/optimized Parquet bytes stay invariant; composed source WAL is absent before/after, not a WAL-present qualification. Backend source-database-plus-WAL rejection/invariance is separately exercised.

Core-only execution forbids/omits I/O/workers/engines/network dependencies while calculation passes; extension-only imports omit calculation library/fixture/backends. Full composition verifies site-packages versions, pipcheck, public positive typing/three rejected calls, exact core fingerprints and actual resolver/forced-pipcheck conflicts. Pure development633 tests and installed numerical/consumer/resource reports remain scoped evidence. No new mathematics, numerical mode, schema, source availability or private execution is introduced by this audit.

Parquet four native forms retain17 physical/eight real-process/two resource cases. DuckDBsink four native forms retain18 physical/nine real-process/two resource cases. The original required Windows PR37579927602 failure is preserved with rework6032201654: venv launcher exit did not establish interpreter/lease-owner exit. Corrected fixtures establish nonce-bound actual runtime ownership before backend imports/storage, retain a Windows process handle before startup acknowledgement, and require actual exit before recovery observation; Malformed-phase cleanup was separately exercised; timeout cleanup was inspected against retained runtime ownership. [EF-L042/043](knowledge/LESSONS.md) preserve cleanup/citation/receipt-serialization findings and dispositions. Raw Windows CRLF qualification and public Git LF receipt digests are explicitly distinct; current release receipt is UTF8 LF and directly reproducible from its public Git blob. No failed required run is replaced by a green sibling or relaxed assertion.

## Limits and migration

Keep original pure contracts/features and standalone source imports. Current I/O API/specification/tutorial/conformance/build docs live in [equity-feature-io](https://github.com/atulsrivas1/equity-feature-io); [migration](DUCKDB_MIGRATION.md) and core API redirects retain accepted R4 history. Canonical result/input schemas remain in canonical contracts; backend conversions/fetching/files/credentials/scheduling/publication never move into calculations. Direct injection and explicit per-run factories remain usable without workers. Local executable custom adapters are trusted caller code, not a remote upload sandbox.

Storage capabilities are backend-specific: single-instance memory sink has caller-owned lifetime/quotas and no eviction/durability/concurrent guarantees; Parquet filesystem/retention controls and DuckDB serialized-writer/OS-lease/transaction assumptions remain explicit in their package docs. Measured two-workload observations require parity and do not prove a speedup, throughput, hardRSS cap, power-loss/network-filesystem certification or arbitrary concurrency. Sink idempotency/replay is not worker task claims/retry/resume/barrier/catalog selection. No worker commands or private historical generation are complete.

Accepted private R4/extraction certificates retain exact immutable scope/script/golden/source/report/archive bindings and their recorded Windows execution limits, without another private rerun. No private dataset rows/names/paths/credentials are published. Synthetic fixture rights and Apache-2.0 code licensing do not establish provider/calendar/PIT/source entitlement. Missing eligibility/known-at/notional/PIT inputs stay missing; source declarations and retrospective hash equality do not establish truth or atomic snapshots.

## Final exit and next authorized work

EQ130 acceptance requires its reviewed docs/publication/current artifacts/readback; all ten stories must then be Closed/ProjectDone before epics close and milestone15 is verified zero-open/closed. Reconcile R5 issue dependencies only after actual287Done. Highest dependency-satisfied next story is EQ057#65, prepared Ready for a future explicitly authorized worker session; the current bounded release stops here. See [exact R5 resume](R5_AUTONOMOUS_HANDOFF.md). No automatic new session, R5 implementation, provider/remote services, registry/stable tags, source-store changes or private generation; no invented deadline/reminder.
