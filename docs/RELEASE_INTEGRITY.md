# Dependency and experimental release integrity

EQ047/R3/issue53 reviews the existing channel after accepted EQ046. The current core pair is0.0.4a4 and the separate consumer is0.3.0. This review changes documentation only: calculation, test, build, benchmark and consumer sources remain identical to the FOUR source pairs qualified for EQ046. No formula, unit, timing, initialization, coverage, schema, algorithm, execution mode or version changes.

## Dependency and license inventory

Contracts have no base third-party dependency; features require exactly matching contracts0.0.4a4. The optional columnar extra pins NumPy2.2.6 and Arrow20.0.0. The consumer independently requires both matching core packages. Core metadata supports CPython>=3.12,<3.13; the consumer's looser Python declaration does not widen the core's support. Actual supported qualification is CPython3.12 on Windows/Linux; base imports do not require optional backends.

[Machine-readable inventory](DEPENDENCY_INVENTORY.json) records13 public upstream wheel archive hashes verified against their exact PyPI version index records, shipped license/notice file hashes and metadata license expressions/classifiers. Eleven Windows wheel notice sets match actual installed bytes; two Linux-target NumPy/Arrow wheels were inspected on Windows without installation or native execution. Native Linux execution is separately supplied by CI. Relative wheel paths contain no local user paths, credentials or private datasets. These upstream wheels are qualification inputs, not redistributed project artifacts.

| Role | Exact package versions | Recorded licensing evidence |
| --- | --- | --- |
| Project runtime and synthetic consumer | contracts/features0.0.4a4; demo0.3.0 | Apache-2.0 project metadata and actual archive license files |
| Build front end/backend/hooks | build1.2.2.post1; setuptools80.9.0; pyproject_hooks1.3.3 | MIT expression/classifier or shipped text; setuptools vendored license and notice files preserved in inventory |
| Development installer | pip25.1.1 | MIT classifier and shipped full license file; distinct bootstrap installer below |
| Build metadata/platform support | packaging26.3; colorama0.4.6 on Windows | packaging Apache-2.0 OR BSD-2-Clause expression and both texts; colorama BSD classifier and shipped text |
| Type checking | mypy1.15.0; mypy_extensions1.1.0; typing_extensions4.16.0 | MIT expression/classifier for mypy components; typing_extensions PSF-2.0 expression; shipped texts hashed |
| Optional native/columnar execution | numpy2.2.6; pyarrow20.0.0 | BSD/Apache metadata respectively, plus complete shipped notices including native/platform components |

A classifier is not invented as a License-Expression field when that field is absent. NumPy notices include OpenBLAS/LAPACK, GCC runtime exception and, in the inspected Linux wheel, libquadmath LGPL-2.1-or-later; other bundled/source notices include BSD/MIT/Zlib/Apache components. Arrow's full shipped license file contains additional bundled notices, including BSD/MIT/ZPL entries. Top-level package labels therefore do not describe every bundled component. File hashes preserve the inspected complete texts rather than stripping or republishing partial notices. The inventory does not certify legal compatibility, rights to arbitrary input data, all native subcomponents or future upstream wheel builds. Current project archives contain owned Python sources and their Apache license, not bundled NumPy/Arrow/tool binaries; consumers obtain pinned upstream packages separately.

## Build and source provenance

[requirements-dev](../requirements-dev.txt) pins all11 development/backends; all three project build-system declarations pin setuptools80.9.0. Fresh sdist pairs install that backend without dependency resolution and install project archives with --no-index --no-deps --no-build-isolation. Wheel pairs install the actual retained consumer wheel; sdist pairs the retained consumer sdist. Python's fresh venv bootstrap pip was25.0.1 on both OS in the observed final EQ046 CI notices, while development requirements install25.1.1. These are distinct steps, not a claim all environments use the development pip. Actual EQ046 source-main73246b1 manifests record Linux3.12.14; final-main0b6aa566 manifests record Linux3.12.15. Both Windows manifests record3.12.10. Setup-python requests the3.12 minor line rather than a fixed patch; source and final interpreter provenance must be read independently even when project archive bytes match.

Observed final EQ046 run37500435856 resolves current workflow tags to:

