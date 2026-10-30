# DV1-6 library: window extremes with the date of the extreme (implementation notes)

Status: library implementation of the draft contract `dv1-definition-variants-1` for `history.window_high`,
`history.window_low`, `history.window_high_offset` and `history.window_low_offset`. Internal, synthetic, pre-release.
Nothing here claims real-data readiness; every MATCH means a library calculation on synthetic data. No performance claim.

## Where it lives

`packages/features/src/equity_features/dv1/` (additive; the default registry, EF1 to EF5 modules and every frozen contract
file are unchanged). Public surface: `build_window_extreme_config`, `decode_window_extreme_config`,
`compute_window_extreme`, `compute_dv1`, `dv1_definitions`, `require_dv1_capability`. Identity `dv1.window_extreme`,
algorithm `dv1-window-extreme-v1`, policy label `dv1-wext1`. The daily grid and the structural BAR admission are the EF3
helpers (`equity_features.ef3._common`), imported not copied; the field values are read from the admitted batch because the
EF3 admission is close-only. Batch capability only (update, restore and merge are `UNSUPPORTED_CAPABILITY`). One nullable
role, `daily`.

## Conventions as implemented

- Window: the `period` (1..4096, explicit, no default; 252 or 253 is the consumer's choice) most recent sessions ending at
  and including the target. A window that begins before the first grid session is `insufficient_history`.
- `extreme_basis` (explicit `intraday` or `close`, no default; `high`, `open` and a missing value are `INVALID_CONFIG`):
  intraday reads the daily high for the high outputs and the daily low for the low outputs; close reads the close for all.
- Comparison is exact on the integer price coefficients; the latest session wins every tie (smallest offset). A price is
  one correctly rounded float64 of `coefficient / 10^scale` (`float(Fraction)`). An offset is the exact int64 count of
  sessions before the target (0 is the target), unit `sessions`.
- Readiness is per output field: a null, unknown, future-known, gapped or absent slot for the field makes that field's two
  outputs unavailable and leaves the other field's outputs available (WX20); the close basis ignores null high and low (WX21).
  Reason precedence is the contract's eleven-entry list; a slot ending after the market cutoff is `future_market`.
- Quality: expected = `period`, observed = READY slots of the window for the output's field; an available row has both equal
  to `period`. Evidence: the consumed rows of the window, target first then ascending, row id `slot:<index>` bound to the
  daily input id; unavailable outputs emit none.
- `history.prior_high` and `history.prior_low` (target excluded) are not touched.

## Gate

`tools/verify_dv1_window_library.py` expands the 25 window fixtures and 10 window refusals from
`docs/dv1/DEFINITION_VARIANTS_CONTRACT_PROPOSAL.json`, runs every output alone and all four jointly (125 runs), and compares
the float64 hex and bit pattern of each price and the exact integer of each offset with the contract literal, with
status, reasons, counts, witnesses, dtype, unit and basis echo. No tolerance. The recorded wrong-convention rivals must differ
from the library value, and each recorded cross-check (prior period) is re-run through the library on the prefix ending one
session before the target: `max(prior extreme, target field)` equals the window extreme bit for bit.

## Alignment with DV1-1 and open point

- Same behaviour as `dv1.relative_log_stats`: `evidence_limit` is validated like the other parameters and omitting it is
  `INVALID_CONFIG` (no default); refusal stages run config checks (parameters, units, cutoff), then version (policy label),
  then identity; evidence rows are `slot:<index>`; a cutoff inside the target session gives `future_market`; in a joint call
  `evidence_limit` caps the combined list. The reason precedence and status mapping are the shared `dv1/_status.py` (DV1-5a), imported by every daily-grid producer; the config checks are the shared `dv1/_config_check.py`.
- Ratified by the PO: `offset_unit` is a required explicit build argument that must equal `sessions` (so RF72 is
  exercisable; RF71 is `sessions` as the price currency). Alternative: a constant, with RF72 then not exercisable.
- No version bump: the registry and catalog are unchanged; the coordinated bump (features a6 to a7) belongs to DV1-4.
- Shared DV1 rules (PO ruling 2026-10-29): the config checks run in the order parameters, currency (three uppercase letters, else
  `INVALID_UNIT`), adjustment pair (`unadjusted`/`raw-v1` or `split_adjusted`/`split-factors-v1`, else `UNSUPPORTED_ADJUSTMENT`),
  `offset_unit`, cutoff, policy label, identity. Rows with no coverage entry are `INVALID_SCHEMA`; coverage declared for only some
  delivered slots is `INCONSISTENT_IDENTITY`. The gate runs RF11, RF21 and RF22 (recorded on the ATR base) and RF73 against this producer.
- Gap: no short-history fixture other than WX15 (all slots ready) pins `observed` when an existing slot is also lost.
