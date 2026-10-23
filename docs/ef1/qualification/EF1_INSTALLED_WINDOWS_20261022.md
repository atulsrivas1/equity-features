# EF1 installed-artifact qualification run, Windows (2026-10-22)

Installed Windows qualification evidence only. This is a manual qualification run; it does not accept or release anything.

## Sources (origin/main at run time)

- core: `984a266137f314763749e5f2da241d99df75e8e5`
- io: `9ef41e0ff976c257c2cbc8367f14289d15673852`
- workers: `e030433b7b1e9397b2730f2f8bde39b0297fdea8`

Platform: Windows 11 Pro 10.0.26300, CPython 3.12.10, pip 25.0.1, setuptools 80.9.0. The `build` package is not installed, so wheels and sdists were produced by calling `setuptools.build_meta.build_sdist` and `build_wheel` from a venv holding only setuptools 80.9.0. The pip-driven sdist installs built in pip isolation (setuptools 80.9.0 resolved offline).

## Method

1. Fresh detached worktrees of each repo at the SHAs above, in a scratch folder; the working clones were not touched.
2. Built an sdist and a wheel for 8 packages: contracts, features, intraday (core); io-contracts, io-sdk, duckdb, duckdb-sink (I/O); workers.
3. Four fresh venvs, each installed with `pip install --no-index --find-links <form folder>` of the workers, duckdb-sink, duckdb and intraday packages (dependencies resolved from the same folder). The form folder held only the archive type selected for that form plus three local third-party wheels (numpy 2.2.6, duckdb 1.5.6, setuptools 80.9.0, copied from an earlier local build cache; hashes in the JSON). No package index was used. No `--system-site-packages`. `pip check` reported no broken requirements in all four.
4. From a clean scratch directory outside any source tree, each demo ran as `python -I -B -c <launcher> <example.py> --output-db ABS --html ABS --run-id ID --case ...` with no PYTHONPATH. The launcher printed each project module `__file__` first; every one resolved to the venv `site-packages`. Example scripts and the contract JSON for venue status (`--contract`) and the oracle JSONs the examples read next to themselves came from the source worktrees as data; all packages came from the installed copies.
5. A demo passes when exit is 0, a printed `verified_readback` line exists with every boolean flag true (`verified_reopen`, `independent_literal_match` or `contract_literal_match` where printed), the database and HTML were written, and the module paths are installed ones.

## Archives (sha256)

- `equity_feature_contracts-0.0.4a4-py3-none-any.whl` 79cdce0fee9e249b99f2a8311c814c5786b09bff23c5e6d3cd1bd20701974a98
- `equity_feature_contracts-0.0.4a4.tar.gz` b0c59800aee465c4bb8f29ef24817bf5ba1de54f47e74be1ba7b2f72a976ee2b
- `equity_feature_duckdb-0.1.0a9-py3-none-any.whl` 60d3c73a57714d57337c7dbc4abbece31341480fc5c2319f817afa78de7de744
- `equity_feature_duckdb-0.1.0a9.tar.gz` c417f880ed5604f65b2eb7225281acbb041ad9a76922205071d0fcf8e1ab0e07
- `equity_feature_duckdb_sink-0.1.0a0-py3-none-any.whl` f19b23b74d33b000e357e76faff3cd7f909e0603d9f0f6433b8bf6e05abadcb4
- `equity_feature_duckdb_sink-0.1.0a0.tar.gz` 6477697f569a6906ace9af4c036c88b806cf5668f182803bf0dead832a252e72
- `equity_feature_io_contracts-0.1.0a2-py3-none-any.whl` c0abbf17c0a5c9aa1836ecf566806659a28b6376fb021ac136a5ccdfb9e9b8eb
- `equity_feature_io_contracts-0.1.0a2.tar.gz` 7bd7168679eb26e8f87b92cb3790e073e3f55a408ba39569d9a071e4e03d9b79
- `equity_feature_io_sdk-0.1.0a2-py3-none-any.whl` f9c77b230ad076ab104060604005f7fbcd2209977525752229a67f52cce885c4
- `equity_feature_io_sdk-0.1.0a2.tar.gz` 5e30f96b265fe229b178298d825a7a4bf9a8fa39e36f73b525f58288257a9620
- `equity_feature_workers-0.1.0a15-py3-none-any.whl` 3602f05fca3e6134fad9eab922fa07aa858946f7fc72f4a688be2448bf56a233
- `equity_feature_workers-0.1.0a15.tar.gz` 6f82ed01733f8a605ff57db06849378a968621e8ace27b0d1ee24c28f9bb1641
- `equity_features-0.0.4a5-py3-none-any.whl` 2ab9da163dde8e20a3a6388c8e83bf8f1ae6ccdcfb0bee7057805992975bb6c1
- `equity_features-0.0.4a5.tar.gz` abc9f767fe665888c6698cfae09bf83c61f949228cbacd31c92a7156566ffc0e
- `equity_features_intraday-0.1.0a3-py3-none-any.whl` 551f8974d9c49f253b33a581ac148289947c267685b2037eae8822a5eca1aac9
- `equity_features_intraday-0.1.0a3.tar.gz` ef139c49840ca8d4e39b6a023947ebefef7c944bb00dc9a4b65afde6530fc9cc

## Results

| Form | install | pip check | demos passed | first-attempt |
|---|---|---|---|---|
| all-wheels | exit 0 | exit 0 | 30/30 | 30/30 |
| all-sdists | exit 0 | exit 0 | 30/30 | 30/30 |
| core-wheels-components-sdists | exit 0 | exit 0 | 30/30 | 28/30 |
| core-sdists-components-wheels | exit 0 | exit 0 | 30/30 | 28/30 |

Demos per form (30): first_trade R001, R019; regular_bar_prices R01, R08; gap_endpoint E01, E26; clock C20 present/missing/unknown/future; anchors trades A01/A02, bars A01, bars A01-missing-notional; status S01-S03; reference_close C01-C03; venue_status MV01, MV05, MV10, MV12, MV20, MV24, MV30, MV40, MV43, MV44 (10 cases, including MV05, MV24, MV43).

Harness note: in the two mixed forms the first-trade R001 and R019 first attempts exited 2 (usage refusal before any work) because my run id embedded the long form name and exceeded the example's 64 character run-id limit. That was a harness mistake, not a package defect. They were re-run in new directories with short run ids and passed (exit 0, all flags true, database and HTML written, installed module paths). Both attempts are disclosed above.

Canonical `content_sha256` printed by each demo was identical across all four forms for every demo (task hashes differ because run ids differ). Archive bytes of the dist folder are single-built once, so form-to-form archive reproducibility was not tested.

## Observations

- Published `equity-feature-duckdb` pins `numpy==2.2.6` while the base interpreter has numpy 2.5.3; the venvs therefore needed the local numpy 2.2.6 wheel. Not an error, but offline installs need that exact wheel.
- `ef1_venue_status` defaults to finding its contract JSON by walking up from the installed `equity_features` package, which is not expected to resolve from an installed copy (not tried without the flag); `--contract` pointing at the core repository file was required.
- The gap, bar-price and first-trade examples read oracle JSON from `../tests` relative to the example script, so they depend on the worker source tree being present beside the examples.

## Not run

- unit test suites (owner policy: manual verification only)
- Linux
- real N-drive data
- original-source parity
- source rights
- benchmarks
- browser inspection
- daily observations demo (needs a corpus)
- remaining 34 venue-status cases and other examples outside the demo list
- independent artifact audit

No claim of acceptance, release, publication, parity, rights, performance or platform coverage beyond this Windows run is made.
