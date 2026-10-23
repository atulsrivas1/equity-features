# EF4 anchored VWAP path

Use `build_vwap_path_config`, `decode_vwap_path_config`, `compute_vwap_path` (or the closed `compute_ef4`), `ef4_definitions` and `require_ef4_capability` from `equity_features.ef4`. Config identity is `ef4.vwap_path`, algorithm `ef4-vwap-path-v1`, schema `1`, policy `ef4-vwap1`.

```python
from equity_features.ef4 import VWAP_POLICY, build_vwap_path_config, compute_vwap_path

config = build_vwap_path_config(policy_version=VWAP_POLICY, series_source="bar", grid_version="grid-5s",
                                session=target_session, availability=availability, adjustment=adjustment,
                                price_unit=price_unit, evidence_limit=25)
result = compute_vwap_path((bounds, grid, None, bars, None), config, entity=entity,
                           features=("vwap.path.last", "vwap.slope.ols"))
```

Outputs (lexical): `vwap.path.change_bps` (`bps`), `vwap.path.last`, `vwap.path.maximum`, `vwap.path.minimum` (`currency/share`), `vwap.path.point_count` (`points`), `vwap.slope.endpoint` and `vwap.slope.ols` (`currency/share/second`).

Parameters (no defaults): `policy_version`, `series_source` (`trade`, `bar` or `prepared_window`), `grid_version` (exactly when the source is `bar` or `prepared_window`, equal to the grid role text), `series_policy_id` (exactly when the source is `prepared_window`, equal to the proof fact text) and `evidence_limit` (0..10000). The five role slots are `bounds` (exactly one `ef4.interval.bounds` fact; its start is the anchor S), and the nullable `grid` (B+1 `ef4.window.edge` facts, absolute and strictly increasing, first S, last E), `trades` (trade source only), `bars` (one BAR row per grid slot with volume and `actual_notional`; a slot may be declared incomplete by a per-slot `IntervalCoverage` entry equal to the slot) and `proof` (prepared source only: exactly one `ef4.series.proof` fact with bounds `[S, E)`).

The path is the anchored cumulative VWAP `W_k = sum(N_i) / sum(V_i)` over the first k points (reset at S, no carry): a point is an eligible trade `(event_ns, price size, size)` or a positive-volume window `(end_ns, actual_notional, volume)` (never close times volume; a covered zero-volume window contributes nothing and its knowledge and notional are not read). A prepared series is accepted exactly as supplied when its proof, grid, anchor, unit and basis bind; trades are never read. Time is UTC nanoseconds; slopes are per second (exact factor 10^9): the endpoint slope `(W_n - W_1) / (x_n - x_1)` and the equal-weight OLS slope of `W_k` on `x_k` (no resampling). `n = 0` is `no_eligible_observations` (`point_count` 0 is a value), `n = 1` is `insufficient_history` for change and both slopes, a zero span or variance is `zero_denominator`. A slot with no row is `governed_gap` (declared incomplete) or `absent_input` and blocks every output; for bar sources the interval end after the market cutoff is a `BOUNDS` refusal. Evidence: every contributing point in order (maximum and minimum: the points through the earliest selecting one). See [the implementation notes](../ef4/QUOTE_VWAP_IMPLEMENTATION.md). Batch only; update, restore and merge are `UNSUPPORTED_CAPABILITY`.
