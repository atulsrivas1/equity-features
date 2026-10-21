# R25 preparation and exact continuation

Owner selected R25 after confirming dedicated repositories, equity-to-option dependency direction and independent versioning. [GOV037 #581](https://github.com/atulsrivas1/equity-features/issues/581) owns this preparation; [E33 #526](https://github.com/atulsrivas1/equity-features/issues/526) and EQ182-187/EQ214 retain implementation scope. R17 accepted; EQ146/R18 remains Backlog. This source-only preparation does not admit option implementation or bypass reviewed contracts.

## Deliverables now prepared

- Three dedicated public repository baselines, with Apache-2.0, source boundaries, exact alpha version policy and continuity. Fresh independent baseline reviewer /root/r25_bootstrap_review found one P3 trailing LICENSE blank line; corrected before initial push and rechecked at exact heads. Initial pushes establish default branches only, with no numerical package or CI/runtime claim.
- [Option canonical/model/layer draft](https://github.com/atulsrivas1/option-features/tree/codex/r25-contracts/docs/r25), including explicit European BSM candidate, signed/absolute delta, price/IV/Greek limits, reference/quote/chain semantics, proposed native records, 22 declarative conformance cases and compatibility blockers. These cases have not executed or established numerical accuracy.
- [I/O handoff](https://github.com/atulsrivas1/option-feature-io/blob/codex/r25-contracts/docs/R25_HANDOFF.md) and [worker handoff](https://github.com/atulsrivas1/option-feature-workers/blob/codex/r25-contracts/docs/R25_HANDOFF.md). Existing a4 equity quantities/results and a14 worker admission are incompatible with native option units/underlying identities; an explicit new interface is required.

## Current gate and exact next steps

1. Retain all seven R25 implementation stories Backlog and preserve active EF1/R18 owners and reserved study windows. Governance preparation can be In progress without pretending its implementation prerequisites passed.
2. Obtain fresh independent contract and source review; resolve named model/error/precision/IV/chain-score and native codec/executor decisions, then freeze contracts, independent expected fixtures and artifact references. Candidate model support never implies coverage of unsupported American/adjusted-deliverable requirements.
3. Verify EQ141/EQ146 acceptance and each story's real prerequisite Done state before Ready. The option source graph does not make all equity indicators prerequisites, but the owner's explicit release gate is unchanged.
4. Only then use fresh minimal-context library/I-O/worker implementation authors with exact writable paths and contract hashes. Coordinator review precedes push; fresh independent PR review and CI precede merge. Integrated direct/worker/stored parity, supported Windows/Linux artifacts, exact versions/inputs and actual local demo precede R25 acceptance.

Reference sources remain core b1f5445/c701, I/O18d86761 and workers231349a, with core/contractsa4, I/O SDK/contractsa2, worker a14, intraday a3. They are reference cohorts, not a tested option install lock. No active EF1 candidate version is silently selected. Adapter/sink artifacts require their own qualification; no database path, dataset rights, option schema or output destination has been admitted.
