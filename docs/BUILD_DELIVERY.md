# Experimental foundation builds and delivery

EQ-009 channel: downloadable **GitHub Actions artifacts from successful main
Foundation package checks**, named `foundation-<commit>-<OS>`. No PyPI/public
registry publication. Public repository readers with appropriate GitHub access
can download authorized code/synthetic artifacts; no private data is included.
The bundle pins its experimental R0 distribution version in package metadata;
EQ-009 began at0.0.1a0 and EQ-011 adds canonical inputs at0.0.1a1. These are
foundation contracts, not production calculators. EQ-012 specifications use0.0.1a2.
R0 review repair is0.0.1a6.post1; original verified foundation is0.0.1a6; [acceptance evidence and actual bundles](R0_ACCEPTANCE.md).
30-day retention is requested, subject to repository limits; record actual expiry
on each issue. After expiry, rebuild from the recorded commit with the pinned
requirements; retained artifacts are a delivery channel, not permanent archival.

```text
python -m pip install -r requirements-dev.txt
python tools/verify_imports.py
python tools/check_boundary.py
python -m mypy --strict packages/contracts/src packages/features/src examples/in_memory_adapter.py
python tools/build_foundation.py
```

The build tool creates both wheels and sdists twice, compares SHA256 bytes,
inspects contents/license/py.typed, and installs each pair in separate fresh venvs
with no package-index fallback for project packages. Sdist install uses the exact
setuptools build pin. Fresh environments install pinned NumPy/PyArrow to run
installed core/columnar unit tests and both canonical/adapter synthetic examples. Core
import isolation is checked separately without optional backend access. Before
building, only previous generated project wheels/sdists are removed from checked
workspace output directories; unrelated files are preserved. SOURCE_DATE_EPOCH
1700000000 fixes wheel timestamps; sdist tar ownership/mode/mtime and gzip headers
are canonicalized at that epoch. This timestamp is a packaging convention, not
market time or an availability claim. Repeatability is within a tested OS/toolchain;
cross-platform archive byte identity is not promised.

`manifest.json` binds source commit, Python/OS, epoch and SHA256 of exactly four
artifacts. CI logs record tool versions and tests. Download the bundle from the
recorded main run, compare all file hashes/manifest commit, then clean-install.
Only after actual download and verification is an implementation Released/Done.
Later foundation revisions retain commit identity and update the experimental
version when public APIs change. CI artifacts from PR refs are review evidence;
main artifacts are the declared delivery. See issue evidence for current run IDs.

## Pure-boundary gate

`check_boundary.py` permits reviewed stdlib/inward imports and an explicit backend
API surface in BACKEND_APIS. Only the current in-memory NumPy arrays/types and
Arrow arrays/schema/types/table constructors are admitted. Unknown backend API
paths and submodules fail, even without a known read/write prefix. Imported aliases,
name/attribute alias chains and annotated/named aliases resolve conservatively.
Backend module namespaces cannot escape via containers/arguments/returns; internal
backend namespace reexports and wildcard imports are rejected. New API paths require
review before extending this surface. Current shipped code contained no backend I/O;
the repair closes guard gaps such as genfromtxt/loadtxt/input_stream and their aliases.

38negative and10positive scanner-only fixtures test these policies; fixtures perform
no file access. Existing source/provider/filesystem/process/clock/reflection/dynamic
execution and common I/O restrictions remain. Global conservative alias resolution
can reject shadowed names; resolve ambiguity explicitly rather than waive the gate.
This is a project-owned AST development policy, not a runtime sandbox or proof about
arbitrary third-party/native code. Instance/object behavior and source truth still
require typed admission, review and tests. Passing CI does not certify source rights.

Primary guidance: [build frontend](https://build.pypa.io/en/stable/) and
[GitHub artifact retention/downloads](https://docs.github.com/en/actions/tutorials/store-and-share-data).
Artifact checksums and actual installations establish delivery; merged source
alone and editable wheels alone do not.

## R1 channel evolution

0.0.2a0 adds twelve experimental batch bar/price calculations. The foundation-prefixed artifact channel is retained; manifests bind the exact source/runtime/hashes as before. Clean wheel/sdist installs now execute session_bars.py as well as both foundation examples and all unit tests. Current supported behavior and migration are in [SESSION_BARS](api/SESSION_BARS.md); actual delivery remains gated by successful main bundles and fresh installed execution.

EQ019 adds the synthetic session_trades.py example to clean wheel/sdist installed checks. Five runnable examples and all unit cases execute against actual installed packages; runtime pins and experimental main artifact channel remain unchanged.


EQ033/0.0.3a0 adds action_policies.py as the twelfth synthetic clean-install example. Both wheel/sdist pairs retain identical build, source-manifest and main artifact gates; no new publication channel.


EQ028 adds history_averages.py as the fourteenth installed synthetic example; the same repeat archive/fresh pair/main artifact gates apply.


EQ029 adds history_recursive.py as the fifteenth installed synthetic example; all existing repeated archive and actual main installed gates apply.


EQ030 adds history_volatility.py as the sixteenth installed synthetic example; existing actual-main/repeated archive/fresh pair gates remain.

EQ031 adds daily_volume.py as the seventeenth installed synthetic example; all actual-main/repeated archive/fresh pair gates remain mandatory.

EQ032 adds interval_volume.py as the eighteenth installed synthetic example; all repeated archive/actual-main/fresh pair gates remain.
