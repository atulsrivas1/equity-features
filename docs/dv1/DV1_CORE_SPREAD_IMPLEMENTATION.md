# DV1-3 library: core spread (implementation notes)

Status: library implementation of the draft contract `dv1-definition-variants-1` for `core.benchmark_return_range_fraction` and
`core.benchmark_return_stdev_fraction`. Internal, synthetic, pre-release. Nothing here claims real-data readiness; every MATCH
means a library calculation on synthetic data. No performance claim.

## Where it lives

`packages/features/src/equity_features/dv1/_core_spread.py` (additive; the default registry, the shipped
`core.benchmark_return_dispersion_fraction` of the EF4 `relative_excess` producer and every EF1 to EF5 module and frozen
contract file are unchanged). Public surface: `build_core_spread_config`, `decode_core_spread_config`,
`compute_core_spread`, and the shared `compute_dv1`, `dv1_definitions`, `require_dv1_capability`. Identity
`dv1.core_spread`, algorithm `dv1-core-spread-v1`, policy label `dv1-core1`. The leg-fact admission (`ef4._legs`) and the
result assembly (`ef4._proj_common`) are the EF4 helpers, imported not copied. Batch capability only (update, restore and
merge are `UNSUPPORTED_CAPABILITY`). One nullable REFERENCE role named `legs` (fact kinds `ef4.leg.start`, `ef4.leg.end`),
passed as a one-element sequence.

Shared edits are minimal: `compute_dv1(batches, grid, config, *, features, entity=None)` takes an optional result entity
and the grid argument may be `None`; the core spread has no daily grid, so the three grid producers refuse a missing grid
with `INVALID_CONFIG`. `dv1_definitions(grid, config)` accepts `None` for the same reason.

## Convention as implemented

- Return of fund k: `r_k = E_k / S_k - 1` from exact integer witnesses (`Fraction`). Range = `max r - min r`, one correctly
  rounded float64 (the value the deprecated EF4 id publishes). Standard deviation = POPULATION standard deviation, divisor K
  (K the number of declared funds): variance `(K sum r^2 - (sum r)^2) / K^2` as an exact rational; an exact zero is `+0.0`;
  the root is exact when the reduced numerator and denominator are both perfect squares, else a Decimal120 square root
  rounded once to float64.
- Profiles `prior_close`, `window_start` (the EF4 rules, unchanged) and `regular_open`: the start leg is the open of the
  regular-session DAILY BAR of the exact session (operand label `daily_bar_open`), the end leg the close of the same session,
  `window_ns` absent. A start leg of any other operand label, of another session or of another profile does not count.
- Eligibility per fund (EF4 I2): start and end facts present and known (original `known_at` not null and at most K), end not
  after the market cutoff, endpoint age within `max_endpoint_age_ns`, one action snapshot on both legs. A fund that fails
  leaves the population partial: `partial_universe`, expected K, observed eligible funds, BOTH values withheld, never zero.
  Funds that are individually eligible but whose end times differ by more than the tolerance, or that sit on different
  sessions (or, for `window_start`, start times beyond the tolerance), make the whole population `ineligible`
  (expected K, observed K). No leg facts delivered at all is `absent_input` (expected K, observed 0).
- Config: policy_version, core_benchmark_ids (2..16 distinct), core_profile, alignment_tolerance_ns, max_endpoint_age_ns,
  window_ns (exactly when `window_start`), evidence_limit; no defaults. Check order: shape, typed inputs, currency (three
  uppercase letters, else `INVALID_UNIT`), labels, cutoff (`BOUNDS` when before the target session open), policy label
  (`INCOMPATIBLE_VERSION`), identity. There is no adjustment pair check because this producer has no adjustment basis
  (contract erratum); the config carries the default `AdjustmentSpec` and the batch adjustment is not compared.
- Refusal stages in compute: wire and shared admission of the leg facts, config shape, selected features, batch metadata
  (unit, order, namespace, coverage), policy label, result entity, identity (undeclared fund, duplicate key), data (a start
  witness not before its end witness).
- Evidence: for an available output, the legs of the funds in declared order, start then end, row id `slot:<index>` (fund k
  start is slot 2k, its end slot 2k + 1) bound to the role input id; `evidence_limit` truncates the combined list across the
  selected outputs (outputs in lexical order, so a joint call cuts mid-list), never the value; unavailable outputs emit none.
- Units: `fraction`, dtype float64 for both outputs. The discovery descriptions name the convention (RANGE, POPULATION
  standard deviation, operand `daily_bar_open`).

## Gate

