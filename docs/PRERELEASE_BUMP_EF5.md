# Coordinated pre-release bump for the EF5 layers - October 28, 2026

PO ruling `work/po-rulings-workers-ef5-2026-10-28.md`. Set of three PRs (core, io, workers). Pre-release label move only.

## Packages moved (this repository)

| Package | From | To | Why (content changed since the last bump) |
| --- | --- | --- | --- |
| equity-features-intraday | 0.1.0a4 | 0.1.0a5 | EF5 library (`_ef5`, `_ef5_config`, `_ef5_registry`) and the additive `SlotFacts.open_price`; catalog digests and result backend_version carry the version |

Pin-only packages keep their versions and follow the pins: in workers, mcp (client pin a1) and service (extras duckdb a11, workers a17); in io the other
packages are unchanged. No tag, no publish, no release claim. Single source: each repository's `tools/_versions.py` (updated) checked by `tools/verify_versions.py`.

## Digests differ from the old versions (confirmed)

- Intraday catalogs (separate catalogs, from the installed a4 and a5 packages): EF5 catalog `0cc61c625779` to `ccb1cdaea7eb`, path-efficiency catalog
  `91ba7fb6a043` to `5f2a343faf87`, intraday (R17) catalog `848e8776ddb1` to `11e0c702d405` (each carries `package_version`).
- Result identity: the same EF5 library result (fixture CD07) encodes to a different SHA-256 under backend_version 0.1.0a5 (`c1f33a43416c...`) than under
  0.1.0a4 (`6b866b365e5c...`), so an a4 artifact and an a5 artifact cannot be confused.
- DuckDB: the receipt `adapter_version` default is now 0.1.0a11, so acquisition receipt identity digests differ from a10 by construction.

## Builder re-pin after the EF5 bump (closed in part)

Commit pins now name the post-bump main commits (core 98778e7, io 94217cf, workers 99b5fed; core `tools/_versions.py` `SIBLING_COMMITS` and `SIBLINGS` carry them and the
sibling versions). Builders were run end to end with the pinned venv against detached checkouts of those commits; each builder builds its archives twice and asserts
repeat equality. Independently, a fresh double build of all 27 packages of the three repositories (SOURCE_DATE_EPOCH, sdists normalized as by
`tools/build_explanations.py`) is byte-equal for wheels and equal for sdists: 27 of 27. Wheel names confirm intraday 0.1.0a5, duckdb 0.1.0a11, workers 0.1.0a17,
client 0.1.0a1, provenance 0.1.0a4 and the earlier versions (contracts 0.0.4a5, features 0.0.4a6, evidence 0.1.0a3, io-sdk 0.1.0a3, mcp 0.1.0a2, duckdb-sink 0.1.0a1,
parquet 0.1.0a2, bundles 0.1.0a2); the conformance and r10 archives carry duckdb 0.1.0a11 and workers 0.1.0a17, the supplied-inputs archive carries intraday 0.1.0a5.

Also in this change: `tools/verify_versions.py` now gates the version pins stated in package READMEs (`name==V`, ``name`V`` or `shortV`; sections headed by an older
version are history and skipped). An altered README fails; stale statements in the workers README were corrected.

**Ran and passed (core):** build_evidence, build_explanations, build_diagnostics, build_continuous, build_research, build_agent_evidence, build_agent_ledger,
build_conformance, build_r10.
**Not run / still open (core):** build_intraday (its gate `tools/test_intraday_band_benchmark.py` already fails on main: the committed EQ-139 measurement predates later
source changes, so there is no intraday builder archive; intraday 0.1.0a5 is confirmed from the fresh wheel build and the supplied-inputs archive), build_r9 and
build_evidence_pilot (re-pinned, not run), build_evidence_evaluation (since retired and stubbed, see docs/RETIRED_BUILDERS.md); superseded 2026-10-29: build_intraday, build_r9 and build_evidence_pilot now run end to end (core PR 749).

The blocker is therefore only partly closed. No release claim until the unrun builders across the three repositories are run or retired.

## Known limits of the README version gate

`tools/verify_versions.py` checks version statements of the forms `name==V`, ``name`V`` and `shortV` (for example `contracts0.0.4a5`) in package READMEs. It does not cover: a wrong version in a
heading (a heading that names an older version opens a section treated as history and skipped); names glued to a version without a separator that the patterns do not know (for example
`workers0.1.0a12`, `workera17`, `MCP0.1.0a1`); versions in prose without the distribution name; and README text outside `packages/*/README.md`. Treat the gate as a net for the common current-pin
statements, not as proof that every README is current. One stale pin of this kind in the io acquisition README was corrected by hand.