| Workflow tag | Actual resolved commit |
| --- | --- |
| actions/checkout@v4 | 11d5960a326750d5838078e36cf38b85af677262 |
| actions/setup-python@v5 | a26af69be951a213d495a4c3e4e4022e16d87065 |
| actions/upload-artifact@v4 | ea165f8d65b6e75b540449e92b4886f43607fa02 |

These are observed provenance, not immutable workflow references: tags can move. Exact version pins, index digest observations and SOURCE_DATE_EPOCH1700000000 repeat-build equality do not make index acquisition hash-locked/hermetic or provide supply-chain attestation. The epoch fixes packaging timestamps, not market availability. Compare within the qualified OS/toolchain; do not invent cross-platform archive identity. Actual clean commit/manifests/current bothOS CI and downloaded archive content/hash/license/typing inspection remain release gates.

[EQ046 receipt](stories/EQ-046_DELIVERY.md) and issue52 record the qualified source73246b1 and finalmain0b6aa5662c10721d405a762925f60cbc2c148ebb. Eight core plus four consumer archives and12 variable reports were inspected; final archives equal FOUR qualified source pairs. Benchmark/resource observations separately bind exact clean source/harness/math/native units/control/shape/statistics, not equal timing or peak bytes. Consumer reports bind the actual installed artifact and core module/distribution metadata before installation, afterward and after execution. SHA digests bind inspected bytes; they are not signatures, credentials or correctness certification of arbitrary code.

## Channel, access and rights

[EQ010 #12](https://github.com/atulsrivas1/equity-features/issues/12) accepted the owner's personal public repository, license and naming/access decision through PR134. It gates this existing experimental channel; it does not reserve registry names or approve a stable/tag/PyPI publication. [Build channel](BUILD_DELIVERY.md) remains successful main Foundation Actions artifacts, with30-day requested retention. Inventory records actual final EQ046 bundle server digests, sizes and expires_at values observed not expired. Server zip digests differ from deterministic inner project archive hashes; the retained channel is not permanent archival. Accepted R3 publications record exact main/run/inner hashes and actual channel expiry; reconstruct after expiry from the recorded commit/pins and requalify the new environment. Never label PR-ref artifacts as the delivered main package. EQ047 also supplements eight earlier accepted R3 issues with actual current expiry/server-digest observations; the inventory preserves their separate original main/run identities without replacing historical package qualification.

Workflows request contents:read and perform builds/tests/artifact retention without package-registry publication or deployment credentials. Development CLI authentication and GitHub's runner mechanism stay outside calculation packages; no credential values are included in this inventory or fixtures. No new publication credential is required by this story. Do not add secrets, environment credential reads, source fetching or publishing inside calculations. Both source and consumer artifacts were inspected for owned namespaces/path/privacy/typing/license boundaries under EQ045; no tracked .env or credential-named file was found in this review. This is a scoped owned-artifact check, not an arbitrary-code secret scanner/security certification.

Public examples are synthetic and repository code carries the selected license. Real-provider/data/source rights and production readiness remain separate future admission. No source datasets or remote custom executor is qualified by R3. Hosted reviewer activation remains unverified GOV005; owner-authorized separate local final-head review is the actual R3 alternative, with identity/commands/findings/limits recorded. No human/hosted review is fabricated.

## Documentation-only acceptance

[Plan](stories/EQ-047_PLAN.md) applies PUBLIC_DEVELOPMENT's unchanged-code documentation publication gates: separate final-head review/all emitted CI, actual published main source equality/owner attribution, bothOS12archive content/hash equality to FOUR qualified EQ046 source pairs and independently checked12 current variable reports/expiry. Current CI repeats complete631units/22examples/typing/installation/execution/benchmark/resource gates; no redundant local installs or second receipt is required. Final actual evidence and postrelease verification are recorded on [issue53](https://github.com/atulsrivas1/equity-features/issues/53) before Done. Then EQ095 independently qualifies the combined installed external consumer, and EQ048 accepts all bounded R3; this review alone does not complete R3.


For inventory reproduction, download the exact upstream wheel filenames referenced in the JSON from their public version index records, compare SHA256 of whole wheel bytes to the index digest, then inspect each listed zip member and compare its separate notice hash. Eleven Windows notice sets were additionally compared to the corresponding installed distribution paths. The two Linux-target wheels were only inspected. Runtime examples and project artifact installation remain the commands in INSTALLING; upstream license inspection is external qualification, not a calculation-package function.
