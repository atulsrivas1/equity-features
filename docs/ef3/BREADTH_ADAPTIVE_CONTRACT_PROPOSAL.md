# EF3 breadth and adaptive volume contract: proposal

Prepared for EQ-220 [#598](https://github.com/atulsrivas1/equity-features/issues/598) (declared-universe session breadth), EQ-242 [#667](https://github.com/atulsrivas1/equity-features/issues/667) (observed-population companion, draft W3D-5) and EQ-237 [#626](https://github.com/atulsrivas1/equity-features/issues/626) (event-time adaptive volume diagnostics), for consumption by EF3 I/O [#611](https://github.com/atulsrivas1/equity-features/issues/611), worker [#612](https://github.com/atulsrivas1/equity-features/issues/612) and release acceptance EQ-157 [#491](https://github.com/atulsrivas1/equity-features/issues/491). **This is a contract proposal, not accepted by any review.** It admits no Ready state, implementation, numerical acceptance, release or performance claim. Every former DECISION-PROPOSED convention is now a coordinator decision (accepted as proposed) and every former OPEN question has a coordinator ruling; all are decided and pending owner review, and the contract carries a coordinator freeze statement.

Companion data: [BREADTH_ADAPTIVE_CONTRACT_PROPOSAL.json](BREADTH_ADAPTIVE_CONTRACT_PROPOSAL.json) holds the machine-readable producers, headers with per-output role dependencies, fact schemas, 48 declared, 20 observed and 29 adaptive result fixtures and 51 typed-refusal fixtures. Expected values were typed by hand (626 hand-asserted output cells) and checked by a throwaway stdlib-only evaluator (exact `fractions.Fraction` arithmetic, `float.hex`) that imports nothing from the equity packages; the library was not imported, run or tested. Fixtures use compact notation (not canonical wire) and need expansion into canonical packets.

## Authority and inspected sources

Read-only: the audit drafts (`docs/ef1/audit/PROPOSED_STORIES.md` W3D-5, `EQ164_WAVE1_DECISIONS.md` B1, B2, B5, B7, `EQ164_WAVE2_DECISIONS.md` X3-1 and X3-4, `EQ164_WAVE2_X3.md` B2, B5, B6, `EQ164_WAVE3_DECISIONS.md`), the output manifest `docs/plans/equity-output-ownership.json` (the 16 declared slot names, units and coarse operands), `docs/features/CONTEXT_FORMULAS.md` and `packages/features/src/equity_features/breadth.py` (existing breadth), the merged EF2 contracts and `docs/ef2/PRODUCER_SET_AMENDMENT.md` (template), `docs/ef1/MULTI_VENUE_STATUS_CONTRACT_PROPOSAL.md` (population reductions), the `packages/contracts` validators and errors, and the sibling EF3 contract E (robust statistics and pace, PR 690) for the shared population kind and SD-1. Opaque ids only. No private source, threshold or default is used. The 16 declared names come from the manifest; the seven observed outputs and the ten adaptive outputs are defined here from standard public concepts (counts and fractions over a population; a time-weighted smoothed rate baseline with a relative rate and a relative rate change) and are coordinator-decided. **The adaptive_volume family is defined generically by this contract; it does not claim equivalence with the audit opaque rows.** F0690, F0692 and F0694 to F0698 are recorded as unmapped (an open audit item, not a gate for this contract); F0699 is mapped to `baseline_available`.

## Unchanged boundary

Existing `CanonicalBatch`, `ConfigSpec`, `FeatureResult`, `Status`, `Reason`, `ErrorCode`, scalar `ValueType` (`int64`, `float64`, `bool`); the shared REFERENCE validators; the frozen ef1-contract1 and every accepted core, R17, EF1 and EF2 header; the accepted historical `breadth.direction_counts` and `breadth.above_sma_fraction` (completed-return and completed-close horizon, fixed members), which are neither changed, aliased nor reused (DP-B4). No new DataKind, DTO, result codec, scheduler or default, no new error code, no validator change. Hosting is an EF3 module in `packages/features` with config namespace `ef3.*`, a separate catalog and no version bump (coordinator ruling, DP-P1). Update, restore and merge are unsupported (`UNSUPPORTED_CAPABILITY`).

## Producers and config identities

| Item | Declared breadth | Observed breadth | Adaptive volume |
| --- | --- | --- | --- |
| Producer | `session_breadth` | `observed_breadth` | `adaptive_volume` |
| Identity | `ef3.session_breadth` | `ef3.observed_breadth` | `ef3.adaptive_volume` |
| Algorithm / schema | `ef3-session-breadth-v1` / `1` | `ef3-observed-breadth-v1` / `1` | `ef3-adaptive-volume-v1` / `1` |
| Policy label | `ef3-breadth1` | `ef3-obsbreadth1` | `ef3-adaptive1` |
| Story | #598 | #667 | #626 |
| Headers | 16 | 7 | 10 |

Parameters are closed and have no defaults (an unsupported label is `INCOMPATIBLE_VERSION`, a missing or extra parameter `INVALID_CONFIG`). Declared: `policy_version`, `membership_profile` (`static_snapshot` or `ordered_history`), `population_id`, `population_revision`, `near_high_tol_num/den` (exactly when `near_high_fraction` is selected), `near_low_tol_num/den` (exactly when `near_low_fraction` is selected; reduced pairs in [0,1], zero only as 0/1, one only as 1/1), `evidence_limit` 0..10000. Observed: `policy_version`, `scope` (`cohort` or `group`), `group_label` (exactly when `scope` is `group`), `record_set_id`, `floor_price_num/den` (reduced, at least 0), `floor_volume` (int64 at least 0), `evidence_limit`. Adaptive: `policy_version`, `epoch`, `tau_ns` 1..2^62, `warmup_count` W 1..4096, `evidence_limit`. The evaluation point is the market cutoff C of the existing availability spec and K the knowledge cutoff; known_at and reconstruction modes give identical results because K only gates knowledge. The declared and observed profiles have distinct producers, identities, versions and names, so their denominators are never mixed.

## Outputs and headers

Order: lexicographic by feature id within a producer. Each output has its own roles and independent readiness (explicit per-output dependency edges, no generic all-output barrier); a call may select a subset and unselected outputs need neither roles nor parameters.

### Declared-universe session breadth (16)

| Feature id | dtype | unit | Roles |
| --- | --- | --- | --- |
| `breadth.session.above_vwap_fraction` | float64 | fraction | population, endpoint_price, vwap |
| `breadth.session.advance_decline_ratio` | float64 | ratio | population, prior_reference_availability, current_return |
| `breadth.session.advancing_count` | int64 | members | population, prior_reference_availability, current_return |
| `breadth.session.declining_count` | int64 | members | population, prior_reference_availability, current_return |
| `breadth.session.direction_net_count` | int64 | members | population, prior_reference_availability, current_return |
| `breadth.session.down_volume` | int64 | shares | population, prior_reference_availability, current_return, cumulative_volume |
| `breadth.session.latest_observed_member_event_ns` | int64 | utc_ns | population, endpoint_price |
| `breadth.session.near_high_fraction` | float64 | fraction | population, endpoint_price, selected_high, selected_low |
| `breadth.session.near_low_fraction` | float64 | fraction | population, endpoint_price, selected_high, selected_low |
| `breadth.session.positive_momentum_fraction` | float64 | fraction | population, momentum |
| `breadth.session.prior_reference_coverage_fraction` | float64 | fraction | population, prior_reference_availability |
| `breadth.session.prior_reference_eligible_count` | int64 | members | population, prior_reference_availability |
| `breadth.session.selected_member_count` | int64 | members | population |
| `breadth.session.unchanged_count` | int64 | members | population, prior_reference_availability, current_return |
| `breadth.session.up_down_volume_ratio` | float64 | ratio | population, prior_reference_availability, current_return, cumulative_volume |
| `breadth.session.up_volume` | int64 | shares | population, prior_reference_availability, current_return, cumulative_volume |

### Observed-population session breadth companion (7)

| Feature id | dtype | unit | Roles |
| --- | --- | --- | --- |
| `breadth.observed.advance_fraction` | float64 | fraction | members, qualifier_price, qualifier_volume, change |
| `breadth.observed.advancing_member_count` | int64 | members | members, qualifier_price, qualifier_volume, change |
| `breadth.observed.nonadvancing_member_count` | int64 | members | members, qualifier_price, qualifier_volume, change |
| `breadth.observed.observed_member_count` | int64 | members | members |
| `breadth.observed.qualifying_fraction` | float64 | fraction | members, qualifier_price, qualifier_volume |
| `breadth.observed.qualifying_member_count` | int64 | members | members, qualifier_price, qualifier_volume |
| `breadth.observed.unknown_member_count` | int64 | members | members, qualifier_price, qualifier_volume, change |

### Adaptive volume diagnostics (10)

| Feature id | dtype | unit | Roles |
| --- | --- | --- | --- |
| `adaptive.volume.acceleration_scored_count` | int64 | observations | observations |
| `adaptive.volume.baseline_available` | bool | boolean | observations |
| `adaptive.volume.baseline_rate` | float64 | shares/s | observations |
| `adaptive.volume.latest_event_ns` | int64 | utc_ns | observations |
| `adaptive.volume.observation_count` | int64 | observations | observations |
| `adaptive.volume.peak_relative_acceleration` | float64 | 1/s | observations |
| `adaptive.volume.peak_relative_acceleration_event_ns` | int64 | utc_ns | observations |
| `adaptive.volume.peak_relative_rate` | float64 | ratio | observations |
| `adaptive.volume.peak_relative_rate_event_ns` | int64 | utc_ns | observations |
| `adaptive.volume.scored_count` | int64 | observations | observations |

Units: `members`, `ratio`, `shares/s` and `1/s` are new to the header ledger; `shares`, `fraction`, `boolean`, `utc_ns` and `observations` exist in the frozen ledger, the EF1 amendment or merged code (contract E also introduces `members`; the two amendments must agree). Header ids were checked against contract E (`cohort.*`, `mean.*`, `pace.*`, `robust.*`) and the EF1/EF2 header ledgers: no collision.

## Inputs and roles

All roles are fixed nullable slots in the order above; `None` is an absent delivery, and a present zero-row batch with its own complete coverage is present-empty. Fact schemas are in the JSON `reference_fact_schemas`.

- **Declared population (DP-P2).** Role `population` reuses the fact kind `ef3.population.member` exactly as contract E (OQ-7) defines it: one row per declared member, `instrument_id` = member, `session_id` = target session, `reference_id` `x1:B(population_id)`, effective bounds = target session bounds, `text` = snapshot id, price and factors null, `known_at_ns` nullable. The declared population is the set of selected (eligible) members; a member that is not eligible is simply not declared (the manifest operand `eligible_membership` is the declaration itself). Profile `ordered_history` needs intervals and re-entry that the E kind cannot express (its bounds are pinned to the session and it has no stint identity), so it uses the distinct kind `ef3.breadth.membership_interval` (`reference_id` `bh1:B(population_id):B(population_revision):stint6`, half-open interval, end null = open). The kind a request uses is fixed by `membership_profile`; a foreign kind is `INVALID_SCHEMA`.
- **Per-member facts.** Roles `prior_reference_availability`, `current_return`, `cumulative_volume`, `endpoint_price`, `vwap`, `momentum`, `selected_high`, `selected_low` are REFERENCE batches, `instrument_id` = member, `reference_id` `bf1:B(population_id)`, one fact kind (or state pair) per role, `effective_start_ns` the member event time, `known_at_ns` the original knowledge. Values travel in the REFERENCE `price` column (DP-B13): `current_return` and `momentum` are signed and only their sign is consumed; `cumulative_volume` is shares at least 0; `endpoint_price`, `selected_high`, `selected_low` are positive coefficients at the request scale; `vwap` is the exact rational `price*factor_num/factor_den` with `factor_num` 1 and `factor_den` the cumulative volume (notional over volume, no float). Prior availability and VWAP availability are fact-kind states (`ef3.member.prior_reference.available|unavailable`, `ef3.member.vwap|ef3.member.vwap.unavailable`). All roles share one `PriceUnit` and one snapshot id.
- **Observed population.** Role `members` (`ef3.observed.member`, `reference_id` `ob1:B(record_set_id)`, `text` = group label or null) is the roster; roles `change`, `qualifier_price`, `qualifier_volume` carry sign-only change, price coefficient and share volume. The roster defines the observed population; a fact row for a non-roster member is `INCONSISTENT_IDENTITY`.
- **Adaptive observations.** One role `observations` (`ef3.adaptive.rate`, `reference_id` `ao1:B(epoch):seq19:B(event_id)`), `effective_start_ns` = event time t, supplied raw rate `price*factor_num/factor_den` in shares per second (factors both null meaning 1/1, or both positive; price at least 0).

### SD-1: duplicate identity (cited, not redefined)

The duplicate-identity rule is stated once, in contract E (RF12): a duplicate (instrument, session, reference_id) is rejected with `DUPLICATE`; there is no first-wins, last-wins or aggregation. This contract only cites it for the declared population, every fact role, the observed roster and the adaptive observations (RB01, RB02, RO01, RA01). The one extension is that two stints of one member whose intervals overlap are the same identity at the same time and are rejected (RB03). The cohort-normalization contract cites the same E section (Q9). E is cited by section name (population kind `ef3.population.member`, duplicate-identity rule), not by line, because E may still receive small edits.

## Exact mathematics: declared-universe breadth

Notation. P is the population expected at C: `static_snapshot` all declared members; `ordered_history` members with a stint where start <= C < end (half open: a stint starting at C is in, one ending at C is out). N = |P|. A fact for member m in a role is *resolved* when the row exists, `known_at_ns` is non-null and <= K, `effective_start_ns` < C (events at C are excluded) and the value is non-null; otherwise it is unresolved with the first applicable reason of: `absent_input` (role None, role empty, or row missing), `governed_gap` (role declares incomplete coverage), `unknown_availability`, `future_knowledge`, `future_market` (event at or after C), `null_field`. Each member predicate is three valued (true, false, unknown) and a known false decides without the other inputs (DP-B3). An output is available iff no member is unknown for it (DP-B1); its quality has expected = N and observed = N minus unknown members; unavailable reasons are the union over the unresolved inputs the predicate actually needed. Population-level findings come first and make every output unavailable: role None `absent_input`; declared incomplete coverage `governed_gap`; any expected row with null known_at `unknown_availability` or known_at > K `future_knowledge`; N = 0 `not_applicable/empty_universe` with expected = observed = 0 (DP-B11).

- `selected_member_count` = N (needs only the population).
- `prior_reference_eligible_count` = members whose prior reference is available; declared unavailable is false. `prior_reference_coverage_fraction` = that count / N.
- Direction: a member is directional only if its prior reference is available (known unavailable is none of the three classes and is not an error); then `current_return` > 0 advancing, < 0 declining, = 0 unchanged (exact, no tolerance). `advancing_count`, `declining_count` and `unchanged_count` each depend on every member's prior availability and, where available, return. `direction_net_count` = A - D (signed int64). `advance_decline_ratio` = A/D; D = 0 gives null `not_applicable/zero_denominator` even when A = 0 (DP-B6). A non-null return for a member declared prior-unavailable is `INCONSISTENT_IDENTITY` (RB07).
- `up_volume` = sum of `cumulative_volume` over advancing members; `down_volume` likewise over declining members. The whole cumulative volume follows the member's current direction (a flip moves all of it, DB14, DB15). Volume of unchanged or non-directional members is irrelevant and may be absent (DB19). Sums are exact; a published value above 2^63-1 refuses the request with `OVERFLOW` when that output is selected (RB23). `up_down_volume_ratio` = up/down with the same zero rule.
- `above_vwap_fraction` = #(endpoint price coefficient > vwap coefficient) / N, strict, by exact cross multiplication (equality is not above, DP-B7); vwap declared unavailable is false.
- `positive_momentum_fraction` = #(momentum > 0) / N (DP-B8).
- `near_high_fraction` = #(H - E <= t_h*(H - L)) / N and `near_low_fraction` = #(E - L <= t_l*(H - L)) / N, with E the endpoint coefficient, inclusive (DP-B9). H = L is false (decided without E); H < L or E outside [L, H] is unresolved `ineligible`.
- `latest_observed_member_event_ns` = maximum member event time (`effective_start_ns` of the endpoint-price row) when all N are resolved; otherwise the maximum resolved time if it equals C - 1 (no later event can exist; quality 1/1); otherwise null (DP-B10).

Float outputs are one correctly rounded division of exact integers (bit exact); counts and volumes are exact int64. Membership, first entry, reset and correction (DP-B12): membership is evaluated only at C; a member that joined during the session contributes with its as-of facts (no backfill); the library keeps no state across evaluations, so a reset is a new request with a new session; a correction is a new snapshot id and one batch never holds two revisions.

## Exact mathematics: observed-population breadth

The roster rows with `effective_start_ns` < C form the observed population (rows at or after C are not yet observed and are ignored whatever their state); roster-level findings (None, incomplete coverage, null or future known_at) make everything unavailable. Scope `group` keeps records whose `text` equals `group_label`; `cohort` keeps all (DP-O4). n = number of records in scope; there is no expected population, so quality expected = n is a record count, not an expected universe.

- qualifies(m) = (price coefficient / 10^scale >= floor_price) and (volume >= floor_volume), both inclusive; a known failure decides false without the other input (DP-O2).
- advancing(m) = qualifies(m) and change > 0 (strict); false if qualifies is false or the change is known <= 0.
- `observed_member_count` = n; `unknown_member_count` = members for which qualifies or advancing is unknown (available whenever the roster is); `qualifying_member_count` and `advancing_member_count` (null if any member is unknown for them); `nonadvancing_member_count` = qualifying - advancing; `advance_fraction` = advancing/qualifying (qualifying 0: `not_applicable/zero_denominator`); `qualifying_fraction` = qualifying/n (n = 0: zero denominator). This is not an advance/decline ratio: non-advancing members are not split. An empty scope gives available zero counts (DP-O5).

## Exact mathematics: adaptive volume

Scope: observations with t < C, ordered by sequence (strictly increasing within the epoch; time non-decreasing; equal times allowed). Every in-scope row must be known (`unknown_availability` or `future_knowledge` null all outputs, expected = in-scope rows). A null rate in scope is `null_field` for all rate outputs; `latest_event_ns` needs only times. With r_k the rate (exact rational), t_k in ns, d_k = t_k - t_(k-1) and tau = `tau_ns`:

- Baseline: B_1 = r_1, B_k = (tau*B_(k-1) + d_k*r_k)/(tau + d_k) (weight d/(tau+d)); d_k = 0 leaves B unchanged. `baseline_available` = (n >= W), available whenever the stream is usable (false for n < W, including n = 0); `baseline_rate` = B_n, else `insufficient_history` (expected W, observed n).
- Observation k is scorable when k >= W+1. Relative rate rho_k = r_k/B_(k-1), defined when B_(k-1) > 0. Relative acceleration u_k = (r_k - r_(k-1))*10^9/(d_k*B_(k-1)) in 1/s, defined when d_k > 0 and B_(k-1) > 0. A zero baseline is known-undefined, not an error; the counts expose it. `scored_count` and `acceleration_scored_count` are available counts (possibly 0); `observation_count` = n.
- `peak_relative_rate` = max rho and `peak_relative_acceleration` = max u (signed; the maximum of negatives is the least negative), each with its `..._event_ns` witness: the event time of the earliest observation attaining the exact maximum. No scorable observation: `insufficient_history` (expected W+1, observed n). Scorable but none defined: `not_applicable/zero_denominator`.
- `latest_event_ns` = t_n; no observation: `not_applicable/no_eligible_observations`.
- Prefix property: each output is a function of the in-scope prefix only; evaluating the full stream at C = t_j + 1 equals evaluating its first j rows (AD07a to AD07c, plus an exhaustive evaluator check for j = 0..6). Equal-time rows, irregular gaps (a long gap is only a large d, weight near 1; there is no gap marker or interpolation), sequence gaps (they carry no meaning) and observed zeros (not null) are covered. A new epoch is a fresh stream; rows of another epoch are `INCONSISTENT_IDENTITY`. Replay with identical inputs gives identical outputs; a correction is a new snapshot id.
- Audit mapping (DP-A9, DP-A10): F0699 corresponds to `baseline_available`. F0700 and F0701 are the supplied identity and event clock mapped by #611 (the entity and `effective_start_ns`); F0721 is the #611 grouping of these headers, the summary being as of C and final only for a request whose C is at or after the session end with complete coverage (a request property, not a library output). F0690, F0692 and F0694 to F0698 are unmapped (Q1): composite and trigger/episode outputs need policy owned by #519/#520 or source knowledge, and no peak over the #490 relative-volume operand exists in v1 (Q2).

## Availability, quality, evidence and refusals

Typed refusal precedes assessment. Quality uses existing `Status` and `Reason` only. Reason precedence: `absent_input`, `unknown_availability`, `future_knowledge`, `future_market`, `null_field`, `ineligible` (`missing_input`), `governed_gap` (`incomplete_coverage`), `insufficient_history`, then `no_eligible_observations`, `zero_denominator`, `empty_universe` (`not_applicable`); all applicable reasons are retained in lexical order and the status follows the first applicable reason; a value is null exactly when the status is not `available`; available requires observed = expected. `partial_universe` is not used because no partial result exists (DP-B1). Evidence (available outputs only, at most `evidence_limit`): count and fraction outputs cite the first contributing members in population order with the deciding row (role, reference id, event time, known_at); volume outputs cite the cumulative_volume rows of contributing members; `latest_observed_member_event_ns` cites the first member holding the maximum; adaptive peak and baseline outputs cite the witness observation (sequence). Derived outputs (net count, ratios, coverage fraction) carry none.

Refusals (51, no new code): each is raised by an existing shared validator or by the library as listed.

| Id | Code | Case | Raised by |
| --- | --- | --- | --- |
| RB01 | `DUPLICATE` | declared population lists member a twice (same instrument, session, reference_id): SD-1 | shared validator |
| RB02 | `DUPLICATE` | current_return lists member a twice: SD-1 | shared validator |
| RB03 | `DUPLICATE` | ordered_history: member b has two stints that overlap in time (even if only one contains C): SD-1 | library |
| RB04 | `INCONSISTENT_IDENTITY` | a fact role carries a row for member z that is not declared in the population (never silently dropped) | library |
| RB05 | `INCONSISTENT_IDENTITY` | fact reference_id carries a population_id different from the config | library |
| RB06 | `INCONSISTENT_IDENTITY` | fact roles carry different snapshot ids | library |
| RB07 | `INCONSISTENT_IDENTITY` | current_return non-null for a member declared prior-reference unavailable (contradiction) | library |
| RB08 | `INVALID_ORDER` | rows of a role not ordered by (effective_start_ns, reference_id) | shared validator |
| RB09 | `BOUNDS` | negative cumulative volume in the price column | library |
| RB10 | `UNSUPPORTED_ADJUSTMENT` | vwap factor_den = 0 (rational factors must be positive) | shared validator |
| RB11 | `BOUNDS` | membership interval with end <= start | shared validator |
| RB12 | `INVALID_UNIT` | two roles declare different PriceUnit (scale or currency) | shared compatibility check |
| RB13 | `INVALID_SCHEMA` | a role carries a fact_kind of another role | library |
| RB14 | `INVALID_SCHEMA` | eight or ten role slots instead of nine | library |
| RB15 | `INVALID_SCHEMA` | non-positive endpoint price, selected high or selected low coefficient (positive prices only) | library |
| RB16 | `INVALID_CONFIG` | near_high tolerance 5/4 (above 1) | library |
| RB17 | `INVALID_CONFIG` | near_low tolerance 2/4 not reduced | library |
| RB18 | `INVALID_CONFIG` | tolerance supplied while its output is not selected, or missing while selected | library |
| RB19 | `INVALID_CONFIG` | membership_profile outside the closed pair | library |
| RB20 | `INCOMPATIBLE_VERSION` | policy_version other than ef3-breadth1 | library |
| RB21 | `UNKNOWN_FEATURE` | selected feature id not produced by session_breadth | library |
| RB22 | `UNSUPPORTED_CAPABILITY` | update, restore or merge requested (no state capability in v1) | library |
| RB23 | `OVERFLOW` | sum of advancing members volumes above 2^63-1 with up_volume selected (published value out of int64; whole request refused) | library |
| RB24 | `BOUNDS` | 4097 rows in one role (4096 bound) | library |
| RB25 | `INCONSISTENT_IDENTITY` | static_snapshot: a population row whose effective bounds differ from the target session bounds | library |
| RB26 | `INVALID_SCHEMA` | vwap row with null factor_num or factor_den | library |
| RO01 | `DUPLICATE` | roster lists member a twice: SD-1 (cited from contract E) | shared validator |
| RO02 | `INCONSISTENT_IDENTITY` | change row for a member that is not in the roster | library |
| RO03 | `INVALID_CONFIG` | scope group without group_label | library |
| RO04 | `INVALID_CONFIG` | group_label supplied with scope cohort | library |
| RO05 | `INVALID_CONFIG` | floor_price 4/2 not reduced, or negative | library |
| RO06 | `INVALID_CONFIG` | floor_volume negative or non-integer | library |
| RO07 | `INVALID_SCHEMA` | roster batch carries fact_kind ef3.population.member (declared kind in the observed role): profiles never mix | library |
| RO08 | `INCONSISTENT_IDENTITY` | roster reference_id record_set_id differs from the config | library |
| RO09 | `BOUNDS` | negative qualifier_volume | library |
| RO10 | `INVALID_UNIT` | roles with different PriceUnit scale | shared compatibility check |
| RO11 | `INCOMPATIBLE_VERSION` | policy_version other than ef3-obsbreadth1 | library |
| RO12 | `UNSUPPORTED_CAPABILITY` | update, restore or merge requested | library |
| RA01 | `DUPLICATE` | same reference_id twice in observations: SD-1 | shared validator |
| RA02 | `DUPLICATE` | equal sequence with different event_id in one epoch | library |
| RA03 | `INVALID_ORDER` | sequence decreases while event time increases | library |
| RA04 | `INCONSISTENT_IDENTITY` | row epoch differs from the config epoch (epochs never mix) | library |
| RA05 | `BOUNDS` | negative rate coefficient | library |
| RA06 | `UNSUPPORTED_ADJUSTMENT` | rate factor_den = 0 | shared validator |
| RA07 | `INVALID_SCHEMA` | factor_num present with factor_den null | library |
| RA08 | `INVALID_CONFIG` | tau_ns = 0 | library |
| RA09 | `INVALID_CONFIG` | warmup_count 0 or 4097 | library |
| RA10 | `INCOMPATIBLE_VERSION` | policy_version other than ef3-adaptive1 | library |
| RA11 | `UNSUPPORTED_CAPABILITY` | update, restore or merge requested (v1 holds no state capability) | library |
| RA12 | `INVALID_SCHEMA` | observations batch carries a foreign fact_kind | library |
| RA13 | `INCONSISTENT_IDENTITY` | row text differs from the batch snapshot id | library |

## Layer responsibilities

- **Library (pure).** Structural validation, three-valued predicates, counts, fractions, ratios, volume sums, proximity, the baseline recurrence, relative rate and acceleration, peaks, quality, evidence and every refusal above. No I/O, clocks, defaults, source access or state across calls.
- **I/O #611.** Maps supplied facts into the fixed roles preserving original identity, snapshot, known_at, event time and coverage; delivers `None` for a missing delivery and a zero-row batch for a covered empty one; maps exact integer coefficients (never a rounded float64, and never rounding a tiny return or momentum to zero); never derives a return, sign, eligibility, VWAP, momentum or rate; never fills a missing member; uses an `unavailable` fact kind only when the supplier declares it (explicit missing, never inferred, Q4); never selects a population or default; envelopes the adaptive headers as F0721 and maps F0700/F0701.
- **Worker #612.** Declares the config (population id and revision, profile, tolerances, floors, scope, tau, W, epoch), enforces the fixed role manifest and digest, runs one pure request per complete result and writes the library result unchanged. No aggregation, predicate, counting or smoothing; direct, worker and stored results must be identical, including refusal class.

## Explicit non-goals

No acquisition of members, returns, volumes, prices, VWAP, momentum or rates; no universe selection algorithm; no regime classification, cut-offs, score scaling or member projection (#518); no trigger, episode or composite policy (#519/#520); no private population minimum, ratio, threshold or default; no raw velocity or relative-volume computation (supplied operands owned elsewhere); no dependency on EF4 production (inputs are supplied through I/O); no reuse or change of the historical breadth APIs; no partial or lower-bound counts; no state, update, restore or merge capability; no performance, parity, release or publication claim; no source equivalence.

## Fixtures

Declared (48):

| Id | Case |
| --- | --- |
| DB01 | empty complete declared population (0 of 0): a declaration of nothing, never a vacuous truth; every output null |
| DB02 | population role not delivered (None slot) |
| DB03 | population batch declares incomplete coverage |
| DB04 | expected member c has null known_at: the population itself is not known |
| DB05 | expected member c known_at 150 > K 100: population not yet known |
| DB06 | population of four declared, no fact role delivered at all: N = 4 is known from the declaration alone; every other output unavailable (observed 0 of 4) |
| DB07 | declared population is the subset {b, c} of the world (facts only for b and c): N = 2 |
| DB08 | complete selected population a,b,c,d with every role complete; all 16 outputs available (witness cap 3) |
| DB09 | c declared prior-unavailable (known, first entry): not directional, remains in the denominator N = 4 |
| DB10 | b prior-availability fact has null known_at: unknown prior never becomes available or unavailable |
| DB11 | prior-availability role not delivered: eligibility, coverage and direction outputs unavailable; operand-independent fractions unaffected |
| DB12 | d has no current return: missing member does not shrink N = 4; direction outputs unavailable, observed 3 of 4 |
| DB13 | d return row present with null value: null_field, not zero and not unchanged |
| DB14 | b flips from down to up: its whole cumulative volume 200 moves to up_volume; D = 0 and down volume 0 give zero-denominator ratios |
| DB15 | a flips from up to down: whole volume 100 moves to down_volume (not a delta); up 400, down 300 |
| DB16 | all four exactly unchanged: A = D = 0; ratio 0/0 is zero_denominator; both volumes are available zeros |
| DB17 | advancing members have observed volume 0: up_volume is the available value 0; ratio 0/200 is exact +0.0 |
| DB18 | advancing member a volume null: up_volume null_field; down_volume independent and available |
| DB19 | volume of unchanged member c is absent: irrelevant to both volume outputs (its direction is flat) |
| DB20 | single selected member a (up): fractions are exact 1/1 or 0/1; D = 0 gives zero-denominator ratios |
| DB21 | changing membership at C = 100: a stays, b left at 80 (facts ignored), c joined at 90, d starts at 120 (not yet); N = 2 {a,c} |
| DB22 | member b leaves at 40 and re-enters at 60 (disjoint stints): counted once at C = 100, N = 2 |
| DB23 | half-open membership [start, end): b with end = C = 100 is out, c with start = C is in; N = 2 {a,c} |
| DB24 | c VWAP declared unavailable (zero volume): not above, endpoint price irrelevant; fraction stays over N = 4 |
| DB25 | d endpoint price absent: above_vwap, near_high, near_low, latest unavailable; momentum fraction unaffected |
| DB26 | vwap batch declares incomplete coverage: every member governed_gap; observed 0 of 4 for above_vwap only |
| DB27 | vwap batch incomplete AND a endpoint price absent: reasons absent_input and governed_gap; status follows the first (absent_input) |
| DB28 | c momentum null: null_field (unknown never false); other fractions unaffected |
| DB29 | strictly positive: only a is positive (1); exact zero is not positive; fraction 1/4 |
| DB30 | near_high tol 1/4: a H-ep = 250 equals 1/4 of range 1000 (near, inclusive); b 251 is not; c at the high; d zero range is not near; 2/4 |
| DB31 | near_low tol 1/5: a ep-L = 200 equals 1/5 of range 1000 (near, inclusive); b 201 is not; c at the low; d zero range is not near; 2/4 |
| DB32 | tolerance 0/1: near only when exactly at the extreme: near_high {a}, near_low {c}; 1/4 each |
| DB33 | tolerance 1/1 (maximum): every non-degenerate member is near both extremes; the zero-range member d is not: 3/4 each |
| DB34 | a endpoint 1300 above session high 1120: inconsistent facts, ineligible (never counted false) |
| DB35 | b selected high 800 below selected low 880: inverted, ineligible |
| DB36 | c has zero range (H = L): decided not near without its endpoint price (absent); other outputs needing c endpoint stay unavailable |
| DB37 | d selected high absent: both proximity outputs need the high/low pair, so both are unavailable (absent_input) |
| DB38 | a,b,c endpoint knowledge unknown; d event at C-1 = 99: no later member event can exist, saturated value 99 with coverage 1/1 |
| DB39 | same but d at 98 < C-1: unknown members could be later, so null |
| DB40 | d endpoint event at exactly C = 100 is not usable (events at C are excluded): future_market for d only |
| DB41 | replay of the complete world with K = 300 in reconstruction mode and original known_at 150: identical outputs to DB08 |
| DB42 | N = 3, one member with a prior reference: coverage fraction 1/3 rounds once (binary64 0x1.5555555555555p-2) |
| DB43 | A = 1, D = 3: ratio 1/3, volumes 1 and 3: ratio 1/3 (single rounding each) |
| DB44 | witness cap 1 on the complete world: first advancing member in population order only (a); latest witness b |
| DB45 | single advancing member with cumulative volume 2^63-1: up_volume exactly at the int64 bound is available |
| DB46 | three members up: counts and the up volume 15 are order independent; population order only decides witness order |
| XB01 | DECLARED universe {a..e} with e missing from every fact role: N = 5 never shrinks; direction counts unavailable (observed 4 of 5) |
| XB03 | DECLARED complete {a..d}, same returns as XB02: advance_decline_ratio = A/D = 2 (unchanged excluded from both terms) versus observed advance_fraction = 2/4; the two are not interchangeable |

Observed (20):

| Id | Case |
| --- | --- |
| OB01 | cohort of six records, floors price >= 10.00 and volume >= 100 (inclusive): a(equal both) d e f qualify; advancing needs strictly positive change: a and f; e (change exactly 0) does not |
| OB02 | group g1 = {a, b, f}: group size 3; b fails the price floor; qualifying {a, f}; both advance |
| OB03 | group g2 = {c, d}: c fails the volume floor; qualifying {d} (change -2): advance fraction exact +0.0 |
| OB04 | group g3 has no records: observed zero is an observation; counts are available zeros, both fractions zero_denominator |
| OB05 | roster not delivered |
| OB06 | roster delivered, complete and empty (cohort): zero observed members, counts 0, fractions zero_denominator |
| OB07 | roster declares incomplete coverage: records may be missing, so nothing is reported |
| OB08 | seventh record g: price-floor input absent (eligibility unknown) but change -3; advancing decided false without it, qualifying and derived outputs unavailable; unknown_member_count 1 |
| OB09 | f qualifies but its change has null known_at: advancing and derived unavailable, qualifying still available |
| OB10 | b has no change row but fails the price floor: change irrelevant, results equal OB01 |
| OB11 | price floor 100.00: nothing qualifies; qualifying 0, advancing 0, advance fraction zero_denominator, qualifying fraction exact +0.0 |
| OB12 | only a and f observed, both qualify and advance: fractions exactly 1/1 |
| OB13 | rational price floor 7/2 = 3.50: coefficient 350 qualifies (equality), 349 does not; volume floor 0 admits volume 0 |
| OB14 | d change fact at exactly C = 100: future_market; d qualifies so advancing cannot be decided |
| OB15 | roster record a known_at 150 > K: the observed population is not yet known |
| OB16 | roster record z at t = C = 100 (not yet observed, null known_at): excluded, results equal OB01 |
| OB17 | d volume qualifier null: price passes, so qualification unknown (null_field); d change -2 decides advancing false |
| OB18 | c volume qualifier null (price passes): qualification unknown; b volume qualifier absent but its price is below the floor: disqualified without it (dominance); qualifying unavailable (null_field), observed 5 of 6 |
| OB19 | qualifier_price batch declares incomplete coverage: no price test can be made (governed_gap); only c (volume floor fails) is decided false and d, e are decided not advancing by non-positive change; qualifying observed 1 of 6, advancing 3 of 6, unknown members 5 |
| XB02 | OBSERVED record set {a..d} (same facts, no e): observed denominator 4; advance fraction 2/4; distinct names and denominators from XB01 |

Adaptive (29):

| Id | Case |
| --- | --- |
| AD01 | observation stream delivered complete and empty (n = 0, W = 2): flag false (available), counts 0, baseline and peaks insufficient_history, latest not_applicable |
| AD02 | observation role not delivered |
| AD03 | observation batch declares incomplete coverage |
| AD04 | n = 1 < W = 2: flag false, baseline needs 2 observations; counts show warm-up |
| AD05 | n = W = 2: baseline available (equals B_2 = 8), no scorable observation yet (needs W+1 = 3) |
| AD06 | regular stream rates 8,8,16,32,8,8 at 1..6 s, tau = 1 s (alpha = 1/2 each step), W = 2: B_6 = 23/2; peak relative rate 8/3 at 4 s; peak relative acceleration 4/3 at 4 s |
| AD07a | prefix property: cutoff C = t_3 + 1 ns on the full six-row stream equals the result of the first 3 rows alone (rows after the cutoff are ignored even if present) |
| AD07b | prefix property: cutoff C = t_4 + 1 ns on the full six-row stream equals the result of the first 4 rows alone (rows after the cutoff are ignored even if present) |
| AD07c | prefix property: cutoff C = t_5 + 1 ns on the full six-row stream equals the result of the first 5 rows alone (rows after the cutoff are ignored even if present) |
| AD08 | rates 4,4,8,12: relative rates 8/4 = 2 and 12/6 = 2 tie exactly; witness is the earliest observation (3 s); acceleration 1 and 2/3 |
| AD09 | rates 4,4,8,14: accelerations 1 and 1 tie exactly (witness earliest, 3 s) while the relative-rate peak 7/3 is the later observation (4 s) |
| AD10 | rates 0,0,5,5: baseline 0 for the third observation makes it unscorable (zero_denominator, not an error); fourth scored: relative rate 5/(5/2) = 2, acceleration 0 (+0.0); B_4 = 15/4 |
| AD11 | all rates exactly 0: baseline available as exact +0.0 (observed zeros, not missing); every ratio has a zero denominator |
| AD12 | third in-scope observation has a null rate: rate-dependent outputs null_field (observed 3 of 4); the latest event time is independent and available |
| AD13 | third observation known_at 150 s > K = 100 s: future knowledge, every output null (the stream prefix is not known) |
| AD14 | second observation known_at null: unknown availability, every output null |
| AD15 | fourth observation at t = C = 100 s with null known_at: outside the half-open scope [.., C), ignored (results equal the first three rows) |
| AD16 | C = 5 s: the observation at C - 1 ns is included, the one at exactly C is excluded; elapsed times are 1 ns so alpha = 1/(1e9+1) |
| AD17 | two observations at 3 s (sequence 3 and 4): alpha = 0 for the second so the baseline is unchanged (12); its relative rate 32/12 = 8/3 is scored; its acceleration (elapsed 0) is not defined; B_5 = 10 |
| AD18 | irregular times 1,2,5,6,13 s with rates 8,8,16,8,24, tau = 1 s: alphas 1/2, 3/4, 1/2, 7/8; B_5 = 179/8; peak relative rate 24/11 at 13 s; peak acceleration 1/3 at 5 s |
| AD19 | W = 1: baseline available after one observation; scorable from the second: rates 8,16,8 give relative rates 2 and 2/3, accelerations 1 and -2/3, B_3 = 10 |
| AD20 | tau = 1 ns, elapsed 1 s: alpha = 1e9/(1e9+1) so B_2 = (8 + 16e9)/(1e9+1) (almost the new rate); exact rational reference, tolerance acceptance |
| AD21 | constant rate 5: relative rate exactly 1, acceleration exactly +0.0, witness is the earliest scorable observation (3 s) |
| AD22 | decreasing rates 16,8,4,2: relative rates 1/3, 1/4 (peak 1/3 at 3 s); accelerations -1/3, -1/4 (maximum is the least negative, -1/4 at 4 s); B_4 = 5 |
| AD23 | rational supplied rates 100/3 and 200/3 shares per second (price 100/200, factor 1/3), W = 1: B_2 = 50, relative rate 2, acceleration 1 |
| AD24 | new epoch e2: sequence restarts at 1 and no state is carried from e1; result equals AD05 for the same two rows |
| AD25 | replay of AD06 with K = 10^12 ns later and original known_at: identical outputs (K only gates knowledge) |
| AD26 | rate 2^63-1 shares per second twice (W = 1): baseline rounds once to 2^63 as binary64; relative rate exactly 1; acceleration +0.0 |
| AD27 | sequence numbers 1, 5, 9 (non-contiguous but strictly increasing): a sequence gap proves nothing and changes nothing; result equals the contiguous three-row stream |

The JSON `coverage_map` indexes tags: empty, partial and complete populations, missing members, known-unavailable versus unknown prior, observed versus declared denominators (XB01 to XB03), zero denominators, ties, boundary equalities, direction flips, changing membership, warm-up and insufficient history, prefix property, equal-time and irregular observations, null and unavailable reasons, replay, rounding and int64 limits. Float cells give the exact rational, float64 and `float.hex`. Acceptance: declared and observed floats are bit exact; adaptive floats within max(8 ulp, 1e-12*|r|) of the single rounding, with +0.0 required where exact zero is argued (AD10, AD21, AD26); ties are decided on exact values and the tie fixtures use dyadic quantities so a floating implementation is exact.

## Coordinator decisions (decided, pending owner review)

All former DECISION-PROPOSED conventions are accepted as proposed:

- **DP-P1**: Hosting: an EF3 module in packages/features, config namespace ef3.*, separate catalog, no version bump (coordinator ruling).
- **DP-P2**: The declared static population reuses fact kind ef3.population.member exactly as defined by contract E (OQ-7). Eligibility is not a per-row flag: a member that is not eligible is not declared. A distinct kind ef3.breadth.membership_interval exists only for the ordered_history profile because the E kind cannot express intervals or re-entry.
- **DP-S1**: SD-1 (duplicate identity) is stated once, in contract E (RF12): a duplicate (instrument, session, reference_id) is rejected with DUPLICATE. This contract only cites it; the one extension is that overlapping stints of one member are the same identity (RB03).
- **DP-B1**: Count and fraction outputs are null unless every selected member is determined for that output (analogue of multi-venue D01). Partial knowledge is carried by quality expected = N, observed = determined members. Alternative: partial counts as lower bounds (not adopted).
- **DP-B2**: The denominator of every fraction is N, the declared population size at C; missing members never shrink it. A member whose input is KNOWN inapplicable (prior unavailable, vwap unavailable, zero range) is not directional / not satisfying and stays in N.
- **DP-B3**: Three-valued logic per member (true, false, unknown): a known false decides a predicate without its other inputs (dominance); unknown never becomes false.
- **DP-B4**: Direction comes from the supplied signed current return, sign only, exact zero is unchanged, no epsilon; a member is directional only with prior_reference available. The existing breadth.direction_counts (completed-return horizon, EQ035) is not reused.
- **DP-B5**: Up (down) volume is the whole cumulative volume of members whose current direction is up (down); a direction flip moves the whole volume.
- **DP-B6**: advance_decline_ratio = A/D and up_down_volume_ratio = up/down; a zero denominator is not_applicable/zero_denominator even when the numerator is also 0.
- **DP-B7**: Above VWAP is strict (endpoint > vwap); VWAP is an exact rational notional/volume pair, not a float.
- **DP-B8**: Positive momentum is strictly greater than 0 on a sign-only supplied value.
- **DP-B9**: Proximity is range based and inclusive: near_high iff H - E <= t_h*(H - L); near_low iff E - L <= t_l*(H - L); t_h and t_l are independent reduced rationals in [0,1], no default. H = L is not near; H < L or E outside [L,H] is ineligible. Alternative: level-based tolerance (future label).
- **DP-B10**: latest_observed_member_event_ns is the maximum endpoint-price event time when all members are determined, or the maximum if it equals C-1 (saturation, coverage 1/1), else null (multi-venue D08).
- **DP-B11**: Empty selected population (N = 0): every output null, not_applicable, empty_universe, expected = observed = 0.
- **DP-B12**: Evaluation point is C; membership is start <= C < end; facts are as of C (effective_start < C, known_at <= K); no backfill and no cross-evaluation state. First entry contributes with its as-of facts. Reset is a new request and session. A correction is a new snapshot id; one batch never holds two revisions; no arbitration.
- **DP-B13**: Non-price quantities (volume, return, momentum) travel in the REFERENCE price column; all roles of a request share one PriceUnit; the scale is unused for them.
- **DP-B14**: Each role holds at most 4096 rows.
- **DP-B15**: Units members, ratio, shares, fraction, utc_ns; members and ratio are new to the ledger, utc_ns is already applied by the EF1 amendment.
- **DP-O1**: The observed profile is a separate producer with its own identity and names breadth.observed.*; the roster defines the population; there is no expected population, and observed records can never feed the declared producer.
- **DP-O2**: A member qualifies iff price >= floor_price and volume >= floor_volume (both inclusive, caller floors, no default); a known failure decides without the other input.
- **DP-O3**: advancing = qualifies and change > 0; advance_fraction = advancing/qualifying; qualifying_fraction = qualifying/observed.
- **DP-O4**: Group scope is configuration: one result per group label, label carried in the roster row text; ungrouped records belong to the cohort scope only.
- **DP-O5**: Empty observed scope: counts are available zeros, fractions zero_denominator (an observed zero is an observation).
- **DP-O6**: unknown_member_count is always available when the roster is.
- **DP-A1**: The raw rate is a supplied exact rational in shares per second. Baseline: B_1 = r_1; B_k = (tau*B_{k-1} + d_k*r_k)/(tau + d_k), d_k the elapsed ns; alpha = d/(tau+d) (rational, no exponential). Alternatives: exponential decay, fixed-count EMA.
- **DP-A2**: Warm-up W observations; baseline_available = n >= W; an observation is scorable when k >= W+1.
- **DP-A3**: Relative rate rho_k = r_k/B_{k-1}; B_{k-1} = 0 makes that observation unscorable (counts exposed); alternative: any zero baseline makes the peak null.
- **DP-A4**: Relative acceleration u_k = (r_k - r_{k-1}) * 10^9/(d_k * B_{k-1}) in 1/s, defined for d_k > 0 and B_{k-1} > 0.
- **DP-A5**: Equal timestamps are allowed (ordered by sequence); alpha = 0, acceleration undefined. Alternative: reject equal times.
- **DP-A6**: Peaks are maxima over scored observations; ties resolve to the earliest; the witness is that observation event time.
- **DP-A7**: Scope is observations with t < C; all must be known (known_at <= K) and have a rate; a null rate is null_field for the rate outputs; later rows are ignored whatever their state.
- **DP-A8**: Per-epoch reset; no state capability in v1 (update, restore and merge unsupported); output is a pure function of the prefix.
- **DP-A9**: F0721 is the I/O grouping of the produced headers (not a header); the summary is as of C. F0700 and F0701 are the supplied identity and event clock.
- **DP-A10**: Only F0699 is mapped (baseline_available); F0690, F0692 and F0694 to F0698 are unmapped.
- **DP-N1**: Numeric policy: integers exact; declared and observed floats are a single correctly rounded division of exact integers (bit exact); adaptive floats are the single rounding of the exact rational with R17 acceptance max(8 ulp, 1e-12*|r|), +0.0 required where exact zero is argued.

## Rulings on the former open questions

- **Q1**: The adaptive_volume family is defined generically by this contract and claims no equivalence with the audit opaque rows. F0690, F0692 and F0694 to F0698 are recorded as unmapped (open audit item, not a gate for this contract); F0699 is mapped to baseline_available.
- **Q2**: No generic peak over the #490 relative-volume operand in v1 (a later amendment).
- **Q3**: VWAP is supplied as an exact notional/volume pair; a float64 VWAP is not accepted.
- **Q4**: The supplier may declare a prior reference or a VWAP unavailable (explicit missing, coverage stated); it is never inferred.
- **Q5**: Role row bound 4096, as the R17 bound (integer(count, 1, 4096) in packages/intraday/src/equity_features_intraday/_context.py).
- **Q6**: Non-price quantities (volume, return, momentum, rate) travel in the REFERENCE price column as the integer-coefficient carrier convention of the EF1/EF2 REFERENCE rows, unit taken from the role declaration. Checked in packages/contracts validation.py and inputs.py: the REFERENCE branch of validate_batch checks only identity uniqueness, (effective_start_ns, reference_id) order, interval bounds and positive rational factors; the negative-quantity check names only the size, bid_size, ask_size, volume and trade_count columns, so the price column accepts signed and zero values (the library adds its own BOUNDS for negative volume); CanonicalBatch requires a price_unit when a price column exists, so all roles share one PriceUnit.
- **Q7**: Adaptive seed (first observation), window convention (the supplied rate is taken as given; its window belongs to #513/#492) and session summary final when the market cutoff is reached, as proposed.
- **Q8**: Observed group scope stays a config parameter (one result per group label).
- **Q9**: Cite contract E sections by name (population kind ef3.population.member and the duplicate-identity rule); cohort normalization cites the same text.
- **Q10**: New units members (exists in the breadth catalog, new to the header ledger), ratio, shares/s and 1/s are accepted as additive, applied by the sibling amendment; the 33 headers are listed in the contract.
- **Q11**: Other open items, coordinator-decided as the most conservative option: update, restore, merge unsupported; reset epoch mode only; the summary is a pure function of the prefix; no defaults for tolerances, floors, tau, W or windows; no partial or lower-bound counts.

## Appendix: the 33 headers for the sibling amendment

To be applied additively by a sibling producer-set and header-ledger amendment (new units `members`, `ratio`, `shares/s`, `1/s`): the three tables under Outputs and headers list all 33 (16 + 7 + 10). Reset is epoch mode only; there are no defaults for tolerances, floors, tau, W or windows.

## Coordinator freeze

Per the coordinator, this contract is frozen as `ef3-breadth1` (config identity `ef3.session_breadth`), `ef3-obsbreadth1` (`ef3.observed_breadth`) and `ef3-adaptive1` (`ef3.adaptive_volume`), version 1, for implementation once this PR merges. This statement is the coordinator's; the author makes no acceptance claim, and numerical, artifact and release gates remain.

## What was not verified

Not verified: no canonical packet expansion, config digest, worker admission or wire encoding was run; the library was not executed; shared-validator behavior was read from source, not run. Hand-typed expectations agree with the scratch evaluator on all asserted cells; the remaining output cells are evaluator-derived. Contract E was read from its branch, not merged.
