# EF1 multi-venue status reducer contract — proposal

Prepared for EQ165 #505 (EF1), supporting EQ212 #570 (I/O mapping) and EQ213 #571 (worker execution). This is contract preparation only. It is not accepted or Ready, and nothing in it was executed. Independent review remains required; the coordinator freeze applies on merge. Coordinator decisions are recorded in the final sections (D01 to D16, R01). The machine-readable companion is [MULTI_VENUE_STATUS_CONTRACT_PROPOSAL.json](MULTI_VENUE_STATUS_CONTRACT_PROPOSAL.json).

## Authority and sources

Governing text: the issue's reviewed output ownership clarification and the proposed opening-observable boundary, [OWNERSHIP_RECONCILIATION.md](OWNERSHIP_RECONCILIATION.md) (multi-venue paragraph), the 47-output manifest `docs/plans/equity-output-ownership.json` (group B12, seven outputs), the frozen `CONTRACT.json` (ef1-contract1, unchanged; recorded SHA256 in the JSON), [STATUS_INPUT_SLOTS.md](STATUS_INPUT_SLOTS.md), [IMPLEMENTATION_ADMISSION.md](IMPLEMENTATION_ADMISSION.md), the existing single-publisher status mathematics (`docs/features/EF1_STATUS.md`) and the structure of [REFERENCE_CONTRACT_PROPOSAL.md](REFERENCE_CONTRACT_PROPOSAL.md). Ownership is planned only; it accepts no formula or default, adds no provider, no private threshold and no default.

## Unchanged boundary

