# EF2 retracement level

Use `build_retracement_config`, `decode_retracement_config`, `ef2_definitions`, `compute_retracement_level` and `compute_ef2` from `equity_features.ef2`. Config identity is `ef2.retracement_level`, algorithm `ef2-retracement-level-v1`, schema `1`; the window is target-only. A different direction or ratio is a different config and a different result.

```python
from equity_features.ef2 import RETRACEMENT_POLICY, build_retracement_config, compute_ef2

config = build_retracement_config(policy_version=RETRACEMENT_POLICY, direction="from_high",
                                  ratio_num=309, ratio_den=500, session=session,
                                  availability=availability, adjustment=adjustment,
                                  price_unit=price_unit, evidence_limit=2)
result = compute_ef2((prior_high, prior_low), config, entity=entity)
assert result.values[0].feature_id == "retracement.level"
```

Parameters are exactly `policy_version` (`ef2-retrace1`; another label is `INCOMPATIBLE_VERSION`), `direction` (`from_high` or `from_low`), `ratio_num`, `ratio_den` and `evidence_limit` (0..10000). The ratio is a reduced exact integer pair with `0 <= num <= den`, `den` in `1..2^63-1`, zero only as `0/1` and one only as `1/1`; floats, bools, text, a missing ratio and extension ratios above 1 are `INVALID_CONFIG`; there is no default ratio. A `PriceUnit` is mandatory and equals both extremum batches, as does the adjustment basis.

The concrete tuple/list has exactly two nullable positional slots `prior_high`, `prior_low`, both REFERENCE batches with at most one row. The row carries `reference_id = x1:B(window_set_id)` (reversible unpadded base64url of UTF8, identical on both roles), `fact_kind` `ef2.extremum.high` or `ef2.extremum.low`, `text` equal to the batch `source.snapshot_id`, the exact integer `price` coefficient at the config scale (never a rounded float64), `factor_num`/`factor_den` (observed slots and required window length of the upstream extremum, all-or-none, equal on a priced row, `factor_den` equal on both roles), the evidence-only `effective_start_ns`/`effective_end_ns` and a causal `known_at_ns`. A null price with `1 <= factor_num < factor_den` is the upstream shortfall (`insufficient_history`); a zero-observed shortfall carries no factors (`null_field`).

The result is one float64 `retracement.level` (`currency/share`), `level = (H - r*(H-L))/10^scale` for `from_high` and `(L + r*(H-L))/10^scale` for `from_low`, computed exactly and rounded once. `H = L` is `not_applicable/zero_denominator`, `H < L` or a non-positive coefficient is `ineligible`; expected is 2 and observed counts the causal, complete sides with a positive price. Witnesses (available only) are the `prior_high` then `prior_low` rows with boundary `ordinary`, bounded by `evidence_limit`. Input bindings are the present roles in lexical order. `ef2_definitions(config)` describes the producer (batch capability only; `require_ef2_capability` refuses update, restore and merge). Refusals use the typed codes of the [contract](../ef2/MONEYFLOW_RETRACEMENT_CONTRACT_PROPOSAL.md); see [mathematics, readiness and open points](../ef2/MONEYFLOW_RETRACEMENT_IMPLEMENTATION.md).
