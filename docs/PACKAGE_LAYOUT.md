# Two-distribution layout

EQ-007. `packages/contracts/src/equity_feature_contracts` owns canonical types,
configuration/results/errors, validation, metadata registry and adapter protocols.
`packages/features/src/equity_features` depends inward on contracts; numerical
families arrive in R1/R2. Future concrete adapters/workers live outside both.
No skeleton module exposes unimplemented calculators. Dependency-light core imports
need no NumPy/PyArrow, source, credentials, calendar or environment configuration.
Explicit columnar extras/compatibility are qualified under EQ-008/011.

Development (Python3.12; EQ-008 qualifies exact tooling):

```text
python -m venv .venv
.venv/Scripts/python -m pip install -e packages/contracts -e packages/features
python tools/verify_imports.py
```

On Linux use `.venv/bin/python`. Install both local distributions together so pip
does not search a public registry for the unreleased contracts dependency. Only
these src trees ship as package APIs; tools/tests/docs remain repository resources.
Each distribution has metadata, its README, Apache license and py.typed marker.
Version0.0.1a0 identifies experimental foundation artifacts; R3 stability and public
publishing remain gated. EQ-009 builds wheels/sdists, clean installs and retains
downloadable internal artifacts with checksums. Until then EQ-007 awaits delivery.


EQ049 adds packages/duckdb, import equity_feature_duckdb, as the optional R4 source
boundary. Its separate requirements-duckdb.txt/workflow/builder/tests/duckdb do not
add DuckDB to pure packages or their runtime/development requirements. Resolver
source/typing checks do not establish R4 canonical or real-data acceptance.


EQ121 establishes the owner-authorized [I/O companion](https://github.com/atulsrivas1/equity-feature-io) and [workers companion](https://github.com/atulsrivas1/equity-feature-workers). Version-marker distributions io-contracts/io-sdk/workers0.1.0a0 have strictly inward metadata dependencies; actual publication acceptance is recorded on [canonical issue278](https://github.com/atulsrivas1/equity-features/issues/278). Worker commands are absent. Existing optional DuckDB source remains here until reviewed/qualified EQ122 extraction; no existing core/import/math changes. [Foundation plan](stories/EQ-121_PLAN.md).
