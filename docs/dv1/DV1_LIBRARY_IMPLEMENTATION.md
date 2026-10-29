# DV1-1 library: log-return beta and correlation (implementation notes)

Status: library implementation of the draft contract `dv1-definition-variants-1` for `relative.log_return_beta` and
`relative.log_return_correlation`. Internal, synthetic, pre-release. Nothing here claims real-data readiness; every MATCH
means a library calculation on synthetic data. No performance claim.

## Where it lives

`packages/features/src/equity_features/dv1/` (additive; the default registry, EF1 to EF5 modules and every frozen contract
file are unchanged). Public surface: `build_relative_log_config`, `decode_relative_log_config`, `compute_relative_log`,
`compute_dv1`, `dv1_definitions`, `require_dv1_capability`. Identity `dv1.relative_log_stats`, algorithm
`dv1-relative-log-stats-v1`, policy label `dv1-rlog1`. The daily grid, close-only BAR admission and shared slot causes are
the EF3 helpers (`equity_features.ef3._common`), imported not copied. Batch capability only (update, restore and merge are
`UNSUPPORTED_CAPABILITY`).

## Numeric policy as implemented

- Each logarithm is `ln(Decimal(C_j) / Decimal(C_(j-1)))` at 120 significant digits, half-even (the primitive of `ef3-dlv1`).
- Means and centred sums are two-pass in Decimal120; `beta = Sxy / Syy`, `rho = Sxy / sqrt(Sxx Syy)`; each published value is
  one correctly rounded float64 (`float(Decimal)`); an exact Decimal zero is published as `+0.0`.
- Zero tests are exact integer comparisons of the close ratios (cross multiplication), never a Decimal variance: benchmark
  ratios all equal gives `zero_denominator` for both outputs; instrument ratios all equal (benchmark not) gives beta exactly
  `+0.0` and correlation `zero_denominator`. A covariance that is zero in rational terms but not detectable from ratios is
  published as computed (the contract's 1e-100 rule); no epsilon anywhere.
- Gate: `tools/verify_dv1_library.py` compares the float64 hex string and bit pattern of every value with the contract
  literal. There is no tolerance band.

## Quality and evidence as implemented

Window slots are the target and the `window` slots before it (pairs `lo+1..t`). Available rows publish expected = observed
= n valid pairs and keep lost-pair causes as reasons; unavailable rows publish expected = window and observed = n. Reason
precedence is the contract's eleven-entry list. A slot that ends after the market cutoff (a target still forming) is the
cause `future_market` (a delivered row beyond the cutoff stays a `BOUNDS` refusal); the envelope therefore accepts a market
cutoff from the target session open to the last grid session close (EF3 requires the completed target). Evidence rows are the
consumed close rows of the used slots, target first then ascending, instrument before benchmark, row id `slot:<index>` bound
to the role input id; the contract witness `inst:<k>` / `bench:<k>` is that pair. Unavailable outputs emit none.

## Points where the contract was silent (decided here, flagged to the PO)

1. Joint calls: `evidence_limit` bounds the whole evidence list of a result (as `ef3-rel1` and EF5), so a call selecting both
   outputs truncates the concatenated list; single-output calls match the per-output witnesses. The gate pins this.
2. Row id vocabulary: `slot:<index>` (EF3 convention) with the role in the input id, instead of the literal `inst:<k>`.
3. A `forming` slot is delivered by neither series in the gate (the market cutoff is the end of the last delivered slot).
4. No version bump: the registry and catalog are unchanged; the coordinated bump (features a6 to a7) belongs to DV1-4.
