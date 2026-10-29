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
