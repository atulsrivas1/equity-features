## Current owner-approved R15 allocation

[Owner decision](https://github.com/atulsrivas1/equity-features/issues/437#issuecomment-6252649998) explicitly accepts PR438's three documentation stories and authorizes separate local review throughout R15. E22#439/milestone18 select exactly governance437, stories432/434/433 and aggregate439. The four children remain subject to actual separate review, checks, publication and acceptance. Existing local permission is automated review, not human review or hosted activation. No repeated per-story review permission is needed within this grant. No completed review or implementation is inferred.

The proposed-scope/pending-review language below is retained as the initial preparation checkpoint and superseded by this decision. Governance delivery still precedes story432 readiness; original criteria/source identities/exclusions remain binding. Exact final head review is renewed after allocation changes. All five milestone members are open at this freeze; closure remains future evidence.

## Original preparation checkpoint retained

# R15 proposal: documentation usability

Status: proposed scope, planning underway under [GOV027#437](https://github.com/atulsrivas1/equity-features/issues/437). The owner requests a handoff and execution; the three-story allocation below requires a scope decision before release assignment. No R15 implementation, Ready admission, completed review or release is claimed.

## Accepted starting point

R14's selected library scope is accepted at main `071e06dcc44665573cc09526016970e04be4f8ea`: [aggregate acceptance](https://github.com/atulsrivas1/equity-features/issues/428#issuecomment-6247703232), E21#428 Done and milestone16 closed, zero open/seven closed members. The source-frozen R14 receipt intentionally retains its then-pending own acceptance; the later numbered acceptance and fresh readback establish closure. Do not replay R14 qualification or rewrite historical receipts to produce a recursive receipt.

## Proposed priority and allocation

| Pull order | Existing issue | Deliverable | Provisional points | Dependency |
| --- | --- | --- | --- | --- |
| 0 | GOV027#437 | Scope, handoff, review and published planning acceptance | 2 | Owner scope decision and supported separate review |
| 1 | [#432](https://github.com/atulsrivas1/equity-features/issues/432) | Four direct links to current API sections, original body preserved | 1 | Accepted handoff and story readiness |
| 2 | [#434](https://github.com/atulsrivas1/equity-features/issues/434) | Current experimental result-contract reading context, original body preserved | 1 | #432 accepted; links to existing API and quickstart |
| 3 | [#433](https://github.com/atulsrivas1/equity-features/issues/433) | Existing continuous-quote example interval table and explanation | 2 | #434 accepted; existing independent mathematical specification |

These are the existing issues, not new EQ IDs or replacements. Their original acceptance and bounded edit targets remain binding. Points are provisional complexity, not days. No deadline is invented. One story at a time. The documentation corrections outrank optional new capabilities because they address concrete reading ambiguity using already supported behavior; the quote walkthrough follows navigation and version context. No new numerical feature is proposed.

## Exact implementation contracts

For #432, edit only `docs/api/PUBLIC_API.md` for the user-facing change: prepend a current-reading block linking `#current-experimental-public-api`, `#imports-and-ownership`, `#invalid-calls-versus-unavailable-calculations` and `#installed-typing-qualification`. End with the exact issue marker and preserve the historical body. Its normalized GitLF SHA256 remains `8d8a7848d39181a7e5c429a46a2ed432968da1a3be3ea7dca12af2de78ba9d7c` at the accepted R14 base.

For #434, edit only `docs/contracts/RESULTS.md` for the user-facing change. Explain the original EQ013 implementation checkpoint versus current experimental contracts/features0.0.4a4 and link `../api/PUBLIC_API.md` and `../QUICKSTART.md`. Preserve structural rules and all prior text after the fixed issue marker. Historical normalized GitLF SHA256 remains `0987cc3de8cab56511a9faead4def157d33c33614c8e3d287a9b02a494c015ec` at the accepted R14 base. No stable registry or production claim.

For #433, edit only `docs/api/CONTINUOUS_QUOTES.md` for the user-facing change. Explain the existing synthetic UTCns100-112 example: [100,103) normal3ns; [103,107) locked4ns; [107,109) crossed2ns; [109,112) invalid3ns; unknown0, expired0, total12ns, valid7ns, valid-only mean spread6/7 and mean bps60000/707. Explain update/cutoff before original expiry, full invalid null-bid replacement, and exclusion of crossed/invalid time from the valid denominator. Link unchanged example and formula derivation. Preserve original formulas and example source. No algorithm change or performance claim.

Each story also updates its own plan/evidence, relevant changelog/knowledge/handoff and linked issue/PR. These continuity edits do not widen the user-facing edit target. If a source-preservation check fails at a later base, stop and explicitly rebase the issue specification; never weaken its expected hash to hide drift.

## Validation and acceptance

1. Read original issue acceptance and actual source/formulas before Ready. Publish concrete per-story plan, base, allowed files and validation; verify identity and live Project before writes.
2. Use the issue's bounded preservation/link check for #432/#434. Inspect actual headings and resolved relative destinations; do not call generic documentation CI a comprehensive link validator.
3. Run existing stdlib `python tools/verify_quote_examples.py` for #433 and independently review every table cell/prose against literal fixtures/formulas. The verifier does not read the new prose or execute the production example. No new production execution is needed for this documentation scope.
4. Establish separate exact final-head semantic/source review, disposition findings, required current-head CI and applicable existing workflow/artifact gates. Hosted unchanged package checks do not become new human usability, mathematical or production evidence. Do not rerun accepted R14 demos/studies or create irrelevant benchmarks.
5. Follow Backlog -> Ready -> In progress -> Code review -> Test -> Ready to release -> Released -> Done. Default-branch publication plus fresh independent verification, evidence-linked acceptance and issue/Project readback are required; merge alone is insufficient.
6. Aggregate acceptance needs all three selected stories plus governance accepted, current final published documentation/source checks and independent final readback of the exact milestone membership. Close only selected scope. No source-frozen receipt should pretend its own future closure is already known.

## Decision and review gates

The proposal selects no milestone or epic yet. On explicit scope acceptance, create an R15 milestone and one aggregate epic, assign only the three existing starter issues and governance, preserve their old bodies/history, and record the exact member set. Keep all three Backlog/unassigned until each actual readiness gate. Do not manufacture new capabilities merely to fill a release.

`CODE_REVIEW.md`'s local alternative currently ends at R14. Before planning merge or R15 story Ready, require supported completed separate review or an explicit owner alternative-review decision covering this concrete handoff, all three stories, necessary companion documentation and final delivery. Permission is not review completion. Record actual identity, exact source/head, checks, findings/disposition and limitations, renewing coverage after relevant changes. Author self-review and CI alone do not qualify.

## Excluded and preserved

Research M2/M3/M5 and combined C1#311 remain open under their separate owners and original requirements. The R14 human pilot stays deferred; no outreach, posting, participant recruitment or uptake claim. EQ118#224/EQ119#225 remain unselected Future Backlog under the accepted negative R13 DEFER; no evaluation rerun or witness selection. Provider EQ069/070/072/074 stay deferred, requiring rights/access/verifiedzero-cost compatible proof. SEC001#374 retains the separate unqualified whole-platform enforcement scope. R7 is accepted under its revised scope; its old automation remains paused and old parked drafts are preserved history, not current instructions.

No account/profile administration, private/paid data, provider acquisition, public service, stable registry, trading, new chat, recurring work or scope relaxation. No package source/API/math/version/dependency/workflow change. A documentation release cannot establish scientific usefulness or complete combined C1. After this bounded release, stop and report remaining choices honestly.
