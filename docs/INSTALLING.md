# Install the qualified experimental distributions

Use an actual successful **main** Foundation package checks bundle, named
`foundation-<full-commit>-<OS>`, from the run linked on the accepted story/release.
Select Windows or Linux for the qualified CPython3.12 x64 environment. Inspect its
manifest exact commit/clean-source flag/epoch1700000000 and verify every archive
SHA256 before installing. [Build delivery](BUILD_DELIVERY.md),
[compatibility](COMPATIBILITY.md), [version/replay policy](VERSIONING.md).
The experimental channel requests30day retention; rebuild the recorded commit
with pinned requirements after expiry. No stable/PyPI/tag channel is declared.

## Contents and ownership

| Files | Purpose |
| --- | --- |
| equity_feature_contracts-0.0.4a4 wheel/sdist | Pure owned contracts/typed schemas/discovery/adapter protocols and finite conformance checks; stdlib runtime, optional columnar bridge explicitly imported. |
| equity_features-0.0.4a4 wheel/sdist | Matching pure supplied-input calculations, supported session state/custom APIs; exact dependency on matching contracts. |
| equity_feature_demo-0.4.0 wheel/sdist | Independent Apache-2.0 synthetic public-API consumer and supplied in-memory BAR adapter; outside core, with its own py.typed/license/implementation identity. |
| manifest.json | Exact source/platform/runtime/epoch; `artifacts` has four core digests and `consumer_artifacts` has two standalone consumer digests. |
| benchmark/resource/consumer-<system>-<whl-or-gz>.json | Actual installed diagnostics and consumer-artifact/fingerprint provenance; inspect independently of deterministic archive digests. Timing/memory observations can vary. |

Core archives contain owned package code/licenses/typing and metadata, excluding
examples, benchmark tools, repository fixture files and source acquisition workers.
Standalone consumer archives contain only their own package namespace/build metadata/
license; they cannot bundle core modules. Public examples use synthetic supplied
inputs. Known private-path/credential-file/path-escape checks and actual archive
inspection establish these inspected artifacts, not certification of arbitrary code.

## Fresh wheel installation

Create a separate virtual environment. Windows uses `.venv/Scripts/python`; Linux
uses `.venv/bin/python`. Replace ARTIFACT_DIR with the downloaded bundle directory.
These commands use external package tooling; calculations do not fetch anything.

```text
python -m venv .venv
VENV_PYTHON -m pip install --no-index --no-deps ARTIFACT_DIR/equity_feature_contracts-0.0.4a4-py3-none-any.whl ARTIFACT_DIR/equity_features-0.0.4a4-py3-none-any.whl
VENV_PYTHON -m pip install --no-index --no-deps ARTIFACT_DIR/equity_feature_demo-0.4.0-py3-none-any.whl
VENV_PYTHON -m pip check
VENV_PYTHON -I -c "import equity_feature_contracts as c, equity_features as f; assert c.__version__ == f.__version__ == f.contracts_version == '0.0.4a4'"
VENV_PYTHON -I -m equity_feature_demo.walkthrough
```

The standalone command needs no repository fixtures, editable install or source-tree
import fallback. It verifies independent session OHLC/volume/notional/prefix/final,
governed history/composition/missingness and custom5/100 versus builtin5/103 plus
actual public adapter conformance. [Example catalog](EXAMPLES.md) distinguishes
repository commands requiring licensed sibling fixtures.

## Sdist and optional backend qualification

For a fresh sdist environment, install `setuptools==80.9.0` using external tooling,
then install the three `.tar.gz` files with `--no-index --no-deps --no-build-isolation`.
The exact backend pin avoids fetching build dependencies implicitly. Supported optional
bridges require NumPy2.2.6/PyArrow20.0.0 installed explicitly; neither is required for
the standalone scalar workflow. Development/static typing tools are separate from
core runtime dependencies. Fresh-environment bootstrap pip is reported as observed,
not assumed equal to development pip25.1.1.

