# EF3 installed-artifact qualification run, Windows (2026-10-23)

Installed Windows qualification evidence only. This is a manual qualification run; it does not accept or release anything. Machine-readable per-demo results: `EF3_INSTALLED_QUALIFICATION.json`.

## Sources (origin/main at run time)

- core: `4cb50ef7ef8138495bb9bfdd13b524ef35743539`
- io: `86cbff27d5adf127c2fb49c71477f554892b7c5b`
- workers: `f92fd6a8c0efbc1b6a59fbe9b67d3683b295e450`

Platform: Windows 11 Pro 10.0.26300, CPython 3.12.10, pip 25.0.1, setuptools 80.9.0. The method follows `docs/ef2/qualification/EF2_INSTALLED_WINDOWS_20261023.md` and `docs/ef1/qualification/EF1_INSTALLED_WINDOWS_20261022.md`.

## Method

1. Fresh detached worktrees of core, io and workers at the SHAs above in a scratch folder; the shared checkouts were not touched.
2. Built an sdist and a wheel for 8 packages by calling `setuptools.build_meta.build_sdist` then `build_wheel` from a venv holding only setuptools 80.9.0 (the `build` package is not installed): contracts, features, intraday (core); io-contracts, io-sdk, duckdb, duckdb-sink (io); workers. These are the project distributions the demos import (the launcher printed the `__file__` of exactly these 8 modules). The three repositories hold more packages (core 13, io 8, workers 4); the others were not built or installed. Versions are unchanged from the EF2 run (the code differs, so archive hashes differ). Archives were built once, so rebuild reproducibility was not tested.
3. Four fresh venvs (all-wheels, all-sdists, core-wheels-components-sdists, core-sdists-components-wheels), each installed with `pip install --no-index --find-links <form folder> equity-feature-workers equity-feature-duckdb-sink equity-feature-duckdb equity-features-intraday`. A form folder held only the selected archive type plus three third-party wheels (numpy 2.2.6, duckdb 1.5.6, setuptools 80.9.0; downloaded once with `pip download --no-deps` because the EF2 cache was gone). No package index during installs; no `--system-site-packages`. "core" means the three core packages; "components" means the io and workers packages.
4. `pip check` in each venv.
5. From the scratch directory, each demo ran as `python -I -B launcher.py <example.py> ... --output-db ABS --html ABS --run-id SHORT [--contract <core docs JSON>]` with no PYTHONPATH. The launcher printed the `__file__` of the 8 project modules before running the example; every one resolved under that venv's `site-packages`. Batches ran with core `tools/run_batch.py` (8 workers, 600 s timeout, one summary per form).
6. A demo passes when exit is 0, the printed `verified_readback` line has every boolean flag true (`verified_reopen`, `contract_literal_match` or `independent_literal_match`), the database and HTML were written, and all module paths are installed ones.

## Archives (sha256)

- `equity_feature_contracts-0.0.4a4-py3-none-any.whl` a2d017a91257b746385ccf58c3b041e53d2e33207cc7f96323a47c21ea1e4fd7
- `equity_feature_contracts-0.0.4a4.tar.gz` 5f73d14140c350f854f9a1ba6b037359d661fd7cae30395df55ed63c60e917f9
- `equity_feature_duckdb-0.1.0a9-py3-none-any.whl` 9313563fbbec820fbb35bc7162c36e1c5f8a40202807ec766e7e849e8ee071e7
- `equity_feature_duckdb-0.1.0a9.tar.gz` 875d4c4a2475d2ad8dfdc17cf79dac5f7e965b4cc9a6590a6e8e2d4e95eac0b6
- `equity_feature_duckdb_sink-0.1.0a0-py3-none-any.whl` e5a1d8959fffe89665d426ae5e064b179ce42be7a5e9dcee8123b3d84c072f73
- `equity_feature_duckdb_sink-0.1.0a0.tar.gz` d32c189315b9d3f56ecaef83a9710118a888e17c6ec66e462abd3c2d88b7ab36
- `equity_feature_io_contracts-0.1.0a2-py3-none-any.whl` e8824c780fb48722d5c6e7e6399443fd42c6937f5990b58ba336a655a9bce451
- `equity_feature_io_contracts-0.1.0a2.tar.gz` 7765cccaae2cf7161d6a98a535da18ec822749d8a03bcd7d0ced290589e8b1f8
- `equity_feature_io_sdk-0.1.0a2-py3-none-any.whl` cc9d56fba8bae5b5f9f8889ad109dbe54f50cbb0ebb10ed41aae6f2c287b74cf
- `equity_feature_io_sdk-0.1.0a2.tar.gz` 43a8ebfac4086926bdcae0691c6785161f6f803c7f9aba9f4a8bdeec95acf1e1
- `equity_feature_workers-0.1.0a15-py3-none-any.whl` 45691b6357235d8b20ad0973c3cc917b2dc37d6eb483cde8bb9768f5f35357bd
- `equity_feature_workers-0.1.0a15.tar.gz` 2387b0e34152bbe5ac9aaf9030d9dc568c0a8185a278fd897758c91132725a58
- `equity_features-0.0.4a5-py3-none-any.whl` 0e9c81d034a53b99038e7f886bea6d049e5e5c567004753b991f523c342ea1f0
- `equity_features-0.0.4a5.tar.gz` abbed559c997e24a9a9455c6fb01a9dccf00f27b5fa0b9b6abfccf03361cb10e
- `equity_features_intraday-0.1.0a3-py3-none-any.whl` aafdfb384e7fc5ad7fa80ea69c89122e259a7db6a087a1f7f193a5f5104f80fa
- `equity_features_intraday-0.1.0a3.tar.gz` a627e4f2c8c491c5c03b0c47be08818fd482b263a2c5a5d73d0d070a84c4d9d9

