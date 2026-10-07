## EQ129 supported combination under qualification

The concrete [canonical matrix plan](https://github.com/atulsrivas1/equity-features/blob/codex/eq-129-compatibility-matrix/docs/stories/EQ-129_PLAN.md) freezes core/contracts0.0.4a4, IO contracts/SDK0.1.0a2, standalone DuckDBsource0.1.0a8, both sinks0.1.0a0, exampleextensions0.1.0a0 and workers skeleton0.1.0a1. Optional engines are DuckDB1.5.6/NumPy2.2.6/PyArrow20.0.0, explicitly installed only for full composition. Core works independently; extension needs only canonical contracts+SDK. Workers.a1 pins SDK.a2 and exports version only, no commands/runtime. Historical workers.a0/SDK.a0 remains separately scoped; forcing oldworker.a0 with newSDK.a2 or IOcontracts.a1 with SDK.a2 must fail actual resolver/pipcheck. This does not certify untested versions/platforms.

Migration: consumers keep original pure contracts/features imports. Standalone acquisition imports equity_feature_duckdb; output implementations equity_feature_parquet/equity_feature_duckdb_sink and custom extension examples remain explicit consumer-selected dependencies. Never add I/O/workers to calculation requirements or rely on automatic registry discovery. Choose a complete declared artifact combination, run pip check, preserve canonical schema/algorithm/config/source/timing/units/nulls, and retain per-backend physical/resource/retention/rights limits. No private/provider/backend/source/math behavior is changed by matrix tests. No source/WAL-present/private rerun is claimed; accepted immutable private receipt bindings remain intact.

Actual native/fresh-form matrix and separate final-head review/current artifact publication/readback remain pending. Old accepted story evidence below stays historical. This qualification does not implement R5 or authorize stable tags/registry/services/private generation.

# DuckDB migration and retired core development paths

EQ122 moves current optional implementation, tests, API specifications and qualification to [equity-feature-io](https://github.com/atulsrivas1/equity-feature-io). `equity-feature-duckdb` and `equity_feature_duckdb` retain their distribution/import names, exports and signatures. Pure contracts/features remain0.0.4a4 with unchanged source/metadata/math/schema. The optional adapter remains independently installable without I/O SDK/workers.

The declared experimental channel is successful-main I/O Actions, not a registry or stable tag. [Actual standalone receipt](stories/EQ-122_STANDALONE_RECEIPT.json) records main7475e1eef2f9d3b834fdf98473d8b40df4b6cc5f, optional run37557267501 and foundation37557267503, channel SHA256/expiry, actual archive hashes, native Windows/Linux qualification and private execution limits. Requested retention is30days; read the current expiry on [canonical issue279](https://github.com/atulsrivas1/equity-features/issues/279) before download. Overall core migration acceptance is separate from this verified standalone prerequisite.

## Install tested artifacts

For CPython3.12 x64 Windows, download the declared bundle and install actual files:

```text
gh run download 37557267501 --repo atulsrivas1/equity-feature-io --name duckdb-7475e1eef2f9d3b834fdf98473d8b40df4b6cc5f-windows-latest --dir adapter-artifacts
python -m pip install duckdb==1.5.6 numpy==2.2.6
python -m pip install --no-index --no-deps adapter-artifacts/equity_feature_contracts-0.0.4a4-py3-none-any.whl adapter-artifacts/equity_feature_duckdb-0.1.0a8-py3-none-any.whl
python -m pip check
```

On native Linux select the `ubuntu-24.04` bundle from the same run. If calculations are needed, install its matching `equity_features-0.0.4a4-py3-none-any.whl` separately. Source distribution installation uses pinned `setuptools==80.9.0`, then `--no-index --no-deps --no-build-isolation` with the actual matching contracts/adapter `.tar.gz` files. Both forms were freshly qualified on both supported native platforms. No project-index fallback is required. Installed receipt/package version is0.1.0a8; no import change is needed.

## Retired development paths

| Former core resource | Current I/O resource |
| --- | --- |
| `packages/duckdb` | `packages/duckdb` |
| `tests/duckdb` | `tests/duckdb` |
| `requirements-duckdb.txt` | `requirements-duckdb.txt` |
| `tools/build_duckdb.py` | `tools/build_duckdb.py --core-root <canonical-checkout>` |
| `benchmarks/duckdb_read.py` | `benchmarks/duckdb_read.py` |
| `examples/duckdb_conformance.py` | `examples/duckdb_conformance.py` |
| `docs/api/DUCKDB_*.md` | Current specifications under the same I/O paths; core retains redirects |

The active core paths/workflow are removed only after actual standalone publication/readback. New optional development belongs in I/O. Source-store files/catalogs are not moved or deleted. Core numerical packages and the external consumer remain independently buildable; their fresh artifacts need no adapter/I/O/worker installation. [I/O build instructions](https://github.com/atulsrivas1/equity-feature-io/blob/main/docs/DUCKDB_MIGRATION.md) retain the separate optional environment and exact frozen core-source binding.

## Evidence compatibility and retained history

a8 changes the package version and `AcquisitionReceipt.adapter_version`; the complete receipt digest changes with that field. Actual olda7/newa8 installed readers on identical synthetic files retain canonical batches, mapping/source identities, receipt fields other than the stamp, non-timing metrics and error behavior. Never relabel a7 receipts as a8. Canonical original-read2/retained-map1 identities and strict ASCII UTCns/nativeHUGEINT, binary64_exact/half_even scale4, unknown known-at/eligibility, TBBO trade_snapshot, UTCdaily and causal/calendar/coverage/budget limits are preserved.

[R4 acceptance](R4_ACCEPTANCE.md), original story receipts and Git history remain. Historical a7 core artifacts are usable within their finite retention and accepted limitations; no stable deprecation date is promised. New delivered a8 bytes equal four separately freshly installed private producer/forms, executed on Windows3.12.10 with frozen independent goldens: each68numeric/status/unit/source checks,9acquisitions,3blocked cases. Linux producer does not imply native Linux private execution. Representative retained qualification does not certify full corpus, provider/PIT/eligibility/rights/exchange-calendar truth. Public receipts contain opaque hashes/counts/limits; private source rows/paths/pins remain private.
