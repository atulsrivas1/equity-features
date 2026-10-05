# R1 experimental session package acceptance

**R1 package qualification accepted: experimental pair 0.0.2a9.** Exact kernel PR160 head `e65d98096503b98501c9a95306ea377c037fb57e`; accepted kernel main `f0343a968aa54322c6d72bfcffd9db6aacedb0c9`. Final documentation publication/checks and milestone/epic closure are recorded in [issue30](https://github.com/atulsrivas1/equity-features/issues/30). All ten R1 implementations and both reused prerequisite fixes have qualified delivery evidence; no R2 implementation or public registry publication.

## Qualified scope and mode matrix

All 23 R1 IDs have callable batch/update/restore implementations;22 have conditional legal merge. Modes refer to SessionAccumulator for the named family. Continuous merge is false. All other 16 catalog IDs and custom numerical execution remain false; metadata-only caller-scoped registration remains available.

| ID | Result type | Implementation / independent fixtures | Batch / update / restore / merge |
| --- | --- | --- | --- |
| `session.bar.open` | `float64` | [bars](../packages/features/src/equity_features/session/bars.py), [independent fixtures](../tests/unit/test_bars.py) | yes / yes / yes / conditional |
| `session.bar.high` | `float64` | [bars](../packages/features/src/equity_features/session/bars.py), [independent fixtures](../tests/unit/test_bars.py) | yes / yes / yes / conditional |
| `session.bar.low` | `float64` | [bars](../packages/features/src/equity_features/session/bars.py), [independent fixtures](../tests/unit/test_bars.py) | yes / yes / yes / conditional |
| `session.bar.close` | `float64` | [bars](../packages/features/src/equity_features/session/bars.py), [independent fixtures](../tests/unit/test_bars.py) | yes / yes / yes / conditional |
| `session.bar.volume` | `int64` | [bars](../packages/features/src/equity_features/session/bars.py), [independent fixtures](../tests/unit/test_bars.py) | yes / yes / yes / conditional |
| `session.bar.notional` | `decimal128` | [bars](../packages/features/src/equity_features/session/bars.py), [independent fixtures](../tests/unit/test_bars.py) | yes / yes / yes / conditional |
| `session.bar.close_weighted_price` | `float64` | [bars](../packages/features/src/equity_features/session/bars.py), [independent fixtures](../tests/unit/test_bars.py) | yes / yes / yes / conditional |
| `session.price.open_close_return` | `float64` | [bars](../packages/features/src/equity_features/session/bars.py), [independent fixtures](../tests/unit/test_bars.py) | yes / yes / yes / conditional |
| `session.price.range_fraction` | `float64` | [bars](../packages/features/src/equity_features/session/bars.py), [independent fixtures](../tests/unit/test_bars.py) | yes / yes / yes / conditional |
| `session.price.close_location` | `float64` | [bars](../packages/features/src/equity_features/session/bars.py), [independent fixtures](../tests/unit/test_bars.py) | yes / yes / yes / conditional |
| `session.price.overnight_gap` | `float64` | [bars](../packages/features/src/equity_features/session/bars.py), [independent fixtures](../tests/unit/test_bars.py) | yes / yes / yes / conditional |
| `session.price.close_close_return` | `float64` | [bars](../packages/features/src/equity_features/session/bars.py), [independent fixtures](../tests/unit/test_bars.py) | yes / yes / yes / conditional |
| `session.structure.interval_ohlcv` | `interval_ohlcv` | [structure](../packages/features/src/equity_features/session/structure.py), [independent fixtures](../tests/unit/test_structure.py) | yes / yes / yes / conditional |
| `session.structure.interval_volume_share` | `interval_volume_shares` | [structure](../packages/features/src/equity_features/session/structure.py), [independent fixtures](../tests/unit/test_structure.py) | yes / yes / yes / conditional |
| `session.trade.count` | `int64` | [trades](../packages/features/src/equity_features/session/trades.py), [independent fixtures](../tests/unit/test_trades.py) | yes / yes / yes / conditional |
| `session.trade.volume` | `int64` | [trades](../packages/features/src/equity_features/session/trades.py), [independent fixtures](../tests/unit/test_trades.py) | yes / yes / yes / conditional |
| `session.trade.notional` | `decimal128` | [trades](../packages/features/src/equity_features/session/trades.py), [independent fixtures](../tests/unit/test_trades.py) | yes / yes / yes / conditional |
| `session.trade.vwap` | `float64` | [trades](../packages/features/src/equity_features/session/trades.py), [independent fixtures](../tests/unit/test_trades.py) | yes / yes / yes / conditional |
| `session.trade.mean_size` | `float64` | [trades](../packages/features/src/equity_features/session/trades.py), [independent fixtures](../tests/unit/test_trades.py) | yes / yes / yes / conditional |
| `session.trade.top_k` | `top_k_trades` | [top_k](../packages/features/src/equity_features/session/top_k.py), [independent fixtures](../tests/unit/test_top_k.py) | yes / yes / yes / conditional |
| `session.quote.sampled_spread` | `sampled_spread` | [quotes](../packages/features/src/equity_features/session/quotes.py), [independent fixtures](../tests/unit/test_quotes.py) | yes / yes / yes / conditional |
| `session.quote.state_counts` | `quote_state_counts` | [quotes](../packages/features/src/equity_features/session/quotes.py), [independent fixtures](../tests/unit/test_quotes.py) | yes / yes / yes / conditional |
| `session.quote.time_weighted_spread` | `time_weighted_spread` | [continuous](../packages/features/src/equity_features/session/continuous.py), [independent fixtures](../tests/unit/test_continuous.py) | yes / yes / yes / no |

Formulas remain frozen in [session](features/SESSION_FORMULAS.md) and [quote](features/QUOTE_FORMULAS.md) specifications. Structured interval rows retain independent quality; sampled summaries/counts and duration summaries are typed, including null undefined means. No provisional quantile/variance/scalar unknown-duration IDs were invented. [Streaming API](api/INCREMENTAL.md) documents migrations, source certificates and conditional merge.

## Accepted story identities

| Story | PR | Experimental pair | Accepted main source | Units | Receipt |
| --- | --- | --- | --- | --- | --- |
| EQ-017 | [PR149](https://github.com/atulsrivas1/equity-features/pull/149) | 0.0.2a0 | `674194de7cc0ecb33b0569768572f4c89a1b354c` | 205 | [delivery](stories/EQ-017_DELIVERY.md) |
| EQ-018 | [PR152](https://github.com/atulsrivas1/equity-features/pull/152) | 0.0.2a1 | `c3faac1ae34c5c3470313c6064210e37ce1cd90d` | 223 | [delivery](stories/EQ-018_DELIVERY.md) |
| EQ-019 | [PR153](https://github.com/atulsrivas1/equity-features/pull/153) | 0.0.2a2 | `80e81d5acc243a025c1d3383256e78064f140db5` | 241 | [delivery](stories/EQ-019_DELIVERY.md) |
| EQ-020 | [PR154](https://github.com/atulsrivas1/equity-features/pull/154) | 0.0.2a3 | `6c42ee24c9c8364fa763f31f76fa23b6cbf12617` | 256 | [delivery](stories/EQ-020_DELIVERY.md) |
| EQ-021 | [PR155](https://github.com/atulsrivas1/equity-features/pull/155) | 0.0.2a4 | `ac5d406e7c44facf166777cef7edc9e92b4d81d8` | 274 | [delivery](stories/EQ-021_DELIVERY.md) |
| EQ-022 | [PR156](https://github.com/atulsrivas1/equity-features/pull/156) | 0.0.2a5 | `7e1a87f67d014614a2d14c94dddba8868a674dba` | 297 | [delivery](stories/EQ-022_DELIVERY.md) |
| EQ-023 | [PR157](https://github.com/atulsrivas1/equity-features/pull/157) | 0.0.2a6 | `b5107ac5db739ddfe6106b5555dd8f4d8e974d50` | 328 | [delivery](stories/EQ-023_DELIVERY.md) |
| EQ-024 | [PR158](https://github.com/atulsrivas1/equity-features/pull/158) | 0.0.2a7 | `10b62eee6ce0757893c5fedf7b66b170a28853e4` | 346 | [delivery](stories/EQ-024_DELIVERY.md) |
| EQ-025 | [PR159](https://github.com/atulsrivas1/equity-features/pull/159) | 0.0.2a8 | `1d360f8975ff186fdaf3cdda27705472c3132e74` | 363 | [delivery](stories/EQ-025_DELIVERY.md) |
| EQ-026 | [PR160](https://github.com/atulsrivas1/equity-features/pull/160) | 0.0.2a9 | `f0343a968aa54322c6d72bfcffd9db6aacedb0c9` | 370 | [delivery](stories/EQ-026_DELIVERY.md) |

[BUG001](https://github.com/atulsrivas1/equity-features/issues/144) exact-cutoff evidence and [BUG002](https://github.com/atulsrivas1/equity-features/issues/145) fail-closed backend I/O gate were reused from accepted [R0 repaired delivery](R0_ACCEPTANCE.md); no duplicate defect work. Author self-review plus agreed CI is the review identity throughout; no independent reviewer claimed. Earlier review findings and failed attempts/recoveries are recorded in each receipt and [continuity](SESSION_HANDOFF.md).

## Independent verification and arithmetic limits

370 unit cases include all family goldens/adversaries,31 lifecycle,18 state,17 equivalence and7 final integration audit cases.123 independent formula reference checks remain separate. Strict mypy covers26 source/example files; purity gate tests38 negative and10 positive fixtures; registry/discovery/import isolation, optional-backend compatibility, license metadata,94 active planning stories and public Markdown UTF8 pass locally. Repeated four-archive reproducibility/content inspection, both local fresh pair installs, all six exact-head checks and all main Windows/Linux checks passed. Both actual OS bundles passed four fresh pair installations, each370 tests/eleven examples.

[Independent final audit](../tests/unit/test_r1_audit.py) gives early-close OHLC(100,120,99,115), Q5/A546, separate proxy551/5, interval shares2/5 and3/5; exact auction boundary evidence; decimal128 notional3*(2^53+1) survives Arrow/merge/restore; scaled quote mean0.015 with valid denominator2 and bps30000/20003; seed original expiry yields7 valid/5 expired nanoseconds after a prefix snapshot and restore. [Equivalence qualification](../tests/unit/test_equivalence.py) uses every split/both argument orders for legal families, chunk sizes1/2/7/10000 for all six, restored replay, merge trees and1,000 skewed/equal-time events in uneven partitions.

Integers and UTCns never route through binary64. Counts/volumes/durations use checked signed int64; notional and exact spread numerators use checked decimal128 with38 digits. Overflow raises before ready publication, or remains a bounded overflow flag while coverage is unready; no wrapping/clamping. Price/ratio outputs use exact rational numerators before Float64 conversion. Quote bps uses compensated binary64; grouping parity uses relative/absolute 1e-12, supported by concrete cases, not universal throughput/precision guarantees.

Eligibility/causal knowledge and caller-declared coverage remain independent. Empty known populations, absent schemas, null fields, zero denominators, crossed/locked/invalid quotes, unknown initialization and known missing delivery preserve separate quality. Prices use positive-volume whole bars; real notional stays separate from close-weighted proxy. Trade totals use eligible prints. Sampled means use valid normal/locked count; duration means use valid elapsed time. Original quote anchors/age never restart on a snapshot or restore.

## Ownership, bounded state and unsupported behavior

Canonical inputs/results/envelopes own immutable tuple/text containers. Updates/snapshots use cloned bounded candidate state and commit after admission/result validation; failures leave original state unchanged. Restores and merges own independent private reducers. Caller serializes mutable access; no concurrent-call guarantee. Core imports are stdlib only with no source lookup, clock/environment acquisition, file persistence, workers or adapter implementation.

Retained scalar reducers are fixed size; interval memory grows with configured windows, topK with K≤10000, sampled observations with N≤10000. One fixed prior/seed may be retained; metadata has fixed input bindings. Top/quote merge unions temporarily retain≤2K/2N rows. Admission and immutable canonical/Arrow/NumPy materialization allocate proportional to supplied chunk/output; batch admission may allocate a full-population duplicate set. Bounded retained state is not a zero-copy or bounded caller input claim. State envelopes cap UTF8 text at16MiB; oversized retained identity text can reject export.

State schema1 uses exact integers and canonical finite binary64 hex; restore requires exact implementation/config/entity/source/schema/unit/basis/math/backend/enrichment identity. No implicit migration between experimental package versions. Digests detect accidental corruption, not authentication of rehashed fabricated history. Global discarded opaque-ID uniqueness and global ordinal span/delivery assertions remain caller-certified. Checks enforce known count/order/retained contradictions; no independent source-truth proof is claimed.

Merge requires adjacent nonempty disjoint ranges, actual consumed counts and compatible immutable declarations, chronological boundary order, no known retained-ID overlap, and no prior snapshot/finalize. Continuous carry/expiry integration merge, arbitrary overlapping/corrected partitions and post-publication merge are unsupported and require replay. No quantiles, variance, missing-row reconstruction, raw-history retention, source data qualification, concrete providers, performance claim, PyPI/stable registry/tag release, R2+ kernels or automation.

## Actual artifact channel and exit gates

Experimental main GitHub Actions bundles contain both wheels and sdists, a clean-source manifest and four SHA256 values. Each accepted predecessor receipt links both actual OS bundles with real expiry and hashes; both bundles were downloaded/inspected, then their wheel/sdist pairs ran in four fresh Windows CPython 3.12.10 environments. CI separately qualifies Linux CPython 3.12.14 and Windows3.12.10 with NumPy 2.2.6/PyArrow 20.0.0; local Windows installs do not claim Linux execution. Final accepted kernel artifacts and post-delivery receipt are linked below. Both actual downloaded bundles passed manifest/clean flag/four SHA256/archive-content checks and four fresh pair installations.

Rebuild from the accepted source with pinned development tools: `python tools/build_foundation.py`. [Build/delivery policy](BUILD_DELIVERY.md) explains retention and access; expired bundles require a qualified rebuild, not an availability promise. Per-story versions are distinct and never silently overwritten.

Final R1 milestone2 closure requires live verification that its ten EQ017–026 stories and both reused defects are closed/Done, with no additional undelivered item. E04 closes only all its delivered children; E03 remains open for R3 contracts. Final documentation source/CI/artifacts and live closure evidence are recorded in [issue30](https://github.com/atulsrivas1/equity-features/issues/30). Live EQ027 is [issue32](https://github.com/atulsrivas1/equity-features/issues/32), under E05 issue31. Its release/math/contract prerequisites are delivered at R1 exit; it stays unstarted/Backlog awaiting a separate R2 instruction. Owner-deferred PR120 and concurrently accepted EQ095/R3 planning are preserved.

### Accepted kernel artifact identities

- [foundation-f0343a968aa54322c6d72bfcffd9db6aacedb0c9-ubuntu-24.04](https://github.com/atulsrivas1/equity-features/actions/runs/37348487501/artifacts/11361601551); actual expiry `2026-11-04T17:27:45Z`. Four SHA256 values are recorded in [EQ026 receipt](stories/EQ-026_DELIVERY.md).
- [foundation-f0343a968aa54322c6d72bfcffd9db6aacedb0c9-windows-latest](https://github.com/atulsrivas1/equity-features/actions/runs/37348487501/artifacts/11360968645); actual expiry `2026-11-04T17:28:26Z`. Four SHA256 values are recorded in [EQ026 receipt](stories/EQ-026_DELIVERY.md).

The final documentation PR changes only root/docs files. Its final main OS bundle hashes must equal these kernel package bytes; exact final source and verification are recorded in issue30. Experimental version meaning is preserved.