`tools/verify_dv1_core_spread_library.py` runs all 21 core-spread result fixtures (CS01..CS21), each output alone and both
together, and the 16 refusals whose base is a core-spread fixture (8 codes) plus the contract's lower-case-currency mutation
(RF22) on a core base, and compares the float64 hex string and bit pattern with the contract literal. There is no tolerance
band and no expectation is derived from the library. The contract literal names a witness `slot:<index>` (fund k start 2k, end 2k + 1); the gate
compares it directly and fails on any other form, including the former `leg:` form (no name map). It checks that
each recorded rival (range for stdev, stdev for range, first-trade, first-bar and prior-close operands) differs from the
library value, that both outputs have a wrong-convention fixture, and that the shipped EF4
`core.benchmark_return_dispersion_fraction`, run through its own public path on the CS01, CS06 and CS07 inputs, publishes
the same bits as the DV1 range output (the deprecation is by the EF4 erratum only, no EF4 file is edited).

## Contract points decided here (flagged to the PO)

1. Operand label wire form. The EF4 leg text grammar is closed (`profile`, optional `slot`, `rev`, `act`) and has no operand.
   The DV1 text adds an optional `op` token after the profile and slot (`profile=regular_open;slot=A;op=daily_bar_open;rev=...;act=...`).
   A `regular_open` start whose operand label is absent or not exactly `daily_bar_open` is not eligible (CS09 first trade
   price, partial universe). The `op` token is ignored for the other two profiles.
2. Evidence names. The fixtures write the declared-order ordinal `slot:<index>` (fund k start 2k, end 2k + 1), the PO convention;
   the former `leg:<fund>:<kind>` literals were renamed in DV1-5b and the gate name map was removed.
3. Currency and adjustment. The contract limits the unit and adjustment-pair config rule to producers with an adjustment basis;
   this producer checks only the currency form (the shared `check_currency` of `dv1/_config_check.py`, DV1-5a) and ignores the batch adjustment; `tools/verify_dv1_shared_checks.py` shows the result is identical whatever adjustment the legs batch declares. Its compute path defers the policy-label refusal until after the input unit checks (the EF4 order); its config builder checks the cutoff before the label like the other producers.
4. Cutoff. Only the lower bound (not before the target session open) is checked; the EOD case places the cutoff after the
   session close.
5. `regular_open` start-time alignment is not checked (the contract expander checks it for `window_start` only). The EF4
   producer's non-`prior_close` branch would check it; no fixture distinguishes the two.
6. Deprecation text. The contract asks for a description-only discovery change on the deprecated id; this story edits no EF4
   file, so the in-code discovery text of the old id is unchanged and the deprecation lives in the EF4 erratum.

## Reviewer follow-ups on #758 (documented, no new refusal)

- Batch adjustment. The EF4 `relative_excess` producer compares the legs batch adjustment with its config adjustment
  (`check_meta(adjustment=True)`); `dv1.core_spread` does not. The contract states that core_spread has no adjustment basis
  (config-checks sentence), that the output has no basis echo, and that the only adjustment rule is the action snapshot
  equal on both legs of a fund (`act`, enforced per fund). Every return here is `E / S - 1` of two legs of one fund, so a
  batch-level basis label cannot change a value unless the two legs of a fund disagree, and that case is the `act` mismatch
  (CS17, partial universe). Adding a batch-level refusal would invent a rule the contract does not state; if the PO wants the
  EF4 comparison, it is a contract decision (it would also need a basis in the config, which core_spread does not have).
- Target distinct from the funds. EF4 refuses a target instrument that is also a declared core fund. The contract states no
  such rule for core_spread (its result entity is only the result key, and the funds are the population), so none is enforced;
  a result entity equal to a declared fund is accepted. Recorded in DECISIONS.md.
- io and workers PRs must emit the `op` token on every start leg, with exactly one start fact per fund and profile (a second
  fact with the same instrument, kind, profile and slot is `DUPLICATE`), `op=daily_bar_open` on the regular_open start only
  when the official exact-session daily-bar open exists, and one end fact per fund.

## Not done here (cascade, reported not built)

The io adapter spec for `dv1.core_spread` must say: emit `op=daily_bar_open` on the regular_open start leg only when the source has the official exact-session daily-bar open, otherwise omit the leg (DV1-4 cascade). Leg text order is profile, slot, op, rev, act. Fixture witness names `leg:<fund>:<kind>` become ordinals in the DV1-5 closeout. The old id's discovery description changes in the DV1-4 bump.

io mapping for the `dv1.core_spread` leg facts (including the `op` token) and a workers family are separate PRs after merge.
