# DV1-2 library: simple-mean ATR (implementation notes)

Status: library implementation of the draft contract `dv1-definition-variants-1` for `history.atr_simple_mean`.
Internal, synthetic, pre-release. Nothing here claims real-data readiness; every MATCH means a library calculation on
synthetic data. No performance claim.

## Where it lives

`packages/features/src/equity_features/dv1/_atr_simple_mean.py` (additive; the default registry, the shipped
`history.atr` and every EF1 to EF5 module and frozen contract file are unchanged). Public surface:
`build_atr_simple_mean_config`, `decode_atr_simple_mean_config`, `compute_atr_simple_mean`, and the shared
`compute_dv1`, `dv1_definitions`, `require_dv1_capability`. Identity `dv1.atr_simple_mean`, algorithm
`dv1-atr-simple-mean-v1`, policy label `dv1-atrs1`. The daily grid and the high/low/close BAR admission are the EF3
helpers (`equity_features.ef3._common`), imported not copied. Batch capability only (update, restore and merge are
`UNSUPPORTED_CAPABILITY`). One nullable role named `daily`, passed as a one-element sequence.

## Convention as implemented

- True range `TR_i = max(H_i - L_i, |H_i - C_(i-1)|, |L_i - C_(i-1)|)`. Value = the plain mean of the N true ranges of
  the N most recent completed sessions ending at AND INCLUDING the target (N + 1 closure slots: the oldest needs its close
  only, the target its high and low only, the middle slots high, low and close). Exact integer sum, one `Fraction`
  (`sum / (N * 10^scale)`), one correctly rounded float64; a zero mean is published as `+0.0` (available, never
  unavailable).
- No `initialization_anchor`, no inclusion parameter, no smoothing; the Wilder `history.atr` is untouched.
- Strict readiness: any closure slot that is not READY makes the output unavailable with its reasons; no skipping, no zero
  fill. Reason precedence is the contract's eleven-entry list; the status follows the first applicable reason.
- Counts: expected N + 1, observed READY closure slots (inside the grid). A target still forming at the market cutoff is
  `future_market` (the envelope accepts a cutoff from the target session open, as DV1-1); a bar delivered past the cutoff
  is still a `BOUNDS` refusal.
- Evidence: one row per closure slot, row id `slot:<index>` bound to the role input id; target first, then the remaining
  closure slots ascending; `evidence_limit` truncates the list, never the value; unavailable outputs emit none.
- Unit `<CCY>/share` (the string the shipped `history.atr` publishes), dtype float64; the declared adjustment basis is
  echoed in the input binding. The discovery description names the convention (SIMPLE mean, not the Wilder recursion).

## Gate

`tools/verify_dv1_atr_library.py` runs all 20 ATR result fixtures (AT01..AT20) and the 27 refusals whose base is an ATR
fixture (12 codes) and compares the float64 hex string and bit pattern with the contract literal. There is no tolerance
band and no expectation is derived from the library. It also checks that each recorded rival (Wilder, prior-only mean,
high-minus-low-only mean) differs from the library value (equal only for the two recorded coincidences AT02 and AT04),
and that the shipped Wilder `history.atr`, run through its own public path with the anchor at session 1, reproduces the
recorded Wilder rival.

## Contract points now settled by the erratum on main

Undeclared coverage is `INVALID_SCHEMA` and partial coverage `INCONSISTENT_IDENTITY` (RF11, RF73; the gate also runs RF73
against an ATR base, AT01), a short history counts the slots that exist as middle slots, and the compact row width is a
gate-decoder fixture-load error. The config checks run in the same order as the window-extreme producer (shape, typed
inputs, currency, adjustment pair, labels, cutoff, policy label). The currency (three uppercase letters) and adjustment
pair (`raw`/`raw-v1`, `split`/`split-factors-v1`) checks are one shared function (`dv1/_config_check.py`) called by this producer, the
window-extreme producer and DV1-1 (DV1-5a); the status resolution is one shared module (`dv1/_status.py`).
