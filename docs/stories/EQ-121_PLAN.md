# EQ-121 concrete foundation plan

Canonical story: [#278](https://github.com/atulsrivas1/equity-features/issues/278), E18, milestone15. GOV014/GOV015 verified Closed/Project Done; published baseline `7a6db8c2317de1ee9dd9116e0897cbf6445e359e`. The dedicated R4.1 execution session now owns bounded delivery; one active story. This plan precedes component implementation.

## Contracts and scope

Create the owner-authorized public Apache-2.0 `equity-feature-io` and `equity-feature-workers` repositories. Canonical issues, epic/milestone and lifecycle remain here. Component PRs link full canonical issue URLs without auto-closing keywords. Carry attribution, privacy, separate final-head review and delivery agreements to both repos. Default branches contain a reviewed foundation; no formulas or source schema change.

Foundation distributions: `equity-feature-io-contracts` / `equity_feature_io_contracts`, `equity-feature-io-sdk` / `equity_feature_io_sdk`, and `equity-feature-workers` / `equity_feature_workers`, initially `0.1.0a0`. Contracts depends only on canonical `equity-feature-contracts==0.0.4a4`; SDK only on matching I/O contracts; workers depends on matching SDK. Foundation imports expose package versions only; they do not pretend to implement pending sink/factory/worker APIs. Backend implementations arrive under EQ122/126/127, preserving `equity-feature-duckdb` identity. No entry points, CLI, scheduling, import registration, source reads or writes are implemented in the worker skeleton.

Supported execution remains CPython3.12 x64 Windows/Linux. Pin existing setuptools80.9.0/build1.2.2.post1/mypy1.15.0 and relevant dependency/toolchain versions. Native CI builds wheel and sdist twice at the established packaging epoch, compares normalized bytes, inspects namespaces/license/py.typed/dependencies, then qualifies each actual form in a fresh venv outside source imports. Experimental successful-main Actions bundles request30day retention; record actual hashes/expiry and downloads before release. No stable registry or tag.

Core prerequisites for component CI are built from the exact accepted public core commit above; no public index fallback for project packages. This is source-pinned dependency preparation, not a claim of native private qualification. Release records bind component source/producer/form and dependency archive hashes. Core source remains unchanged by EQ121.

## Independent expected checks frozen before code

- All three declared package versions are0.1.0a0 and imports resolve inside fresh site-packages, with no editable source path.
- Metadata dependency graph has only the named inward edges; canonical contracts has no I/O/worker edge. Wheel/sdist contain Apache license, py.typed and their own namespace only.
- Importing all foundation packages performs no acquisition/registration; worker has no console/script entry points and no commands. No backend dependency is required.
- A core-only fresh installation imports/discovers all39 built-ins with I/O/worker imports explicitly forbidden. Installing companion foundations preserves canonical core file and distribution metadata fingerprints.
- Strict installed typing resolves each public package through PEP561. Wheel and sdist repeat builds match within each native toolchain; cross-OS byte identity is not promised.
- Public governance/docs link canonical issue, architecture, future story boundaries, experimental installation/build channel and same-story continuity. Review actual final heads independently before merge.

## Delivery and Done

Create repo baselines without implementation, open early component PRs and a linked core planning/evidence PR. Record actual separate final-head reviewers, findings disposition, native CI and actual main artifact download/hash/form installation/readback. Advance exact eight stages on canonical issue only. Record repository access/default branches/owner attribution and accepted artifact/version map in this plan's delivery receipt and each affected SESSION_HANDOFF. EQ122 is next only after EQ121 Done. No R5 execution.