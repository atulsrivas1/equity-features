# EF2 money flow

Use `build_money_flow_config`, `decode_money_flow_config`, `compute_money_flow`, `describe_money_flow`, `money_flow_catalog_digest` and `require_money_flow_capability` from `equity_features_intraday`. The context is the unchanged R17 `IntradayContext` and must be `reset` mode (carry is out of v1). Config identity is `ef2.money_flow`, algorithm `ef2-money-flow-v1`, schema `1`.

```python
from equity_features_intraday import (
    MONEY_FLOW_POLICY, build_money_flow_config, compute_money_flow, describe_money_flow)

config = build_money_flow_config(context, policy_version=MONEY_FLOW_POLICY, cmf_period=20,
                                 availability=availability, adjustment=adjustment,
                                 price_unit=price_unit, evidence_limit=8)
result = compute_money_flow(batches, context, config,
                            features=("intraday.ad_line", "intraday.cmf", "intraday.obv"))
```

Parameters are exactly `policy_version` (`ef2-mf1`; any other label is `INCOMPATIBLE_VERSION`, there is no default label), `evidence_limit` (0..10000), `cmf_period` (1..4096, no default, present exactly when `intraday.cmf` is selected) and the R17 context transport (`context_schema`, `context_sha256`, `context_chunks`, `context_000`...). `decode_money_flow_config(context, config)` validates the closed envelope and returns `MoneyFlowSettings(policy_version, cmf_period, evidence_limit)`.

`batches` is `None` (absent delivery) or a tuple of R17 BAR chunks on the governed grid with the R17 per-slot coverage, ordering, duplicate and cutoff rules; volume is an int64 share column of at least 0 in the config adjustment basis. OBV needs `close` and `volume`; A/D and CMF need `high`, `low`, `close` and `volume`. A zero-volume interval must have null OHLC (shared BAR rule). The result has one scalar per selected feature, in lexical order: `intraday.ad_line` (float64, `shares`), `intraday.cmf` (float64, `fraction`), `intraday.obv` (int64, `shares`), each with its own quality row, column algorithm `ef2-money-flow-v1`, backend `intraday.python` and the R17 input bindings `bars:000`.... Discovery (`describe_money_flow`) lists the three IDs with batch capability only; `require_money_flow_capability` refuses update, restore and merge with `UNSUPPORTED_CAPABILITY`. The R17 `describe_intraday` and its catalog digest are unchanged.

Typed refusals (no `FeatureResult`): `INVALID_ORDER`, `DUPLICATE`, `INVALID_SCHEMA` (non-positive or incoherent OHLC, zero volume with prices), `BOUNDS` (negative volume, bar past the cutoff), `INCONSISTENT_IDENTITY`, `INVALID_UNIT`, `UNSUPPORTED_ADJUSTMENT`, `INVALID_CONFIG` (period, evidence limit, carry mode, missing or surplus `cmf_period`), `INCOMPATIBLE_VERSION`, `UNKNOWN_FEATURE` and `OVERFLOW` for a published OBV outside int64 (the whole request, only when `intraday.obv` is selected). See [mathematics, readiness and open points](../ef2/MONEYFLOW_RETRACEMENT_IMPLEMENTATION.md) and the [frozen contract](../ef2/MONEYFLOW_RETRACEMENT_CONTRACT_PROPOSAL.md).
