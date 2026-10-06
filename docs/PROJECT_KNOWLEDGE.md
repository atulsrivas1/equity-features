# Project knowledge

GOV-011, prepared October 5, 2026. This is the repository's cross-session knowledge entry point. It complements existing specifications and receipts; it does not establish new numerical correctness, delivery acceptance or performance.

## Start a session

Read [work agreements](../AGENTS.md), this overview, [current handoff](SESSION_HANDOFF.md), [delivery policy](DELIVERY_POLICY.md) and the live [Project](https://github.com/users/atulsrivas1/projects/2). Then read the selected story, its dependencies and only the relevant source documents.

- [Decision history](knowledge/DECISIONS.md): agreed direction and superseded proposals.
- [Engineering lessons](knowledge/LESSONS.md): observed failures, evidence and revisit conditions.
- [Source map and review coverage](knowledge/SOURCE_MAP.md): authoritative contracts and import limits.
- [Backlog and learning workflow](knowledge/BACKLOG_WORKFLOW.md): how to identify, rank and deliver the next useful work.

The live Project owns current lifecycle status. [BACKLOG.md](BACKLOG.md) owns versioned scope/dependencies. An old handoff paragraph, chat completion statement or successful test count does not override a newer owner decision or delivery gate. A new checkout uses the same issues and ownership rules.

## Purpose and architecture

Build reusable, source-independent equity calculations for research, backtesting and machine-readable analysis. The owner selected a separate personal open-source project, public engineering records and Apache-2.0. Code licensing does not grant provider-data or private-source rights.

Two distributions share one repository: `equity-feature-contracts` owns typed inputs/specifications/results/validation/discovery/adapter protocols; `equity-features` owns calculations. Calculations receive supplied facts and return results. Adapters own acquisition and normalization; workers own scheduling, resources and persistence; downstream strategies own scanners, rankings and outcomes.

Python is the selected public interface. Backend acceleration follows measurements and parity checks. The earlier Go-first worker proposal and earlier provider-prefixed package names are historical. A package metadata interface is not a delivered adapter, worker, hosted service or stable registry release.

## Release and ownership orientation

The agreed sequence is packages R0–R3, DuckDB adapter R4, independent workers R5, provider/file adapters R6, remote tools R7, and measured acceleration/separate strategy-label packages R8. Read [scope and dependencies](BACKLOG.md) rather than treating every later capability as a prerequisite for the current release.

On October 5 the owner restored **R2 before R3 feature work**. The repair session finishes BUG-003/BUG-004 and stops; the dedicated R2 session may prepare, but calculation implementation depends on verified repairs and handoff publication. Consult [GOV-010](https://github.com/atulsrivas1/equity-features/issues/167), [PR168](https://github.com/atulsrivas1/equity-features/pull/168), and current issue/Project evidence. This dated decision does not claim those gates are now complete.

[R0 acceptance](R0_ACCEPTANCE.md) and [R1 acceptance](R1_ACCEPTANCE.md) remain versioned historical receipts. The later [R1 review](reviews/R1_REVIEW.md) found two further defects despite extensive tests. Current repair status is linked, not inferred from the old acceptance report. [BUG-003](https://github.com/atulsrivas1/equity-features/issues/162), [BUG-004](https://github.com/atulsrivas1/equity-features/issues/163).

External application architecture remains outside this project. EQ-094 was withdrawn and its ID remains reserved. Custom features/adapter conformance remain agreed scope under EQ-093/EQ-095; no application-specific integration is required. The October5 owner direction resumed the separate final-head Codex review gate; hosted activation remains unverified under GOV-005. The owner selected a separate local Codex reviewer during bounded R2 delivery; EQ035 through EQ038 record the actual reviewed heads and limitations. See [review policy](CODE_REVIEW.md). Hosted activation remains unverified; older receipts retain their original review evidence.

## How learning persists

Keep evidence in linked review, decision, story and delivery records. Add a scoped lesson when a correction changes how future work should proceed. Record supporting and contradicting evidence, affected version/scope, action and revisit condition. Update priorities and the exact resume step. Saved documents supply durable context; they do not retrain a model or create an unattended worker.

The import screened relevant active/archived development chats and inspected repository records. It was targeted, not an account-wide archive or fresh source-code audit. See the [coverage record](knowledge/SOURCE_MAP.md). No numerical feature or bulk dataset work was performed by GOV-011.

## Additional planned evidence capabilities

[E13–E15 / R9–R11](EVIDENCE_ROADMAP.md) contain fifteen Backlog stories for execution receipts/replay, declared leakage checks and agent events/ledger/MCP integration. This is future planning, not implemented capability or current execution ownership. Existing R7 owns the base MCP service. Calculations remain pure and source-independent.

## Revised ledger and continuous-market proposals

[Ledger design](AGENT_EVIDENCE_DESIGN.md) refines existing R9–R11 stories. [Continuous-market design](CONTINUOUS_MARKET_DESIGN.md) adds conditional E16/R12/EQ-111–115 future scope; prove gaps and freeze formulas before code. No present execution priority or existing schema/equation changes.

## Deferred evidence service pilot

[E17/R13](EVIDENCE_SERVICE_PILOT.md) adds EQ-116–120 as low-priority Backlog. Reuse existing R9–R11 packages to measure debugging/replay usefulness before optional independent checkpoint witnesses. No blockchain, new repository, outreach or deployment authorized. Current core work retains priority.

## Accepted bounded R2 exit — 2026-10-05

All twelve R2 stories EQ027–038 are closed/Project Done; E05 and milestone3 are closed.
[Acceptance](R2_ACCEPTANCE.md) and [final integration receipt](stories/EQ-037_DELIVERY.md)
bind actual pair0.0.3a13, independent numerical/review evidence, bothOSCI and verified
installed artifacts. The supported inventory is39batch/23sessionupdate-restore/22conditionalmerge;
all16R2IDs remain batch-only. R3 is paused; next work requires a later owner pull decision.
119activeEQstories:38Done/81futureBacklog, retired094excluded. No hosted reviewer activation,
registry publication, provider readiness or performance claim is implied.


## October6 owner-directed R3 resumption

Owner resumes bounded R3 autonomously after accepted R2 and both Done repairs. EQ093#113/PR237 is Code review with600unit and installed consumer source qualification; [report](stories/EQ-093_IMPLEMENTATION_REPORT.md). No merge/release/Done yet. Required separate final-head reviewer remains unresolved: hosted activation unverified and existing local alternative is R2-bounded. Resume at that gate, then actual main publication/installation acceptance and dependency-ready EQ043. Preserve earlier paused-history notes; this direction supersedes their feature-pull pause. No R4, stable registry or account scope.


October6 owner authorizes the separate local Codex reviewer alternative throughout bounded R3. The earlier pending-choice block is superseded; retain final-head review and all acceptance/publication gates. [Policy](CODE_REVIEW.md).


EQ093 corrected0.0.4a3 source/main/actualbothOSbundles are qualified after separate final-head review,605tests and FOUR fresh installed pairs with independent public consumer. [Delivery](stories/EQ-093_DELIVERY.md). Final receipt publication/byte-equality gates remain before Done; EQ043 is next. Built-in39 and actual session modes unchanged; no full R3 release acceptance or stable/custom-code certification claim.


EQ093 finalreceipt/main6d93888 actualbundle equality and postrelease evidence accepted on issue113; storyDone/E03closed. R3remainsopen with11stories. Dependency-ready EQ043SDK is next under its pre-code plan; hostedreview/stable/R4remainoutside this delivery.

EQ043 corrected source2c4a39c/maince04e4d is separately reviewed,619tests/strict46/TWOinstalledpairs and mainbothOSCI pass. ActualbothOSsource bundles are downloaded/inspected; FOURinstall and same-story receipt publication gates remain. [Receipt](stories/EQ-043_DELIVERY.md). Next EQ039 after issue49verifiedDone; R3 is incomplete.

EQ043 issue49 is verifiedDone after finalreceiptmain7e21c89 actualbundleequality/CI. EQ039 current API/error/extension guide and actualinstalledtyping are separately reviewed/source-main91378fc bothOSCI pass; [receipt](stories/EQ-039_DELIVERY.md) retains FOURfreshpairs/finalpublicationgates beforeDone. Then EQ040; R3 remainsopen.

EQ039 finalreceiptmain864884a passed actual final artifact equality and postrelease readback; issue45 is Done. EQ040 source-main01da58f publishes separately reviewed consumer0.3.0 installed workflows/catalog with corepaira4 unchanged. TWO author fresh pairs and exact-head CI pass; source-main bothOSCI/FOURactual installs and reviewed receipt/final publication remain required before Done. Continue EQ041 only after that accepted delivery; do not infer whole R3 completion.

EQ040 finalmain96d420c passed actualfinalarchiveequality/postrelease source+archive readback; issue46Done. EQ041 separately reviewed source-main ef99dd2 publishes measured clean-source Windowsbaseline and isolatedinstalledbenchmarksmoke with accurate processpeak/copy/thread/provenance limits; [methodology](BENCHMARKS.md). Actualmain bothOS artifacts/FOURinstalls/variablebenchmarkJSON verification and reviewedreceipt/finalpublication remain required beforeDone. Corepaira4/consumer0.3.0 unchanged; R3 incomplete, EQ042resources next.


EQ041 finalmain910abd6 accepted actualarchiveequality/independentvariablebenchmarkJSON and postreleaseverification; issue47Done. EQ042 separately reviewed correctedsourcef94407b/main df9c943 publishes21clean-source resource cases and installed sixfamily diagnostics. BothOSCI/mainpublishedsource and actualvariablebenchmark/resourceJSON checks pass; FOURsourcefreshpairs/reviewedreceipt/finalpublication remain beforeissue48Done. [Resource contract](RESOURCE_BEHAVIOR.md), [receipt](stories/EQ-042_DELIVERY.md). Sixlater R3stories remain; no math/schema/coreversion/mode change.


EQ042 finalmain89a24a4 actualfinalarchives equalFOURqualifiedsourcepairs and variablebenchmark/resource facts/postreleaseverification accepted; issue48Done. EQ044 actual version/replay policy is documentation-only with existing626unit/strict48/policy evidence and unchanged runtime/test/build/consumer. [Guide](VERSIONING.md), [plan](stories/EQ-044_PLAN.md). Required separate finalheadreview/CI and actualmainartifact-equivalence/publication remain beforeDone; five subsequent R3stories follow.


EQ044 version/replay guide accepted afteractualmain e7077b6 source/artifact-equivalence/currentvariableJSON/postreleaseverification; issue50Done. EQ045 reviewedsource434be80/main c88a282 fixes consumer-install fingerprint gap and publishes repeat-built standalone consumerwheel/sdist with separate hashes/actualform-specific installs.628units/strict48/authorTWOpairs/currentmainbothOSCI and actual12archives+12report checks pass; FOURactualsourcepairs/reviewedreceipt/finalpublication remain beforeDone. [Install](INSTALLING.md), [receipt](stories/EQ-045_DELIVERY.md). Corea4/consumer0.3/math/schema/modes unchanged; fourlaterR3stories follow045.


EQ045 finalmain5442746 actual12archive equality/current12report facts/postreleaseverification accepted; issue51Done. Pull EQ046 owned43module AST plus guarded existing synthetic numerical/admission fixtures and declared module-data audit. [Plan](stories/EQ-046_PLAN.md). Corepaira4/consumer0.3 unchanged; no arbitrarycallback/nativebackend sandbox claim. Then047/095/048; R3 incomplete.


### EQ-046 reviewed source publication

SourcePR252 finalfe095898dd0b044d7964a1b8b66a9d85346d558f separate review/no unresolvedfindings, Reviewer independently631units/threeauditcases/strict48/boundary38negative10positive/import-registry-license/fivemathverifiers/201links and exactguardcount/moduledata/Arrow20versionedsource/UTF8history verified; authorfrozenTWO actualpairs 631units/22examples/consumer0.3.0walkthrough/publictyping(threeconsumerfiles+caller/threeinvalidcalls)/corebefore-afterinstall-executioninvariance/benchmark-resource smokes and allheadCI pass. Guardedmain73246b1d970bba4f2284424c5933ef5548f949f5 exacttree/publicblobs/owner/docs37499007161/Foundation37499007035 bothOS verified. Actualsource12archives+12variable report facts inspected; FOURsourcefreshpairs running/required before receiptmerge/Done. [Receipt](stories/EQ-046_DELIVERY.md) needs separatefinalreview/allCI/finalmainarchiveequality/currentvariableprovenance/postreleaseverification. ThreeR3stories remain after046acceptance:047dependency-integrity,095combinedinstalledexternalconsumer and048finalpackageacceptance. E06/milestone4 remainopen; noR4scope.


EQ046 finalmain0b6aa56 actual12archive equality/current12report provenance/expiry and postreleaseverification accepted; issue52Done. [Purity audit](PURITY_AUDIT.md), [receipt](stories/EQ-046_DELIVERY.md). Pull documentation-only EQ047 existingdependency/license/provenance/channel review from this qualified code; [plan](stories/EQ-047_PLAN.md). Then095/048, R3 remainsopen.


EQ047 finalmain07b4f3d actual12archiveequivalence/current12reportfacts/expiry/postrelease accepted; issue53Done. [Integrity](RELEASE_INTEGRITY.md), [inventory](DEPENDENCY_INVENTORY.json). Pull EQ095 combined publicinstalledcustom+syntheticadapterqualification, consumerimplementation0.4.0/corea4/mathv2; [plan](stories/EQ-095_PLAN.md). Final048acceptance remains; R3 notcomplete.


EQ095 consumer0.4.0 combines existing public custom/adapter experience in43actualsynthetic outcomes and independently detects a contract-valid wronggolden callback; corea4/math/schema unchanged. [Qualification](EXTERNAL_QUALIFICATION.md) and plan record actualadmissioncorrection. NativeLinux isCI; currentdelivery review/install/publication remains beforeDone, then048R3acceptance.


### EQ-095 reviewed source publication

SourcePR255 finalc6d1ed90a75fe80b5d75d13d4165afd4efe6b681 separate review/no unresolvedfindings, Independent633units/strict49/123references/policies/43qualification outcomes/354links/publicfourconsumerimports/coreunchanged. Initial86a8eaa P3 planfulltyping48vs49 corrected finalc6d1ed9 and independentlyre-reviewed documentation/head; no unresolvedfindings; authorfrozenTWO actualpairs 633units/22repositoryexamples/consumer0.4.0walkthrough+43casequalification/publictyping(fourconsumerfiles+caller/threeinvalidcalls)/corebefore-afterinstall-executioninvariance/benchmark-resource smokes and allheadCI pass. Guardedmain823aecdb06cfc2aebcd492d46daf0b87111ef9d7 exacttree/publicblobs/owner/docs37505488147/Foundation37505488106 bothOS verified. Actualsource12archives+12variable report facts inspected; FOURsourcefreshpairs running/required before receiptmerge/Done. [Receipt](stories/EQ-095_DELIVERY.md) needs separatefinalreview/allCI/finalmainarchiveequality/currentvariableprovenance/postreleaseverification. Only EQ048#54 finalboundedR0-R3packageacceptance remains after095. E06/milestone4 stayopen until actualfinalacceptance; no stable/registry/tag/provider/R4scope.


### EQ095 Done / EQ048 final bounded acceptance pull

EQ095 sourcePR255 finalc6d1ed9(review6021920519) actualsource823aecdb; reviewedreceiptPR256 final08de533(review6022053642) actualfinalmain82ac35e86447cd958c0672d1c977a4e91a23ece1 exacttree/all3publishedreceiptblobs/docs37506725120/Foundation37506725210bothOSpass. AuthorTWO plusFOUR actualdownloadedsourcepairs each633units/22examples/publictyping/43qualifiedconsumer/corefingerprint/benchmark-resource pass. Final12archives equalqualifiedsource and12currentreports exactcleanmain/facts independentlyverified; Releasedreadback→Done150comment6022215660. Currentcorea4/consumer0.4, coremath/schema/modes unchanged; originalP3count resolved standardstrict49. Liveall49otherR0-R3storiesclosedDone/priormilestones1–3closed/repairsDone; pulllastEQ048#54/5points onorigin/main82ac35e. [Plan](stories/EQ-048_PLAN.md). One doc-only finalacceptancePR with currentCI/review/publication/archiveequality/currentreports/Releasedverification, thenall50/E06/milestone4 closure. R3notyetclosed; noR4scope.


EQ048 finaldocumentation acceptance mapsoriginalR0–R2receipts, current49Donepredecessors/repairs, qualifieda4/consumer0.4 and all39modes/purity/benchmark/resource/integrity/43caseexternalconsumer proofs. [Acceptance](R3_ACCEPTANCE.md) preserves originalbaselineversions and exactcurrentartifact facts. Finalreview/actualpublication/Releasedreadback plusall50/E06/milestone4closure remain next; nocodechange/R4scope.

## Bounded R4 execution

[GOV013 handoff](R4_AUTONOMOUS_HANDOFF.md) is delivered; explicit owner local-review
policy covers R4. EQ049 source43e003c resolver is reviewed/qualified with27optional/
633core/strict2, actualmain bothOS artifacts and FOUR downloaded source-form installs.
[Receipt](stories/EQ-049_DELIVERY.md) retains final receipt publication/readback gates
before Done. Both core packages/consumer remain unchanged. Metadata resolution does
not acquire canonical rows or establish source/PIT/numerical acceptance. EQ050–056
remain planned; real numerical and actual conformance layers remain mandatory.


EQ049 is accepted Done. EQ050 source6f3891f mapping0.1.0a2 is separately reviewed/qualified with46optional/633core/strict3, actual bothOS source-main artifacts and FOUR actual downloaded-form Windows installs. [Receipt](stories/EQ-050_DELIVERY.md) retains final receipt/publication gates before Done. Pure core unchanged; no canonical historical reads or real numerical acceptance yet. EQ051 follows; EQ052-056 remain planned.


EQ050 is acceptedDone. EQ051 reviewed source34a0615 optional0.1.0a3 is qualified
with62 optional/633core/strict4, actual bothOS source-main artifacts and FOUR fresh
downloaded producer/form Windows installs. [Receipt](stories/EQ-051_DELIVERY.md)
retains final doc-only review/CI/publication/readback gates before Done. Bounded
original reads, explicit supplied sessions/coverage and actual measured costs;
optional NumPy2.2.6 UDF requirement corrected after clean-install failure. Pure core
unchanged. EQ052-056 remain planned; actual conformance/private numerical layers
remain mandatory and no real slice/golden is frozen.
