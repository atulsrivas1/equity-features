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
