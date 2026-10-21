# Equity delivery releases: revised plan

Owner requested October 20, 2026. [GOV035 #567](https://github.com/atulsrivas1/equity-features/issues/567). This is an equity-only replanning proposal based on delivered capabilities and the owner's new three-layer working agreement. It replaces the proposed future equity allocation when reviewed, published and migrated; it does not renumber historical releases or silently change live issue dependencies. [Machine-readable allocation](plans/equity-delivery-replan.json) retains every EQ147–181 story and the proposed new integration work.

## What changes

Deliver a usable local pipeline first. Add later features as complete library/I/O/worker slices, with output-store readback and a browser demonstration in every release. Move scope reconciliation to the first delivery. Bring sessions/references forward, combine channels with trend work, put remaining statistical projections with tape prerequisites, and split structures, events and delayed outcomes into individually qualified deliveries. Do not defer worker and I/O integration to a final catch-all release.

The new release names are **EF1–EF9** (Equity delivery 1–9). Thus “EF4” means relative statistics/anomalies, while historical R4 still means the already accepted original DuckDB adapter release. Existing EQ story IDs and historical acceptance receipts stay stable. R18 remains the active measured execution improvement release; EF names are the proposed functional delivery series, not a reset of R0–R18.

This document is a concrete draft plan, not implementation acceptance or a timetable. Current status belongs to the [Project](https://github.com/users/atulsrivas1/projects/2). Existing milestone memberships/dependencies remain binding until the reviewed migration below occurs. Options R25–R29 and their planning records are outside this replan and unchanged. API/SaaS and production application work are outside the EF release gates.

## Reuse the delivered baseline

| Established scope | Reuse | Qualification limit |
| --- | --- | --- |
| Original equity core | 39 named built-in batch features across bars/trades/quotes, daily history, baselines, relative and breadth subsets | A broad source-family label does not make every member implemented; update/restore/merge support is per feature |
| R4/R4.1 I/O | Canonical adapter contracts, public SDK, catalog-backed historical reads and DuckDB/Parquet sinks | Historical DuckDB adapter selects original Parquet via a catalog; arbitrary DuckDB-table input needs explicit mapping/qualification |
| R5/R5.1 workers | Manifests, bounded execution, retries/cancellation, immutable generations and serialized publication | Accepted synthetic execution is not admitted private historical generation or universal multiwriter support |
| R17 intraday | Eight batch outputs: EMA/RSI/ATR and five band outputs; supplied-history replay and accepted worker bindings | No inferred incremental/update/restore/merge capability; prior measured alternatives were nonwins and sequential remains the baseline |
| Existing generic consumers | Configurable scanners/rankings/watchlists and endpoint labels | Reuse their APIs; do not claim complete source-specific policy catalogues or observed-path labels |

Evidence: [R17 accepted aggregate #465](https://github.com/atulsrivas1/equity-features/issues/465), [R4.1 acceptance](R4_1_ACCEPTANCE.md), [R5 acceptance](R5_ACCEPTANCE.md), [BUG006 #337](https://github.com/atulsrivas1/equity-features/issues/337). This readback is not a new source audit or numerical rerun. Freeze actual compatible core/I/O/worker package versions and artifacts in each EF contract before implementation.

## Revised functional releases

| Release | Usable outcome | Existing story allocation | New layer/delivery work |
| --- | --- | --- | --- |
| **EF1 — Working equity pipeline** | Selected accepted session OHLCV outputs run from admitted local DuckDB or labelled synthetic input to a new output DuckDB, with browser readback | EQ164 (#504): reconcile accepted/remaining family and worker scope | Compatibility/independent fixture contract; source/mock mapping and output-store configuration; worker composition; executable demo and integrated acceptance |
| **EF2 — Sessions, levels and references** | Supplied session/status clock, extended sessions, calendar-period levels, VWAP anchors/gaps/opening drive and governed reference/action context | EQ165–169 (#505–509) | Family-specific I/O mapping and worker binding; EQ169 becomes the complete EF2 gate |
| **EF3 — Trend, momentum and channels** | MACD, DMI/ADX, stochastic/%R, OBV/A-D/CMF, aligned Ichimoku, admitted price channels and squeeze components | EQ147–152 (#481–486), EQ170 (#511) | Family I/O and worker binding; EQ152 gate expands to include EQ170 and its independent channel/squeeze evidence |
| **EF4 — Relative statistics and anomalies** | Correlation/beta/residuals, separately defined daily/intraday log-return RV, robust history/ranks and volume pace/anomaly measures | EQ153–157 (#487–491) | History/benchmark mapping, worker/readback qualification and EQ157 complete EF4 gate |
| **EF5 — Tape, quotes and path statistics** | Rolling trade/signing windows, microprice/quote dynamics, VWAP/path slopes, efficiency/choppiness, notional-ranked prints and remaining equity projections | EQ158–163 (#492–497), EQ172 (#513) | Tape/quote/history mapping and bounded workers; EQ163 gate expands to include EQ172 |
| **EF6 — Price structures and patterns** | Independently specified candle/structural catalogue and the price-action projections assigned to that scope | EQ171 (#512) | Pattern-window mapping, workers and a new bounded EF6 acceptance/demo story |
| **EF7 — Events and fundamentals** | Arithmetic over supplied point-in-time event/fundamental/short-interest/reference facts | EQ173 (#514) | Versioned PIT input mapping, workers and a new EF7 acceptance/demo story; no provider or model acquisition |
| **EF8 — Observed outcomes** | Mature observed-path MFE/MAE, barriers and time-to-target, separate from current signals | EQ174–175 (#515–516) | Mature-path input/output mapping, delayed workers and demo; EQ175 retains its cumulative EQ170–174 numerical audit |
| **EF9 — Equity policies and complete coverage** | Explicit admitted scanner/watchlist/context policies, confirmation/candidate lifecycle, score/membership history and complete worker/output reconciliation | EQ176–181 (#518–523) | Policy-specific I/O and execution; EQ180 audits accumulated per-release receipts and EQ181 verifies all selected equity scope and residuals |

EF1–EF9 are prioritized delivery slices, not mathematical dependencies on every preceding release. Every one of the 35 EQ147–181 stories has exactly one allocation. The existing 78-family/command ledger remains the reconciliation source for EQ164: inventory records are not counts of unique formulas or accepted numerical parity. Discovered finer gaps require a numbered story before their containing release is Ready, never a silent omission.

## EF1 contract and missing work

Start with five accepted session-bar outputs: open, high, low, close and volume. The contract freezes exact instrument/session/input eligibility, price and volume units, timing/known-at/coverage, missing versus empty semantics and the accepted feature identities. This is a bounded first execution slice; it does not declare every accepted feature source-mapped. EQ180 ultimately verifies every admitted output, including accepted baseline features.

Four proposed new stories are identified in the allocation file; they are **task specifications, not yet created GitHub issues**. Assign canonical IDs/issues during reviewed migration before implementation:

1. **EF1-C:** verify the accepted library contract and independent synthetic expected fixtures, preserving pure numerical code; record no-change if no kernel change is needed.
2. **EF1-IO:** qualify exact configured local DuckDB source/schema read-only, reuse the catalog adapter when applicable or implement a direct-table adapter only where needed; supply deterministic synthetic fallback and configure the existing sink for a separate output database.
3. **EF1-W:** compose the admitted adapter, existing calculations and sink through bounded workers, with exact source/task/run identity, missingness, cancellation, retry, conflict and factual commit-lookup behavior.
4. **EF1-A:** qualify direct-library/worker/stored full-result parity and the actual browser journey, plus relevant installed/artifact/CI/publication evidence.

Operational flow: **source DuckDB / synthetic input -> input adapter -> worker -> pure feature library -> output sink -> separate output DuckDB**. Workers invoke adapters and libraries, then pass canonical results to sinks. Adapter/sink conversion preserves canonical library contracts. Real observations and synthetic facts retain distinct explicit provenance; fallback does not invent missing observed fields, historical availability or completeness. If an input is unsuitable, use a declared synthetic example or return unavailable rather than manufacturing an admitted real-data result.

Exact local source/output paths, rights, schema and repeat-write/ownership policies are pre-code inputs, not facts established by this plan. No database has been opened or created here. Output filesystem qualification is separate from source-drive selection. Reuse the existing sink's serialized publication, receipts and readback; do not create a competing DuckDB writer per worker or infer network-store safety.

Each EF2–EF9 has separately scoped **IO** and **W** task specifications. EF6 and EF7 additionally need their own **A** acceptance stories. They must become numbered, linked issues before those releases are admitted; existing aggregate stories do not erase layer-specific ownership. A no-change decision with evidence is valid where existing adapters/workers suffice. Demo delivery is part of each acceptance story rather than a final cleanup task.

## Dependency amendments proposed for review

Preserve every real operand, state, coverage and publication dependency. Replace only blanket portfolio sequencing with the exact accepted capabilities actually consumed. Common baseline means the reviewed EF1 composition plus pinned accepted runtime; it is not an unqualified reuse of changed EQ142 development tools.

| Story | Existing blanket edge | Proposed replacement/addition |
| --- | --- | --- |
| EQ152 | EQ146, full R18 aggregate | EF1 acceptance plus EQ147–151 and EQ170; R18 adoption qualifies separately when used |
| EQ157 | EQ152, unrelated indicator release | EF1 acceptance plus EQ153–156 and its new IO/W tasks |
| EQ163 | EQ157, entire statistics release | EF1 acceptance plus EQ158–162 and EQ172; retain EQ172's actual EQ155 dependency |
| EQ169 | EQ163, entire tape release | EF1 acceptance plus EQ165–168 and its new IO/W tasks |
| EQ175 | Combined EQ170–174 plus EQ169 | Retain these cumulative numerical/reference checks; add EF8 delayed-path qualification. Do not close after only patterns/events |
| EQ164 | GOV032 planning publication plus accepted inventory/coverage decisions | Explicitly substitute published GOV035 equity allocation only after reviewed migration; retain accepted inventory/coverage decisions and complete reconciliation obligations |
| EQ176/EQ177 | EQ175 prerequisite | Retain EQ175 until exact per-policy producer catalogues/contracts justify a separately reviewed replacement. No placeholder producer set establishes Ready |
| EQ180/EQ181 | Existing aggregate equity acceptance | Retain every admitted policy/worker coverage gate, EQ175 and EQ146; consume per-release receipts rather than doing all integration here |

These replacements take effect only through reviewed publication and explicit issue/epic/milestone/Project reconciliation. Until then original issue dependencies apply. EQ143–146 inside R18 are unchanged: measured reuse follows actual EQ142 acceptance; legal scheduling follows reuse; resource adoption follows qualified scheduling; EQ146 audits the measured result. Hardware efficiency remains a core goal, not an optional optimization discarded by this replan.

Additional exact prerequisites: EF2 supplies the reference facts required by EF7; EF4 EQ155 supplies robust summaries required by EF5 EQ172; EF5 EQ158 supplies its trade primitives. EF3 EQ170 requires EQ149 and must freeze bandwidth-percentile population/rank conventions; if the approved design consumes EQ155, record that exact dependency and sequence that part after EF4 instead of assuming an earlier release number makes it ready. This unresolved choice blocks the affected contract's Ready admission. EF6's whole assigned price-action scope and EF5's whole EQ172 projection scope remain accounted for. EF8 uses mature observations in a separate path; current EF9 signals never consume future observations. Their current EQ175 story-level admission gate remains until exact reviewed producer sets support an amendment; release admission is distinct from runtime causality.

## Parallel preparation versus implementation

EF1 contracts, fixtures, source/schema plans and three handoffs can be prepared while EQ142 completes under its current owner. Independent EF feature contracts can likewise prepare once their own inputs/specifications are known. This removes a planning stop; it does not admit blocked code or claim R18 completion.

Implementation is allowed only after reviewed plan/dependency migration, actual story Ready admission and an isolated resource window or separately isolated execution resources. Preserve all frozen EQ142 sources, runtime environments, existing original qualification jobs, original synthetic protocol and official-study evidence. Do not launch competing local builds/tests, scans, demonstrations or benchmarks during its reserved qualification/timing window. No private data read is authorized merely by creating this public plan.

Use three fresh implementation workers for the selected functional release: libraries/contracts, I/O and workers. Each gets only layer context and pinned shared boundaries, with a fresh independent PR reviewer and coordinator integration. Separate release work requires its own ownership/resource decision; three layers do not mean three unrelated releases at once. Do not reuse a completed release worker. Use suitable token-efficient models, never Astra. Coordinator review precedes push; current independent review and CI precede merge.

## Acceptance for every EF release

- Reviewed mathematics and contracts first: identities, dimensions/precision, clocks, availability, initialization, coverage, revisions, errors and explicit batch/update/restore/merge/replay capability limits.
- Independent synthetic/licensed expected fixtures, including temporal, missing/empty/zero, incompatible-scope, mutation/alias and numerical edge cases. Output comparison includes values/nulls/status/quality/reasons/evidence/headers and identity, not only floats.
- Compatible adapter mapping and worker binding, bounded resources and deterministic persistence/retry/readback. Preserve full-task failure granularity and publication authority.
- Actual direct/worker/output-store roundtrip parity plus relevant installed both-platform/artifact/build/typing/CI checks. A changed source cannot inherit an old artifact by version label alone.
- A browser demo of that release's new slice: selected inputs and real/synthetic provenance, run status, outputs/evidence and matching stored readback. Show missing-input/retry behavior relevant to the slice. A local demonstration harness is enough; it is not a new production application or SaaS.
- Measured performance against declared baselines where changed execution claims improvement; preserve nonwins and safe fallback, one coordinated CPU/memory/I/O budget and prospective adoption rules. Do not invent speed/SLA claims.
- Same-story docs, independent final-head review, actual delivery/readback and exact Backlog -> Ready -> In progress -> Code review -> Test -> Ready to release -> Released -> Done lifecycle evidence. Mere merge or demo success is not completion.

## Public migration checklist

1. Review this packet under GOV035, retaining its allocation and exact dependency amendments. Update the packet and renew review if scope changes. No approved mathematics is changed by release grouping.
2. Create EF1–EF9 milestones and numbered epics/new task issues from the allocation. Link all new tasks and retained EQ stories to their owning delivery without changing completed historical releases or unrelated options records. New implementation starts Backlog, unassigned, without deadlines. Record migration receipts and reverse mappings.
3. Update the 35 existing equity story bodies/milestones and epic child lists together, with old allocation/dependency history preserved. Acknowledge R19–R24 are superseded allocations after migration; never close them as implemented or reassign an accepted story to pretend a new release is delivered. Resolve old epic rollup disposition explicitly as planning supersession with actual Project state, not Done implementation.
4. Reconcile GOV032's equity allocation and the equity portion of PR524 through linked follow-up; preserve GOV033/options source/history and all their actual dependencies. Do not treat this packet as publication of unrelated option planning.
5. Pin actual EF1 runtime artifacts and exact selected source/mock/output contracts, review independent fixtures and the resource window, then admit only dependency-ready EF1 work. Parallel functional preparation is permitted; active EQ142 remains owned elsewhere.

Until migration is completed and read back, EF labels are a proposed delivery map. The machine-readable file marks this explicitly and contains every old-to-new story allocation and every proposed new task. GOV035 can be delivered as a reviewed plan, while actual migration is a separately evidenced gate before EF implementation. No old issue has been moved or closed by drafting this document.

## Evidence and remaining work

Author preparation used live Project pagination on October 20, current R17/EQ142 records, accepted-release receipts, original source-safe R19–R24 plans, and the owner-designated local matrix/processing plan. Local source inventories informed scope checks but are not included in public files. Three read-only preparation agents identified delivered reuse, exact dependencies and scope traps; their reports are not independent numerical/runtime acceptance.

Prepared files are source-safe planning documents only. No numerical implementation, N: data access, output DB creation, benchmark or hosted service was performed. Initial author inspection hit a missing guessed planning directory and a PowerShell pipeline parse error; both were corrected through actual file discovery/valid syntax without source/runtime changes. Current CI and final delivery evidence are recorded on the linked PR; do not infer them from this draft.
