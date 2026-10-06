# EQ-095 — External extensibility qualification

Issue [#150](https://github.com/atulsrivas1/equity-features/issues/150), R3/E06.
Backlog; no implementation. Estimate: 5 provisional points.

Start after EQ-093 registration, EQ-039 guide, EQ-040 examples, EQ-043 SDK and
EQ-045 install tooling. Inspect accepted APIs/artifacts, then implement a separately
packaged synthetic consumer with no editable install, private imports or repository
source fallback. Register/discover a versioned namespaced custom feature and use
an independently implemented synthetic adapter passing the public conformance kit.
Check typed values, units, quality, timing and provenance against hand-derived
expectations; verify built-ins and installed core source remain unchanged.

Resolve fixture location, supported execution modes, portable import-isolation
checks and artifact matrix when pulled. Routine implementation choices remain
autonomous. No providers, credentials, plugin discovery, remote execution or
extension security/resource/correctness certification.

Tests: clean supported Windows/Linux wheel and sdist installs, independent output,
discovery, registry isolation, collisions, invalid schema/units/results, missing
inputs, unsupported modes, incompatible versions and core-source integrity.
Supported configuration changes and changed feature meaning are shown separately.

Documentation: reproducible extension guide, consumer fixture, failure/capability
matrix, trusted-code limitations, issue/PR evidence, release notes and continuity.
EQ-048 includes acceptance. Done requires verified artifacts, clean installed tests
and publication; this story qualifies EQ-093/043, not duplicate implementation.


## October6,2026 execution decisions supersede prepared Backlog status

Original preparation above is retained. The following current plan resolves its open fixture/mode/isolation/artifact choices under actualaccepted dependencies; live Project owns current execution status.

# EQ095 combined installed external consumer qualification plan

R3/E06/issue150,5 provisional points; prerequisites093/039/040/043/045 accepted and integrity047Done. Pull from actualmain07b4f3d747f822e93bc557ab65a1b0f8fe44dc3a, one active story. Qualify the already implemented public custom registry/calculator and synthetic adapter together from separately retained consumerwheel/sdist on supported Windows/Linux. No core calculation or schema/API/private import change.

Mathematics is the existing demo: supplied bars open100/high104/low99/close103 yield(maxhigh-minlow)/firstopen=5/100=0.05, fraction; independently distinct unchanged builtin range/lastclose=5/103. Complete coverage2/2, namespace/demo entityA/S, explicit session100..200 and availability200/210/210, USDscale0; metadata must bind callerconfig/actualadapterinput/implementation and typedquality/evidence behavior. Demonstrate supported configuration identity changes separately from changed feature meaning, registry/discovery isolation and unavailable/zero-denominator outcomes without fabricated availability. Retain custom algorithmv2; new public qualification module advances only independent consumerimplementation to0.4.0. Corepair0.0.4a4/math/state/schema/modes remain unchanged.

Qualification reports actual positive and typed-negative outcomes for collision/reservednamespace/badinput/output/unit/type/identity/config/algorithm/implementation/mode/capability/sourcebinding, adapter conformance/limits/cancellation/missingfixture and unchanged builtin definitions/results. Public-only installedexecution plus strictPEP561caller/consumer typing and before-afterconsumerinstallation-execution corefingerprints prevent private/source fallback/overwrite. Trustedlocal callbacks are not sandbox/security/resource/correctness certified. Define report schema/version/case IDs and expected codes before writing implementation; assertions use hand goldens and actual public contract semantics, not duplicate kernels.

External qualification driver and meaningful report tests stay outside owned calculation packages. Existing pure audit retains its frozen619/593 calculationcase cohort; separately exclude new external package-qualification driver and document current fullsuite count. Builder must run installed public qualification and retain its report within actualconsumerinstallation evidence, not substitute repo execution. Update guide/catalog/version/build/install/changelog/lesson/handoff and relevant issue/PR alongside change; preserve historical baseline/license/source observations. Current resource runtime consumer-version validator must follow actualcurrentpackage metadata while oldmeasurements remain historical.

Non-doc consumer/tool/test changes require frozen repeat sixarchives/TWO actualfresh core+consumerform pairs, complete numerical/type/boundary/policy/123references, separateactualfinalheadreview/allCI, guardedsource-main/publicbytes/bothOSactual12archives/FOURactualsourcefreshpairs/currentbenchmark-resource-consumerqualification reports; then separatelyreviewed docsreceipt/finalpublication/archiveequality/independentcurrentreports/expiry/Released-postreadbackDone. NativeLinux proof is actualCI, localFOUR isWindows. Then EQ048 finalboundedR3acceptance, no R4/stable/registry/tag/provider/credential/account scope.


Public qualification report schema external-qualification1 has producer implementation0.4.0, corepaira4/customalgorithmv2, handgoldens5/100 and5/103, before/after builtin catalog digest and immutable typed per-case outcomes(case_id,group,expected,observed). Positive outcomes require actual golden/metadata/quality/evidence-emptycompletefixture/registry/config/zero-denominator/unavailable and adapter whole/chunk/missing conformance checks. Negative contract cases expect actualpublic duplicate/inconsistent_identity/invalid_schema/incompatible_version/invalid_config/unsupported_capability/unknown_feature codes at their respective boundaries; source schema/unsupported/resource_limit/cancelled outcomes are captured separately. Exact final case inventory/counts is recorded after tests, not invented beforehand. No credentials/files/clock/native rights certificate in the report.


Implementation investigation corrected unreachable zero-open numerical expectation to invalid_schema at positive OHLC admission; a zero-volume missing price is skipped for next price-bearing open. Valid unavailable fixture uses unknown known_at on both rows and actual missing_input/unknown_availability. All43cases pass:13positive/23contracterrors/7sourceerrors, with10 actual finite SDK conformance cases. Two driver tests independently check goldens/case inventory and reject a contract-valid wrong0.06 callback. Consumer0.4.0 only, core/math/schema/modes unchanged; current full633 and strict48sourcefiles, frozen619/593 guarded cohort retained.
