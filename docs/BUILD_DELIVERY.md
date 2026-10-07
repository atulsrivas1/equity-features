## EQ129 Windows process qualification rework / In progress

Canonical286 returned Test -> In progress in [6032201654](https://github.com/atulsrivas1/equity-features/issues/286#issuecomment-6032201654). Required PR DuckDB sink run [37579927602](https://github.com/atulsrivas1/equity-feature-io/actions/runs/37579927602) failed three installed Windows recovery cases: lookup remained BUSY after the harness terminated/waited the venv launcher. Successful push37579924006 does not clear that failed gate. Earlier source receipt83f2a9889b445018aa50650ab5a7e69cf9b6222f086340a4d4d97a36f88c28c1 and metadata readbackd1915f91d0f24bf28e724fff2937e5fc5e02c06f13451020461ab7e283e7132d remain historical qualification of their stated heads, not acceptance of the corrected harness or release evidence.

Committed-head reviewer independently passed all nine refined process tests in42.728s; found P3 broken CPython source citation (nonexistent PC/venvlauncher.c). Corrected to PC/launcher.c, whose build binding is [venvlauncher.vcxproj](https://github.com/python/cpython/blob/v3.12.10/PC/venvlauncher.vcxproj). This document-only correction requires renewed head review; the original finding is preserved. Separate local automated reviewer /root/eq121_component_review independently reproduced the harness assumption with twelve disposable Windows venv children: every launcher PID differed from its interpreter PID; every actual runtime handle remained nonsignaled immediately after launcher termination/wait; the byte lock remained held in two of twelve probes. Waiting the actual runtime handle established lock reacquisition in all twelve. The author separately observed differing wrapper/runtime PIDs and WAIT_TIMEOUT after wrapper exit. These are test-owned diagnostics, not a backend defect demonstration or universal failure rate. CPython's [3.12 venv launcher source](https://github.com/python/cpython/blob/v3.12.10/PC/launcher.c) distinguishes launcher and interpreter processes.

Correction is confined to the two DuckDB sink process test fixture files. Review found a further pre-checkpoint timeout/cleanup gap; it was corrected before source freeze. A generated per-child ownership nonce and actual interpreter PID are emitted in a startup handshake before backend imports/storage. The parent validates ownership and retains the actual Windows process handle before sending the required startup acknowledgement; EOF before acknowledgement cannot resume SQL. Phase checkpoints, including source_wal, must match that same owner. Termination requires the retained runtime handle to signal exit before recovery/storage observation, then waits the launcher; nested cleanup closes owned handles/pipes and attempts every child. The reviewer independently injected a malformed phase nonce in an owned temporary fixture: rejection, actual owner exit, all pipe closure, STAGING lookup and full result recovery passed in5.896s. This diagnostic covers the working refinement, not final-head/native acceptance. Existing live-owner BUSY, five interrupted recovery boundaries, receipt/full-result bytes, two-writer conflict/replay and source database-plus-WAL invariance assertions remain. All nine local development tests passed in39.451s before renewed review; native fresh wheel/sdist qualification is pending. No sink/source/SDK/pure/extension/worker runtime, mathematics, package version or accepted private binding changes; no private execution.

Next freeze corrected source and continuity, renew separate exact-head review, enter Test and require every current PR check plus actual native fresh artifacts/source guards. Record new qualification separately, renew final metadata/head review, then exact-head publication and successful actual-main artifacts/readbacks before Released/Done. EQ130 follows accepted129. One active story; stop before R5/providers/services/registry/stable tags/private generation. Earlier snapshots below preserve history; the live Project is status authority.

## EQ129 source qualification / final documentation review

Canonical286 Test6032051791. Source IOdfea32211edef36178d91f35723a8aac8deb96ba / worker8ee8719eda773efef838805475173f2b474488df / core778c5980b13a4fb6a2f0e339230dc80c1c479f6f completed separate local automated reviews6032044565/6032045184/6032045794, no unresolved findings. Actual local repeat/current native/fresh forms and all source CI passed. Receipt SHA256 83f2a9889b445018aa50650ab5a7e69cf9b6222f086340a4d4d97a36f88c28c1 verifies146 archive files/sixteen actual ZIP digests/all202 downloaded files/current source/probe/harness/report identities/Atul ownership/all three public blob trees/finite expiry. Counts include repeated current dependencies and16 historical candidate archives, not146 unique packages. Source receipt is qualification, not actualmain release acceptance.

Four fresh native matrix forms each six meaningful methods/nine full source-result-sink routes, installed9package/exact3engine versions, core-only absence/deny/calculation, dependency-light extension without calculation/fixture/backends, full composed imports/public external typing/three invalidcalls/two real offline resolver conflicts plus two fresh forcedpipcheck conflicts and exact pure package fingerprints pass. Four aligned worker freshforms/public versions/typing/provenance/coregoldens pass. Nonworker matrix archives equal accepted EQ128 native artifacts; Windows allmatrix/current+historical and worker archives equal local committed repeats. Baseline core633/factory21/publication25/source94+30SDK16numerical/Parquet17physical8process/DuckDBsink18physical9process/extensions12methods21cases18facts stay separately qualified current. Actual report runtimes: matrix: Linux CPython3.12.15, Windows CPython3.12.10; worker: Linux CPython3.12.14, Windows CPython3.12.10; core: Linux CPython3.12.14, Windows CPython3.12.10. No runtime extrapolation between producers.

Custom source500/51200/102.6 remains distinct from minute source8/11.625/notionalnull/MISSING_INPUT. All12 complete facts/readback metadata/quality/UTCns/units/nulls/evidence and source catalog/original/optimized Parquet byte invariance pass; source WAL absent before/after only. Worker.a1 changes version/dependency/build/probe metadata, exports version only; no commands/jobs/claims/scheduling/catalog/generation. Pure/source/SDK/backend/extension runtime/math unchanged; accepted private immutable bindings retained without execution. No new performance/rights/remote safety/processdurability/hardRSS/human/hosted claim.

Next freeze these final documentation heads, renewed exact-head separate review/current CI/current146archives/16ZIP202files source/channel guards, exacthead publication/successful actualmain artifact equality/sourceowner/report/expiry readback before Released/postreadDone. EQ130 final audit follows; STOP before R5/providers/services/registry/stabletags/privategeneration. Earlier snapshots below remain historical; live Project is authority.

## EQ129 supported combination under qualification

The concrete [canonical matrix plan](https://github.com/atulsrivas1/equity-features/blob/codex/eq-129-compatibility-matrix/docs/stories/EQ-129_PLAN.md) freezes core/contracts0.0.4a4, IO contracts/SDK0.1.0a2, standalone DuckDBsource0.1.0a8, both sinks0.1.0a0, exampleextensions0.1.0a0 and workers skeleton0.1.0a1. Optional engines are DuckDB1.5.6/NumPy2.2.6/PyArrow20.0.0, explicitly installed only for full composition. Core works independently; extension needs only canonical contracts+SDK. Workers.a1 pins SDK.a2 and exports version only, no commands/runtime. Historical workers.a0/SDK.a0 remains separately scoped; forcing oldworker.a0 with newSDK.a2 or IOcontracts.a1 with SDK.a2 must fail actual resolver/pipcheck. This does not certify untested versions/platforms.

Migration: consumers keep original pure contracts/features imports. Standalone acquisition imports equity_feature_duckdb; output implementations equity_feature_parquet/equity_feature_duckdb_sink and custom extension examples remain explicit consumer-selected dependencies. Never add I/O/workers to calculation requirements or rely on automatic registry discovery. Choose a complete declared artifact combination, run pip check, preserve canonical schema/algorithm/config/source/timing/units/nulls, and retain per-backend physical/resource/retention/rights limits. No private/provider/backend/source/math behavior is changed by matrix tests. No source/WAL-present/private rerun is claimed; accepted immutable private receipt bindings remain intact.

Actual native/fresh-form matrix and separate final-head review/current artifact publication/readback remain pending. Old accepted story evidence below stays historical. This qualification does not implement R5 or authorize stable tags/registry/services/private generation.

# Experimental foundation builds and delivery

## Current optional ownership — EQ122

Current optional DuckDB source/tests/API/qualification harness and its successful-main experimental channel are in [equity-feature-io](https://github.com/atulsrivas1/equity-feature-io). Core owns only contracts/features plus the external consumer example. The active core optional package/test/workflow/builder/development requirement is removed after verified standalone main7475e1e publication. [Migration](DUCKDB_MIGRATION.md), [standalone receipt](stories/EQ-122_STANDALONE_RECEIPT.json) and [canonical issue279](https://github.com/atulsrivas1/equity-features/issues/279) bind compatibility and actual acceptance gates. Purepair0.0.4a4 modules/metadata/schema/math remain byte-identical; no I/O/workers dependency is introduced. Original R4 ownership/version/workflow paragraphs below describe historical delivery and are retained as chronology, not current build instructions.

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


## Optional DuckDB artifact channel

EQ049 tools/build_duckdb.py builds matching unchanged core and optional adapter
wheel/sdist archives twice, normalizes sdists at the existing epoch and requires
byte equality/namespace-license-typing/private-path inspection. Each form is
installed in a separate fresh environment outside source: core without DuckDB,
then pinned DuckDB and actual adapter archive, public resolver tests, installed
strict typing and core import/registry with DuckDB forbidden. Actual installed core
module/distribution-metadata bytes must match before/after adapter install/execution.
The optional bothOS workflow retains dist/duckdb under duckdb-<commit>-<OS> for
requested30days. Successful main run, actual download/hash/report inspection and
fresh published-artifact installations precede Released/Done. Source builds/PR
artifacts are review evidence only; core Foundation workflow remains independent.


EQ050 optional0.1.0a2 adds [explicit retained mapping](api/DUCKDB_MAPPING.md),
three strictly typed adapter modules and independently expected mapping fixtures.
The optional builder now qualifies the expanded installed suite/forms; exact pinned
contracts0.0.4a4/DuckDB1.5.6 and pure core remain unchanged. No read/calendar/real
numerical acceptance yet; actual review/artifact/publication gates remain.


EQ051 optional0.1.0a3 expands actual installed bothOS wheel/sdist qualification to
bounded original-Parquet reads with supplied sessions/coverage,62 independent cases,
strict4 and retained read-<system>-<form>.json synthetic timing/parity/native-lifetime
peak reports. Clean UDF runtime pins DuckDB1.5.6/NumPy2.2.6 separately from unchanged
pure packages. SQL/materialization/copy costs and whole-process high-water limits
are explicit; selected file bytes are not measured I/O. [Receipt](stories/EQ-051_DELIVERY.md)
binds actual source forms/publication gates; no R4 conformance/private acceptance yet.


EQ052 optional0.1.0a4 adds [supplied calendar/history/reference governance](api/DUCKDB_GOVERNANCE.md)
with five strictly typed adapter modules and expanded installed independent fixtures.
Existing contracts/math/source isolation and DuckDB1.5.6/NumPy2.2.6 pins remain
unchanged. Calendar authority, row-presence certificates, UTCdaily/RTH and reference
availability stay explicit; actual review/installed/artifact/publication gates on
issue59 remain before Done. R4 conformance/private numerical acceptance still open.


EQ052 [delivery receipt](stories/EQ-052_DELIVERY.md) binds source823ae1d, optionala4,75installed cases/strict5/fouractual sourceproducer forms/current20native reports. Unchanged purecore/consumer; final receipt publication/readback precede Done.


EQ053 optional0.1.0a5 adds [bounded acquisition evidence](api/DUCKDB_EVIDENCE.md): cumulative original/catalog pre-post hashes, supplied optimized pins, normalization/source receipts and explicit observed-versus-pinned limits. Six typed modules, independent actual-Parquet mutation/budget/pin/cancellation/identity fixtures. Corepaira4/math/schema/runtimepins unchanged; current installed forms/measurement/finalreview/artifact publication gates remain beforeDone.


EQ053 [receipt](stories/EQ-053_DELIVERY.md) binds correctedsource db5c509, optionala5/90cases/strict6/fouractualdownloadedforms/current20reports/verificationcosts and resolvedP2. Final receipt/publication/readback gates remain.

EQ054 optional0.1.0a6 adds [actual installed SDK conformance](api/DUCKDB_CONFORMANCE.md): thirty actual DuckDB/Parquet outcomes and sixteen independent numerical/unit/status/source-binding assertions. The standalone public example requires site-packages imports for installed acceptance. Six adapter modules plus example are strictly typed; actual bothOS wheel/sdist builds retain conformance reports, expanding optional/Foundation native reports to24 while archives remain24. Corepaira4/consumer0.4.0/math/schema/runtimepins remain unchanged. Source checks are not installed delivery; final review, currentCI, fourfresh downloaded forms and actual publication/readback remain required. Private real numerical qualification stays separate under EQ055.

EQ054 [receipt](stories/EQ-054_DELIVERY.md) binds source6180247/optionala6/92cases/strict6+example1/fouractualforms/30SDK16numeric/current24reports. Final reviewed receipt/publication/readback remain.

EQ055 optional0.1.0a7 moves strict UTCns SQL parsing into a connection-local native exact-integer macro after real-source callback diagnostics. ASCII ISO guards/null/calendar/clock/fraction/int64bounds match Python mapping, including both int64 endpoints; Unicode-digit clock/fraction permissiveness is narrowed. [Methodology](api/DUCKDB_REAL_QUALIFICATION.md) records94source cases/strict7 and frozen private independent goldens; no current installed/private numerical acceptance yet. Core/math/schema/canonical identity/runtimepins remain unchanged; receipt binds actual adaptera7. Current installed SDK/CI/actualmain/fourfreshrealforms/review/publication/readback remain required.

EQ055 [receipt](stories/EQ-055_DELIVERY.md) binds optionala7/source9a82f1d/94tests/current24archives24reports/four delivered synthetic forms and four private forms each68numerical9acquisitions3blocked/core isolation. Final reviewed receipt/publication/Released readback remain.

EQ056 [R4 audit](R4_ACCEPTANCE.md) reconciles all eight numbered stories, both actual layers and optionala7/corea4/current24archives24reports. Documentation only; acceptedEQ055 forms may be reused only with actual final archive equality/currentreport+harness/privatehash/livechannel/publication/Released readback. Exact finalhead/workflows/channels remain on issue63.
