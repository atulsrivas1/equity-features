# Experimental foundation builds and delivery

EQ-009 channel: downloadable **GitHub Actions artifacts from successful main
Foundation package checks**, named `foundation-<commit>-<OS>`. No PyPI/public
registry publication. Public repository readers with appropriate GitHub access
can download authorized code/synthetic artifacts; no private data is included.
The current bundle pins matching experimental corepair0.0.4a4 and independently packaged consumer0.4.0; installation is documented in [INSTALLING](INSTALLING.md). All39builtin batch/23sessionupdate-restore/22conditionalmerge modes remain experimental. Historical channel revisions:
EQ-009 began at0.0.1a0 and EQ-011 adds canonical inputs at0.0.1a1. Current session/history calculations and public extension/SDK APIs retain their documented source-independent inputs and qualification limits. EQ-012 specifications use0.0.1a2.
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
core artifacts in `artifacts`. EQ045 separately records two standalone consumer archives in `consumer_artifacts`; they are repeat-built at the same epoch and inspected before actual wheel/sdist installation. CI logs record tool versions and tests. Download the bundle from the
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

EQ034 adds relative_returns.py as the nineteenth installed synthetic example; all repeated archive/actual-main/fresh pair gates remain.


EQ035 adds declared_breadth.py as the twentieth installed synthetic example; repeated archive/actual-main/fresh wheel-sdist gates remain mandatory.

EQ036 adds feature_composition.py as the twenty-first installed synthetic example. Repeated archive, fresh wheel/sdist, actual-main manifests and final byte-equality gates remain mandatory. No new publication channel.

EQ038 adds legacy_comparison.py as the twenty-second installed synthetic example. It replays captured actual Go observations and verifies public EMA/ATR APIs against independent math; it does not execute unpublished private source in CI. Package archives are unchanged; source-manifest, actual-main and installed example gates remain.


EQ093 adds a separately built synthetic consumer wheel to each isolated core wheel/sdist installation. Installed public module locations/imports and core-file byte invariance are checked alongside22 existing examples and the complete unit suite. The consumer is outside both core distributions; actual main bundles and final source remain separate delivery gates. No custom-code purity/sandbox claim.

EQ043's separately packaged typed synthetic BAR adapter and public pure supplied-case conformance checks retain the existing experimental artifact channel. Both core archives include py.typed; consumer0.2.1 is independently built during each fresh pair install. Actual review/source/CI/artifact receipt is [EQ043](stories/EQ-043_DELIVERY.md); its verification gates apply before Done.

EQ039 adds installedpubliccaller/consumer typing to each fresh pair using pinnedmypy1.15, package-name PEP561 lookup, installedpy.typed/exports/noeditable and THREE independent wrongconfig/unit/case argument diagnostics. Initial directsitepackages typing failed and was corrected; [delivery](stories/EQ-039_DELIVERY.md) records exactreview/source/CI/actualbundle gates. Corepair0.0.4a4 bytes/equations unchanged.

EQ040 builds consumer0.3.0 independently for each fresh pair and runs `python -I -m equity_feature_demo.walkthrough` from installed packages. Supplied batch/chunk/history/composition and existing custom/adapter goldens, absent-input quality, public-only imports, core-byte invariance and installed typing of all three consumer files are required. The [catalog](EXAMPLES.md) distinguishes standalone packaged commands from repository examples with external sibling fixtures. Corepair0.0.4a4 and the experimental channel remain unchanged.

EQ041 executes the isolated installed small benchmark from each fresh wheel/sdist pair after backend installation, saving variable `benchmark-<system>-<whl-or-gz>.json` alongside retained CI artifacts. Its source commit/measurement cleanliness/normalized harness hash, independent parity, native memory units and actual timing/thread/backend provenance are separate from the four deterministic corearchive checksums. [Methodology and full local samples](BENCHMARKS.md) state scope/limits; actual main receipt verifies bothOS smoke JSON without requiring timing-byte equality between runs. Corepaira4 and consumer0.3.0 unchanged.


EQ042 adds six installed resource diagnostic children per fresh core pair, retaining variable resource-<system>-<whl-or-gz>.json beside benchmark JSON. Independently verify exact clean source, normalized diagnostic/native-probe hashes, allsix family parity/bounded records/atomic rejections/caller controls and native memory units. Corearchive determinism does not require diagnostic byte equality. Full21case Windows measurements and scoped reachable Python sizes are documented in RESOURCE_BEHAVIOR.md; corepaira4/consumer0.3.0 unchanged.


EQ045 inspects standaloneconsumer namespace/license/py.typed/privatepath boundaries and requires core module plus installed distribution-metadata fingerprints before/after consumerinstallation and afterexecution, excluding bytecode caches. It retains repeat-built consumerwheel+sdist with separately scoped consumer_artifacts hashes and consumer-<system>-<whl-or-gz>.json actualartifact/source/installfingerprint receipts. Wheelpair installs actualconsumerwheel; sdistpair actualconsumersdist with pinnedsetuptools80.9/noindex/nodeps/nobuildisolation. Existing22examples/completeunits/publictyping/public-only imports/invariance/benchmark/resource gates remain. Independent adversarial archive fixtures reject core namespace contamination/path escapes/known private-path content. These owned artifact checks do not certify arbitrary downloaded code or source rights. Finalreview/currentCI/mainFOURactualpairs/receiptpublication remain required; no numerical/schema/coreversion/channel change.


EQ047 [integrity review](RELEASE_INTEGRITY.md) and [inventory](DEPENDENCY_INVENTORY.json) record actual upstream license notices/index digests, source/action/tool/bootstrap/OS provenance and channel expiry limits. Exact version pins and repeat archive bytes do not imply hermetic acquisition or native license/security certification. Existing experimental channel/credentials outside core remain unchanged.


EQ095 adds consumer0.4.0 [combined installed qualification](EXTERNAL_QUALIFICATION.md):43 actual synthetic outcomes with independent goldens, actual adapter conformance, typed negatives and unchanged core/catalog. Builder retains this report inside each consumer-installation JSON. Customalgorithmv2/corepaira4 remain unchanged; historical consumer0.3.0 measurements and integrity inventory remain dated evidence. Actual release acceptance requires linked current issue/receipt gates.


EQ048 [finalR0–R3 acceptance](R3_ACCEPTANCE.md) maps original receipts, current633unit/strict49/reference/purity/installedconsumer evidence and actualqualified corepaira4/consumer0.4.0 bundles. Its docs-only sources equal095 FOURqualifiedpairs; one reviewedPR/currentbothOSCI/actualfinalarchiveequality/currentreportprovenance/Releasedreadback suffice under PUBLIC_DEVELOPMENT, no newpublicationchannel. Final issue54 records actualSHA/runs/digests/expiry; finiteActionsretention remains explicit.
