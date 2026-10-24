# EF4 installed-artifact qualification run, Windows (2026-10-23)

Installed Windows qualification evidence only. This is a manual qualification run; it does not accept or release anything. Machine-readable per-demo results: `EF4_INSTALLED_QUALIFICATION.json`.

## Sources (origin/main at run time)

- core: `c4e4c70279808fd8462d835fc5b43ec97f0a47e0`
- io: `4ebfa30084ab7ce755b589f2a0d3f8195bc015ad`
- workers: `51f5e7f3d8931acf0ad8d3ae8035c7e0f2ba75c2`

After the run started, core origin/main advanced to `a18f6fd` (PR #713), which adds only `docs/ef4/EF4_SHARED_AMENDMENT.json` and `.md` over the tested `c4e4c70`; no code differs. This report is committed on top of `a18f6fd`.

Platform: Windows 11 Pro 10.0.26300, CPython 3.12.10, pip 25.0.1, setuptools 80.9.0. The method follows `docs/ef3/EF3_INSTALLED_QUALIFICATION.md`.

## Method

1. Fresh detached worktrees of core, io and workers at the SHAs above in a new scratch folder; the shared checkouts were not touched.
2. Built an sdist and a wheel for the same 8 packages by calling `setuptools.build_meta.build_sdist` then `build_wheel` from a venv holding only setuptools 80.9.0: contracts, features, intraday (core); io-contracts, io-sdk, duckdb, duckdb-sink (io); workers. Versions are unchanged from the EF3 run (the code differs, so archive hashes differ). Archives were built once; rebuild reproducibility was not tested.
3. Four fresh venvs (all-wheels, all-sdists, core-wheels-components-sdists, core-sdists-components-wheels), each installed with `pip install --no-index --find-links <form folder> equity-feature-workers equity-feature-duckdb-sink equity-feature-duckdb equity-features-intraday`. A form folder held only the selected archive type plus three third-party wheels (numpy 2.2.6, duckdb 1.5.6, setuptools 80.9.0, copied from the EF3 run's folder). The forms shared nothing but archives. No package index during installs; no `--system-site-packages`. "core" means the three core packages; "components" means the io and workers packages.
4. `pip check` in each venv.
5. From the scratch directory, each demo ran as `python -I -B launcher.py <example.py> --contract <core docs/ef4 JSON> ...` with no PYTHONPATH (`--case ID --output-db ABS --html ABS --run-id SHORT`, or `--refusals`). The launcher printed the `__file__` of the 8 project modules before running the example; every one resolved under that venv's `site-packages`. `EF4G_HARNESS`, `EF4H_HARNESS` and `EF4I_HARNESS` pointed at the vendored expanders in core `tools/contract_fixtures`. Batches ran with core `tools/run_batch.py` (8 workers per form, 900 s per-command timeout); each demo was its own process (no pool), which the session/bar projection routes require. The four form batches ran concurrently on one machine.
6. A result demo passes when exit is 0, the printed line has `verified_readback`, `verified_reopen` and `contract_literal_match` true, the database and HTML were written, and all module paths are installed ones. A refusal run (one process per example, all refusal fixtures of that contract) passes when exit is 0 and every refusal matched, as the example's own check decides.

## Archives (sha256)

- `equity_feature_contracts-0.0.4a4-py3-none-any.whl` b86997228691231e7b3c9b92e04da6219913a008526af217a0a44c1094383e7e
- `equity_feature_contracts-0.0.4a4.tar.gz` 4cc849543af3f141e1f6e6780291d93fb8cf9ad21a481ff36e5f5ca3d41cb029
- `equity_feature_duckdb-0.1.0a9-py3-none-any.whl` 891969ceffa9e48eb1e5030199e9c9b7c9056434e57768981dc70633713fe70c
- `equity_feature_duckdb-0.1.0a9.tar.gz` 497bed950b859dc10edb015680dbc052c0fc08d5b765e55c46d9c6b5a3172b6e
- `equity_feature_duckdb_sink-0.1.0a0-py3-none-any.whl` 7de0cbb74328365b754e4373cb988b4b77c712bf78100a2081c33c88816ff193
- `equity_feature_duckdb_sink-0.1.0a0.tar.gz` 597919dbabfd06236d289a8dfeb7b240ddcac9cf406fab38b926e69ac8131bd0
- `equity_feature_io_contracts-0.1.0a2-py3-none-any.whl` d9a39eebc7e929cd9f7cf4d985fabc9410ef391cd942e7adcb0f94ee4645c67a
- `equity_feature_io_contracts-0.1.0a2.tar.gz` 5665be08593b1bb6466d5c292055dca5b5b448f83cc0d29f2ae776bbb3495f6f
- `equity_feature_io_sdk-0.1.0a2-py3-none-any.whl` 4f3293c40fd45d5878357156be8d79fc470d448dad1c77eb4e899c7bbaa9ec9a
- `equity_feature_io_sdk-0.1.0a2.tar.gz` 1a0c61fa213215640e31d99419d0da7271a7b3fcdfb91d2a14dc3ce678272c92
- `equity_feature_workers-0.1.0a15-py3-none-any.whl` d3f8cc066b4b5fb8be0aafadd06f1512d534ecab99e2212d6ea03cb7b572f17d
- `equity_feature_workers-0.1.0a15.tar.gz` e7340a5c2c0a423d799b6c168727a61ba1d4ba6e9d6cf6e589d2be99ed601691
- `equity_features-0.0.4a5-py3-none-any.whl` fdec73ab10481d7220b5f05410411285e349a2ea174875fae63b36d15a6fd9b8
- `equity_features-0.0.4a5.tar.gz` 3782f5436e3b7f1a44ded24214ef94e7d586dff4bc12e336b0499e0ca7285f93
- `equity_features_intraday-0.1.0a3-py3-none-any.whl` 57b101e8209eaeea409773f637996883cf6358bd4dc561eda1e62005a7bfd517
- `equity_features_intraday-0.1.0a3.tar.gz` e2b58b727ae28a3d85c5a940f787796b412161016884a7fcd2bd7e747e7b7ae2

Third-party wheels (not project artifacts):

- `duckdb-1.5.6-cp312-cp312-win_amd64.whl` 09ff51b230219f0d8b47fc8a1e17fb595ba9fab0c3d96a6de4d00b8ff86b3cf1
- `numpy-2.2.6-cp312-cp312-win_amd64.whl` c1f9540be57940698ed329904db803cf7a402f3fc200bfe599334c9bd84a40b2
- `setuptools-80.9.0-py3-none-any.whl` 062d34222ad13e0cc312a4c02d73f059e86a4acbfbdea8f8f76b28c99f306922

Fixture expanders as checked out in the scratch core worktree (CRLF working copy on this machine, so the hashes differ from the LF hashes in `tools/contract_fixtures/README.md`):

- EF4G (ef4g_fixture_expand.py) 7a757bb239f865943eb2671d471ec096c5639b7c810e41e17387a0769880d9d8
- EF4H (ef4h_fixture_expand.py) e77089d7805970a9b0729db26c404efac9c3e53b8b4bf2f7ab3fcfeb78c01a1d
- EF4I (ef4i_fixture_expand.py) 9c9c4ef0ba4bd2df962c354e7906af91f00f2ff89c6cbc08c41dfe691240aed7

Line endings: the core worktree was checked out with CRLF (git `core.autocrlf=true`), so core archive members contain CRLF (for example 82 of 89 text members in the `equity_features` wheel). Core archive hashes therefore depend on the checkout setting; the demo `content_sha256` values do not. The sdist members were not compared with committed blobs in this run. The io and workers archives each hold one to three CRLF text members (wheel and sdist metadata files), counted with a broad extension filter.

## Results

| Form | install | pip check | demos passed | first attempt | batch time |
|---|---|---|---|---|---|
| all-wheels | exit 0 | exit 0 | 297/297 | 297/297 | about 3556 s (concurrent) |
| all-sdists | exit 0 | exit 0 | 297/297 | 297/297 | about 3556 s (concurrent) |
| core-wheels-components-sdists | exit 0 | exit 0 | 297/297 | 297/297 | about 3556 s (concurrent) |
| core-sdists-components-wheels | exit 0 | exit 0 | 297/297 | 297/297 | about 3556 s (concurrent) |

Demo set per form (297, the same list in every form), per example:

| Example (contract) | result fixtures run | refusal run | refusals driven |
|---|---|---|---|
| ef4_tape (G) | 82 | 1 | 75 |
| ef4_quote_vwap (H) | 69 | 1 | 80 |
| ef4_path_efficiency (I1) | 31 | 1 | 39 |
| ef4_projections (I2) | 111 | 1 | 114 |

Every result fixture of the four contracts ran once (293): tape W01-W22b, TK01-TK19 and PM01-PM06 (82; the window fixtures run once per selected output and once jointly inside the case); quote and VWAP (69); PE01-PE31; projections SP, BP, RX and RP (111). Each case ran its own runs inside one process (the join of per-output and joint runs the example defines), all through adapter, worker, library, separate DuckDB sink, SDK readback, replay and close/reopen. All 1188 demo processes (297 x 4) passed on the first attempt. The canonical `content_sha256` printed by each result demo was identical across all four forms for all 293 result cases. Per-case hashes are in the JSON.

Tape refusals: 75 driven; two (RF18 and RF35) carry the example's `known_adapter_deviation` mark, where a shared adapter validator refuses first with another code (documented in the io tape input notes); the example counts them as expected.

Harness disclosures (no demo was affected): before the full run I profiled the example set with 8 commands in the all-wheels form (the first case and the refusal run of each example, 8/8 passed, 33 s) and deleted those outputs before the full run; the all-wheels batch then re-ran those cases. Nothing failed in any attempt, so there is no failure output to record. Running the four 8-worker batches at once made each batch take about 59 minutes, far longer than the profile suggested, but no command approached the 900 s timeout.

## Source-tree reads (installed run is not fully standalone)

- Example scripts: every demo ran an `examples/ef4_*.py` file from the workers worktree (not part of any wheel or sdist).
- Contract JSON from the core worktree `docs/ef4` folder, passed with `--contract` in every demo.
- Fixture expanders from the core worktree `tools/contract_fixtures` (G, H and I2 examples; the I1 example needs none).
- The default contract lookup walks up from the installed `equity_features` package and cannot resolve from an installed copy; it was not exercised.

## Not run

- unit test suites
- Linux
- real data / real source
- original-source parity
- source rights
- benchmarks
- Parquet or bundles round trip for notional cells
- tape generator fixtures G01-G03
- packages other than the 8 listed
- browser inspection of generated HTML
- independent artifact audit
- default contract path resolution from an installed copy

No claim of acceptance, release, publication, parity, rights, performance or platform coverage beyond this Windows qualification run is made.
