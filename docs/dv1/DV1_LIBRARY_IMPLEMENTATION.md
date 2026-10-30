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
to the role input id; the contract witness `<role>/slot:<index>` is that pair. Unavailable outputs emit none.

## Points settled by PO ruling (work/po-rulings-dv1-1-2026-10-29.md), now written in the contract

1. Market cutoff inside the target session; slot ending after it is `future_market`; a delivered row past it is `BOUNDS`.
2. `evidence_limit` bounds the combined evidence list across the selected outputs (lexical order); fixture RL20 pins a joint
   call that cuts mid-list (`joint_evidence`).
3. Row id `slot:<index>` bound to the role input id; contract witnesses are written `<role>/slot:<index>`.
4. `forming` is fixture notation only (the row is not delivered); the gate fails if a forming slot is delivered and checks that
   the library refuses a forced delivery as `BOUNDS`.
5. No version bump: the registry and catalog are unchanged; the coordinated bump (features a6 to a7) belongs to DV1-4. The
   ownership manifest is not touched (flipped for all 10 headers at the closeout).

## Review follow-ups (core #755 review)

- `evidence_limit` has no default: `build_relative_log_config` takes it as an optional-typed keyword that is validated like every
  other parameter, so an omitted value is `INVALID_CONFIG` (not 0).
- Refusal stage order follows the contract (wire, shared, config, version, identity, data): parameter type and bound checks
  and the unit, adjustment and cutoff checks come first, then the policy label (`INCOMPATIBLE_VERSION`), then the self-pair
  check (`INCONSISTENT_IDENTITY`).
- Joint-call `evidence_limit` (one bound over the combined list, outputs in lexical order) is a PO ruling now written in the
  contract and pinned by RL20; it is noted here for PO ratification before the contract is frozen.

## Alignment with the shared checks (DV1-5a)

`build_relative_log_config` now calls the shared `dv1/_config_check.py` (units and adjustment, labels, cutoff, policy label) and
admission calls its coverage check; the status mapping is the shared `dv1/_status.py`. Behaviour change recorded in DECISIONS.md first:

| Input | Before | After |
| --- | --- | --- |
| currency not three uppercase letters (RF22) | accepted | INVALID_UNIT |
| adjustment pair not raw/raw-v1 or split/split-factors-v1 (RF21) | accepted | UNSUPPORTED_ADJUSTMENT |
| rows with no per-slot coverage entry (RF11) | INCONSISTENT_IDENTITY (EF3 admission) | INVALID_SCHEMA |
| every existing fixture value, status, reason, witness | | bit for bit unchanged |

Stage order is the same as ATR and window: parameters, units and adjustment, labels and cutoff, policy label, identity (self-pair).
`tools/verify_dv1_shared_checks.py` runs every bad input against all four producers.
