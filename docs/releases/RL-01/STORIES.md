# RL-01 stories (the nine Ready)

> Working document, not a decision. PO, 2026-10-30. Internal, synthetic, pre-release. Template: `docs/playbook/TEMPLATES/story.md`. Status, order and bumps: [RELEASE-MAP](../../planning/RELEASE-MAP.md). Every story: one branch, one PR, three reviews, the repo's own checks (core: `python tools/pre_merge_check.py` and `check_boundary`; io and workers: that repo's `verify_versions` plus its gates, io also `check_extraction`; `check_boundary` is core-only), no new unit tests, changelog with Verified/Not verified, no provider names, no performance or "production" wording.

**Catalogue rulings** (cited as CAT below): [`docs/plans/records/po-rulings-contract-catalogue-2026-10-29.md`](../../plans/records/po-rulings-contract-catalogue-2026-10-29.md) (verbatim copy of the `work/` original; acceptance A-K, wording section 5). The Architect's contract-home note stays local in `work/` and is not cited as a contract.

### RL-01-03: DV1 reviewer-verdict record
- Lane core, size S, no blockers. Priority: C4 evidence.
- A new `docs/qa/DV1_PR_REVIEWER_VERDICTS.md` follows the layout of `docs/qa/EF4_PR_REVIEWER_VERDICTS.md`.
- It has one row per merged DV1 PR named in DECISIONS.md rows dated 2026-10-29 to 2026-10-30 (core, io, workers).
- Each row is sourced only from PR bodies, comments, commits, DECISIONS.md and recorded verdict files; where verdict text is absent the cell says "not recorded". No verdict is invented.
- No code, contract, fixture or version change.
- **Contract:** none (record only); format precedent `docs/qa/EF4_PR_REVIEWER_VERDICTS.md`.
- **Data capability:** reads GitHub PR text and repo docs; writes one markdown file; no source data, no client/server split.

### RL-01-07: S6 part 2, catalogue lookups in io-contracts (bump 1)
- **Status (2026-10-30): Merged: io #68 (3410402); io-contracts bump #69 (927372a) to 0.1.0a6.**
- Lane io, size M, no blockers. First in the io writer order S6p2, S8, S2, S4, S5. Priority: client value first (S6 and S8 ahead of S2). Decisions: catalogue rulings D1-D5 apply.
- `equity_feature_io_contracts.catalogue` exposes `producers()`, `by_feature_id(feature_id)`, `version()` returning catalogue version plus per-producer contract_version (CAT A, G).
- It imports only io-contracts types and packaged data; no core or workers import (CAT J).
- Docs copy, packaged data and regeneration from core stay byte-equal under the existing gate (`tools/check_contract_catalogue.py`).
- io-contracts takes a minor pre-release bump announced in the PR; `verify_versions` passes; changelog lists producers touched (CAT, section 6). The coordinator assigns the version string.
- Frozen core bytes, `check_boundary.py`, `check_extraction.py` unaffected, each stated with its result (CAT I).
- **Contract:** frozen core contract JSON is the authority (CAT section 2, item 1); catalogue families present on main: EF3, EF4, EF5 (RELEASE-0-RULINGS section 1).
- **Data capability:** reads packaged catalogue data (synthetic contract metadata); no market data; library-only, client of installed wheel.

### RL-01-08: S8, `check_input` and `check_output`
- **Status (2026-10-30): Merged: io #70 (3409c7a).**
- Lane io, size M, after RL-01-07.
- Both are structural checks only; they never compute or replace library refusals and cite the failed catalogue rule (CAT section 2, item 3).
- The docs carry a copy-paste example; a client validates a sample input and output in under 10 minutes using only the installed wheel (CAT D); a reviewer who did not write it times it and the time goes in the PR.
- Wording calls them structural checks, never value-correctness checks (CAT section 5).
- A bump, if any, follows the RELEASE-MAP order.
- **Contract:** catalogue pages for EF3, EF4, EF5 (generated); CAT sections 2 and 4.
- **Data capability:** reads catalogue data and a small synthetic example; no source data.

### RL-01-09: S2, EF2 and EF1 catalogue families
- **Status (2026-10-30): Merged, partial EF1: io #71 (e47b0c5); PO accepted partial EF1, follow-up RL-01-20.**
- Lane io, size M, after RL-01-08 (serial on the io writer).
- Generated pages and JSON for the EF2 and EF1 producers exist beside the existing families; INDEX.md lists the families present (CAT M5).
- The unparsed-keys list is present and empty, or PO-accepted in writing (CAT M4, H).
- Drift gate green; docs, packaged and regenerated copies byte-equal; no hand-edited generated file (CAT M7).
- Only new per-family map files and generated output change.
- **Contract:** frozen EF1 and EF2 core contracts (authority); catalogue extraction map is new.
- **Data capability:** reads core contract JSON; writes generated pages; no source data.

