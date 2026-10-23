# EQ164 wave 3: proposed story drafts (W3-D)

Status: these are drafts. None has been created, no number is assigned (shown as TBD), and creation is pending the coordinator and owner approval. Nothing here is accepted: no mathematics, API, source, rights, consumer equivalence or Ready status, and full EQ164 #504 stays open. No tracker issue was created or edited. For information only, the highest existing EQ number observed is EQ-237 (#626). Opaque ids only; no source formulas, thresholds, names or code. Machine-readable copy: [PROPOSED_STORIES.json](PROPOSED_STORIES.json). Sources: [wave 2 decisions](EQ164_WAVE2_DECISIONS.md), [A](EQ164_SELECTED_A.md), [B](EQ164_SELECTED_B.md), [C](EQ164_SELECTED_C.md), [X1](EQ164_WAVE2_X1.md), [X2](EQ164_WAVE2_X2.md), [X3](EQ164_WAVE2_X3.md), [X4](EQ164_WAVE2_X4.md); layer map in [NUMBERED_LAYER_OWNERS](../NUMBERED_LAYER_OWNERS.md).

Epic and milestone choices follow the native homes recorded in the layer map (EF1 #569 / milestone 34; EF2 #467 / 23; EF3 #468 / 24; EF8 #517 / 28); dedicated release epics are not claimed. Native epics are coordinator-accepted, pending owner review. Shared decision SD-1 (coordinator-decided, pending owner review): the duplicate-identity rule is frozen once and cited identically by the cohort-normalization (W3D-2) and observed-population (W3D-5) stories; neither may define its own.

| Draft | Layer | Release | Parent / milestone | Rows served |
| --- | --- | --- | --- | --- |
| W3D-1 Retracement-level producer | library | EF2 | #467 / 23 | 9 consumers |
| W3D-2 Cohort-normalization producer | library | EF8 | #517 / 28 | 10 consumers |
| W3D-3 Anchor discovery primitive | library | EF8 | #517 / 28 | 4 fields |
| W3D-4 Mean companion | library | EF3 | #468 / 24 | 13 consumers, 1 field |
| W3D-5 Observed-population companion | library | EF3 | #468 / 24 | 4 consumers |
| W3D-6 Neutral provider-admission contract | I/O | EF1 (extended by later EF I/O tasks) | #569 / 34 | 10 commands |
| W3D-7 Candidate-artifact representation contract | library | EF8 | #517 / 28 | 1 command |

## W3D-1: [EQ-TBD] Implement caller-parameterized retracement-level producer

- Parent epic: #467 (R19 native home of the EF2 tasks)
- Milestone: 23 (R19 - Trend, momentum and money-flow features)
- Release: EF2
- Layer: library
- Origin: Wave 1 decision A1; wave 2 X3 proposed story N1; wave 2 decisions, proposed story 1.

### Outcome

A narrow pure producer of a retracement level from a prior-window extrema pair and a caller-supplied ratio, so the nine retracement consumer rows have a numbered level owner. #511 (channels and squeeze) is not stretched to cover it.

### In scope

- Pure arithmetic over a prior-window high/low pair and a caller ratio, with an explicit side convention.
- Extrema taken from existing prior-window extrema (delivered history extrema or #473/#483), not re-derived.
- Explicit unavailable, degenerate-range, non-finite and ratio-out-of-domain behavior; versioned config identity.

### Out of scope

- Prior-window extrema computation (existing owners).
- Proximity tolerance, crossing and score policy (#518).
- Range-average operand and close-variant selection.
- Any default ratio value.

### Owning and consuming stories

- Owns: the level operand (OP-LEVEL) for S0276-S0284.
- Consumed by: #518 proximity, crossing-up and crossing-down predicates; #511 only if the owner later folds it in.

### Dependencies

- #473 (closed baseline, reuse unproved)
- #483 (EQ-149, open)
- #518 (EQ-176, policy consumer)
- #609/#610 (EF2 I/O and worker layers)
- #486 (EF2 release acceptance)

### Opaque rows served

- consumers (9): S0276 S0277 S0278 S0279 S0280 S0281 S0282 S0283 S0284

### Mandatory acceptance for this story

- [ ] Freeze original formulas, units, timing and known-at availability, initialization, coverage, edge cases and supported capabilities before Ready; no private source formulas or thresholds copied without rights.
- [ ] Keep calculations pure; adapters own acquisition and workers own scheduling and persistence. Reuse existing qualified APIs; document no-change decisions.
- [ ] Independent synthetic or licensed expected fixtures, hand-specified separately from the implementation, with complete result, status, quality and evidence parity; explicit unsupported or missing inputs.
- [ ] Plan reuse of compatible inputs and intermediates, legal ordered state and bounded shared CPU, RAM, I/O and backend-thread budgets. Measure defined workloads against credible baselines before any speed claim; no invented SLA or fastest result.
- [ ] Update story, PR, formula, API, example, decision and release documents; complete required review, applicable tests, CI and installed artifacts, publication and actual readback before Done.

### Non-goals

- No source formula, threshold, default, name or code is copied; opaque ids only.
- No provider-specific rule is adopted; no provider, live, production or publication operation is authorized.
- Drafting, filing or merging this story accepts no mathematics, API, source, rights, consumer equivalence or Ready status; full EQ164 stays open.

### Coordinator decisions


### Open questions for the contract author

- Which close variant and side conventions does the level use; are both retracement directions one output or two?
- Is the ratio a free caller parameter or a fixed set; allowed domain and precision policy.
- Degenerate range (high equals low), inverted range, missing history: refuse, null or flag?
- Reuse #473/#483 extrema by exact profile proof, or take supplied extrema (reuse of closed #32 is unproved)?
- Add as a proposal-only entry to the 47-output manifest (decision A2) before or after filing?
- Does the prior-window length belong to this story's config or only to the extrema owner?

## W3D-2: [EQ-TBD] Implement current-cohort normalization and rank producer

- Parent epic: #517 (EF8 native epic)
- Milestone: 28 (R24 - Equity policies, lifecycle and complete worker integration)
- Release: EF8
- Layer: library
- Origin: Wave 1 decision C1; wave 2 X3 proposed story N2; X3-2 (closed #102 reuse not accepted until proved).

### Outcome

A separately numbered pure producer of rank position within a current observed cohort (whole cohort or supplied group), including the population admission step, so catalogue policy #518 no longer hides the arithmetic.

### In scope

- Current-cohort rank position over finite values, whole cohort and per supplied group, with a group-size gate.
- Population admission step over caller-supplied eligibility facts and floors.
- Identity, duplicate, tie and non-finite handling stated once.
- Separate profile identities per cohort family.

### Out of scope

- Tail cut, catalogue selection and thresholds (#518).
- Prior-only history summaries (#489).
- Producing the cohort values themselves (existing owners).
- Reuse of closed #102 unless proved.

### Owning and consuming stories

- Owns: OP-ELIG-RANK and OP-COHORT-RANK.
- Consumed by: #518 cohort-rank scanners; #621/#622 layers.

### Dependencies

- #518 (EQ-176)
- #621/#622 (EF8 I/O and worker)
- #523 (EF8 acceptance)
- #506/#507/#508/#513 for cohort value, change, group and excess-return operands
- #102 (closed; reuse unproved)

### Opaque rows served

- consumers (10): S0090 S0091 S0092 S0093 S0094 S0095 S0096 S0097 S0098 S0099

### Mandatory acceptance for this story

- [ ] Freeze original formulas, units, timing and known-at availability, initialization, coverage, edge cases and supported capabilities before Ready; no private source formulas or thresholds copied without rights.
- [ ] Keep calculations pure; adapters own acquisition and workers own scheduling and persistence. Reuse existing qualified APIs; document no-change decisions.
- [ ] Independent synthetic or licensed expected fixtures, hand-specified separately from the implementation, with complete result, status, quality and evidence parity; explicit unsupported or missing inputs.
- [ ] Plan reuse of compatible inputs and intermediates, legal ordered state and bounded shared CPU, RAM, I/O and backend-thread budgets. Measure defined workloads against credible baselines before any speed claim; no invented SLA or fastest result.
- [ ] Update story, PR, formula, API, example, decision and release documents; complete required review, applicable tests, CI and installed artifacts, publication and actual readback before Done.

### Non-goals

- No source formula, threshold, default, name or code is copied; opaque ids only.
- No provider-specific rule is adopted; no provider, live, production or publication operation is authorized.
- Drafting, filing or merging this story accepts no mathematics, API, source, rights, consumer equivalence or Ready status; full EQ164 stays open.

### Coordinator decisions

- Coordinator-decided, pending owner review: independent producer; reuse of closed #102 is not accepted until proved.
- Shared decision SD-1 (coordinator-decided, pending owner review): the duplicate-identity rule is frozen once and cited identically by the cohort-normalization (W3D-2) and observed-population (W3D-5) stories; neither may define its own.

### Open questions for the contract author

- Rank convention (base, direction), tie rule and non-finite handling.
- Who owns the availability marker of the excess-return operand that admits a member?
- Is the group-size gate here or in #518 policy?
- Population admission here or in #518 (the X3 alternative)?

## W3D-3: [EQ-TBD] Implement pure anchor discovery primitive

- Parent epic: #517 (EF8 native epic)
- Milestone: 28 (R24 - Equity policies, lifecycle and complete worker integration)
- Release: EF8
- Layer: library
- Origin: Wave 1 decision C2 (slice C finding 2); #520 consumes it and it must not gate earlier primitives.

### Outcome

A separately numbered pure primitive that discovers an anchor from causal history, extending the EF1 anchor family from EF8 (#507 consumes a supplied anchor only), so EF8 #520 lifecycle consumes it rather than owning hidden numerical discovery.

### In scope

- Pure discovery of an anchor point from causal ordered history with explicit not-found, tie and reset semantics.
- Output as a supplied-anchor-compatible fact consumable by existing anchored calculations.
- Discovery kept separate from state projection (latched and episode state stay in #520).

### Out of scope

- Anchored arithmetic already on main.
- Lifecycle, episode and tenure state (#520, #521).
- Thresholds and policy (#518).
- Provider acquisition.

### Owning and consuming stories

- Owns: the discovery operand for F0343-F0346.
- Consumed by: #520 ordered transitions; #507 anchored arithmetic may consume discovered anchors.

### Dependencies

- #507 (EQ-167): delivered EF1 anchor outputs are consumed, not changed
- #505/#506 operand producers named by the contract
- #520 (EQ-178, consumer)
- #621/#622 (EF8 I/O and worker layers)
- #523 (EF8 acceptance)

### Opaque rows served

- fields (4): F0343 F0344 F0345 F0346

### Mandatory acceptance for this story

- [ ] Freeze original formulas, units, timing and known-at availability, initialization, coverage, edge cases and supported capabilities before Ready; no private source formulas or thresholds copied without rights.
- [ ] Keep calculations pure; adapters own acquisition and workers own scheduling and persistence. Reuse existing qualified APIs; document no-change decisions.
- [ ] Independent synthetic or licensed expected fixtures, hand-specified separately from the implementation, with complete result, status, quality and evidence parity; explicit unsupported or missing inputs.
- [ ] Plan reuse of compatible inputs and intermediates, legal ordered state and bounded shared CPU, RAM, I/O and backend-thread budgets. Measure defined workloads against credible baselines before any speed claim; no invented SLA or fastest result.
- [ ] Update story, PR, formula, API, example, decision and release documents; complete required review, applicable tests, CI and installed artifacts, publication and actual readback before Done.

### Non-goals

- No source formula, threshold, default, name or code is copied; opaque ids only.
- No provider-specific rule is adopted; no provider, live, production or publication operation is authorized.
- Drafting, filing or merging this story accepts no mathematics, API, source, rights, consumer equivalence or Ready status; full EQ164 stays open.

### Coordinator decisions

- Coordinator-decided, pending owner review: placed in EF8 (epic #517, milestone 28), depending on the delivered EF1 anchor outputs (#507) with #520 as consumer; it must not gate EF1 acceptance.

### Open questions for the contract author

- Is each of F0343-F0346 discovery or state projection; how many are truly numerical?
- Causal prefix, tie and reset rules; not-found semantics.
- Does any earlier primitive need it (an EF8 owner would then gate it, which is forbidden)?
- Relation to the existing supplied-anchor proof in the first anchored slice.

## W3D-4: [EQ-TBD] Implement mean-ratio volume pace companion

- Parent epic: #468 (R20 native home of EF3)
- Milestone: 24 (R20 - Relative statistics, realized volatility and robust anomalies)
- Release: EF3
- Layer: library
- Origin: Wave 1 decision B3; wave 2 X4 class MISSING_PRODUCER_STORY (NS-MEAN-COMPANION).

### Outcome

A separately versioned pure mean-ratio companion to the median/MAD normalization of #490, so #490 keeps its stated median scope and the mean-ratio consumers have a numbered owner with their own prerequisites.

### In scope

- Mean-ratio normalization against a baseline (target-inclusion per contract) with explicit warm-up, minimum history, zero or negative denominator and unavailable behavior.
- Version and config identity separate from the median profile.
- Explicit baseline operand edge (#489), not an implied one.

### Out of scope

- Median/MAD normalization (#490).
- Thresholds and catalogue policy (#518).
- Replacing median profiles with mean ratios.

### Owning and consuming stories

- Owns: the mean-ratio operand for 13 scanners and F0452 (moved out of #490).
- Consumed by: #518 catalogue; #611/#612 layers.

### Dependencies

- #489 (EQ-155)
- #490 (EQ-156, sibling)
- #470 (baseline prerequisite named by #490)
- #611/#612
- #491 (EF3 acceptance)
- #518 (EQ-176)

### Opaque rows served

- consumers (13): S0341 S0342 S0343 S0344 S0345 S0346 S0347 S0348 S0349 S0350 S0351 S0352 S0356
- fields (1): F0452

### Mandatory acceptance for this story

- [ ] Freeze original formulas, units, timing and known-at availability, initialization, coverage, edge cases and supported capabilities before Ready; no private source formulas or thresholds copied without rights.
- [ ] Keep calculations pure; adapters own acquisition and workers own scheduling and persistence. Reuse existing qualified APIs; document no-change decisions.
- [ ] Independent synthetic or licensed expected fixtures, hand-specified separately from the implementation, with complete result, status, quality and evidence parity; explicit unsupported or missing inputs.
- [ ] Plan reuse of compatible inputs and intermediates, legal ordered state and bounded shared CPU, RAM, I/O and backend-thread budgets. Measure defined workloads against credible baselines before any speed claim; no invented SLA or fastest result.
- [ ] Update story, PR, formula, API, example, decision and release documents; complete required review, applicable tests, CI and installed artifacts, publication and actual readback before Done.

### Non-goals

- No source formula, threshold, default, name or code is copied; opaque ids only.
- No provider-specific rule is adopted; no provider, live, production or publication operation is authorized.
- Drafting, filing or merging this story accepts no mathematics, API, source, rights, consumer equivalence or Ready status; full EQ164 stays open.

### Coordinator decisions

- Coordinator-decided, pending owner review: F0452 and the 13 consumers move out of #490 into this story. Required scope note for #490: it stays median/MAD only and no longer houses the mean companion or F0452, and #490 text naming the mean companion as a companion, and its planning fallback with the #36 reference, is retired by this story; the #490 body needs that note when this story is filed.

### Open questions for the contract author

- Which baseline profile (#489 only, or closed baseline reuse) and is reuse proved?
- Prior-only versus including-current baseline; zero-baseline behavior.
- Common versus per-key operand across the 13 consumers.

## W3D-5: [EQ-TBD] Implement observed-population session breadth companion

- Parent epic: #468 (R20 native home of EF3)
- Milestone: 24 (R20 - Relative statistics, realized volatility and robust anomalies)
- Release: EF3
- Layer: library
- Origin: Wave 2 decision X3-1 (narrow companion keeping #598 scope clean); X3 answer B5; wave 1 B5.

### Outcome

A narrow companion to #598 with a separately versioned observed-population profile over supplied records, distinct from the declared-universe profile so denominators are never mixed.

### In scope

- Seven draft outputs under distinct observed-population names: qualifying member count; advancing member count; advance fraction; the same three per supplied group with group size; a per-cohort and per-group coverage record (provisional).
- Per-member eligibility from caller floors with explicit unknown-input handling.
- Duplicate-identity handling frozen once.

### Out of scope

- Declared-universe profile and its sixteen slots (#598).
- Regime classification, cut-offs, score scaling and member projection (#518).
- Any private population minimum, ratio or threshold.

### Owning and consuming stories

- Owns: OP-OBS-BREADTH and OP-ELIG-BREADTH.
- Consumed by: #518 observed-population regime scanners.

### Dependencies

- #598 (EQ-220, companion parent)
- #506/#507/#508 per-member change, eligibility and group operands
- #613 for the volume operand
- #611/#612
- #491
- #518

### Opaque rows served

- consumers (4): S0003 S0004 S0005 S0006

### Mandatory acceptance for this story

- [ ] Freeze original formulas, units, timing and known-at availability, initialization, coverage, edge cases and supported capabilities before Ready; no private source formulas or thresholds copied without rights.
- [ ] Keep calculations pure; adapters own acquisition and workers own scheduling and persistence. Reuse existing qualified APIs; document no-change decisions.
- [ ] Independent synthetic or licensed expected fixtures, hand-specified separately from the implementation, with complete result, status, quality and evidence parity; explicit unsupported or missing inputs.
- [ ] Plan reuse of compatible inputs and intermediates, legal ordered state and bounded shared CPU, RAM, I/O and backend-thread budgets. Measure defined workloads against credible baselines before any speed claim; no invented SLA or fastest result.
- [ ] Update story, PR, formula, API, example, decision and release documents; complete required review, applicable tests, CI and installed artifacts, publication and actual readback before Done.

### Non-goals

- No source formula, threshold, default, name or code is copied; opaque ids only.
- No provider-specific rule is adopted; no provider, live, production or publication operation is authorized.
- Drafting, filing or merging this story accepts no mathematics, API, source, rights, consumer equivalence or Ready status; full EQ164 stays open.

### Coordinator decisions

- Coordinator-decided, pending owner review: companion story (not an amendment of #598).
- Shared decision SD-1 (coordinator-decided, pending owner review): the duplicate-identity rule is frozen once and cited identically by the cohort-normalization (W3D-2) and observed-population (W3D-5) stories; neither may define its own.

### Open questions for the contract author

- Final output list and names (seven drafted in X3, provisional).
- May a declared-universe profile later reuse the same arithmetic?
- Observed denominator, per-sector scope, empty or missing population result.
- Adaptive-consumer edges (S0336, S0337, S0357) are out of this story; they read adaptive outputs.

## W3D-6: [EQ-TBD] Define neutral provider-admission contract for supplied facts

- Parent epic: #569 (EF1 native epic; I/O owner #570)
- Milestone: 34 (EF1 - Sessions, levels and reference features)
- Release: EF1 (extended by later EF I/O tasks)
- Layer: I/O
- Origin: Wave 2 decision X1-1; X1 finding F5 and suggestion S5.

### Outcome

A reviewed neutral contract expressing admission of provider-sourced records as caller-supplied facts (validity, normalization status, identity and clock), so shipped provider adapters stay optional and pluggable and no provider rule enters the core.

### In scope

- Neutral admission fact schema: what the caller asserts about a record's validity, normalization and known-at time.
- Opaque accept and reject reasons without provider vocabulary.
- Mapping obligations for #570 and later EF I/O tasks (trade-print admission rows stay #570 mapping).
- Conformance fixtures any adapter can run.

### Out of scope

- Any provider-specific rule or threshold.
- Acquisition, credentials, scheduling, storage.
- Pure mathematics (library stories).
- Notification builders and product-private wire schemas.

### Owning and consuming stories

- Owns: the neutral admission contract (documentation and I/O mapping).
- Consumed by: #570, #609, #611, #613, #615, #617, #619, #621 I/O layers and optional shipped adapters.

### Dependencies

- #570 (EQ-212)
- #569
- later EF I/O tasks listed above

### Opaque rows served

- commands (10): C0040 C0043 C0044 C0056 C0057 C0060 C0089 C0101 C0102 C0197
- Note: C0053 is a cross-reference only and is not served by this story.

### Mandatory acceptance for this story

- [ ] Contract text frozen and independently reviewed before Ready: fields, units, timing and known-at semantics, versioning, refusal and unsupported cases; no private source rules or thresholds copied without rights.
- [ ] Keep the contract source-independent: adapters own acquisition and mapping, workers own scheduling and persistence, libraries own mathematics; document no-change decisions for existing qualified APIs.
- [ ] Independent conformance cases, authored separately from any implementation, covering accepted, refused, missing and contradictory inputs; no provider rules or private thresholds.
- [ ] State compatibility and versioning obligations for existing and optional consumers; no speed or SLA claim.
- [ ] Update story, PR, contract, example, decision and release documents; complete required review, applicable checks and actual readback before Done.

### Non-goals

- No source formula, threshold, default, name or code is copied; opaque ids only.
- No provider-specific rule is adopted; no provider, live, production or publication operation is authorized.
- Drafting, filing or merging this story accepts no mathematics, API, source, rights, consumer equivalence or Ready status; full EQ164 stays open.

### Coordinator decisions

- Coordinator-decided, pending owner review: ONE neutral contract story (I/O). The trade-print admission rows (C0148, C0109, C0161-C0163) are NOT in it; they stay I/O mapping under #570 (decision X2-1).

### Open questions for the contract author

- Contract only, or also a reference conformance suite?
- Which facts are caller-asserted versus adapter-private?
- C0053 also cites this question; is it a cross-reference only?
- Versioning and compatibility across optional adapters.

## W3D-7: [EQ-TBD] Define candidate-artifact representation contract

- Parent epic: #517 (EF8 native epic)
- Milestone: 28 (R24 - Equity policies, lifecycle and complete worker integration)
- Release: EF8
- Layer: library
- Origin: Wave 2 decision X2-5; X2 question Q5 (C0209).

### Outcome

A representation contract, owned within #521 scope with #520 as consumer, for the equity candidate artifact schema that an option-domain command currently rewrites, so schema, versioning and consumer links are defined in EF8.

### In scope

- Artifact field set, identity, versioning and score and membership history representation.
- Which columns are equity-owned and which are downstream joins.
- Compatibility and refusal rules for added enrichment columns.

### Out of scope

- The option-domain enrichment logic.
- Product-private wire schema (#522 checks consistency only).
- Numerical producers.

### Owning and consuming stories

- Owns: the representation obligation (via #521).
- Consumed by: #520; #522 consistency check; #523.

### Dependencies

- #521 (EQ-179)
- #520 (EQ-178)
- #519 (EQ-177)
- #522 (EQ-180)
- #621/#622

### Opaque rows served

- commands (1): C0209

### Mandatory acceptance for this story

- [ ] Contract text frozen and independently reviewed before Ready: fields, units, timing and known-at semantics, versioning, refusal and unsupported cases; no private source rules or thresholds copied without rights.
- [ ] Keep the contract source-independent: adapters own acquisition and mapping, workers own scheduling and persistence, libraries own mathematics; document no-change decisions for existing qualified APIs.
- [ ] Independent conformance cases, authored separately from any implementation, covering accepted, refused, missing and contradictory inputs; no provider rules or private thresholds.
- [ ] State compatibility and versioning obligations for existing and optional consumers; no speed or SLA claim.
- [ ] Update story, PR, contract, example, decision and release documents; complete required review, applicable checks and actual readback before Done.

### Non-goals

- No source formula, threshold, default, name or code is copied; opaque ids only.
- No provider-specific rule is adopted; no provider, live, production or publication operation is authorized.
- Drafting, filing or merging this story accepts no mathematics, API, source, rights, consumer equivalence or Ready status; full EQ164 stays open.

### Coordinator decisions

- Coordinator-decided, pending owner review: its OWN story, linked to #521 as representation owner and #520 as consumer.

### Open questions for the contract author

- Is option enrichment a product-owned downstream join outside the equity artifact?
- Schema versioning and forward-compatibility policy.
- Interaction with option release gates (EQ153, EQ158).
