# EQ164 wave 2, story X1: command exclusions labelled operational ingest / admin / validation

October 22, 2026. Adjudicated findings for the 101 command rows of [the route coverage plan](../../plans/equity-audit-route-coverage.json) whose planned disposition is `proposed_operational_ingest_admin_validation_exclusion` (opaque ids C0001 to C0276, all with no retained equity component and `no_retained_component_requires_individual_exclusion_review: true`). Companion data: [EQ164_WAVE2_X1.json](EQ164_WAVE2_X1.json), one record per row. This is a findings document. It records no scope, numerical, source, consumer or release decision. Full EQ164 stays open, no tracker issue was created or edited, no plan row flag was changed, and every "retained" statement below is a proposal for the owner. Context: [AUDIT_ROUTE_PUBLICATION.md](../AUDIT_ROUTE_PUBLICATION.md) exit item 3, [OWNERSHIP_RECONCILIATION.md](../OWNERSHIP_RECONCILIATION.md), [wave 1 decisions](EQ164_WAVE1_DECISIONS.md), [numbered owners](../NUMBERED_LAYER_OWNERS.md), and the [nine-command review](../../plans/equity-nine-command-source-review.json) used as the model (standalone feature excluded, represented-field, delegated-child and source-universe responsibilities retained).

## Method

Each row was judged on its own evidence, not on its label. For every command: the entry source was read (owner-local source tree at the recorded revision; the public evidence digest and file and call-witness counts in the plan are quoted per row), the delegated helper functions reachable from its direct call witnesses were read at function level, subprocess children were resolved to their own opaque rows, the owner-private route-proposal record was compared with the public plan, and a static scan counted arithmetic, subprocess use and equity references in the command and in the helpers it reaches. A verdict of CONFIRM_EXCLUSION requires that the command defines, derives, normalizes or selects no equity value, fact or policy. Carrying, validating, hashing, copying, activating, persisting or administering equity-typed data is not an embedded fact; where the represented fields already have an I/O owner, that is recorded as a retained obligation (not a component), as in the nine-command review. Public digests were quoted from the plan, not recomputed.

## Summary

| Verdict | Rows | Confidence |
| --- | --- | --- |
| CONFIRM_EXCLUSION | 80 | 42 high, 38 medium |
| REJECT_EXCLUSION | 5 | 3 high, 2 medium |
| NEEDS_OWNER_DECISION | 16 | 16 medium |
| NEEDS_MORE_EVIDENCE | 0 | |

CONFIRM_EXCLUSION by reason class (80 rows): other domain option computation or ops 14; artifact validation shell 10; pipeline orchestration tooling 6; format or diagnostic migration 5; provider archive transfer or census 5; reference or baseline activation loader 5; capacity evidence audit 4; lake maintenance 4; ai analyst product knowledge 3; parity audit exact compare 3; ai analyst product worker 2; external boundary archive audit 2; inventory audit 2; observability measurement 2; publication to keyed store 2; serving proxy 2; typed row persistence transport 2; admin cost estimate 1; ai analyst product restore 1; ai analyst product trigger routing 1; control job plumbing 1; notification delivery planning 1; raw record transcoding 1; stream or object store transport 1.

## Findings