### RL-01-10: S4, link layer
- **Status (2026-10-30): io half merged: io #72 (0dbe5f5). Workers docs half stays open as 'RL-01-10 workers lane'.**
- Lane io + workers (docs only), size S, after RL-01-09.
- io adapter API docs and workers docs link each producer to its input and output catalogue pages; every link resolves (checked by a link check in the PR).
- Only docs files change; catalogue directory untouched.
- **Contract:** catalogue pages (RL-01-07/09 output).
- **Data capability:** none; docs links.

### RL-01-11: S5, header cross-check and IO_V1 reference
- **Status (2026-10-30): Merged: io #73 (f1251ce).**
- Lane io, size S, after RL-01-10.
- This story owns the catalogue-versus-code header check across the io AND workers declarations (one check; RL-01-12 does not reimplement it). A check compares catalogue output headers with the headers the io and workers code declare; every mismatch is listed, none is silently dropped.
- The IO_V1 doc gains one cross-reference line.
- The PR states zero golden or hash churn, confirmed before the edit (CAT order item 7); if churn appears, stop and report to the PO.
- **Contract:** catalogue output pages; IO_V1.
- **Data capability:** reads header declarations from code; no source data.

### RL-01-12: S3 remainder, workers gate and core advisory hook
- **Status (2026-10-30): workers part merged: workers #111 (1df482e). Core advisory hook still open.**
- Lanes workers and core, size S, no order between the two (single-repo, parallel).
- Both only invoke the io gate script (`tools/check_contract_catalogue.py`, merged in io #66); neither reimplements it, and the header check across declarations is RL-01-11's.
- Workers: a gate entry runs the io gate and fails when it fails.
- Core: an advisory hook runs the io gate script by path and is skipped silently when the io checkout is absent; no core dependency change (CAT M6).
- A seeded-drift demonstration (gate fails on a deliberate drift, passes after) is run in a scratch worktree and recorded as non-merged evidence in the PR body with commands, commit and output; the seeded change is never merged.
- **Contract:** io gate `tools/check_contract_catalogue.py` (merged in io #66).
- **Data capability:** none; script checks over repo files.

### RL-01-13: S7, core pointer note
- **Status (2026-10-30): Merged: core #774 (f43434b).**
- Lane core, size S, no blockers.
- One short markdown pointer in core docs names the catalogue (io-contracts module and docs path) as the place clients find input/output contracts, stating core remains the authority.
- Markdown only; no code, contract or manifest change.
- **Contract:** none.
- **Data capability:** none.

### RL-01-14: Bars job spec lists the closed 13-id set
- **Status (2026-10-30): core part merged: core #773 (e646fe7). Workers part still open (needs the workers re-pin).**
- Lanes core part first, then workers; size S + S; blocker: the core export must merge and the workers pin must move with it (core PR, then workers re-pin per ADOPTION cross-repo rule). Workers part is Blocked until then; the core part is Ready now.
- Core part: `BAR_IDS` (private in `_implemented.py`) is exported publicly from `equity_feature_contracts/__init__.py`; no value change, no frozen-contract change.
- Workers part: a native `bars` job spec lists all 13 `BAR_IDS`, imported directly from core (allowed: ADR-1 forbids only upward edges), not retyped, in the workers builders and docs (RELEASE-0-RULINGS section 3).
- A 12-id spec is refused with INVALID_COMMAND; shown by a refusal recipe that fails on the old behaviour (DEFINITIONS, Done item 3).
- The 39 per-job cap is unchanged.
- **Contract:** core `BAR_IDS` (public after the core part); workers `docs/PRERELEASE_BUMP_DV1.md`.
- **Data capability:** reads synthetic bars through the existing source adapter; server-side worker; degrades to a typed refusal on a missing id.

### RL-01-20: EF1 proposed core contracts: catalogue pages once frozen
- Lane io, size S. **Blocked** on the core freeze of the EF1 proposed contracts. Origin: PO ruling on io #71 (partial EF1 accepted).
- Once core freezes them, generate the missing EF1 catalogue pages beside the existing families; INDEX.md and the unparsed-keys list updated; drift gate green.
- **Contract:** frozen core EF1 contracts (authority). **Data capability:** reads core contract JSON; writes generated pages; no source data.

### RL-01-21: check_input/check_output hardening
- Lane io, size S, no blockers. Origin: reviewer and Tester findings on io #70 (verdicts kept in the coordinator's local work/ folder, not in the repo).
- Handle a non-hashable `feature_id`, a bare-string `reasons` argument and `roles=None` (currently a TypeError) with typed, structural results; document the behaviour in the check docs.
- Structural checks only; no new unit tests (refusal recipe or regression fixture per defect class).
- **Contract:** CAT sections 2 and 4. **Data capability:** none beyond the packaged catalogue.

### RL-01-22: Header cross-check v2
- Lane io, size M, no blockers. Origin: io #73 result.
- Extend the header cross-check to feature ids, dtype, unit and schema_version, and resolve the 34 NOT_DECLARED pairs (declare or record each as accepted); every mismatch listed, none dropped.
- Zero golden or hash churn, confirmed before the edit; if churn appears, stop and report to the PO.
- **Contract:** catalogue output pages; IO_V1. **Data capability:** reads header declarations from code; no source data.
