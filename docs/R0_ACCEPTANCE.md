# R0 foundation acceptance — 2026-10-05

All EQ-001–016 acceptance and actual delivery gates are met. The scope is the
experimental design/contracts/repository foundation, not the later full calculation
package phase. The R0 milestone contains 16 EQ stories and 3 accepted governance items;
all 19 are closed, all 16 EQ Project statuses are Done. Milestone closure follows verification of this report’s publication and final-head/main
checks; the live milestone records that completed delivery decision.

## Delivered behavior

39 frozen V1 IDs have accepted formulas/units, initialization, coverage, causal timing,
adjustment and edge references. Both distributions are experimental **0.0.1a6**:
`equity-feature-contracts` owns immutable canonical inputs, supplied sessions/windows/
C/K/E/configuration, typed result/quality/evidence/errors, semantic validation,
explicit owned normalization, immutable discovery and dependency-light adapter
protocols. `equity-features` depends inward and reexports discovery. Both include
Apache-2.0 metadata, py.typed, wheels and sdists. Core imports use stdlib only;
Arrow/NumPy bridges are explicit optional imports and copy their inputs.

The 39-ID catalog and custom caller namespaces are metadata only. Every actual
batch/update/restore/merge calculation capability is false. Formula text is never
executed; custom callbacks remain EQ-093/R3. Adapter interfaces are declarations,
with one outside-package synthetic historical ordinary-trade example. Source coverage,
chunk coverage and acquisition bounds are distinct from calculation eligibility.
Missing, observed-empty, unavailable, null and zero remain distinguishable.

## Verified gates and review

- 123 independent exact mathematics/policy references: 17 session, 26 quote, 31 history,
  26 context and 23 timing. They establish specification examples, not production kernels.
- 170 unit tests, including 25 adapter and 22 registry cases, pass in both OS CI and
  fresh installed wheels/sdists. 14 negative boundary fixtures pass. Registry parity
  checks 39 IDs/releases and 31 table formulas against accepted public documents.
- Strict mypy checks 14 source files, including static HistoricalAdapter assignment
  in the synthetic example. Canonical/result Arrow precision/masks are covered.
- Core/inward import isolation, compatibility pins, licensing/content checks,
  repeat four-artifact SHA256 parity within each OS/toolchain and clean installations
  with both executable synthetic examples pass. No cross-OS byte parity is promised.
- Six exact-head checks and all main checks/workflows passed for final implementation
  PR141, head `67be802cf30177e4b6958cdd9ac0d4cc199b23ed`, squash `8a857f1270a1b9a976ed8404ed70de9facd5636a`. All 15 changed
  Git blobs matched GitHub published bytes. Both actual main bundles were downloaded,
  manifest commit/clean source and every archive hash/content verified, then four
  additional fresh wheel/sdist pair installations passed 170 tests and both examples.
- Review was author self-review plus CI, as owner-authorized. No independent reviewer
  or hosted review bot is claimed. GOV-005/PR120 remains explicitly deferred.

## Story evidence

