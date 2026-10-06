# R3 bounded experimental package acceptance

EQ048 [issue54](https://github.com/atulsrivas1/equity-features/issues/54), E06 [issue44](https://github.com/atulsrivas1/equity-features/issues/44), [milestone4](https://github.com/atulsrivas1/equity-features/milestone/4), [plan](stories/EQ-048_PLAN.md). This record maps accepted implementation and current installable evidence; exact final acceptance SHA/runs/archive hashes/expiry and completed lifecycle are recorded on issue54 after publication/readback. Live Project is current status authority.

At this record's preparation on October6,2026, all49 predecessor R0–R3 stories are live CLOSED/Project Done; EQ048 is the sole active story. Milestones1–3 are closed with zero open issues. Repairs [BUG003#162](https://github.com/atulsrivas1/equity-features/issues/162) and [BUG004#163](https://github.com/atulsrivas1/equity-features/issues/163) are separately delivered/Done. E06/milestone4 close only after this story's actual reviewed final publication/Released readback and all50 live Done verification. Historical R0/R1/R2 evidence is preserved rather than retroactively rewritten.

## Current delivered mathematics and scope

Matching contracts/features0.0.4a4 and independent consumer0.4.0 are experimental. All39 frozen built-in IDs have batch implementations;23sessionIDs support update/restore and22conditional legal merge (continuousquotes merge unsupported). All16R2 IDs and custom calculations are batch-only. Contract/config/input/result/catalog schemas1, saved session state2 and exact implementation restore admission remain distinct; built-in mathv1/internal compensated-state revisions and custom demoalgorithmv2 remain unchanged. Caller supplies canonical facts, C/K/E, target/session/window/reference/config/coverage/initialization; no fetching, credentials, files, scheduling or publication inside calculations.

Original [R0 acceptance](R0_ACCEPTANCE.md), [R1 acceptance](R1_ACCEPTANCE.md) and [R2 acceptance](R2_ACCEPTANCE.md) retain their original versions/SHAs and independent mathematical receipts. Subsequentstructure omission governance and overflowingquote-state rejection are covered by162/163, exact current artifacts and regression suite. [39-ID scope](features/V1_SCOPE.md), [API guide](api/EXTENSIONS.md), [versions](VERSIONING.md), [compatibility](COMPATIBILITY.md) and [state API](api/INCREMENTAL.md) define units/timing/readiness/edge cases and truthful execution modes.

## Full story evidence mapping

Rows link their public acceptance authority; historical current-status prose in prepared plans is not execution authority. EQ048's own row is this documentation/change and issue54's final publication evidence.

| Release | Story | Public issue | Durable evidence |
| --- | --- | --- | --- |
| R0 | EQ-001 | [#2](https://github.com/atulsrivas1/equity-features/issues/2) | [Release acceptance](R0_ACCEPTANCE.md) |
| R0 | EQ-002 | [#3](https://github.com/atulsrivas1/equity-features/issues/3) | [Release acceptance](R0_ACCEPTANCE.md) |
| R0 | EQ-003 | [#4](https://github.com/atulsrivas1/equity-features/issues/4) | [Release acceptance](R0_ACCEPTANCE.md) |
| R0 | EQ-004 | [#5](https://github.com/atulsrivas1/equity-features/issues/5) | [Release acceptance](R0_ACCEPTANCE.md) |
| R0 | EQ-005 | [#6](https://github.com/atulsrivas1/equity-features/issues/6) | [Release acceptance](R0_ACCEPTANCE.md) |
| R0 | EQ-006 | [#7](https://github.com/atulsrivas1/equity-features/issues/7) | [Release acceptance](R0_ACCEPTANCE.md) |
| R0 | EQ-007 | [#9](https://github.com/atulsrivas1/equity-features/issues/9) | [Release acceptance](R0_ACCEPTANCE.md) |
| R0 | EQ-008 | [#10](https://github.com/atulsrivas1/equity-features/issues/10) | [Release acceptance](R0_ACCEPTANCE.md) |
| R0 | EQ-009 | [#11](https://github.com/atulsrivas1/equity-features/issues/11) | [Release acceptance](R0_ACCEPTANCE.md) |
| R0 | EQ-010 | [#12](https://github.com/atulsrivas1/equity-features/issues/12) | [Release acceptance](R0_ACCEPTANCE.md) |
| R0 | EQ-011 | [#14](https://github.com/atulsrivas1/equity-features/issues/14) | [Release acceptance](R0_ACCEPTANCE.md) |
| R0 | EQ-012 | [#15](https://github.com/atulsrivas1/equity-features/issues/15) | [Release acceptance](R0_ACCEPTANCE.md) |
| R0 | EQ-013 | [#16](https://github.com/atulsrivas1/equity-features/issues/16) | [Release acceptance](R0_ACCEPTANCE.md) |
| R0 | EQ-014 | [#17](https://github.com/atulsrivas1/equity-features/issues/17) | [Release acceptance](R0_ACCEPTANCE.md) |
| R0 | EQ-015 | [#18](https://github.com/atulsrivas1/equity-features/issues/18) | [Release acceptance](R0_ACCEPTANCE.md) |
| R0 | EQ-016 | [#19](https://github.com/atulsrivas1/equity-features/issues/19) | [Release acceptance](R0_ACCEPTANCE.md) |
| R1 | EQ-017 | [#21](https://github.com/atulsrivas1/equity-features/issues/21) | [Delivery](stories/EQ-017_DELIVERY.md) |
| R1 | EQ-018 | [#22](https://github.com/atulsrivas1/equity-features/issues/22) | [Delivery](stories/EQ-018_DELIVERY.md) |
| R1 | EQ-019 | [#23](https://github.com/atulsrivas1/equity-features/issues/23) | [Delivery](stories/EQ-019_DELIVERY.md) |
| R1 | EQ-020 | [#24](https://github.com/atulsrivas1/equity-features/issues/24) | [Delivery](stories/EQ-020_DELIVERY.md) |
| R1 | EQ-021 | [#25](https://github.com/atulsrivas1/equity-features/issues/25) | [Delivery](stories/EQ-021_DELIVERY.md) |
| R1 | EQ-022 | [#26](https://github.com/atulsrivas1/equity-features/issues/26) | [Delivery](stories/EQ-022_DELIVERY.md) |
| R1 | EQ-023 | [#27](https://github.com/atulsrivas1/equity-features/issues/27) | [Delivery](stories/EQ-023_DELIVERY.md) |
| R1 | EQ-024 | [#28](https://github.com/atulsrivas1/equity-features/issues/28) | [Delivery](stories/EQ-024_DELIVERY.md) |
| R1 | EQ-025 | [#29](https://github.com/atulsrivas1/equity-features/issues/29) | [Delivery](stories/EQ-025_DELIVERY.md) |
| R1 | EQ-026 | [#30](https://github.com/atulsrivas1/equity-features/issues/30) | [Delivery](stories/EQ-026_DELIVERY.md) |
| R2 | EQ-027 | [#32](https://github.com/atulsrivas1/equity-features/issues/32) | [Delivery](stories/EQ-027_DELIVERY.md) |
| R2 | EQ-028 | [#33](https://github.com/atulsrivas1/equity-features/issues/33) | [Delivery](stories/EQ-028_DELIVERY.md) |
| R2 | EQ-029 | [#34](https://github.com/atulsrivas1/equity-features/issues/34) | [Delivery](stories/EQ-029_DELIVERY.md) |
| R2 | EQ-030 | [#35](https://github.com/atulsrivas1/equity-features/issues/35) | [Delivery](stories/EQ-030_DELIVERY.md) |
| R2 | EQ-031 | [#36](https://github.com/atulsrivas1/equity-features/issues/36) | [Delivery](stories/EQ-031_DELIVERY.md) |
| R2 | EQ-032 | [#37](https://github.com/atulsrivas1/equity-features/issues/37) | [Delivery](stories/EQ-032_DELIVERY.md) |
| R2 | EQ-033 | [#38](https://github.com/atulsrivas1/equity-features/issues/38) | [Delivery](stories/EQ-033_DELIVERY.md) |
| R2 | EQ-034 | [#39](https://github.com/atulsrivas1/equity-features/issues/39) | [Delivery](stories/EQ-034_DELIVERY.md) |
| R2 | EQ-035 | [#40](https://github.com/atulsrivas1/equity-features/issues/40) | [Delivery](stories/EQ-035_DELIVERY.md) |
| R2 | EQ-036 | [#41](https://github.com/atulsrivas1/equity-features/issues/41) | [Delivery](stories/EQ-036_DELIVERY.md) |
| R2 | EQ-037 | [#42](https://github.com/atulsrivas1/equity-features/issues/42) | [Delivery](stories/EQ-037_DELIVERY.md) |
| R2 | EQ-038 | [#43](https://github.com/atulsrivas1/equity-features/issues/43) | [Delivery](stories/EQ-038_DELIVERY.md) |
| R3 | EQ-039 | [#45](https://github.com/atulsrivas1/equity-features/issues/45) | [Delivery](stories/EQ-039_DELIVERY.md) |
| R3 | EQ-040 | [#46](https://github.com/atulsrivas1/equity-features/issues/46) | [Delivery](stories/EQ-040_DELIVERY.md) |
| R3 | EQ-041 | [#47](https://github.com/atulsrivas1/equity-features/issues/47) | [Delivery](stories/EQ-041_DELIVERY.md) |
| R3 | EQ-042 | [#48](https://github.com/atulsrivas1/equity-features/issues/48) | [Delivery](stories/EQ-042_DELIVERY.md) |
| R3 | EQ-043 | [#49](https://github.com/atulsrivas1/equity-features/issues/49) | [Delivery](stories/EQ-043_DELIVERY.md) |
| R3 | EQ-044 | [#50](https://github.com/atulsrivas1/equity-features/issues/50) | [Release acceptance](R3_ACCEPTANCE.md) |
| R3 | EQ-045 | [#51](https://github.com/atulsrivas1/equity-features/issues/51) | [Delivery](stories/EQ-045_DELIVERY.md) |
| R3 | EQ-046 | [#52](https://github.com/atulsrivas1/equity-features/issues/52) | [Delivery](stories/EQ-046_DELIVERY.md) |
| R3 | EQ-047 | [#53](https://github.com/atulsrivas1/equity-features/issues/53) | [Release acceptance](R3_ACCEPTANCE.md) |
| R3 | EQ-048 | [#54](https://github.com/atulsrivas1/equity-features/issues/54) | [This acceptance](R3_ACCEPTANCE.md) |
| R3 | EQ-093 | [#113](https://github.com/atulsrivas1/equity-features/issues/113) | [Delivery](stories/EQ-093_DELIVERY.md) |
| R3 | EQ-095 | [#150](https://github.com/atulsrivas1/equity-features/issues/150) | [Delivery](stories/EQ-095_DELIVERY.md) |

## Current numerical, installed and review evidence

EQ095 actual source-main823aecdb06cfc2aebcd492d46daf0b87111ef9d7 and final receipt-main82ac35e86447cd958c0672d1c977a4e91a23ece1 are verified. SourcePR255 finalc6d1ed90a75fe80b5d75d13d4165afd4efe6b681 [separate local automated review](https://github.com/atulsrivas1/equity-features/pull/255#issuecomment-6021920519) resolved an initial P3 fulltyping-count correction; receiptPR256 final08de533aee4ebbbde2f0a9b2c4cf4377234e994c [separate review](https://github.com/atulsrivas1/equity-features/pull/256#issuecomment-6022053642) has no unresolved findings. Reviewer identity/actual checks/limits are recorded. These are local automated reviews, not hosted activation or human review; GOV005 remains separate/open. Owner author/committer and actual public bytes/tree were checked.

Full633 units, strict49 sourcefiles,123 independent mathematical references,38negative/10positive boundary cases, registry/import/license/compatibility checks pass. [Pure boundary audit](PURITY_AUDIT.md) retains619existing guarded fixtures and593strict-environment fixtures,16 guardpositivecontrols/exact26Arrow timezone cases and43owned module-data snapshots/mutationcontrol. Tests audit Python entrypoints after initialization; arbitrary callbacks/native globals are outside that proof. [Benchmark baseline](BENCHMARKS.md) retains full small/large/skewed Windows measurements, parity/timing/copy/nativepeak/thread provenance/noise limits; [resource evidence](RESOURCE_BEHAVIOR.md) retains21cases/sixfamilies, bounded dimensions/atomic failures/legal merge and supplied caller cancellation/limits. CurrentbothOS installs repeat small diagnostics without claiming byte-identical timing or production/platform speed.

Author frozen repeat allsixarchives/TWO core+consumerforms and FOUR additional actualdownloadedsource pairs pass633units/22repositoryexamples/publictyping/threeinvalidcalls/installedwalkthrough/43qualification outcomes/corefingerprint invariance/benchmark-resource smokes. LocalFOURexecute Windows; nativeLinux evidence is actualCI. [Combined consumer qualification](EXTERNAL_QUALIFICATION.md) records independent5/100vs5/103 goldens, actual10case adapterconformance,13positive/23contracterror/7sourceerror outcomes, exact identities/units/quality/config/source/implementation, unknownavailability, limits/cancellation, built-in/catalog/result invariance and wrong0.06callback detector. Four public consumer modules use installed APIs; no editable/source fallback at installed gates. [SDK](contracts/ADAPTER_KIT.md) and [custom API](api/CUSTOM_FEATURES.md) remain source-independent; concrete acquisition remains external.

Source-main [docs37505488147](https://github.com/atulsrivas1/equity-features/actions/runs/37505488147)/[Foundation37505488106](https://github.com/atulsrivas1/equity-features/actions/runs/37505488106) and receipt-main [docs37506725120](https://github.com/atulsrivas1/equity-features/actions/runs/37506725120)/[Foundation37506725210](https://github.com/atulsrivas1/equity-features/actions/runs/37506725210) pass both supportedOSs. Source20/receipt3 changed publicblobs verified. Bothfinal12core+consumerarchives equal qualifiedsourcebytes withinOS; all4benchmark/4resource/4consumerinstallationreports independently check exactcleanmain, math/harness/runtime/nativeunits/control/shape/statistics, actualconsumerartifact/version/fingerprints and nested43case qualification. EQ095 Releasedreadback→Done [evidence](https://github.com/atulsrivas1/equity-features/issues/150#issuecomment-6022215660).

## Current reference artifact and report provenance

The following observations bind accepted EQ095 finalmain82ac35e, not this record's eventual finalmain. EQ048 final issue records its own actualSHA/runs/innerhashes/currentreports/serverdigests/expiry after verification; no future facts are invented. Epoch1700000000, source_dirty=false, names/licenses/typing/consumernamespace inspected. CrossOS bytes are not assumed equal.

### Linux / CPython3.12.15

- `equity_feature_contracts-0.0.4a4-py3-none-any.whl` SHA256 `acaa84fc0340c4640ced2b7cdbef04d5ba7cfaec20cd0525b866b415147635cc`
- `equity_feature_contracts-0.0.4a4.tar.gz` SHA256 `f32a66f31759b10c9ac251f4dffb2388a3e2ce50d2e5e15c69ac7038828f97a9`
- `equity_features-0.0.4a4-py3-none-any.whl` SHA256 `cf8965e1600a3d8ef10dbefcfdea21f2d48ad8c8f80e0268abe12c365b1cd26e`
- `equity_features-0.0.4a4.tar.gz` SHA256 `14e7b8b0ec1b245747d53081a73c9ef060c0f637d205ae97b5e14304b4d95c8f`
- `equity_feature_demo-0.4.0-py3-none-any.whl` SHA256 `210b4b823d2d0c76b0051785e5fc3aef32ebea3ddbcfd9c0c35efa639827ec35`
- `equity_feature_demo-0.4.0.tar.gz` SHA256 `33f15232fac42cb7056847c12025c7977162a9b28d5dc4a74b710461b2e93c07`

### Windows / CPython3.12.10

- `equity_feature_contracts-0.0.4a4-py3-none-any.whl` SHA256 `3fb31963c1f51b64c4b82fc874c1c38cc9c73461b933fb06d52f84bb29b7c7b2`
- `equity_feature_contracts-0.0.4a4.tar.gz` SHA256 `c0f35f1fd775b83ab9fdd48177c6332f38b1c83cc2f9986467e0852ca758ae57`
- `equity_features-0.0.4a4-py3-none-any.whl` SHA256 `0ff0745acf75f45ae7a2b38c7c106af200448f3026e4997fd0747101c79071f0`
- `equity_features-0.0.4a4.tar.gz` SHA256 `c25ab736eb267cd11a11d52cbeda6931d23796c94bb264164014f0dd542f1d06`
- `equity_feature_demo-0.4.0-py3-none-any.whl` SHA256 `8a8afc9b450936804887231a86aeff4bfb71b326ffb26821994137fc21735b5e`
- `equity_feature_demo-0.4.0.tar.gz` SHA256 `7d163e4e420e5272323d941b1876bf13e4fb23348ec668aa52d3027ca9b45fc9`

### Current benchmarks report hashes

- Linux `benchmark-Linux-gz.json` SHA256 `2ef24e6b31f21e2ae4ffd1531db5342f3d5f93220309897f387de6659abd775a`
- Linux `benchmark-Linux-whl.json` SHA256 `888c46e2cacee83bea533c9b7ed1892fb31fcd022a1ef78ec1e4a552a2540104`
- Windows `benchmark-Windows-gz.json` SHA256 `343b4757b1e549d00f2204f606704ad6e7aa8f0ec35dae03823a11137e6981b8`
- Windows `benchmark-Windows-whl.json` SHA256 `f72448f439081e0e2593bec486771b79b4a863dffc64fec1fa9e4465ac1b4c0b`

### Current resources report hashes

- Linux `resource-Linux-gz.json` SHA256 `a06016c824c51fd89f80ea8dab8db5b0709990e6c5b2e72fbe383f17071e4869`
- Linux `resource-Linux-whl.json` SHA256 `252ac8d8ba21bc1c16ad64b6c88f851051e231f4a63d7cac2cbf438aa1b0b983`
- Windows `resource-Windows-gz.json` SHA256 `a2fd18ea3ee4a0434b04f2abc71d56f3a584b6621818c79675493efc22240788`
- Windows `resource-Windows-whl.json` SHA256 `8da0e54485a4b695cbed1acfa550d52d09ce4df15fdce55c70deeb4a310004d5`

### Current consumers report hashes

- Linux `consumer-Linux-gz.json` SHA256 `ec2b175d01c9969375bedee18f8ebbe9138a80fe32f83c74febcdebfb326d437`
- Linux `consumer-Linux-whl.json` SHA256 `0231a20391650d8f35696c336fec4fa733002cfdd24ba8a788f978a6b65a1e64`
- Windows `consumer-Windows-gz.json` SHA256 `812b1806cab44ea60a899c07529f9194348e8d8ecb62a1f45441eb03718d1059`
- Windows `consumer-Windows-whl.json` SHA256 `593482d6cf56e9a7f0b97a7639e4f8701a4ca2d7f0b42013d1590d1597a8d5ee`

### Actual reference channel observations

- `foundation-82ac35e86447cd958c0672d1c977a4e91a23ece1-ubuntu-24.04` serverbundle `sha256:dbbe003e431c0d248afb3e090a6b7d119bae75fb42afdfb742d07bb0957d2836`, bytes `273814`, actualexpiry `2026-11-05T17:53:07Z`, observednotexpired.
- `foundation-82ac35e86447cd958c0672d1c977a4e91a23ece1-windows-latest` serverbundle `sha256:6c7f42ab66b519fa9042ebd56333ad6c06a1e4e499fb6c917399ff699b3497e4`, bytes `275108`, actualexpiry `2026-11-05T17:53:47Z`, observednotexpired.

Server bundle hashes differ from innerarchive hashes. The accepted channel is experimentalmain Actions artifacts with requested30day retention and finite observedexpiry; no stable version, public registry publication, tag, permanent archive or production/provider/data readiness is claimed. Apache2 projectlicense/public synthetic examples and accepted EQ010 owner/accessdecision apply. [Integrity review](RELEASE_INTEGRITY.md) preserves its EQ047 consumer0.3baseline,13 upstreamwheel/indexdigests/45noticefiles/actions/bootstrap/dependency/version observations; no dependency change in consumer0.4. Pins and repeat archives do not constitute hermetic builds, upstream attestation or a transitive/legal/security certification.

## Final acceptance procedure and boundary

This final documentation change leaves core, consumer, tests, tools, examples, benchmarks, dependency pins and workflows unchanged from the FOUR qualified EQ095 source pairs. One reviewed PR is sufficient under [public development policy](PUBLIC_DEVELOPMENT.md); no new mirror tests, redundant localFOURinstall or secondreceipt PR. Required exacthead localreview/allCI, guardedmerge/exacttree/actualpublicblobs, bothOS actualfinalCI/downloadedall12archive equality to qualifiedsource, independent current12reports and expiry are verified before Released. Reinspect publicsource/archives/reports after Released, then close54Done; re-read all50stories/repairs/epics andcloseE06/milestone4 with actual evidence. Final authority is linked issue54/milestone4, not a prepared plan or historical status line.

All bounded R3 work ends here. R4+ storage/DuckDB/provider/file adapters, independent workers, remote interfaces, chart services, unrelated products and account/profile administration remain outside this delivery. Owner decides the next release's scope; no background schedule/reminder or furtherstory pull is created.
