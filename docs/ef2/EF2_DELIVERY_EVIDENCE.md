# EF2 delivery evidence (EQ-152 #486 package)

October 23, 2026. Evidence summary for the EF2 release (trends, momentum, money flow and channels). This is delivery evidence, not acceptance: EQ-152 #486 stays open until the owner accepts the release, and every decision recorded here is a coordinator decision, pending owner review.

## Scope delivered

| Contract | Stories | Producers and headers | Frozen contract |
| --- | --- | --- | --- |
| A: momentum and trend | EQ-147 #481, EQ-148 #482, EQ-149 #483 | `intraday.momentum.v1`: macd_line, macd_signal, macd_histogram, plus_di, minus_di, dx, adx, stoch_k, stoch_d, williams_r (10 float64) | `docs/ef2/MOMENTUM_TREND_CONTRACT_PROPOSAL.*` (#678) with Amendment 1 (#683) |
| B: money flow and retracement | EQ-150 #484, EQ-238 #663 | `ef2.money_flow`: intraday.obv (int64), ad_line, cmf (float64); `ef2.retracement_level`: retracement.level (float64) | `docs/ef2/MONEYFLOW_RETRACEMENT_CONTRACT_PROPOSAL.*` (#677) |
| C: Ichimoku and channels | EQ-151 #485, EQ-170 #511 | six producers, 25 headers under `trend.ichimoku.*` and `channel.*` | `docs/ef2/ICHIMOKU_CHANNELS_CONTRACT_PROPOSAL.*` (#679) |

Shared contract boundary: the additive producer-set and header-ledger amendment is `docs/ef2/PRODUCER_SET_AMENDMENT.*` (#685). The frozen `docs/ef1/CONTRACT.json` is unchanged. The EF2 catalogs are separate registries; `describe_intraday()` and its digest are unchanged.

## Layers merged

| Layer | Contract A | Contract B | Contract C |
| --- | --- | --- | --- |
| Library (core) | #682 | #680, #681 | #684 |
| I/O (equity-feature-io) | #34 | #33 | #35 |
| Workers (equity-feature-workers) | #77 | #76 | #78 |

Readable results view fix for multi-run cases: workers #79. Manifest entry for `retracement.level` (proposed, unaccepted): core #687.

## How each part was verified

- Contracts: every contract was recomputed by a fresh independent reviewer from the contract text alone with exact fractions; several real defects were found and fixed before freeze (null-field fixtures not constructible under the shared validator, an unnecessary zero-volume rule change, a non-positive price in one fixture, an anchor-rule fixture gap).
- Libraries: each library was checked by a fresh independent harness over every result fixture and refusal, a randomized comparison against an independent exact reference, and a before/after byte-identity snapshot of published R17 outputs (2,520, 4,320 and 2,657 requests identical; `describe_intraday()` digest unchanged).
- I/O: synthetic fixtures keyed by the contract's own ids; configs byte-identical to the library builders; every fixture through the real library; sink round-trips with the new data types and units; the extraction census check exits 0.
- Workers: every contract result fixture run end to end (adapter, worker, new DuckDB, readback, replay, close and reopen) with the per-fixture acceptance rule; results demo 304 of 304 cases (62 EF1, 68 EF2-B, 100 EF2-A, 74 EF2-C), 0 failures, 0 view failures.
- Installed artifacts: Windows qualification run `docs/ef2/qualification/EF2_INSTALLED_WINDOWS_20261023.*` (#686): four install forms, 59 of 59 demos each, identical content hashes across forms, independently re-run.

## Known limits and release-gate items

- Exact zeros: `+0.0` is guaranteed only for the contract's marked fixtures. Outside them, Decimal120 recurrences can leave residuals of about 1e-119 (momentum) and the channels squeeze `inside` flag can flip on an exact boundary tie with a non-terminating EMA (about 2% of a targeted random search). Documented in the implementation docs; not snapped.
- Batch API holds chain lists in memory (O(n)); the per-bar O(1) state requirement belongs to a future incremental API. Carry, update, restore and merge are out of v1 (reset epoch mode only).
- Package versions were not bumped (a bump changes the R17 digest); a version bump and release publication are owed and need the owner.
- The three new unit strings (`DMI points`, `stochastic points`, `Williams %R points`) and float64 `shares` are recorded as additive in the amendment but not applied to the frozen shared contract file.
- `retracement.level` is only a proposed entry in the output manifest; the route rows for the nine consumer scanners still name the earlier owners (#511, #518), so a plan edit linking #663 is still to do.

## Not done (not claimed)

- Linux installed qualification (blocked: the WSL Ubuntu image lacks `python3-venv` and pip; owner action).
- A real-source demo for EF2 indicators, source-parity and dataset rights, benchmarks, strict typing (mypy not installed), unit suites by policy, refusal fixtures in the installed runs, owner demo of the EF2 results page, the owner's review of all coordinator decisions, and release acceptance of EQ-152 #486.