| Story | Issue / acceptance evidence | Delivered outcome |
| --- | --- | --- |
| EQ-001 | [#2](https://github.com/atulsrivas1/equity-features/issues/2) | 39-ID scope |
| EQ-002 | [#3](https://github.com/atulsrivas1/equity-features/issues/3) | Session/trade mathematics |
| EQ-003 | [#4](https://github.com/atulsrivas1/equity-features/issues/4) | Quote sampling/state/time mathematics |
| EQ-004 | [#5](https://github.com/atulsrivas1/equity-features/issues/5) | Historical initialization/windows |
| EQ-005 | [#6](https://github.com/atulsrivas1/equity-features/issues/6) | Baseline/relative/breadth mathematics |
| EQ-006 | [#7](https://github.com/atulsrivas1/equity-features/issues/7) | Timing/adjustment policy |
| EQ-007 | [#9](https://github.com/atulsrivas1/equity-features/issues/9) | Two-distribution boundary/layout |
| EQ-008 | [#10](https://github.com/atulsrivas1/equity-features/issues/10) | Qualified runtime/dependency pins |
| EQ-009 | [#11](https://github.com/atulsrivas1/equity-features/issues/11) | Builds/CI/import policy/artifact channel |
| EQ-010 | [#12](https://github.com/atulsrivas1/equity-features/issues/12) | Apache licensing/release access |
| EQ-011 | [#14](https://github.com/atulsrivas1/equity-features/issues/14) | Canonical input/columnar contracts |
| EQ-012 | [#15](https://github.com/atulsrivas1/equity-features/issues/15) | Supplied specifications/config identity |
| EQ-013 | [#16](https://github.com/atulsrivas1/equity-features/issues/16) | Result/quality/evidence/error contracts |
| EQ-014 | [#17](https://github.com/atulsrivas1/equity-features/issues/17) | Semantic validation/explicit normalization |
| EQ-015 | [#18](https://github.com/atulsrivas1/equity-features/issues/18) | Immutable discovery/scoped metadata |
| EQ-016 | [#19](https://github.com/atulsrivas1/equity-features/issues/19) | Adapter protocols/synthetic conformance |

## Actual final implementation artifacts

Both successful main bundles contain the two wheels, two sdists and manifest.
Requested retention is 30 days; expiry below is actual API evidence. After expiry,
rebuild the recorded source with requirements-dev.txt and tools/build_foundation.py.
CPython3.12 x64 Windows/Linux are qualified; optional NumPy2.2.6/PyArrow20.0.0.
Other runtimes/platforms remain unqualified. These are retained internal foundation
artifacts, not a PyPI/stable production release or permanent binary archive.

- [foundation-8a857f1270a1b9a976ed8404ed70de9facd5636a-windows-latest](https://github.com/atulsrivas1/equity-features/actions/runs/37264166777/artifacts/11326150257); expires `2026-11-04T04:36:23Z`; Windows CPython3.12.10.
- [foundation-8a857f1270a1b9a976ed8404ed70de9facd5636a-ubuntu-24.04](https://github.com/atulsrivas1/equity-features/actions/runs/37264166777/artifacts/11325936094); expires `2026-11-04T04:36:00Z`; Linux CPython3.12.14.

| OS | Distribution archive | SHA256 |
| --- | --- | --- |
| Windows | equity_feature_contracts-0.0.1a6-py3-none-any.whl | `f73d4ae70735a1eb2ae53f13b7ad5f94c43212389806a1890b1df7568f980b3f` |
| Windows | equity_feature_contracts-0.0.1a6.tar.gz | `f2e9615d692eb140971570379ed117a8e01116ba52ce45096d8cd8b5f266c890` |
| Windows | equity_features-0.0.1a6-py3-none-any.whl | `9cc1870e9ddaa06e3e84592e906fc420e3f9158226ce87da9d3fee9e47ac35dd` |
| Windows | equity_features-0.0.1a6.tar.gz | `1a991eac98476d4bfe7b2020dbd331f0fc7eb98895b00206d8931a4cb7d470d5` |
| Linux | equity_feature_contracts-0.0.1a6-py3-none-any.whl | `87550100fede08a5c4b452f4a9f023531bb16d3f56b8a8a682d138f307bd0410` |
| Linux | equity_feature_contracts-0.0.1a6.tar.gz | `59d09b89644b8fc0cae3a2d36873aad3d066f3fccc676a4ea5e5ff5c62df8a71` |
| Linux | equity_features-0.0.1a6-py3-none-any.whl | `c31cab62a923527845c332f58311e1b03afdbd66e098f0f3212abe83f3d5b915` |
| Linux | equity_features-0.0.1a6.tar.gz | `a7ee79a9e2cf64a3dce89aa424c45a232183ca00512423c041d161d3c23c68cb` |

## Corrections, reconciliation and stop boundary

EQ-009 was reopened for imported-function/wildcard boundary bypass; PR133 fixed it
with negative fixtures and renewed acceptance. EQ-014 was reopened after registry
mapping found nonpositive close-only daily prices bypassed validation without volume.
PR139/alpha4.post1 adds independent price/coherence checks and 3 regressions; renewed
main artifact acceptance preceded resuming EQ-015. Later alpha5/6 retain both fixes.
Failures and checked retry/publication corrections remain in SESSION_HANDOFF.md.

E01 and E02 are Done. E03 issue13 spans R0 and R3: its milestone was already null,
and Project has no separate Release field. Its six R0 children are accepted; keep
E03 open/In progress and unassigned to a single milestone for open R3 EQ-093 #113.
No later child is closed or reassigned to manufacture R0 completion. EQ-094 remains
retired. Deferred GOV-005 #119/PR120 remains unchanged.

The acceptance procedure closes R0 milestone 1 and sets EQ-017 #21 Ready after
this report’s publication/main gates, because the formulas and R0 foundation prerequisites are satisfied. No R1
implementation starts in this mission. Do not create automations or imply dates.
Numerical kernels, incremental engines, package-phase benchmarks/composition and
stable release qualification, concrete DuckDB/provider/file adapters, workers,
remote services and general custom execution remain later releases. No performance,
provider truth, financial accuracy, data rights or private-data admission follows
from R0 acceptance. There is no public registry publication.
