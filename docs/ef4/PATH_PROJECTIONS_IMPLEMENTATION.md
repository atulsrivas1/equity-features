# EF4 equity statistical projections implementation

[EQ-172 #513](https://github.com/atulsrivas1/equity-features/issues/513) library layer: the pure `ef4.session_projection` (7 `projection.*` session outputs), `ef4.bar_projection` (6 `projection.*` bar outputs), `ef4.relative_excess` (6 `relative.session.*` excess outputs and 2 `core.benchmark_*` outputs) and `ef4.rate_projection` (5 `rate.window.*` outputs) producers, 26 outputs in all, in `packages/features` (module `equity_features.ef4`, next to the EF4 tape producers). The frozen [contract](PATH_PROJECTIONS_CONTRACT_PROPOSAL.md) (policy labels `ef4-proj1`, `ef4-rel1`, `ef4-rate1`, decisions DP-J*, rulings OQ-J* and its coordinator freeze) governs; this slice implements it and redefines nothing. The EF4 I/O mapping (#613), worker (#614) and release acceptance (EQ-163) layers remain separate. The path-efficiency sibling (EQ-161, contract I1) is a separate library.

## Structure

`packages/features/src/equity_features/ef4/`: `_proj_common` (feature selection, canonical decimal and token grammar, REFERENCE row admission, metadata discipline, result assembly with result-wide evidence), `_legs` (the `ef4.leg.start|end` facts shared by two producers), `_session_projection`, `_bar_projection` (with the local `BarGrid` codec), `_relative_excess`, `_rate_projection`, and the own catalog `_path_projections_definitions` (`ef4_path_projections_definitions`, `require_ef4_path_projections_capability`) and `_path_projections_dispatch` (`compute_ef4_path_projections`, routed by the config identity). It reuses the EF3 daily-grid and robust helpers (`DailyGrid`, `admit_role`, `envelope`, `make_config`, `parameter_map`, `check_policy`, `first_status`, `to_float`) unchanged; `ef4/__init__.py` only gains an appended import and `__all__` block. The R17 catalog, `describe_intraday()` and every catalog digest, the shared validators, the default registry and every EF1/EF2/EF3/EF4-tape output are unchanged; no package version is bumped.

## Public surface

Per producer: `build_*_config` (explicit keyword parameters with no default, including `evidence_limit`; a mandatory `PriceUnit`), `decode_*_config` (closed envelope, byte-identical rebuild) and `compute_*`. Session and bar projections take their grid (`DailyGrid`, `BarGrid`); relative excess and rate projection take the result `entity` and fixed nullable role slots (`legs`, `membership`; `tape`, `legs`). Optional parameters are present exactly when their outputs are selected (benchmark ids, `window_ns`, `core_benchmark_ids`/`core_profile`; `alignment_tolerance_ns`, `adjacency`); the check runs at compute because the selection is a compute argument. Roles no selected output needs are neither examined nor bound.

## Rulings and choices beyond the contract text

1. **Bar grid.** The contract names an R17 chunked BAR delivery; the library has no R17 dependency, so `BarGrid` (instrument, reset-epoch session, fixed `bar_ns`, `bar_count`, `target_index`; digest in the config like the EF3 daily grid) is a local codec. Per-slot coverage entries are named `bar:<i>`. One batch per role: chunks are concatenated by the I/O layer. Cutoff must lie between the target bar end and the session close; rows after the target are admitted but never read (prefix property).
2. **Daily role.** The role is a close-only BAR batch (as EF3). Because the BAR validator keys rows by interval, an extra check refuses two rows with one (instrument, session) as `DUPLICATE` (contract SPR12).
3. **Config scalars.** `Parameter` values are scalars, so `core_benchmark_ids` is a canonical compact JSON array text (`encode_core_ids`); `evidence_limit` has no default (stricter than EF3 builders).
4. **Leg text.** Ordered closed grammar `profile=..[;slot=..];rev=..;act=..` (start) and `[slot=..;]rev=..;act=..` (end), tokens printable ASCII without `;` and `=`. Relative excess admits slot A only (omitted means A) and any of the three profiles; rate projection admits slots A/B and profile `window_start` only. A leg has no effective end and a positive price (null price is `INVALID_SCHEMA`, not `null_field`).
5. **Reference ids** are checked only for the `x1:B(..)` grammar; identity uses the fields: a second leg with the same (instrument, kind, profile, slot), a second membership or a second tape fact of one kind is `DUPLICATE` at the identity tier even with a distinct reference id.
6. **Tape facts.** `effective_end_ns` must be non-null, price null, instrument and session the target's, text a canonical decimal (`count`/`volume` at most 2^63-1, `notional` below 10^38, else `OVERFLOW`). A batch carrying `ef4.tape.notional` must declare the config `PriceUnit`; a count/volume-only batch is not unit compared. Basis is compared for tape and legs, not for the membership batch.
7. **Evidence.** Boundary `ordinary` for REFERENCE witnesses (the shared validator admits `completed_interval` only for BAR/DAILY), `completed_interval` for slots and bars. Event times: leg time, membership effective-from, tape window end. Evidence is for available outputs only and the cap is result-wide (a joint selection truncates in lexical output order; the fixtures with a small limit select one output).
8. **Absent notional column.** When the `actual_notional` column (or the whole role) is absent every dollar output is `absent_input` with observed 0, replacing other causes, as fixture BP07 pins.
9. **Overflow** of a published int64 or decimal128 sum is raised only when that output would be available.
10. **Refusal tiers.** For every present batch the shared `validate_batch` runs before the slot-kind check and before config decoding; then config (parameters, ranges, selection, unit, basis, capability, feature ids), version (checked after those, so a wrong label is reported only when the rest of the config tier passes), identity (including self-benchmark, undeclared instrument, duplicates) and data (leg start not before end, checked sums). Unknown feature ids are `UNKNOWN_FEATURE` even when the list is longer than the producer's output set.
11. **Self and shared benchmarks.** A benchmark (or core member) equal to the target instrument, and two roles bound to one instrument, are `INCONSISTENT_IDENTITY`; the builder refuses the latter, the compute call the former.

## Mathematics and numeric policy

Exact `int`/`Fraction` arithmetic everywhere; one correctly rounded float64 per published value (`to_float`, exact zero is `+0.0`); no logarithm or square root. Returns are `E / S - 1` from the witnesses; the excess is the arithmetic spread; the SMA comparison is `N C_t / S - 1` with strict `N C_t > S`; drawdown, max drawdown (running peak) and distance from low use the N closes; rates divide by `window_ns / 1e9`; the rate difference is `r_A/s - r_B/s`.

## Author source validation

A standalone manual script (not committed, no test files) expanded the compact notation of all 111 result fixtures into canonical packets (daily BAR, epoch BAR, REFERENCE legs, membership and tape) and ran every output (340 outputs, 1360 cells) under two id bindings (all instrument, benchmark and session ids renamed) and both availability modes (`known_at` and `reconstruction`), comparing status, reasons, expected, observed, value per the fixture acceptance rule (`exact_float64` and `exact_plus_zero` bit for bit, `tolerance` within `max(8 ulp, 1e-12 |r|)`, integers and booleans exactly, decimal128 as the coefficient) and the witness lists (single-output runs where the fixture limit truncates). Each valid config was also rebuilt through its builder and compared with the manual envelope. All 114 refusal recipes were applied to their base fixtures (and run under both bindings) and each raised exactly the recorded code. A negative control (three deliberately altered expectations) fails as expected. Before/after snapshots of the intraday, money-flow, momentum, channels and realized-variance catalog digests and the builtin registry are identical. mypy was not available in the authoring environment, so strict typing is unchecked.

## Notes, risks and contract nits

1. The tape carrier is provisional (OQ-J2); the I/O mapping of contract G may change facts, not the mathematics.
2. The compact fixtures do not exercise `regular_open` start facts, `reconstruction` mode differences (checked here: none), slot B in relative excess, `price` null facts, or rational factor columns (refused).
3. Reference-id components and per-slot coverage names (`bar:<i>`, `slot:<i>`) are implementation-chosen and need pinning in the I/O mapping.
4. The session `up/down` closure and the other projections use independent closures; a gap at the base slot only blocks up/down (SP08), as written.
5. No cost measurement is made or claimed.

No acquisition, source rights, installed, cross-layer, performance or release claim follows from this source result.

## Rulings to pin in the EF4 shared amendment

1. REFERENCE evidence uses boundary `ordinary` (the contract's `completed_interval` is unimplementable for REFERENCE inputs under the shared result validator).
2. The daily role refuses two rows with one (instrument, session) as `DUPLICATE`, a library check on top of the BAR validator.
3. Relative excess admits slot A only (slot B is `INVALID_SCHEMA`); rate projection admits only `window_start` starts (a `prior_close` or `regular_open` start is `INVALID_SCHEMA`).
4. The bar grid is the local `BarGrid` codec with one batch per role: the I/O layer must concatenate R17 chunks and name per-slot coverage `bar:<i>`.
5. `core_benchmark_ids` is carried as canonical compact JSON text (scalar config parameters).

## Contract nits and review follow-ups

- Per-slot readiness keeps the EF3 `slot_reasons` precedent: a row that is both null and unknown/future reports both `null_field` and the knowledge reason (lexical order, status by precedence). Recorded as a contract nit.
- REFERENCE text-grammar (wire) faults are checked after the shared duplicate/order check, because the shared validator runs before the slot-kind check; a batch with both faults reports the shared one. Single-fault recipes are unaffected.
- Distinct input ids are enforced for the two REFERENCE roles of relative excess and rate projection (`DUPLICATE`).

