# Foundation compatibility and environment policy

EQ-008. R0 supports only CPython3.12 x64, Windows and Linux, with the actual patch
and OS reported by each CI job. Local evidence: CPython3.12.10 on Windows AMD64.
Linux/Windows clean matrix installs must pass on the final PR head before acceptance.
Other Python versions, macOS/ARM, native builds and provider SDKs are unqualified.
The Python metadata range is >=3.12,<3.13; it is not a claim about every patch/OS.

The core contracts is stdlib-only; features depends on matching contracts. Optional
`columnar` uses **NumPy==2.2.6 / PyArrow==20.0.0**. These are intentionally narrow
compatibility ranges; no latest-version or broad backend promise. Exact int64
extremes, UTC nanoseconds and nulls round-trip in smoke checks. R0 tests contract
interoperability as it is added; R1/R2 qualify numerical kernels. Polars/native
acceleration remains absent until a profiled later story. Backend I/O APIs are
never exposed by calculation contracts, even though PyArrow itself contains I/O.

Create an isolated venv and use the fully version-pinned development requirements:

```text
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements-dev.txt
.venv/Scripts/python -m pip install --no-build-isolation -e packages/contracts -e packages/features
.venv/Scripts/python -m pip check
.venv/Scripts/python tools/verify_compatibility.py
```

Linux uses `.venv/bin/python`. Pins cover build, typing, optional runtime and their
applicable transitive dependencies; colorama is Windows-only. Setuptools80.9.0 is
pinned in both build metadata files. The lock records versions, not wheel hashes;
EQ-009 records artifact hashes/provenance, and R3 performs broader release integrity.
Dependency changes require a numbered change, clean installation and exact-head CI.
No global install, public package publication or credentials are required.

Primary references consulted: [setuptools pyproject configuration](https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html)
documents src discovery/SPDX metadata support since77;
[PyArrow20 installation](https://arrow.apache.org/docs/20.0/python/install.html)
and [NumPy2.2.6 distribution metadata](https://pypi.org/project/numpy/2.2.6/)
describe upstream installation. Actual matrix checks, not upstream compatibility
alone, establish this repository's qualified foundation. Build artifacts arrive EQ-009.


## Optional DuckDB qualification

EQ049 optional equity-feature-duckdb0.1.0a1 pins DuckDB1.5.6 and the existing
contracts0.0.4a4. requirements-duckdb.txt is a separate development/build environment;
requirements-dev.txt and both core runtime dependencies are unchanged. Optional
Windows/Linux CI tests metadata resolution and clean actual wheel/sdist forms.
Core import/discovery runs with DuckDB absent/forbidden before/after optional
installation; core-file/metadata invariance is checked. Pending review/CI/artifact
acceptance on issue56; no broader version/platform/source readiness promise.

[Optional upstream inspection](DUCKDB_DEPENDENCY_INVENTORY.json) records actual
CPython312 Windows/Linux wheel SHA256 matched to the PyPI index and shipped notice
hashes. Windows installed notices match its wheel; Linux wheel inspection is not
native execution. DuckDB foundation MIT and experimental Spark Apache2 notice
texts remain upstream; metadata is not a universal/native dependency certificate.


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


EQ052 optional0.1.0a4 adds [supplied calendar/history/reference governance](api/DUCKDB_GOVERNANCE.md)
with five strictly typed adapter modules and expanded installed independent fixtures.
Existing contracts/math/source isolation and DuckDB1.5.6/NumPy2.2.6 pins remain
unchanged. Calendar authority, row-presence certificates, UTCdaily/RTH and reference
availability stay explicit; actual review/installed/artifact/publication gates on
issue59 remain before Done. R4 conformance/private numerical acceptance still open.