- F1. 80 of 101 label-based exclusions hold under row-level evidence. None of the 80 embeds an equity calculation or defines a supplied equity fact. The bar is not "has no equity data": 13 of the 80 move equity-typed values and keep a represented-field obligation toward an existing I/O owner (C0007, C0028, C0052, C0054, C0059, C0067, C0068, C0075, C0078, C0087, C0095, C0100, C0155).
- F2. 5 exclusions are rejected because the command embeds an equity component (table below).
- F3. The owner-private proposal records differ from the public plan. Three rows (C0002, C0003, C0008) carry a private supplied-operand route to #520 (candidate lifecycle identity passing through analyst tooling) that the public plan lacks; I treat it as a consumer join, not a component, and flag it. Twelve rows (C0007, C0028, C0059, C0067, C0075, C0078, C0087, C0095, C0099, C0100, C0155, C0257) have private representation or per-field routes that the public command rows do not link; 302 distinct field ids are listed in the JSON `field_representation_obligations` for C0067, C0075, C0078, C0087, C0095 and C0257. Recommend adding a `retained_obligations` link on command rows.
- F4. 21 of the 101 rows are option-domain tooling, or option knowledge for the analyst product, filed under the ingest/admin/validation bucket (pattern P6). The equity-side exclusion holds for all 21, but the label is wrong and they belong in the other-domain bucket. The four capacity-gate rows (C0226, C0227, C0228, C0232) compare equity latency receipts against operational limits; those are measurements, not equity values.
- F5. Provider-row admission rules are embedded in commands and have no owner: bar-validity exclusion with governed quality thresholds and next-day spill handling, a tick normalization policy (degenerate prints and crossed quotes excluded, unavailable quote sides null), corporate-action split-ratio handling, and a normalized short-interest contract. The short-interest fact family has no row among the 721 inventoried fields. This is the largest owner decision (Q-X1-1).
- F6. Delegated and subprocess closure was checked for every row. Closure is not a clean tree: C0178 (24 planned children), C0181 (60 release-bundle children), C0180 (2) and C0015 (2) run other commands. C0015's two children are rows with retained components (C0009, C0013). C0178 and C0181 children include 8 and 29 rows of this set respectively, whose verdicts are in the JSON, so the orchestrators' CONFIRM_EXCLUSION does not discharge the children, and some children are themselves NEEDS_OWNER_DECISION.
- F7. Five CONFIRM rows delegate to policy functions that remain obligations without being components of the shell: classification point-in-time and symbol-identity rules (C0030, C0155 toward #508), event availability and capture guards (C0061, C0154, C0155 toward #514), and bar-admission thresholds (C0053 toward Q-X1-1).

## Patterns

- P1. Stream, lake and object-store transport and maintenance (persistence, compaction, deletion, mirroring, trimming): payloads preserved by identity; no value change. Hold, high or medium confidence.
- P2. Reference, baseline and seed loaders and typed-row persisters: copy or re-encode values already produced elsewhere; they differ in whether the represented fields are routed. C0067 narrows stored precision when it compacts baseline values, which belongs in the I/O representation contract (#611).
- P3. Provider acquisition and normalization (Q-X1-1): ten NEEDS_OWNER_DECISION rows. Pure transfer and census rows with no normalization are CONFIRM.
- P4. Duplicated watchlist ranking map: the same field-to-ranking mapping with completeness gating is repeated in two replay commands (C0099, C0257); a live-path copy is plausible but was not inspected in this story. It is one policy for #518, not independent facts.
- P5. Batch and historical orchestration tooling: no value is computed, but the planned children are partly retained, partly in this set. Recorded as tooling, not as a retained orchestration component; owner may prefer the stricter reading.
- P6. Option-domain and analyst-product rows in this bucket (21): reclassify, no equity component found. The analyst products are consumers of equity outputs (candidate, strategy score, breadth) and need consumer joins.
- P7. Validation and parity shells (exact comparison, no tolerance, non-finite rejection) feed release qualification as evidence tooling; they are not producers.

## Rejected exclusions

| Row | Embedded component | Kind | Numbered owner | Notes |
| --- | --- | --- | --- | --- |
| C0034 | Confirmation evaluation worker: derives reference prices from a momentum percentage and a sampled rolling price window, derives option premium differences, gates readiness, publishes observations | orchestration; pure producer/policy; operand derivation | EQ-178 #520, worker #622 | The operand derivations have no named producer: story S1. |
| C0099 | Mapping of stored fields to watchlist rankings with gating and sign inversion | policy | EQ-176 #518, representation EQ-212 #570 | Same map as C0257. |
| C0257 | Replay of raw events through the equity context producer plus the same ranking map | policy; orchestration; source access | EQ-176 #518, worker #622, representation #570 | Producer fields (168 rows) keep their own routes. |
| C0187 | Cross-session pass re-deriving strategy classifier and scores, with fail-closed gap rule | pure producer/policy; orchestration | EQ-177 #519, worker #622 | Option-volatility ranking inside it is other-domain. |
| C0029 | Classification facts with an embedded sector-to-reference-instrument mapping, sector-fund flag and effective-from carry rule | supplied fact; policy | EQ-168 #508 (mapping consumed by EQ-172 #513) | Provider fetch part falls under Q-X1-1. |

## Rows needing an owner decision (16)

Each question is exact. The adjudicator's leaning is advisory.

- Q-X1-1, rows C0040, C0043, C0044, C0056, C0057, C0060, C0089, C0101, C0102, C0197 (C0053 also references it). Are provider acquisition and provider-row normalization or admission commands retained source-access components that need numbered stories now, or optional shipped provider adapters outside the retained inventory until rights approval, with only a neutral admission contract retained under EF1 #570 and EF6 #617? Leaning: the second reading, plus a separate owner for the short-interest family, which has no routed field.
- Q-X1-2, row C0058. Is the declared-universe membership rule (class-derived union constituent-derived members, unknown symbols dropped) a retained supplied-fact or policy component, as universe admission was for C0215? If yes, which numbered owner, or is a new story needed? Leaning: caller-supplied input for the core library, with the rule documented as an adapter profile.
- Q-X1-3, row C0184. May its independent reference formulas (trade-derived totals, technical indicators, option flow, quote reduction, model checks, coverage reconciliation) be recorded as qualification-evidence assets under the release owners (exit item 6), or must independent evidence be authored fresh? Leaning: asset, after an independence review of its provenance.
- Q-X1-4, rows C0031, C0062, C0064. Do the strategy-specific notification envelope builders (causal occurrence selection, entry-shape and persistence and context reason classification, parity replay, shadow export) belong to retained policy under #519/#520, or are they consumer-side products with consumer joins only? Leaning: consumer-side delivery, but check the reason classification against #519 profiles for duplicated policy.
- Q-X1-5, row C0204. Is the equity candidate and the direction it stamps, consumed by the option selection worker, a retained supplied equity operand under #520 (precedent C0206 to #506) or only a consumer join? Leaning: consumer join.

## Recommended next stories (proposed, none created)

- S1. Confirmation-input operand derivation: add to the #520 contract or create a narrow EF8 gap story for the derived reference prices and option-premium-difference operands (C0034).
- S2. Docs amendment to #518: single owner for the field-to-watchlist-ranking map and its gating, replacing duplicate command-local copies (C0099, C0257).
- S3. #519 contract clause for cross-session finalization and gap-failure semantics (C0187).
- S4. Short-interest fact family: route or exclude explicitly (C0101, C0102), depending on Q-X1-1.
- S5. Neutral provider-row admission profile (bar validity and thresholds, tick normalization, corporate-action ratio handling) under #570/#617, if Q-X1-1 takes the second reading.
- S6. Qualification-evidence register entry for the independent reference calculations (C0184), if Q-X1-3 takes the first reading.
- S7. Docs-only bookkeeping PR: reclassify the 21 option and analyst rows to the other-domain bucket, add `retained_obligations` links from command rows to field rows, and record the private-versus-public discrepancy (F3).

## What could not be verified

- Public evidence digests were quoted from the plan and not recomputed; the digest formula is not public.
- External capture-authority module: read only for equity content (none found); its authority and recovery semantics were not adjudicated (C0115, C0116, medium confidence).
- The proxy response hooks (C0019) and the gateway (C0193) were read for equity computation, not for full request semantics.
- Static scans are heuristics; function-level reading backed every verdict, but a deeper dynamic-route review (route tables, environment configuration) was not done. Source-rights, numerical and consumer gates remain as in the plan.

## Per-row verdicts

| Row | Verdict | Class | Conf. | Question |
| --- | --- | --- | --- | --- |
| C0001 | CONFIRM_EXCLUSION | control job plumbing | high |  |
| C0002 | CONFIRM_EXCLUSION | ai analyst product restore | medium |  |
| C0003 | CONFIRM_EXCLUSION | ai analyst product trigger routing | medium |  |
| C0007 | CONFIRM_EXCLUSION | typed row persistence transport | medium |  |
| C0008 | CONFIRM_EXCLUSION | ai analyst product worker | medium |  |
| C0011 | CONFIRM_EXCLUSION | parity audit exact compare | medium |  |
| C0014 | CONFIRM_EXCLUSION | pipeline orchestration tooling | high |  |
| C0015 | CONFIRM_EXCLUSION | pipeline orchestration tooling | medium |  |
| C0016 | CONFIRM_EXCLUSION | format or diagnostic migration | high |  |
| C0018 | CONFIRM_EXCLUSION | format or diagnostic migration | high |  |
| C0019 | CONFIRM_EXCLUSION | serving proxy | medium |  |
| C0020 | CONFIRM_EXCLUSION | inventory audit | high |  |
| C0023 | CONFIRM_EXCLUSION | notification delivery planning | medium |  |
| C0028 | CONFIRM_EXCLUSION | format or diagnostic migration | medium |  |
| C0029 | REJECT_EXCLUSION | supplied fact and policy classification | medium |  |
| C0030 | CONFIRM_EXCLUSION | artifact validation shell | medium |  |
| C0031 | NEEDS_OWNER_DECISION | strategy specific notification envelope | medium | Q-X1-4 |
| C0034 | REJECT_EXCLUSION | embedded equity orchestration and operand derivation | high |  |
| C0038 | CONFIRM_EXCLUSION | artifact validation shell | medium |  |
| C0039 | CONFIRM_EXCLUSION | artifact validation shell | high |  |
| C0040 | NEEDS_OWNER_DECISION | provider row normalization policy and archive curation | medium | Q-X1-1 |
| C0042 | CONFIRM_EXCLUSION | provider archive transfer or census | high |  |
| C0043 | NEEDS_OWNER_DECISION | provider row normalization policy and archive curation | medium | Q-X1-1 |
| C0044 | NEEDS_OWNER_DECISION | provider row normalization policy and archive curation | medium | Q-X1-1 |
| C0045 | CONFIRM_EXCLUSION | admin cost estimate | high |  |
| C0046 | CONFIRM_EXCLUSION | provider archive transfer or census | high |  |
| C0048 | CONFIRM_EXCLUSION | provider archive transfer or census | high |  |
| C0052 | CONFIRM_EXCLUSION | publication to keyed store | medium |  |
| C0053 | CONFIRM_EXCLUSION | artifact validation shell | medium | Q-X1-1 |
| C0054 | CONFIRM_EXCLUSION | publication to keyed store | medium |  |
| C0056 | NEEDS_OWNER_DECISION | provider row normalization policy and archive curation | medium | Q-X1-1 |
| C0057 | NEEDS_OWNER_DECISION | provider row normalization policy and archive curation | medium | Q-X1-1 |
| C0058 | NEEDS_OWNER_DECISION | declared universe membership rule | medium | Q-X1-2 |
| C0059 | CONFIRM_EXCLUSION | format or diagnostic migration | medium |  |
| C0060 | NEEDS_OWNER_DECISION | provider row normalization policy and archive curation | medium | Q-X1-1 |
| C0061 | CONFIRM_EXCLUSION | artifact validation shell | medium |  |
| C0062 | NEEDS_OWNER_DECISION | strategy specific notification envelope | medium | Q-X1-4 |
| C0064 | NEEDS_OWNER_DECISION | strategy specific notification envelope | medium | Q-X1-4 |
| C0067 | CONFIRM_EXCLUSION | reference or baseline activation loader | medium |  |
| C0068 | CONFIRM_EXCLUSION | raw record transcoding | medium |  |
| C0075 | CONFIRM_EXCLUSION | reference or baseline activation loader | medium |  |
| C0078 | CONFIRM_EXCLUSION | reference or baseline activation loader | medium |  |
| C0079 | CONFIRM_EXCLUSION | observability measurement | high |  |
| C0080 | CONFIRM_EXCLUSION | inventory audit | high |  |
| C0087 | CONFIRM_EXCLUSION | reference or baseline activation loader | medium |  |
| C0089 | NEEDS_OWNER_DECISION | provider row normalization policy and archive curation | medium | Q-X1-1 |
| C0095 | CONFIRM_EXCLUSION | reference or baseline activation loader | medium |  |
| C0099 | REJECT_EXCLUSION | embedded equity policy watchlist score mapping | high |  |
| C0100 | CONFIRM_EXCLUSION | typed row persistence transport | medium |  |
| C0101 | NEEDS_OWNER_DECISION | provider row normalization policy and archive curation | medium | Q-X1-1 |
| C0102 | NEEDS_OWNER_DECISION | provider row normalization policy and archive curation | medium | Q-X1-1 |
| C0115 | CONFIRM_EXCLUSION | external boundary archive audit | medium |  |
| C0116 | CONFIRM_EXCLUSION | external boundary archive audit | medium |  |
| C0147 | CONFIRM_EXCLUSION | provider archive transfer or census | high |  |
| C0154 | CONFIRM_EXCLUSION | artifact validation shell | medium |  |
| C0155 | CONFIRM_EXCLUSION | format or diagnostic migration | medium |  |
| C0178 | CONFIRM_EXCLUSION | pipeline orchestration tooling | medium |  |
| C0179 | CONFIRM_EXCLUSION | pipeline orchestration tooling | high |  |
| C0180 | CONFIRM_EXCLUSION | artifact validation shell | medium |  |
| C0181 | CONFIRM_EXCLUSION | pipeline orchestration tooling | medium |  |
| C0183 | CONFIRM_EXCLUSION | pipeline orchestration tooling | high |  |
| C0184 | NEEDS_OWNER_DECISION | embedded independent reference calculations | medium | Q-X1-3 |
| C0185 | CONFIRM_EXCLUSION | parity audit exact compare | medium |  |
| C0187 | REJECT_EXCLUSION | embedded equity policy and orchestration cross session pass | medium |  |
| C0190 | CONFIRM_EXCLUSION | lake maintenance | medium |  |
| C0191 | CONFIRM_EXCLUSION | lake maintenance | high |  |
| C0192 | CONFIRM_EXCLUSION | lake maintenance | high |  |
| C0193 | CONFIRM_EXCLUSION | serving proxy | medium |  |
| C0194 | CONFIRM_EXCLUSION | ai analyst product worker | medium |  |
| C0197 | NEEDS_OWNER_DECISION | provider row normalization policy and archive curation | medium | Q-X1-1 |
| C0198 | CONFIRM_EXCLUSION | other domain option computation or ops | high |  |
| C0200 | CONFIRM_EXCLUSION | other domain option computation or ops | high |  |
| C0201 | CONFIRM_EXCLUSION | other domain option computation or ops | high |  |
| C0202 | CONFIRM_EXCLUSION | other domain option computation or ops | high |  |
| C0204 | NEEDS_OWNER_DECISION | equity candidate driven option selection | medium | Q-X1-5 |
| C0207 | CONFIRM_EXCLUSION | provider archive transfer or census | high |  |
| C0208 | CONFIRM_EXCLUSION | artifact validation shell | high |  |
| C0218 | CONFIRM_EXCLUSION | other domain option computation or ops | high |  |
| C0221 | CONFIRM_EXCLUSION | parity audit exact compare | high |  |
| C0222 | CONFIRM_EXCLUSION | other domain option computation or ops | medium |  |
| C0224 | CONFIRM_EXCLUSION | other domain option computation or ops | high |  |
| C0225 | CONFIRM_EXCLUSION | other domain option computation or ops | high |  |
| C0226 | CONFIRM_EXCLUSION | capacity evidence audit | high |  |
| C0227 | CONFIRM_EXCLUSION | capacity evidence audit | high |  |
| C0228 | CONFIRM_EXCLUSION | capacity evidence audit | high |  |
| C0229 | CONFIRM_EXCLUSION | other domain option computation or ops | high |  |
| C0230 | CONFIRM_EXCLUSION | other domain option computation or ops | high |  |
| C0232 | CONFIRM_EXCLUSION | capacity evidence audit | high |  |
| C0238 | CONFIRM_EXCLUSION | other domain option computation or ops | medium |  |
| C0241 | CONFIRM_EXCLUSION | other domain option computation or ops | high |  |
| C0245 | CONFIRM_EXCLUSION | other domain option computation or ops | high |  |
| C0246 | CONFIRM_EXCLUSION | artifact validation shell | high |  |
| C0250 | CONFIRM_EXCLUSION | other domain option computation or ops | medium |  |
| C0251 | CONFIRM_EXCLUSION | artifact validation shell | high |  |
| C0252 | CONFIRM_EXCLUSION | observability measurement | high |  |
| C0257 | REJECT_EXCLUSION | embedded equity policy and orchestration replay | high |  |
| C0258 | CONFIRM_EXCLUSION | stream or object store transport | medium |  |
| C0266 | CONFIRM_EXCLUSION | lake maintenance | high |  |
| C0274 | CONFIRM_EXCLUSION | ai analyst product knowledge | high |  |
| C0275 | CONFIRM_EXCLUSION | ai analyst product knowledge | high |  |
| C0276 | CONFIRM_EXCLUSION | ai analyst product knowledge | high |  |
