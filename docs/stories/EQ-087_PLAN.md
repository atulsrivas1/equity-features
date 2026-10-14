# EQ087 optional accelerator packaging proposal

Local unreviewed readiness preparation, October14,2026. [EQ087 #98](https://github.com/atulsrivas1/equity-features/issues/98), E11#95, R8 milestone9; provisional three complexity points. Blocked on accepted EQ086 outcome and verified Atul Project access. This packet does not mark either story Ready or accepted.

## Conditional selection

If [EQ086's proposed no-change decision](EQ-086_PLAN.md) is accepted, select #98's explicit no-change alternative: no new accelerator, native wheel, ABI, backend selector, fallback implementation, binary license or thread policy. Existing definitions and supported packaging remain unchanged. If EQ086 instead selects an accelerator, replace this packet with its actual platform/build/ABI/dependency/thread/fallback and parity protocol before Ready; never reuse no-change checks for changed binaries.

Read source metadata at canonical da74650e03d67acc5de6f8881065518f68b1f24f:

| Distribution | Version / Python | Required dependencies | Existing optional extra |
| --- | --- | --- | --- |
| equity-feature-contracts | 0.0.4a4 / >=3.12,<3.13 | none | columnar: numpy==2.2.6, pyarrow==20.0.0 |
| equity-features | 0.0.4a4 / >=3.12,<3.13 | equity-feature-contracts==0.0.4a4 | columnar: equity-feature-contracts[columnar]==0.0.4a4 |

Both use setuptools==80.9.0, Apache-2.0 metadata and py.typed. The columnar extra is existing packaging, not a new EQ086 accelerator. Source metadata inspection is not an installation test. Relevant files: packages/contracts/pyproject.toml and packages/features/pyproject.toml. No build, metadata, dependency or executable change is proposed.

## Readiness and validation

First verify actual EQ086 acceptance, fresh source/package identities and current Project ownership; publish this packet, points and no-impact documentation to #98 with a linked draft. Use the owner-authorized R8 separate local reviewer on the exact final head. Resolve findings before Test. No runtime or numerical definition changes mean no new performance, native-build or installed-artifact claim; preserve accepted [EQ085 qualification](EQ-085_SOURCE_QUALIFICATION.json) and [receipt](EQ-085_RELEASE_RECEIPT.json) within their original scope.

Formal acceptance verifies a docs-only diff, unchanged actual metadata/versions/dependencies and applicable public documentation checks. Document supported no-new-binary/fallback/thread-policy outcome explicitly, with limitations. Same-story issue/PR, changelog, scoped lesson and handoff are required. Documentation merged and verified on default branch is the declared release channel; final public UTF8/source/Atul attribution and relevant CI readback precede Released then Done/closure. Neither existing columnar installation nor a successful source check proves new accelerator wheels.

Any intervening package/build/runtime changes trigger reassessment of applicable installed bothOS/current artifact gates. This no-impact proposal does not qualify future distributions or excuse EQ092.