Third-party wheels (not project artifacts):

- `duckdb-1.5.6-cp312-cp312-win_amd64.whl` 09ff51b230219f0d8b47fc8a1e17fb595ba9fab0c3d96a6de4d00b8ff86b3cf1
- `numpy-2.2.6-cp312-cp312-win_amd64.whl` c1f9540be57940698ed329904db803cf7a402f3fc200bfe599334c9bd84a40b2
- `setuptools-80.9.0-py3-none-any.whl` 062d34222ad13e0cc312a4c02d73f059e86a4acbfbdea8f8f76b28c99f306922

Line endings: the core worktree was checked out with CRLF (git `core.autocrlf=true` on this machine), so the core archive members contain CRLF (for example 61 of 66 text members in the `equity_features` wheel); io and workers members are LF. For every sdist, each member that exists in git was compared with the committed blob (CRLF normalised to LF): all match, none differ (contracts 25, features 69, intraday 26, io-contracts 7, io-sdk 9, duckdb 24, duckdb-sink 10, workers 52 members; 7 or 8 members per sdist, such as `PKG-INFO` and `setup.cfg`, are generated and not in git). Core archive hashes therefore depend on the checkout line-ending setting; the demo `content_sha256` values below do not.

## Results

| Form | install | pip check | demos passed | first attempt | batch time |
|---|---|---|---|---|---|
| all-wheels | exit 0 | exit 0 (No broken requirements found.) | 346/346 | 346/346 | 992 s |
| all-sdists | exit 0 | exit 0 | 346/346 | 346/346 | 1082 s |
| core-wheels-components-sdists | exit 0 | exit 0 | 346/346 | 346/346 | 970 s |
| core-sdists-components-wheels | exit 0 | exit 0 | 346/346 | 346/346 | 962 s |

Demo set per form (346, same list in every form):

- EF3 worker examples, every contract result fixture: `ef3_relative_rv` 64 (RS01-RS24, DV01-DV17, RV01-RV21, PX01, PX02), `ef3_robust_pace` 124, `ef3_breadth_adaptive` 99 (49 declared, 20 observed, 30 adaptive). 287 per form.
- Regression sample, 59 EF1/EF2 demos, the identical list the EF2 run used: first_trade R001, R019; regular_bar_prices R01, R08; gap_endpoint E01, E26; clock C20 present/missing/unknown/future; anchors trades A01/A02, bars A01, bars A01-missing-notional; status S01-S03; reference_close C01-C03; venue_status MV01, MV05, MV10, MV12, MV20, MV24, MV30, MV40, MV43, MV44; ef2_money_flow M05, M26, M34, M36; ef2_retracement T12, T32; ef2_momentum M01, M05, M25, M26, D01, D04, D22, P02, T01, T05, T10; ef2_channels ICH-17, SQ-10, PCT-10, PIV-11, KEL-04, DON-05, ICH-01, KEL-01, DON-01, PIV-01, PCT-01, SQ-01.

All 1384 demo runs (346 x 4) passed on the first attempt. The canonical `content_sha256` printed by each demo was identical across all four forms for all 346 demos. For the 59 sample demos it was also identical to the value recorded in the EF2 run (59 of 59), so those outputs did not change. Per-demo flags and hashes are in the JSON.

Harness disclosures (no demo was affected): my first attempt to enumerate the EF3 case ids ran in the system interpreter and failed with `ModuleNotFoundError: equity_feature_contracts`, so ids were enumerated with the installed all-wheels venv instead (counts 64, 124, 99 as expected); my first run of the results analysis script had a syntax error and was corrected before any result was read. The install script exceeded the tool's foreground timeout and ran in the background; it completed normally.

## Source-tree reads (installed run is not fully standalone)

All packages came from the installed copies in every form. The following still came from source trees as data:

- Example scripts: every demo ran an `examples/*.py` file from the workers worktree (not part of any wheel or sdist).
- Contract JSON from the core worktree `docs` folder, passed with `--contract`: all three EF3 examples (287 demos), `ef1_venue_status` (10) and the four EF2 examples (29), 326 of 346 demos.
- Oracle JSON from the workers worktree `tests` folder, read by the example relative to its own path: `ef1_regular_first_trade_price`, `ef1_regular_bar_prices`, `ef1_gap_endpoint` (6 demos). The examples hash-check it.
- `ef1_clock`, `ef1_anchors`, `ef1_status`, `ef1_reference_close` (14 demos) showed no source-tree read when their scripts were read (they only write the HTML); file access was not traced.
- The default contract lookup walks up from the installed `equity_features` package and cannot resolve from an installed copy; it was not exercised (`--contract` always given where an example accepts it).

## Not run

- unit test suites (owner policy: manual verification only)
- Linux: owner action pending
- real data
- original-source parity
- source rights
- benchmarks
- refusal fixtures and the other non-result fixtures of the EF3 contracts (for example 48 refusals in the relative/RV contract); only result fixtures were driven
- EF1/EF2 demos outside the 59-demo sample
- default contract path resolution from an installed copy
- packages other than the 8 listed
- browser inspection of the generated HTML
- independent artifact audit

No claim of acceptance, release, publication, parity, rights, performance or platform coverage beyond this Windows qualification run is made.
