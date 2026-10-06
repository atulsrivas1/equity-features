# EQ051 installed historical read measurements

[Issue58](https://github.com/atulsrivas1/equity-features/issues/58),
[API](../api/DUCKDB_READER.md), [raw report](EQ-051_WINDOWS.json).
Synthetic population only; no private rows or R4 numerical acceptance.

Clean measurement source9f806700e1cbc22ba292f14e7f061a67bad59885,
CPython3.12.10/Windows AMD64, optional0.1.0a3/contracts0.0.4a4,
DuckDB1.5.6/NumPy2.2.6. Actual locally repeat-built wheel forms were installed
in a separate environment; pip check passed. Source-tree fallback is rejected by
the harness. Independent integer time/price/share goldens, distinct occurrences,
unknown known-at and public delivery validation passed before results were retained.

| Selected rows | Whole read median (ns), 3 samples | Reachable canonical/envelope Python bytes | Native process lifetime peak bytes |
| --- | --- | --- | --- |
| 512 | 1538765000 | 174926 | 75612160 |
| 4096 | 13053876000 | 1384947 | 82649088 |

Elapsed whole public reads include preflight/query/fetch/materialization/mapping/copy.
The raw report retains all samples, phase costs, controls and separately timed
fixture/resolver setup. Owned Python bytes deduplicate shared references and exclude
config/wrapper/native/global code. Native Windows PeakWorkingSetSize is a whole
process lifetime high-water, including imports/setup/prior cases, not read-exclusive
allocation or a hard process cap. Runs use supplied single-process synthetic
workloads; no warm/cold storage distinction, improvement target or throughput claim.
Selected physical file lengths are not measured I/O. These observed costs constrain
bounded experimental usage; no full corpus performance/readiness is claimed.

Actual installed project wheel SHA256:

- `equity_feature_contracts-0.0.4a4-py3-none-any.whl`: `3fb31963c1f51b64c4b82fc874c1c38cc9c73461b933fb06d52f84bb29b7c7b2`.
- `equity_feature_duckdb-0.1.0a3-py3-none-any.whl`: `6e0e12e70ec9e505491799980a6af791aa569399b6b9129f01f9f387d296e64e`.
- `equity_features-0.0.4a4-py3-none-any.whl`: `0ff0745acf75f45ae7a2b38c7c106af200448f3026e4997fd0747101c79071f0`.

This dated local source measurement is distinct from later native CI/actual delivered
form reports. Only unchanged runtime/harness bytes permit reuse for doc-only heads;
final actual archive installation/publication evidence still belongs to issue58.
The first missing-NumPy installed failure and COPY fixture restriction were corrected;
those failed attempts are excluded. Existing upstream NumPy pin/notices are recorded
in [release integrity](../RELEASE_INTEGRITY.md).
