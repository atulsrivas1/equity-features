# EQ164 wave 2, story X2: other-domain command exclusions

October 22, 2026. Adjudicated findings only. Nothing here approves an exclusion, changes a contract, edits the tracker or creates a story. Full EQ164 stays open. Per-row records are in [EQ164_WAVE2_X2.json](EQ164_WAVE2_X2.json). Opaque ids only (C####, F####, S####, W##); numbered owners follow [NUMBERED_LAYER_OWNERS.md](../NUMBERED_LAYER_OWNERS.md).

## Scope and method

Audit exit item 3 in [AUDIT_ROUTE_PUBLICATION.md](../AUDIT_ROUTE_PUBLICATION.md) requires each exclusion to be adjudicated individually, because a product label or a repeated rationale is not enough. This pass covers:

- (a) the 101 command rows whose planned disposition in [equity-audit-route-coverage.json](../../plans/equity-audit-route-coverage.json) is `proposed_other_domain_exclusion`;
- (b) the six standalone-feature exclusion rows (C0139, C0153, C0156, C0215, C0247, C0267) from [equity-nine-command-source-review.json](../../plans/equity-nine-command-source-review.json). Only their kept obligations were re-checked.

Every one of the 101 rows carried the same flags in the plan (no retained component, individual review required, interface/subprocess closure not approved). Those flags are unchanged by this pass.

Evidence used for each row (private, read-only, not reproduced here):

1. the owned command source, read in full;
2. the source of the packages it calls directly;
3. an import-closure scan for equity-domain packages;
4. a scan of the command for subprocess launch, interface dispatch and stream keys;
5. a static call-graph from the command to the producers of equity-shaped facts. It matches methods by name, so it over-approximates reach and does not prove a runtime path;
6. a reverse-import scan: which equity-side workers and libraries import the packages the row uses.

The public evidence digest for each row is in the JSON. The 101 rows fall into four product-family clusters, K1 (46 rows), K2 (21), K3 (19) and K4 (15). Clusters appear in the JSON only to show the shape of the patterns. They are not a basis for any verdict.

## Summary counts

| Verdict | Other-domain rows (101) | Standalone rows (6) |
| --- | --- | --- |
| CONFIRM_EXCLUSION | 82 | 5 |
| REJECT_EXCLUSION (component retained) | 8 | 0 |
| NEEDS_OWNER_DECISION | 11 | 1 |
| NEEDS_MORE_EVIDENCE | 0 | 0 |

Reason classes for the 82 confirmed rows (the exclusion stands for the command, subject to the cross-cutting notes below):

| Class | Meaning | Rows |
| --- | --- | --- |
| RC1 | Operational shell of another product (API, admin, migration, delivery, repair, capacity, retention) with no equity fact | 20 |
| RC2 | Other-product calculation or transport worker. Any equity-looking value is only a supplied operand and no equity result is produced | 40 |
| RC3 | Verification, audit or import shell that re-executes components retained elsewhere and adds no new obligation (C0110, C0114, C0143) | 3 |
| RC4 | Other-product registration of supplied facts into its own store, no equity output | 6 |
| RC5 | Wrapper of a shared kernel that equity-side workers consume as supplied facts. The wrapper is excluded; the consumer link is noted below | 13 |

Confidence: 72 rows are high and 29 are medium. Medium applies to large reach sets, interface dispatch, or rows that touch a retained component only as an operand or for verification. Every row with a verdict other than CONFIRM_EXCLUSION is either high or medium as stated in the JSON.

## What "other domain" was hiding

Most rows are clean. The label hid real equity-shaped content in these places:

- **P1. A pure equity producer embedded in a product evidence path (8 rows rejected).**
  - Daily realized volatility from supplied adjusted daily closes is reached by C0280, C0281, C0284, C0290 and C0291.
  - An observed-path underlying return with favourable and adverse excursions from an event anchor is run by C0140 and C0132. C0135 replays it and verifies its archived price binding.
  - These match EQ-154 #488 and EQ-174 #515, which already own the producer kinds. The commands are shells around them. The shell can stay excluded, but the "no retained component" flag is wrong.
- **P2. Product-private adapters of equity trade prints into underlying-price observations (Q1).** One live adapter, one archive publisher and three historical or coordinator paths (C0148, C0109, C0161, C0162, C0163), plus C0291 through its normalisation step. The rules (action eligibility, validity, identity and clock policy) are source-access and representation logic with no equity result. They overlap what the EF1 I/O and regular-price stories must define for trade eligibility.
- **P3. A fixed-size stock universe selection (Q2, C0151)** from supplied activity and classification facts. It is the same universe-admission family as the retained C0215 obligation.
- **P4. The equity-side dated-event schema and validator reused by non-equity commands (Q3, C0118, C0279).** The event-free-interval test over a supplied schedule is reached by the five rows in P1. C0123 only attaches the context and depends on the same answer.
- **P5. A first-to-last window return of product-carried underlying price samples (Q4, C0122, C0249)** feeding a confluence indicator.
- **P6. An equity candidate artifact rewritten by an option-domain command (Q5, C0209).** This is a schema and consumer link on an equity artifact.
- **P7. Option-domain kernels consumed by equity-side workers (16 rows carry an `equity_consumer_link`).** The reverse-import scan found strategy-context, confirmation, end-of-day candidate-context and intraday workers importing the kernels these commands wrap. The commands themselves are excluded. The kernels' outputs must appear in the consumer operand lists as supplied facts (see the 245 consumer operand gaps) and must not be assumed produced by the equity layers.

Checks that came back clean: no row launches a subprocess. Interface dispatch appears in five rows (C0110, C0129, C0132, C0133, C0135), and only C0132 and C0135 are rejected. No row writes equity-side stream or table names that the scans could find. The static call-graph cannot prove runtime reachability, so medium confidence is used where it is the only evidence.

## Rejected rows and component owners

| Rows | Retained component | Kind | Numbered owner |
| --- | --- | --- | --- |
| C0280, C0281, C0284, C0290, C0291 | Daily realized volatility from supplied adjusted daily closes | pure producer | EQ-154 #488 (EF3); I/O #611; worker #612 |
| same | Adjusted daily closes with adjustment basis and corporate-action reference | supplied fact | EF3 I/O #611 with EF1 reference/action gates #508 |
| same | Event-free interval test over a supplied dated-event schedule | policy | EQ-173 #514 (EF6), or NEEDS_NEW_STORY pending Q3 |
| C0140, C0132, C0135 | Observed-path underlying return and favourable/adverse excursion over fixed horizons | pure producer | EQ-174 #515 (EF7); I/O #619; worker #620 |
| same | Session-close-capped horizon targets | supplied fact | EF1 clocks #505/#506; calendar predecessor C0051 still open |
| same | Underlying samples admitted from trade prints | source access | pending Q1 |

Open sub-question on the first row: the product variant has its own adjustment-basis handling, calendar alignment and annualisation. The #488 contract must either name it as a profile or declare it a distinct product-private profile. Until then the match to #488 is by producer kind, not by profile. C0135 is also an orchestration of the outcome component and depends on Q1. The second block mirrors #515's published scope, so no new story is needed unless the owner decides the anchor-based form is out of scope there.

## Rows needing an owner decision

| Id | Rows | Exact question |
| --- | --- | --- |
| Q1 | C0148, C0109, C0161, C0162, C0163 (plus C0291, with dependants C0164, C0289, C0280, C0281, C0284, C0290, C0135, C0140, C0132) | Is the product-private admission of equity trade prints into underlying-price observations (action eligibility, validity, identity and clock policy) a retained source-access/representation obligation owned by the EF1 I/O story (#570) or the regular-price story (#506), or an excluded product-private adapter? |
| Q2 | C0151 (and the C0215 open item) | Is the product-defined selection of a fixed-size stock universe from supplied activity and classification facts a retained universe-admission obligation (same treatment as C0215; candidate owners #598 or #508), or an excluded product policy? |
| Q3 | C0118, C0279 (dependants C0123 and the five P1 rows) | Is the dated-event-source schema/validator reused from the equity side, together with the event-free-interval test over a supplied schedule, a retained supplied-fact obligation (candidate owners EQ-173 #514 and EF6 I/O #617) or product-private? |
| Q4 | C0122, C0249 | Is a first-to-last window return computed from product-carried underlying price samples and used for a confluence indicator a retained raw-return profile (candidate owners #513 or #507) or a product-private composite excluded with its product? |
| Q5 | C0209 | The command rewrites option-derived columns into the equity candidate artifact. Which numbered equity owner (#520 lifecycle, #521 history, or a gap story) owns that artifact schema and consumer contract, and is the enrichment a product-owned downstream join? |
| Q6 | C0139 | Which numbered owner holds the obligation that the product wire schema stays consistent with the outputs of retained components (observed outcomes, event context): EQ-180 #522, or is the schema product-private? |

## The six standalone-feature rows

Each kept obligation was checked for a numbered owner or an explicit open item:

| Id | Kept obligation | Tie status | Verdict and finding |
| --- | --- | --- | --- |
| C0139 | schema/consumer links | UNTIED | NEEDS_OWNER_DECISION (Q6). The generator covers the outcome and event types retained by the findings above. No owner or open-item flag exists. |
| C0153 | dynamic child graph | open item (plan flag) | CONFIRM_EXCLUSION. It launches configured child binaries. The child set lives in deployment configuration that is not in the source, so the graph cannot be closed statically. The flag is the open item. No numbered owner holds it, so #522/#523 should carry it until the configuration is supplied. |
| C0156 | measurement only | none remains | CONFIRM_EXCLUSION. It is a latency client, reads no feature value and nothing retained needs an owner. |
| C0215 | universe admission | open item (plan flag) | CONFIRM_EXCLUSION of the command. It computes nothing, but reuses the equity-definition membership. The flag is the open item and no numbered owner holds it. Same family as Q2. |
| C0247 | storage retention only | none remains | CONFIRM_EXCLUSION. It touches product-scoped keys only and refuses to apply without persistence markers. |
| C0267 | filesystem provenance only | none remains | CONFIRM_EXCLUSION. It reads sizes and column-file metadata, not feature values. |

## Recommended next stories

None of these exist. All need owner approval before any issue is created.

1. **Operand and profile task for #488 and #515** (existing owners, row-level operand list). Add the product variant of daily realized volatility and the anchor-based outcome form as named profiles, or declare them distinct. This closes P1.
2. **Trade-print admission contract** (EF1 I/O #570 amendment or a gap story), if Q1 is answered "retained".
3. **Universe-admission gap story** covering C0151 and C0215 together, if Q2 is answered "retained".
4. **Event-schedule supplied-fact contract** under #514/#617, if Q3 is answered "retained", including the event-free-interval test.
5. **Candidate artifact schema record** under #520/#521 for the option-derived columns (Q5).
6. **Consumer operand lists for option-domain kernels** that the equity strategy and confirmation workers consume (P7). This is a row-level task inside the consumer-operand work in wave 2.
7. **Dynamic child graph carrier** for C0153 under #522/#523.

## Limits

- The call-graph is static and over-approximate. It does not prove which paths run. No runtime, deployment-configuration or stream-content evidence was inspected.
- Nothing here checks numerical equivalence, source rights, consumer parity or any release gate. A CONFIRM_EXCLUSION means no retained component was found in the sources read, not that the exclusion is approved.
- Product family clusters K1 to K4 are descriptive only.
- The 245 consumer operand gaps, the C0051 and C0055 calendar and session-policy choices, and the full 1,399-identity review remain open.
