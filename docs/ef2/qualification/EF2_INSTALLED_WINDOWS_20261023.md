# EF2 installed-artifact qualification run, Windows (2026-10-23)

Installed Windows qualification evidence only. This is a manual qualification run; it does not accept or release anything.

## Sources (origin/main at run time)

- core: `a53f4402d437de75274ccf878a427e0459d2f31b`
- io: `c15f540b57fa59a4bd6e6ecc3b017a69d5ee039a`
- workers: `d2fc901b9b73d8acbf86f9e43192b363e1835cd2`

Platform: Windows 11 Pro 10.0.26300, CPython 3.12.10, pip 25.0.1, setuptools 80.9.0. The `build` package is not installed, so wheels and sdists were produced by calling `setuptools.build_meta.build_sdist` then `build_wheel` from a venv holding only setuptools 80.9.0 (exit 0 for all 8 packages). Pip-driven sdist installs built in pip isolation (setuptools 80.9.0 resolved offline). The method follows `docs/ef1/qualification/EF1_INSTALLED_WINDOWS_20261022.md`.

## Method

1. Fresh detached worktrees of each repo at the SHAs above in a scratch folder; the working clones were not touched.
2. Built an sdist and a wheel for 8 packages: contracts, features, intraday (core); io-contracts, io-sdk, duckdb, duckdb-sink (I/O); workers. These are all the project distributions the demos import. Versions are unchanged from the EF1 run (contracts 0.0.4a4, features 0.0.4a5, intraday 0.1.0a3, io-contracts 0.1.0a2, io-sdk 0.1.0a2, duckdb 0.1.0a9, duckdb-sink 0.1.0a0, workers 0.1.0a15) although the code contents differ, so the archive hashes below differ from the EF1 run.
3. Four fresh venvs (all-wheels, all-sdists, core-wheels-components-sdists, core-sdists-components-wheels), each installed with `pip install --no-index --find-links <form folder>` of workers, duckdb-sink, duckdb and intraday (the rest resolved from the same folder). A form folder held only the selected archive type plus three local third-party wheels (numpy 2.2.6, duckdb 1.5.6, setuptools 80.9.0, copied from the EF1 run's local build cache). No package index; no `--system-site-packages`.
4. `pip check`: no broken requirements in all four (exit 0).
5. From a clean scratch directory outside any source tree, each demo ran as `python -I -B -c <launcher> <example.py> --output-db ABS --html ABS --run-id SHORT --case ... --contract <core docs JSON>` with no PYTHONPATH. The launcher imported and printed the `__file__` of all 8 project modules first; every one resolved to the venv `site-packages`. Example scripts and the contract JSONs came from the source worktrees as data; all packages came from the installed copies.
6. A demo passes when exit is 0, a printed `verified_readback` line exists with every boolean flag true (`verified_reopen`, `contract_literal_match` or `independent_literal_match`, `witness_identity_checked` where printed), the database and HTML were written, and the module paths are installed ones. Run ids were short (64 character bound).

## Archives (sha256)

- `equity_feature_contracts-0.0.4a4-py3-none-any.whl` 570d11fc2b1a990490a2f10aa58466f0e6e26d66471dd3f68e5150f6ff561739
- `equity_feature_contracts-0.0.4a4.tar.gz` ea8af7c79010eab969e8c272847fc8dd47f12c5b8b1a52637386ce6f8acdcfe7
- `equity_feature_duckdb-0.1.0a9-py3-none-any.whl` d6561fc3ac1c09716181ad31e5613a5be88c6e24960c876d1ce380263119bd47
- `equity_feature_duckdb-0.1.0a9.tar.gz` ae179703de7d18a3450810c5ef9fc2a94c3f0585aab77d84a2d24dcb4374edba
- `equity_feature_duckdb_sink-0.1.0a0-py3-none-any.whl` 601030b2c28f4f0cba252c821cca58197e0ede5fa14ef13a07c5c1a3d81c7e79
- `equity_feature_duckdb_sink-0.1.0a0.tar.gz` 0c64d068566bf3051ff07456e8a958ea8ed09cd43ca1082600da2e95db897708
- `equity_feature_io_contracts-0.1.0a2-py3-none-any.whl` 85c74e6cb92854befaa35f051eac6899689e92d7cbe8f1d01d12e5acf67104d7
- `equity_feature_io_contracts-0.1.0a2.tar.gz` 820383afef87795b219109e6c89a951c2ed82c6e2760b7ab5505ae0b1af15acd
- `equity_feature_io_sdk-0.1.0a2-py3-none-any.whl` f31b5b103ca58e56ab2c27aa69b9bed1dc31875f9505cb93e4a05d5885c48a7e
- `equity_feature_io_sdk-0.1.0a2.tar.gz` 7f3223c6ef170ebb28ca29cf9b04c8ed70034a2701b18c61750d86ba62d01d1e
- `equity_feature_workers-0.1.0a15-py3-none-any.whl` f985dea9ef46d8862cb8ab82c4ee899db40aff0f339531a7fa616ef29ee68d5e
- `equity_feature_workers-0.1.0a15.tar.gz` 0da2ace5e60f946f4e9217b4d4d6d13650baf32e011a09ecd9deb78f8c89cdb7
- `equity_features-0.0.4a5-py3-none-any.whl` dcd745153c37b371eb91ae82cd6b0087eea3bc3717024cca32bc12a6708439cd
- `equity_features-0.0.4a5.tar.gz` 61e849ee854a553b265f6de14e0a1864d18480903f76150deea45badb138864f
- `equity_features_intraday-0.1.0a3-py3-none-any.whl` 29931ed3d54538c3c0013e7bf0d694a89330e441754852d866e0eec655cc65c1
- `equity_features_intraday-0.1.0a3.tar.gz` 92afff14116072dacbb28a3efc913b417264d652851f22de4e757465e6ee8c58

Local third-party wheels (not project artifacts):

- `duckdb-1.5.6-cp312-cp312-win_amd64.whl` 09ff51b230219f0d8b47fc8a1e17fb595ba9fab0c3d96a6de4d00b8ff86b3cf1
- `numpy-2.2.6-cp312-cp312-win_amd64.whl` c1f9540be57940698ed329904db803cf7a402f3fc200bfe599334c9bd84a40b2
- `setuptools-80.9.0-py3-none-any.whl` 062d34222ad13e0cc312a4c02d73f059e86a4acbfbdea8f8f76b28c99f306922

## Results

| Form | install | pip check | demos passed | first attempt |
|---|---|---|---|---|
| all-wheels | exit 0 | exit 0 | 59/59 | 59/59 |
| all-sdists | exit 0 | exit 0 | 59/59 | 59/59 |
| core-wheels-components-sdists | exit 0 | exit 0 | 59/59 | 59/59 |
| core-sdists-components-wheels | exit 0 | exit 0 | 59/59 | 59/59 |

Demos per form (59, same list in every form):

- EF1 sample (30): first_trade R001, R019; regular_bar_prices R01, R08; gap_endpoint E01, E26; clock C20 present/missing/unknown/future; anchors trades A01/A02, bars A01, bars A01-missing-notional; status S01-S03; reference_close C01-C03; venue_status MV01, MV05, MV10, MV12, MV20, MV24, MV30, MV40, MV43, MV44.
- ef2_money_flow (4): M05, M26, M34, M36.
- ef2_retracement (2): T12, T32.
- ef2_momentum (11): MACD M01, M05, M25, M26; DMI D01, D04, D22, P02 (DMI prefix property); stochastic T01, T05, T10.
- ef2_channels (12): ICH-17, SQ-10, PCT-10, PIV-11, KEL-04, DON-05, ICH-01, KEL-01, DON-01, PIV-01, PCT-01, SQ-01.

All 59 demos in all four forms passed on the first attempt (exit 0, every printed boolean flag true including `verified_readback`, `verified_reopen` and `contract_literal_match`/`independent_literal_match`, database and HTML written, installed module paths). The canonical `content_sha256` printed by each demo was identical across all four forms for every demo (task hashes differ because run ids differ). Per-demo flags and hashes are in the JSON. Archives were built once, so form-to-form archive reproducibility was not tested.

## Observations

- `equity-feature-duckdb` pins `numpy==2.2.6` while the base interpreter has numpy 2.5.3, so offline installs need that exact wheel.
- The EF2 and venue-status examples default to finding the contract JSON by walking up from the installed `equity_features` package, which cannot resolve from an installed copy (default not tried); `--contract` pointing at the core repository file was passed for every EF2 and venue-status demo. The EF1 gap, bar-price and first-trade examples read oracle JSON from the worker source tree's `tests` folder beside the examples, so they depend on that tree being present. Both are source-tree data dependencies of the examples, not of the installed packages.

## Not run

- unit test suites (owner policy: manual verification only)
- Linux
- real data
- original-source parity
- source rights
- benchmarks
- refusal fixtures
- the full contract fixture sets (304 cases); only the 29 listed EF2 cases were run
- default contract path resolution from an installed copy
- browser inspection
- daily observations demo (needs a corpus)
- other examples outside the demo list
- independent artifact audit

No claim of acceptance, release, publication, parity, rights, performance or platform coverage beyond this Windows qualification run is made.