Existing `equity_features.ef1`, `CanonicalBatch`, `ConfigSpec`, `FeatureResult`, scalar `ValueType` values, `compute_ef1(batches, config, *, entity)` and `ef1_definitions(config)`. One homogeneous producer/config returns its complete sorted header set. No new DataKind, DTO, result codec, scheduler default or manifest limit. The ef1-context1 envelope (exact keys version/producer/calendar/selection, canonical ASCII JSON, at most 4096 codepoints and UTF8 bytes, depth at most 8), the aggregate bound of 4096 REFERENCE rows across all present slots, the 128-row result evidence limit and the 1 MiB task bound apply unchanged. The single-publisher `status:*` producer, its roles and its headers stay as they are: it remains the selected-publisher state/age path. This producer never reads, replaces or aliases it, and it carries no inferred opening-delay diagnostic (#518 owns the delay predicate, #520 ordered episode state, #506 first-trade/bar prices). Nothing here arbitrates between venues or infers a publisher's state from prices, prints or calendars.

## Producer and config identity

- Producer `multivenue_status`; config identity `ef1.multivenue_status`; algorithm `v1`; schema `1`; exactly one parameter `ef1_context_json`. Calendar is null (D04).
- Context selection exact keys: `clock_dimensions`, `epoch`, `max_age_ns`, `population_id`, `population_revision`, `state_policy`. `state_policy` exact keys `policy_id`, `policy_version`, `precedence`. `precedence` is a permutation of `[active, halted, closed]`, highest precedence first, supplied by the caller; no default order exists; `policy_id` is exactly `venue_precedence_v1` and `policy_version` exactly `1` (D03). `clock_dimensions` is a nonempty strictly ascending subset of `[quoting, ssr, trading]`. `max_age_ns` is null (no expiry) or a nonnegative int64 and applies to every dimension (D13). The policy id and version therefore enter the config digest. Context holds no acquired state, time, sequence, seed or knowledge value.
- Session, window, availability (market cutoff C, knowledge cutoff K, effective cutoff E, mode, reconstruction reason) and price unit/adjustment follow the frozen reconstruction rule; price unit and adjustment are null. The worker reconstructs the full ConfigSpec and compares the digest.
- Adding this producer enlarges the frozen 45-header ledger and needs an additive, EF1-only amendment and worker admission (D10). No frozen byte changes.

## Inputs and roles

Exactly five slots in fixed order, each an actual REFERENCE `CanonicalBatch` or `None`. `None` is missing delivery; a present zero-row batch with its own coverage is present-empty. Never infer a role from vocabulary or count. B(x) is canonical unpadded UTF8 base64url; D is `t`, `q` or `s` (trading, quoting, ssr). Every full reference_id is at most 128 codepoints and 512 UTF8 bytes. Rows arrive already ordered by effective_start_ns then reference_id; no layer sorts. Mapping version and grammars are new (D09).

1. `venue_population`: `vp1:B(population_id):B(population_revision):B(publisher_id)`, fact_kind `ef1.venue.population_member`, text `member`. Finite interval; a member is expected at C iff start <= C < end. known_at required at most K for expected members. This is the versioned expected population. Coverage must be complete with expected = observed = row count.
2. `venue_seed`: `vs1:D:B(epoch):B(publisher_id):seq19`, fact_kind `ef1.venue.seed`, text D. Names the original semantic sequence at which the (publisher, dimension) stream restarts. Finite interval; applicable iff start <= C < end; known_at at most K.
3. `venue_states`: `v1:D:B(epoch):B(publisher_id):seq19:B(event_id)`, fact_kind `ef1.venue.state.<dimension>`, text in the closed dimension vocabulary (trading active/halted/closed; quoting enabled/disabled; ssr on/off). seq19 is a 19-digit nonnegative int64 semantic sequence.
4. `venue_prefix`: `vc1:D:B(epoch):B(publisher_id):B(P):B(certificate_id)`, fact_kind `ef1.venue.prefix_complete`, text D. P is the actual `venue_states` input_id.
5. `venue_validity`: same grammar, fact_kind `ef1.venue.validity`.

Instrument/session binding is the actual target entity and namespace, as for existing status roles (D16). Epoch is one shared context value (D05). Fact semantics for slots 3-5 are the existing single-publisher status mathematics applied independently per (publisher, dimension) stream.

## Structural validation (before any semantics; typed refusal)

All rows of all present slots are validated even if irrelevant to C.

- Population: id parses and its population_id and population_revision equal the context, else INCONSISTENT_IDENTITY (this is the conflicting-revision rule); interval end > start else BOUNDS; a publisher repeated within the batch is DUPLICATE (D14).
- States, seeds, prefix, validity: epoch equals the context, else INCONSISTENT_IDENTITY (a reset is a new epoch; epochs never mix). Publisher must be a declared population member of any interval, else INCONSISTENT_IDENTITY (an unexpected publisher is never silently dropped; it is skipped only when the population slot is missing). Fact_kind/text/vocabulary closed, else INVALID_SCHEMA. Certificates and seeds need a finite interval with end > start, else BOUNDS; a state's optional end must exceed its start, else BOUNDS. Certificates bind P to the actual states input_id, else INCONSISTENT_IDENTITY.
- Per (publisher, dimension) stream: semantic sequence strictly increasing (equal DUPLICATE, smaller INVALID_ORDER) and effective time nondecreasing (INVALID_ORDER). Sequence gaps alone prove nothing.
- states, seed, prefix and validity batches must share one source_id and snapshot_id (the publisher-stream revision), else INCONSISTENT_IDENTITY. The population batch is a separate declaration and carries its revision in its ids.
- More than one applicable seed, prefix certificate or validity certificate for a (publisher, dimension) is DUPLICATE regardless of knowledge, text agreement or ordering; no stitching or arbitration.
- Slot count other than five is INVALID_SCHEMA; a precedence that is not a permutation of the closed trading vocabulary, or any malformed context, is INVALID_CONFIG (D15).

## Population and per-fact semantics

**Expected population** P = the applicable population members, in batch order, N = |P|. The denominator is never reduced by missing facts. Population-level outcomes, in precedence: slot missing -> `absent_population`; coverage incomplete or expected != observed or observed != row count -> `incomplete_population`; any applicable member with null known_at -> unknown_availability, with known_at > K -> future_knowledge (the population itself is not yet known); N = 0 -> `empty_population`. For any such outcome no fact is evaluated and every output is unavailable (table below).

**Fact for (p, d)**, with p in P, at cutoffs C and K, replicating the single-publisher rules per stream:

1. The applicable seed row selects semantic sequence s0. If none is applicable the initialization is absent: finding `absent_input`. The first delivered row is never inferred. The seed row's own known_at is checked: null -> unknown_availability, > K -> future_knowledge.
2. The seed's state row must exist with effective time < C, else absent_input. Transitions are the stream's rows from s0 with effective time t < C (events at C or later are excluded; irrelevant future-effective rows, even with large known_at, create no failure). Each transition needs known_at nonnull and <= K (null -> unknown_availability; > K -> future_knowledge) in both known_at and reconstruction modes; reconstruction never makes unknown or future knowledge eligible. Rows before s0 are not consulted for state or knowledge.
3. A states batch whose coverage is incomplete gives `incomplete_status_prefix` for every fact. A (p, d) with no prefix rows, or no validity rows, gives absent_input. The prefix certificate must satisfy start <= seed effective time and C <= end, else `incomplete_status_prefix`; its known_at is checked. A prefix batch or validity batch with incomplete coverage gives `incomplete_status_prefix`. The validity certificate must satisfy start <= C < end; its known_at is checked independently of everything else.
4. Only when no earlier finding exists for the fact (prefix and transitions prove the current event) is expiry evaluated: validity rows exist but none applicable, or the selected state's own end <= C -> `outside_effective_interval`.
5. The current event is the last transition strictly before C. Its state is the closed text; its original clock is its effective_start_ns t; age = C - t. If max_age_ns is not null and age > max_age_ns the fact is **stale**: its clock t remains proved, its state is withheld (finding `stale_state`).

A fact is **known** (state and clock proved), **stale** (clock proved, state withheld), or **unknown** (findings listed above). The scalar finding of a fact is the first of: absent_input, incomplete_status_prefix, unknown_availability, future_knowledge, outside_effective_interval, stale_state. Legacy reasons: absent_input->absent_input, incomplete_status_prefix->governed_gap, unknown_availability, future_knowledge unchanged, outside_effective_interval and stale_state->ineligible. Selected-publisher state/history is untouched by any of this.

## Mathematics of the seven outputs

Let T = trading facts, Q = quoting facts, R = ssr facts over P; "all known" means every one of N facts is known.

- `known_trading_count` (int64, publishers): if T is all known, the number with state `active`. Otherwise null.
- `known_nontrading_count` (int64, publishers): if T is all known, the number with state `halted` or `closed` (so the two counts sum to N). Otherwise null. The mapping is D02.
- `quoting_any` (bool): true if at least one known Q fact is `enabled`, even if others are unknown or stale (one positive determines an OR). Else false only if Q is all known (all `disabled`). Else null. An unknown publisher is never counted as a negative.
- `restriction_any` (bool): same over R with positive `on`.
- `aggregate_state` (string, state): the policy rank of a state is its index in `precedence` (0 is highest). Let best be the highest-ranked state among known T. If T is all known, the value is best. Otherwise, if best exists and its rank is 0, the value is best (nothing can outrank it; **dominance**). Otherwise null. Ties between different states do not exist because the policy is a strict total order; ties between publishers with the same state are the same value.
- `aggregate_reason` (string, reason), always available with quality 1/1: when `aggregate_state` is available it is `unanimous` (all known, one distinct state), `precedence_resolved` (all known, at least two distinct states) or `precedence_saturated` (dominance with unknown/stale others). When unavailable it is the first applicable item of the precedence `absent_population, incomplete_population, empty_population, absent_input, incomplete_status_prefix, unknown_availability, future_knowledge, outside_effective_interval, stale_state` over the population outcome or over the scalar findings of the non-known T facts (D11).
- `latest_event_ns` (int64, utc_ns): over the declared clock population {(p, d): p in P, d in clock_dimensions} (M = N x number of dimensions), eligible = known or stale facts. If all M are eligible the value is the maximum original t. Otherwise, if the maximum eligible t equals C - 1, the value is that maximum (no current event can be at or after C). Otherwise null. C and K are only used for eligibility; query time is never a value. See D08.

## Availability, coverage, quality

Per output, quality status and reasons:

- Value present: status `available`, reasons empty. expected = observed = N (or M) when all facts were required and known; expected = observed = 1 when the value was determined by a single dominating or positive witness (D06).
- Value null from fact findings: status `missing_input` if any legacy reason is in {absent_input, unknown_availability, future_knowledge, ineligible}, else `incomplete_coverage` (only governed_gap). Reasons are the lexically sorted union of legacy reasons over exactly the non-eligible facts that output requires. expected = N (or M); observed = number of eligible facts. This keeps known/unknown/stale and coverage visible even when the scalar is null.
- Empty population: `not_applicable`, reasons [empty_universe], expected = observed = 0, value null (D07).
- Population unavailable: absent_population -> missing_input [absent_input]; incomplete_population -> incomplete_coverage [governed_gap]; member known_at null/future -> missing_input [unknown_availability] and/or [future_knowledge]; expected null, observed 0.
- A positive observed flag never creates a negative for other publishers; unknown, future and stale facts never become eligible by mode or by reconstruction. Missing publishers never reduce N.

Evidence: bounded witnesses, `evidence_limit` 4, use `consumed`, event_ns = original effective_start_ns, original known_at and effective bounds, never C or query time: `aggregate_state` the first publisher in population order whose known T state equals the value; `quoting_any`/`restriction_any` (only when true) the first publisher with a known positive state; `latest_event_ns` the first (population order, then dimension lexical) fact whose t equals the value. Counts, false and unanimous bulk facts carry none; all inputs remain bound in full metadata (D12). Result inputs sort lexically by role; manifest order is the slot order.

## Units and timing

All clocks are UTC integer nanoseconds (int64, utc_ns). Counts are int64 in `publishers`. Intervals are half-open [start, end); events at C are excluded; age = C - t via checked int64 subtraction (overflow is typed OVERFLOW). Exact integer arithmetic only; there is no rounding, no float and no private threshold. Unit strings are D10.

## Layer responsibilities

- **Library (pure, EQ165):** `compute_ef1` with producer `multivenue_status`: structural validation, the reduction and quality above, and nothing else. No I/O, clocks, scheduling, persistence, provider calls, defaults or inference.
- **EQ212 I/O mapping:** maps supplied facts into the five slots preserving original publisher identity, epoch, revision, sequence and order, effective bounds and known_at; delivers `None` for a missing delivery and a zero-row batch for a covered empty one; never synthesizes a publisher, seed, certificate or population row; never selects a population or policy; carries the original coverage truthfully.
- **EQ213 worker:** declares the config (population id/revision, epoch, policy, clock_dimensions, max_age_ns), enforces the exact five-role manifest and context/digest reconstruction, invokes the pure producer once per homogeneous result, and writes the complete result unchanged. It performs no aggregation, no precedence, no counting.

## Explicit non-goals

No provider or venue acquisition; no inferred venue arbitration; no derivation of state from prices, volume, quotes or calendar phase; no new live provider; no private source thresholds or formulas; no default precedence order; no opening-delay or episode diagnostics (#518, #520); no first-trade/bar prices (#506); no change to single-publisher status; no lower-bound or partial counts (D01); no numerical, source or release acceptance; no version bump or package publication.

## Independent fixtures

The JSON holds 50 fixtures with full expanded rows, expected values, quality, evidence and 13 expected refusals. Expected results were typed by hand as literals; a throwaway stdlib-only evaluator of the mathematics above (importing nothing from the equity packages, library not used) agreed on every output, quality tuple and witness. Fixtures use policy_id `venue_precedence_v1` with synthetic precedence orders that are test data, not recommended orders. Default world: publishers A, B, C; entity SYN/X/S; epoch `e`; C = K = 20; every stream seeded at its first event with certificates covering [0,100).

| ID | Case | Expected |
| --- | --- | --- |
| MV01 | empty complete population (0/0): not a vacuous truth | state None / reason empty_population / trading None / latest None |
| MV02 | population batch missing (None slot) | state None / reason absent_population / trading None / latest None |
| MV03 | expected {A,B,C}; C has no rows: population is not shrunk | state None / reason absent_input / trading None / latest None |
| MV04 | partial population: C supplies trading only; negative quoting not fabricated, positive ssr stands | state halted / reason precedence_resolved / trading 2 / latest 5 |
| MV05 | all three known trading; distinct original clocks 5,7,9 | state active / reason unanimous / trading 3 / latest 9 |
| MV06 | mixed trading/non-trading A active B halted C closed, policy halted>active>closed | state halted / reason precedence_resolved / trading 1 / latest 5 |
| MV07 | quoting_any true from A; B,C quoting unknown (no streams): true stands, no complete-negative claim | state active / reason unanimous / trading 3 / latest 5 |
| MV08 | restriction_any true from B while C ssr transition is future-known (25>K=20) | state active / reason unanimous / trading 3 / latest 5 |
| MV09 | no positive restriction and C unknown (future): restriction_any null, not false | state active / reason unanimous / trading 3 / latest 5 |
| MV10 | population A,B,C declared, no state rows at all: zero known | state None / reason absent_input / trading None / latest None |
| MV11 | equal-time conflict in A resolved by semantic sequence (halted); B active; C closed | state halted / reason precedence_resolved / trading 1 / latest 5 |
| MV12 | A halted B active C closed under precedence ['halted', 'active', 'closed'] | state halted / reason precedence_resolved / trading 1 / latest 5 |
| MV13 | A halted B active C closed under precedence ['closed', 'active', 'halted'] | state closed / reason precedence_resolved / trading 1 / latest 5 |
| MV14 | A halted B active C closed under precedence ['active', 'halted', 'closed'] | state active / reason precedence_resolved / trading 1 / latest 5 |
| MV15 | top-ranked state (closed) observed, B,C unknown: aggregate determined by dominance | state closed / reason precedence_saturated / trading None / latest None |
| MV16 | observed halted is not top-ranked under closed>active>halted and B,C unknown: undetermined | state None / reason absent_input / trading None / latest None |
| MV17 | B transition known_at 25>K=20 (future); A halted dominates | state halted / reason precedence_saturated / trading None / latest None |
| MV18 | B transition known_at null: unknown availability | state None / reason unknown_availability / trading None / latest None |
| MV19 | reconstruction mode, K=20: future-known B stays ineligible | state None / reason future_knowledge / trading None / latest None |
| MV20 | max_age 10 at C=20: B age 15 stale; stale clock still a proved original clock | state None / reason stale_state / trading None / latest 12 |
| MV21 | B has a later transition at t=25>=C (known 99): irrelevant, not a knowledge failure | state active / reason unanimous / trading 3 / latest 5 |
| MV22 | B trading prefix certificate ends 19<C=20 | state None / reason incomplete_status_prefix / trading None / latest None |
| MV23 | B trading validity [0,20) at C=20 (half-open): outside effective interval | state None / reason outside_effective_interval / trading None / latest None |
| MV24 | status_states batch coverage incomplete: every fact governed_gap | state None / reason incomplete_status_prefix / trading None / latest None |
| MV25 | population batch declares expected 4 observed 3 | state None / reason incomplete_population / trading None / latest None |
| MV26 | member A known_at 25>K=20: population itself not yet known | state None / reason future_knowledge / trading None / latest None |
| MV27 | members D (starts 30>C) and E (ended 10<=C) are not expected at C; N stays 3 | state active / reason unanimous / trading 3 / latest 5 |
| MV28 | restore seed A=seq2: rows before the seed (incl. null known_at) are not consulted; current is seq3 | state active / reason unanimous / trading 3 / latest 9 |
| MV29 | replay of MV28 inputs with K=30 in reconstruction mode: identical outputs | state active / reason unanimous / trading 3 / latest 9 |
| MV30 | A trading has rows but no seed row: absent initialization, first row not inferred | state None / reason absent_input / trading None / latest None |
| MV31 | A seed names seq1 effective at t=20=C: events at C excluded so seed unusable | state None / reason absent_input / trading None / latest None |
| MV32 | reset: context epoch e2, all rows and seeds in e2; earlier epoch absent from the batch | state active / reason unanimous / trading 3 / latest 10 |
| MV33 | latest saturation: A current event at C-1=19 known; B,C unknown | state None / reason absent_input / trading None / latest 19 |
| MV34 | no saturation: A current event at 18<C-1; B,C unknown could be later | state None / reason absent_input / trading None / latest None |
| MV35 | clock_dimensions [trading,quoting]: max over 6 (publisher,dimension) clocks is 11 | state active / reason unanimous / trading 3 / latest 11 |
| MV36 | C=K=50 with validity to 100: latest stays the original clock 9, never the query time | state active / reason unanimous / trading 3 / latest 9 |
| MV37 | latest tie: B and C both at 9, witness is first in population order | state active / reason unanimous / trading 3 / latest 9 |
| RF01 | duplicate semantic sequence in A trading stream | refusal DUPLICATE |
| RF02 | publisher A declared twice in the population | refusal DUPLICATE |
| RF03 | population row carries revision 2 while context selects revision 1 | refusal INCONSISTENT_IDENTITY |
| RF04 | validity batch snapshot R2 conflicts with states snapshot R1 | refusal INCONSISTENT_IDENTITY |
| RF05 | state rows for publisher Z, not in the declared population | refusal INCONSISTENT_IDENTITY |
| RF06 | two applicable prefix certificates for (A,trading); knowledge never arbitrates | refusal DUPLICATE |
| RF07 | A state row under epoch e0 while context epoch is e | refusal INCONSISTENT_IDENTITY |
| RF08 | A semantic sequence decreases while time increases | refusal INVALID_ORDER |
| RF09 | A state interval end 5 <= start 5 | refusal BOUNDS |
| RF10 | policy precedence is not a permutation of the closed trading vocabulary | refusal INVALID_CONFIG |
| RF11 | four slots supplied instead of exactly five | refusal INVALID_SCHEMA |
| RF12 | population member interval end 0 <= start 0 | refusal BOUNDS |
| RF13 | A trading state text 'enabled' outside the closed trading vocabulary | refusal INVALID_SCHEMA |


## Coordinator decisions

Former questions D01 to D16 are decided (pending owner review); the references D01 to D16 above point here.

- **D01**: Accepted: counts are null unless every expected publisher is known. Partial information is carried by aggregate_state/aggregate_reason and by quality coverage (expected = N, observed = number of known publishers). Partial-count outputs may be added only by a later reviewed amendment.
- **D02**: Accepted: trading = active; non-trading = halted, closed; quoting_any positive = quoting enabled; restriction_any positive = ssr on.
- **D03**: Accepted: the policy is caller-supplied with no default order. policy_id comes from a closed reviewed vocabulary declared in this contract: exactly [venue_precedence_v1]; policy_version exactly [1]. A policy may map to a distinct aggregate label (for example mixed) only if that label is added to this closed vocabulary by amendment; v1 declares none, so aggregate_state is one of active, halted, closed.
- **D04**: Accepted: no calendar slot or calendar context (calendar null).
- **D05**: Accepted: one epoch shared by all publishers.
- **D06**: Accepted for v1: outputs decided by one witness report coverage 1/1. Observable elsewhere: the expected-population size N is the row count and coverage of the bound venue_population input in result metadata, and equals expected on every counts, aggregate_state and non-witness quality row; the unknown-publisher count is observable as expected minus observed on known_trading_count and known_nontrading_count (trading dimension) when they are unavailable. For quoting_any, restriction_any and latest_event_ns decided by one witness, and for aggregate_state decided by dominance, the unknown count is not on the output: the canonical EvidenceRow has fixed fields that cannot carry counts, and no canonical change is proposed. This is a stated v1 limitation; a reviewed amendment may add outputs. The independent reviewer should confirm.
- **D07**: Accepted: empty complete population gives not_applicable/empty_universe with null values.
- **D08**: Accepted: latest_event_ns is included, with the clock population, stale-clock, expired-validity and C-1 saturation rules above.
- **D09**: Accepted: seeds are REFERENCE rows (slot venue_seed); new mapping version ef1-venue-map1 and the new reference_id and fact_kind grammars.
- **D10**: Accepted: unit strings publishers, bool and utc_ns, and the enlarged header ledger (45 plus 7 headers), are introduced by an additive EF1-only amendment with matching worker admission and version handling. The frozen CONTRACT.json bytes do not change.
- **D11**: Accepted: aggregate_reason labels and precedence form a closed new vocabulary.
- **D12**: Accepted: evidence_limit 4.
- **D13**: Accepted: a single max_age_ns for all dimensions.
- **D14**: Accepted: a repeated publisher id within one population revision is rejected DUPLICATE; membership history needs distinct revisions.
- **D15**: Finalized as proposed: invalid_config for context and policy violations, invalid_schema for slot shape and closed vocabularies.
- **D16**: Accepted: instrument/session binding is the target entity only.
- **R01**: Explicit item for the independent reviewer: validate against the QualityRow rules that not_applicable with expected = observed = 0 (empty population) and expected = null with observed = 0 (unavailable population) are admissible. Not verified here.

## Coordinator freeze

Per the coordinator, the contract is frozen as `ef1-multivenue-status1` v1 for implementation once this PR merges. This statement is the coordinator's; the author makes no acceptance claim, and numerical, artifact and release gates remain.

## Verification status

Not verified: no canonical dataclass construction, no config digest, no worker admission and no wire encoding were run; QualityRow behavior for empty and unavailable populations is unverified (R01). No library or test code was written or executed. Original EQ165 scope, the full EQ164 audit and all release gates remain.