Current qualification repeat-builds allsix archives within each tested OS/toolchain,
inspects licenses/typing/package namespaces/private paths, installs actual standalone
wheel or sdist alongside the matching core form, and runs the full unit suite,
22repository examples, isolated public consumer/typing plus benchmark/resource cases.
Before/after consumer installation and after execution, owned core modules and
installed distribution metadata are fingerprinted, excluding bytecode caches.
The consumer installation report binds its actual input artifact SHA256 and those
equal fingerprints. No source rebuild substitutes for the actual retained artifact
at this gate; cross-platform archive byte equality is not promised.

EQ045 adds this delivery qualification, without changing corepair/consumer versions,
equations/schema/modes. Final-head separate review/currentCI/actualmain FOURfreshpair
and receipt publication gates remain required before story acceptance. Issue51 and
its linked receipt record exact accepted commits/runs/digests; package installation
alone does not complete R3 or certify provider readiness/custom callback behavior.


Dependency license notices, pinned build/bootstrap provenance, upstream hash observations and experimental channel expiry/rights limits are recorded in the [integrity review](RELEASE_INTEGRITY.md). Upstream backends/tools are installed separately rather than bundled into these project archives.


EQ095 adds consumer0.4.0 [combined installed qualification](EXTERNAL_QUALIFICATION.md):43 actual synthetic outcomes with independent goldens, actual adapter conformance, typed negatives and unchanged core/catalog. Builder retains this report inside each consumer-installation JSON. Customalgorithmv2/corepaira4 remain unchanged; historical consumer0.3.0 measurements and integrity inventory remain dated evidence. Actual release acceptance requires linked current issue/receipt gates.


## Optional R4 DuckDB adapter — pending delivery acceptance

The optional adapter remains separate from both pure packages. Its initial resolver
API is documented in [DUCKDB_RESOLVER](api/DUCKDB_RESOLVER.md). Development uses
requirements-duckdb.txt and packages/duckdb; no provider credentials are needed.
Qualified main optional bundles are named duckdb-<commit>-<OS>; until issue56's
actual published installation/readback is accepted, do not treat source as delivery.
Each bundle binds six matching core/adapter wheel/sdist archives in manifest.json
and has actual form-specific installed test/typing/core-invariance reports. Install
matching contracts/features archives before adapter, using --no-index --no-deps
--no-build-isolation for project archives and the pinned DuckDB1.5.6 runtime. Sdist
installation uses setuptools80.9.0. R4 remains incomplete; no stable registry/tag.


EQ050 optional0.1.0a2 adds [explicit retained mapping](api/DUCKDB_MAPPING.md),
three strictly typed adapter modules and independently expected mapping fixtures.
The optional builder now qualifies the expanded installed suite/forms; exact pinned
contracts0.0.4a4/DuckDB1.5.6 and pure core remain unchanged. No read/calendar/real
numerical acceptance yet; actual review/artifact/publication gates remain.


EQ051 optional0.1.0a3 adds [bounded original-Parquet reads](api/DUCKDB_READER.md),
four strictly typed adapter modules, explicit supplied sessions/scope/coverage and
physical original occurrence identity. Installed wheel/sdist qualification includes
reader fixtures and synthetic read-cost/native-memory reports. Corepaira4 and pinned
DuckDB1.5.6 remain unchanged. No R4 conformance/private numerical acceptance yet;
final reviewed-head CI and actual delivery/readback gates remain required.


EQ051 clean installation additionally pins NumPy2.2.6 in the optional adapter
runtime. DuckDB1.5.6 create_function requires NumPy in the observed fresh environment;
the development environment had masked this dependency. Install DuckDB1.5.6 and
NumPy2.2.6 explicitly before --no-deps project archive installation. Core runtime
dependencies remain unchanged; NumPy's existing upstream notice/hash provenance
is recorded in [release integrity](RELEASE_INTEGRITY.md). Both native installed forms must verify
this exact runtime. Null timestamps pass through the parser and fail closed, following
[DuckDB UDF null semantics](https://www.duckdb.org/docs/current/clients/python/function).
