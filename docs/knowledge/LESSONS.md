# Engineering lessons

Imported review/delivery evidence, October 5, 2026. No production unit suite or source-code audit was independently rerun for this knowledge import. Existing formula reference checks were run as documentation gates. These lessons guide work; the linked records define tested scope and actual acceptance.

| ID | Observed lesson and evidence | Future action / limit |
| --- | --- | --- |
| EF-L001 | Extensive successful tests did not cover every timing/evidence boundary. R0 excluded ordinary events at the cutoff correctly but rejected their diagnostic reason. [R0 repaired acceptance](../R0_ACCEPTANCE.md), [BUG-001](https://github.com/atulsrivas1/equity-features/issues/144) | Check consumption and exclusion independently for ordinary events, completed bars and auction exceptions, including equality and unknown/future knowledge. Preserve the historical failure and corrected version. |
| EF-L002 | An import/name rule missed aliased backend readers. R0 later required reviewed backend API admission and alias fixtures. [Boundary policy](../BUILD_DELIVERY.md), [BUG-002](https://github.com/atulsrivas1/equity-features/issues/145) | Check aliases, namespace escape, lazy iterables and valid in-memory paths. The AST gate is a development policy, not a sandbox or universal proof of purity. |
| EF-L003 | Whole-prefix gap state did not retain a known omission in a closed interval. Re-certification could make an unfilled window Available after restore. [R1 review](../reviews/R1_REVIEW.md), [BUG-003](https://github.com/atulsrivas1/equity-features/issues/162) | Preserve bounded window-level missing facts across update/restore/merge; test atomic contradictory-certificate rejection and unaffected-window readiness. Read [current incremental policy](../api/INCREMENTAL.md) for schema/version consequences; merged repair code is not proof of completed delivery. |
| EF-L004 | A correctly rehashed state can still be structurally invalid. An overflowing hexadecimal float leaked OverflowError rather than the promised ContractError. [R1 review](../reviews/R1_REVIEW.md), [BUG-004](https://github.com/atulsrivas1/equity-features/issues/163) | Exercise structural admission past checksum checks with independent malformed cases. Preserve stable error codes and atomicity. A digest detects corruption, not authenticated history. |
| EF-L005 | Final source and installed packages can disagree: early development builds and stale discovery/example expectations failed later checks. [Continuity](../SESSION_HANDOFF.md), [story receipts](../R1_ACCEPTANCE.md) | Verify examples/inventory with the final changed head and actual main artifacts. Record failed gates; never reuse an old green run after a relevant source change without justified byte/version equality. |
| EF-L006 | Batch parity alone can share the same mistake. R1 review added an independent duration oracle, exact rational arithmetic and restore steps. [R1 review](../reviews/R1_REVIEW.md) | Pair cross-mode parity with independently calculated results and adversarial boundaries. Passing those cases proves those cases, not universal numerical correctness or performance. |
| EF-L007 | Quote sampling defines the measure. Sampled observations and continuous duration require different inputs, initialization and expiry semantics. [Quote formulas](../features/QUOTE_FORMULAS.md), [continuous API](../api/CONTINUOUS_QUOTES.md) | Reject unsupported sampling instead of inventing time weighting. Retain original seed expiry and unknown duration; continuous partition merge remains unsupported unless separately qualified. |
| EF-L008 | Reconstructed data and imported file presence do not prove decision-time availability. [Timing policy](../features/TIMING_ADJUSTMENT_POLICY.md) | Bind revisions, known-at, corporate-action basis and membership to the decision. Leave unavailable outputs null; do not silently certify a legacy corpus or source. |
| EF-L009 | Documentation dependencies can form a delivery cycle. Extension registration was separated from its final documentation gate and qualified together by the consumer story. [EQ-095 plan](../stories/EQ-095_PLAN.md), [PR151](https://github.com/atulsrivas1/equity-features/pull/151) | Check dependency direction before marking Ready. Distinguish implementation prerequisites from later integration/release acceptance; retain full release gates. |
| EF-L010 | Local Windows default text encoding repeatedly damaged appended continuity. [Continuity](../SESSION_HANDOFF.md), documentation CI | Write UTF-8 explicitly, then read the final files strictly. Encoding repair does not invalidate unchanged numerical artifacts; qualify the changed documentation normally. |
| EF-L011 | A planned API or accepted specification is not an implemented consumer experience. [Extension issues](https://github.com/atulsrivas1/equity-features/issues/150), [backlog](../BACKLOG.md) | Keep design/implementation/test/delivery states distinct. Prove custom features and adapters with clean installed public APIs before claiming support. |
| EF-L012 | More workers or a language switch cannot establish maximum performance. [Design](../PACKAGE_DESIGN.md), [delivery policy](../DELIVERY_POLICY.md) | Benchmark representative workloads, copies, throughput, peak memory and parity; change one bottleneck at a time. A justified no-acceleration decision can complete a conditional performance story. |

For a new lesson record claim/status, source and version, supporting/contradicting cases, scope, action and revisit condition. Amend or supersede it when new evidence changes applicability. Invalid implementation is not evidence that a financial hypothesis fails.

## EF-L004 implementation qualification supplement —2026-10-05

BUG004/PR171 pair0.0.2a11 normalizes oversized saved-state hexadecimal float
conversion to ContractError(INVALID_SCHEMA) with original OverflowError cause.
Three production API regression cases pass independently for rehashed malformed
states, atomic rejection and valid finite continuation. Integrated head9e78e14
passes380units/123references and repeated-build/fresh local installations. Main
793a188 bothOS/doc CI and actual bothOS bundles/FOUR fresh installed pairs each
380tests/eleven examples are now qualified; source-bound receipt publication gates
remain before Done. This correction does not establish hosted reviewer activation.
Source and failed/cancelled/queued attempts: [issue163](https://github.com/atulsrivas1/equity-features/issues/163),
[pending receipt](../stories/BUG-004_DELIVERY.md). Revisit when actual main artifacts
and published receipt are accepted; retain the original failure and schema2/version
binding lesson rather than replacing historical R1 acceptance.

EF-L003 closure supplement: BUG003/PR166 schema2/pair0.0.2a10's377unit qualification
and original four installed main artifact checks are preserved. Published receipt
PR169, renewed main65e66fd full CI and BOTH actual bundle equality to those qualified
bytes establish final delivery; issue162 is Done. Known omissions remain explicit,
and caller certificates still do not authenticate arbitrary source truth. GOV010's
same main/publication verification is accepted on issue167; R2 still waits for
BUG004 final receipt rather than inferring dependency readiness from either merge.


EF-L004 final receipt acceptance: [PR173](https://github.com/atulsrivas1/equity-features/pull/173)
all final-head checks, published main29ff0ca source, main docs/bothOS CI and actual
bundle equality to the four qualified installed byte sets passed. [BUG004 final
acceptance](https://github.com/atulsrivas1/equity-features/issues/163#issuecomment-6003581353)
records Done. Preserve original failure, qualification limits and earlier queue
failures. EQ033 may now pull; superseded pending-receipt notes above remain history.


## EF-L013 supplied-policy and field readiness —2026-10-05

[EQ033](https://github.com/atulsrivas1/equity-features/issues/38)/
[PR174](https://github.com/atulsrivas1/equity-features/pull/174) separates action
admission from market readiness: complete usable factors do not establish known-at
market observations, and classification does not depend on action factor operands.
Local independent production API tests demonstrate those boundaries. Preserve
explicit quantity basis with policy evidence; generic shares metadata alone cannot
prove reciprocal split adjustment. [Policy guide](../api/ACTION_POLICIES.md).
Scope: supplied schema1 utility, not authenticated source truth or implemented
historical IDs. Revisit with dependent historical/context consumer qualification
and final main installed artifacts; local tests alone are not accepted delivery.


EF-L013 review correction: complete coverage metadata alone could contradict the
actual supplied population. EQ033's two independently failing regressions now
require coverage.observed equal row_count and selected evidence row_index within
the original bound. Green head58bd47f builds were superseded; lifecycle returned to
In progress. Requalify corrected source/artifacts before acceptance, and apply the
same certificate-versus-delivery check to later HistoryContext consumers.


EF-L013 implementation qualification: corrected b2ef4b8 and main da116c8 pass
422units/42policycases/123refs/all policy gates and bothOS CI; both actual main
bundles and FOUR fresh installed pairs each422tests/twelve examples pass. This
qualifies the supplied-policy utility, not the sixteen numerical historical/context
IDs or source truth. [Receipt](../stories/EQ-033_DELIVERY.md). Final documentation
publication gates remain before Done; subsequent consumers must retain these
explicit original binding/quantity/certificate/availability semantics.


EF-L013 final publication accepted on issue38: PR175/d3e9fc9 full head/main checks
and actual bothOS archive equality to qualified installed bytes passed; EQ033 is
Done. EQ027 now owns consumer qualification of action/context/certificate identities.
Keep utility acceptance distinct from mathematical feature acceptance; sixteen
R2 numerical IDs remain unimplemented at this pre-code pull.


## EF-L014 finite window and capability independence —2026-10-05

EQ027/PR176 local independent production API fixtures distinguish valid return
endpoints from complete h+1governed closes, and certify finite-window recovery only
when the missing slot exits that exact window. Whole-frame future/incomplete
coverage does not override per-slot selected proof, but certificates still must
match actual delivered rows. [History API](../api/HISTORY.md). Local438unit evidence
is implementation qualification, not accepted artifact delivery.

Capability inventory must separate all batch IDs from session update/restore IDs;
otherwise the previous UPDATE_IDS=BATCH_IDS alias would falsely grant modes to
new history kernels. Keep explicit independent catalog expectations as capabilities
evolve and preserve historical R1 checks for its actual session scope. Revisit
under final installed delivery and subsequent numerical families; no unqualified
history state capability can be inferred from an existing session accumulator.


EF-L005 EQ027 corroboration:438source unit cases did not catch a stale installed
canonical example expecting total23batch IDs; local wheel and four CI package jobs
failed. Keep foundation tutorial assertions scoped to its actual session modes,
and maintain independent whole-catalog capability assertions alongside each new
family. Copying built-in metadata for a custom definition must clear execution
flags until a custom executor is separately qualified. Revisit every capability
extension under actual clean installed examples; source unit passes cannot waive
this gate. Failed8ea565c and corrected head remain in EQ027 continuity/PR176.


EF-L014 implementation qualification: corrected27d9ff6/main1896ff2 bothOS/docs
CI and actual bundles/FOUR fresh installed pairs each438tests/thirteenexamples pass;
[receipt](../stories/EQ-027_DELIVERY.md). Selected windows and truthful26batch/
23session modes are qualified; final receipt publication remains before Done.
Derived context coverage counts supplied grid definitions, not usable prices;
per-slot proof/quality owns numerical readiness. Preserve installed example failure
and correction under EF-L005; do not infer history state support from batch.

## EF-L015 exact dependency comparisons —2026-10-05

EQ028's independent int64-limit fixture shows a Float64 SMA and latest close can
round equal while their mathematical difference is half a coefficient tick.
The owned SMAReference exact sum/count witness preserves comparison signs by
cross multiplication while retaining the ordinary scalar result and original
bindings. [API](../api/HISTORY.md), [plan](../stories/EQ-028_PLAN.md). This is
structural validation, not authenticated truth: matching rounded projection alone
does not prove the supplied source or exact operands. Later breadth must admit
supplied config/context/dependency identities and use the exact witness, without
recomputing a missing dependency. No public history accumulator follows from a
bounded batch recurrence; registry modes remain explicit. Revisit under actual
installed delivery and EQ035/EQ037 consumer qualification.

EF-L015 implementation qualification: final e54d2e1/main39d1535 exact head/source/
main docs/bothOS CI and actual bundles/FOUR installed pairs each454tests/fourteen
examples pass. [Receipt](../stories/EQ-028_DELIVERY.md). Exact comparison and
bounded batch recurrence are qualified; final receipt publication remains before
Done. Corrected UTF8/spacing and premature install-count commentary are preserved
in continuity. Consumer admission/source authenticity remain caller responsibilities.

## EF-L016 recursive arithmetic memory versus admission —2026-10-05

EQ029's independent actual API fixtures preserve a nonneutral RSI through20,001
flat sessions by separating gain proportion from normalized total magnitude.
Absolute underflow must not fabricate the all-flat neutral50 convention. A later
new movement is combined relative to the still explicitly represented old
magnitude, with independent Decimal expected ratios. [API](../api/HISTORY.md),
[plan](../stories/EQ-029_PLAN.md). Bounded scalar recurrence is not a public
state mode or bounded total batch-memory claim; transient admitted prefix data
and TR construction costs remain visible.

ATR's current close is not in current TR arithmetic; predecessor close and each
TRhigh/low remain mandatory. Period1 may erase arithmetic memory but the frozen
epoch coverage rule still rejects earlier gaps unless caller replays or selects
a new epoch. Revisit under actual installed delivery, causality audit and semantic
legacy comparisons; local numerical passes are not artifact acceptance.

EF-L016 implementation qualification: corrected final d1b552c/main6311882 all head/
source/main docs/bothOS CI and actual bundles/FOURfresh installed pairs each472tests/
fifteenexamples pass. [Receipt](../stories/EQ-029_DELIVERY.md). Explicit epoch and
ratio-preserving batch behavior are qualified; final receipt publication still
gates Done. Numerical representation and admitted source proof remain distinct.

## EF-L017 tiny nonzero centered variance —2026-10-05

EQ030's int64-limit fixture has three closes that all round to the same Float64
price but distinct exact simple returns; the resulting sample volatility is
strictly positive near1e-38. Absolute atol1e-12 alone would permit an incorrect0.
Independent Decimal expectations plus strict positivity/relative checks qualify
that boundary. [API](../api/HISTORY.md), [plan](../stories/EQ-030_PLAN.md).

Exact transient centered fractions avoid raw-moment cancellation and need no
negative-variance clamp. Their finite arithmetic/storage cost remains explicit;
no public state or throughput claim follows. Default A1 is a frozen convention,
not a provider/calendar inference; explicit factor and sample denominator remain
part of configuration/math identity. Revisit under actual installed artifacts,
cross-family causality audit and any future measured numerical backend.

EF-L017 implementation qualification: final363b99f/main3162152 pass exact-head/source/main gates; both actual bundles and FOUR fresh Windows installed pairs each485tests/sixteen examples pass. [Receipt](../stories/EQ-030_DELIVERY.md). Tiny positive variance survives actual archive installation; final receipt publication remains before Done.

## EF-L018 original frame versus selected volume fact —2026-10-05

A selected target certificate must preserve original source-frame counts and row index, while its own coverage certifies only the chosen complete EOD row or explicit observed BAR prefix. Deduplicate exactly identical input identity/kind/metadata so prior and target rows from one frame do not forge a second source; reject conflicting revisions using the same ID. Derived dependency identities bind exact witnesses, not source authentication. [Plan](../stories/EQ-031_PLAN.md), [API](../api/DAILY_VOLUME.md).

Volume-only means no price fields enter arithmetic; existing canonical market PriceUnit metadata remains required. Initial fixtures incorrectly omitted it, and later had positional ConfigSpec/SourceBinding/reconstruction mistakes; corrected without widening schema or counting failed evidence. Exact witness/coverage/zero-denominator/explicit prefix behavior must be qualified in installed artifacts before acceptance. Revisit under bucket/composition/causality integration and future source qualification.

EF-L018 implementation qualification: finalbb0db95/mainffe8ddd exact-head/source/main gates and both actual bundles/FOUR fresh installed pairs each504tests/seventeen examples pass. [Receipt](../stories/EQ-031_DELIVERY.md). Original-frame identity and exact dependency/prefix/quantity guards are qualified; final receipt publication still gates Done. Status requires both actual jobs, not one completed job screenshot/output.

## EF-L019 bucket coverage is independent —2026-10-05

Actual early close can exclude a late bucket while an earlier bucket remains complete. Preserve N required slots, observed/expected coverage and ineligible reason; neither0fill nor observed-count denominator is valid under frozen EQ005. Daily coverage cannot certify a particular bucket. A supplied target prefix can carry observed data yet remain unavailable for a whole-bucket ratio. [Plan](../stories/EQ-032_PLAN.md), [API](../api/INTERVAL_VOLUME.md).

Single-bucket typed results retain existing Float64 output schemas and separate identities/quality. Future composition must preserve multiple bucket/horizon instances instead of overwriting by feature ID alone. Exact witness/source-row/cutoff/adjustment behavior still needs installed delivery before acceptance; revisit under composition/causality/source qualification.

EF-L019 implementation qualification: final3a493bf/main3fdbfb3 exact-head/source/main gates, both actual bundles and FOUR fresh installed pairs each522tests/eighteenexamples pass. [Receipt](../stories/EQ-032_DELIVERY.md). Independent bucket coverage and fixed N are qualified; final receipt publication still gates Done.

## EF-L020 alignment preserves actual component identity —2026-10-05

Compatible return comparisons need explicit horizon/selected grid/unit/policy/C-K-E and benchmark identity, while each child retains its real configuration/evidence bound and action snapshot. Parent identity cannot replace child digests. Sector label and benchmark instrument are distinct declarations; membership point is explicit, and missing membership affects sector only. [Plan](../stories/EQ-034_PLAN.md), [API](../api/RELATIVE_RETURNS.md).

Structural reference proof is not source authentication. Available return frame counts/completion and intrinsic positive-int64-price projection bounds can still reject contradictory claims. Bounded borrowed evidence maps to output entity but retains original source row plus full child identity. Initial example Float64-union typing errors were corrected using qualified typed casts before acceptance. Revisit under breadth/composition/causality/installed delivery and any future cross-namespace policy.

EQ034 final author review found conflicting supplied original-row proof could escape validation when the output evidence limit was zero/full. A separate validation map now checks every supplied proof independently of retained output size. A seventeenth regression covers compatible self-benchmark versus contradictory row known-at with limit0. Final539units/strict46files and nineteenth example pass. An attempted pytest invocation failed because this project uses unittest; the actual full unittest gate passed. No failed command counted as acceptance. Next remaining reference/source gates, exact-head repeated artifacts/local installations/CI/main actual bundles/final receipt; R3paused.


## EF-L021 expected universes and exact member witnesses —2026-10-05

Declared expected U is independent of supplied eligible data; preserve M and typed member exclusions, never fill absent returns with0 or shrink the fraction to K/M. Above-SMA comparison must use the exact sum/count witness; float equality near int64 can conceal an actual half-tick. Original-row proof must keep completed_interval boundaries when reusing SMA and close observations, deduplicate equal proof and reject conflict even limit0. [Plan](../stories/EQ-035_PLAN.md), [API](../api/DECLARED_BREADTH.md).

Initial source typing used a nonexistent cutoff field and a broad text edit misplaced a reasons assignment; corrected using existing AvailabilitySpec.knowledge_reason and proper scope. Registry breadth flags were initially stale, then corrected. Fixture assumptions incorrectly used FeatureResult.identity_digest/EvidenceRow.disposition/retrospective_reconstruction; corrected to metadata.identity_digest/use/reconstruction. Failed checks are not evidence. Revisit under composition/final causality/installed delivery and future source qualification.

EF-L021 source review also binds the explicit aggregate BreadthSpec identity separately from U/config and checks close auction policy against the actual session.21independent API cases/final560units/strict49files pass; installed delivery remains pending.

EF-L021 final acceptance found a compound diagnostic gap despite560passing tests: unavailable SMA plus unknown/late/absent close lost the secondary reason, especially visible with outputlimit0. Actual failing new regression preserved; pre-code addendum31c4439/PR219 returns035 from Released to In progress. Pair0.0.3a9 unions all dependency reasons without changing status priority/math/coverage, and repeats every artifact gate. Historical0.0.3a8 qualification retained, not final acceptance.


EF-L021 corrected actual main artifacts: bothOS four-archive manifests and FOUR fresh installed pairs each561tests/twenty examples verified; see [receipt](../stories/EQ-035_DELIVERY.md). External account merge had no recorded separate review, so tests/publication did not imply accepted delivery. Under resumed review policy, owner explicitly authorized an EQ035 separate local Codex reviewer; preserve its final-head coverage/findings separately from self-review, CI and hosted activation. The reviewer found a stale formula-page planned-status sentence, corrected alongside delivery docs. Next final frozen-head confirmation and final receipt publication verification remain; no Done claim from request or preliminary review.

## EF-L022 composition preserves actual producer contracts —2026-10-05

Distinct horizon/bucket instances must retain whole configs/results/owned contexts and exact companions; feature IDs alone are not a collection key. Direct normalized source ID ownership is instrument-specific and, for bucket_history, scope-specific even evidence_limit0. Separate pre-code review found this guard before implementation. Actual sampled/state-count and continuous quote producers share compensated backend but retain distinct evidence conventions; do not impose a false common default.

Separate source review reproduced two validation gaps: removing mandatory history/bucket context bindings from missing-source outputs could pass a wrapper, and changing history.return dtype/unit could pass. Mandatory producer context now derives from delivered IDs and exact consumed bindings; actual builtin output schema is checked with production price/currency/breadth conventions. SMA companions reuse SMAInput config/context admission. Regression fixtures cover removed-context missing sources and forged dtype/unit plus actual EUR prior extrema. An early-close test fixture lacked scheduled-close evidence; corrected without relaxing contracts. Exact producer schema mapping initially overused descriptive discovery units for breadth; corrected to actual members/fraction. Failed checks are not evidence. [Plan](../stories/EQ-036_PLAN.md), [API](../api/FEATURE_COMPOSITION.md). Final source review/installed delivery remain required.

EF-L022 post-installation audit found daily/bucket ownership guards were not enough: direct R1 producers also own instrument frames. Actual trade/bar/quote zero-evidence regression failed three subcases on a10; corrected a11 cross-validates direct session source population without banning same-instrument sampled/continuous reuse or derived-proof differences. Historical a10 BOTH main bundles/FOUR580test/21example installations retained, not accepted.21composition fixtures now pass; full gates/review/installed delivery must repeat before Done.

EQ036 separate a11 review reproduced a false rejection between actual session bars and unavailable bucket baseline sharing a valid original frame. Missing bucket scope is not a contradictory bucket claim. Both-order regression failed before population/bucket dictionaries were separated, then passed; conflicting instruments and two explicit conflicting bucket scopes still reject.

### EF-L023 — equation similarity is narrower than migration parity

EQ038 [evidence](../stories/EQ-038_COMPARISON.md): actual exportedGo EMA/ATR ordinary/warm-up/flat/period1/wide vectors executed on synthetic data, source fingerprints unchanged; wide nativeFloat64 ATR0 differs from exact-coefficient1. Broader inspection found worker/reference/robustmedian/breadth definitions beyondinitialkernels: source-only matching arithmetic does not establish grid/seed/unit/denominator/member/availability/state parity. Public CI replays captured observations and actual public APIs, not unpublished privateGo source. Preserve limits and do not claim fullworker parity or copyprivatecode.

## EF-L024 discovery must match actual producers — 2026-10-05

Three EQ037 integration tests exposed four actual descriptor mismatches before the
correction: prior high/low Float64 columns versus int64 discovery, and members/fraction
breadth units versus explanatory compound text. Actual failing subcases are retained
in local qualification logs. Correct the four catalog rows and remove consumer overrides
rather than change already qualified producer math. Whole-result future invariance and
independent eight-feature goldens pass; old recursive gaps remain unavailable while
finite complete windows recover. [Plan](../stories/EQ-037_PLAN.md),
[regressions](../../tests/unit/test_r2_integration.py). Full release gates remain pending;
revisit descriptor/producer parity whenever a builtin output representation changes.


Independent final R2 review reproduced a P2 missed by586green tests: supplied daily/bucket
baseline row0 and target row0 shared identity but contradictory timing could pass when
retention1 was full. At20 it rejected only via generic duplicate output validation.
Public pre-code0852392 precedes two actual failing regressions (four subcases).
a13 validates all supplied proof before retention, rejects typed inconsistent_identity,
and preserves same-frame targetrow3/2.5 ratios. Daily20/bucket19 targeted tests pass.
No source-authentication or proof reconstruction claim. Full suite/review/build gates repeat.


## EF-L011 R3 implementation checkpoint — October6

EQ093/PR237 now exercises an independently packaged synthetic calculator through public APIs, with independent5/100 versus5/103 results and negative identity/config/unit/mode cases. Its installed qualification is pending final frozen source/review/publication; do not infer Done from editable consumer success. Canonical positive-volume null OHLC is an admission error, not an unavailable calculation operand. Keep malformed schema, valid incomplete coverage and unknown/future knowledge as separate fixtures. Initial builds cannot qualify subsequently changed source/tests; freeze and rerun relevant gates. [Plan](../stories/EQ-093_PLAN.md), [API](../api/CUSTOM_FEATURES.md).


## EF-L015 nested extension result admission

Separate EQ093 reviewer /root/r3_reviewer at1d7de22 reproduced malformed nested result acceptance despite600green tests: outer dataclass reconstruction did not re-run nested column/quality/structured/metadata constructors. [PR237](https://github.com/atulsrivas1/equity-features/pull/237) corrects this in0.0.4a2 with recursively reconstructed owned contract types and pre-callback copied metadata. A frozen annotation is no conformance guarantee at a trusted-code return boundary. Preserve actual mutated-object regressions, requalify corrected final head and artifacts, and keep this contract check distinct from sandbox/source-truth certification. Prior a1 results remain historical, not accepted corrected delivery.

## EF-L016 adapter-owned typed error normalization

Separate EQ043 reviewer reproduced an external adapter leaking ContractError for incoherent OHLC and overflowing source bounds despite617green units. Constructor and owned chunk validation now translate only owned contract failures to safe SourceError(SCHEMA), retaining the original cause; actual two-failure regressions and619unit final-head review pass. Preserve source errors and trusted callback exceptions instead of indiscriminate wrapping. Consumer0.2.1 supersedes0.2.0 independently of unchanged corepair0.0.4a4. [Review](https://github.com/atulsrivas1/equity-features/pull/239#issuecomment-6018192856), [receipt](../stories/EQ-043_DELIVERY.md). Revisit at every new adapter-owned mapping/validation boundary; generic captured error fixtures alone cannot demonstrate real failures.

## EF-L017 installed typing lookup and workflow quota

EQ039's firstactualinstall failed despite stricteditable47green: directsite-packages folder input to pinnedmypy shadowed typing_extensions. Package-name discovery and separate caller check preserve PEP561 installedlookup; an independentfresha4wheel+consumer0.2.1 probe passes caller/consumer and3deliberately invalid calls. Preserve this failure and qualify installed signatures, not just source checks. [Pinned primary CLI](https://raw.githubusercontent.com/python/mypy/v1.15.0/docs/source/command_line.rst), [installed lookup](https://raw.githubusercontent.com/python/mypy/v1.15.0/docs/source/installed_packages.rst), [verifier](../../tools/verify_public_typing.py). Revisit when changing typingtoolchain/installtopology.

Repeated fullProject snapshots perstatus exhausted GraphQL quota duringR3; RESTrate_limit alone did not reveal actualGraphQLuserquota, whereas minimalGraphQL rateLimit query did. Use establisheditemidentity and targetedfieldmutations/readback, record unsuccessfulupdates honestly, and keep author/reviewer work distinct from actualProject state. No requirement to waive lifecyclegates or seek newownerpermission.

## EF-L018 executable installed workflow examples

EQ040's consumer0.3.0 executes supplied batch/chunk/history/composition/custom/adapter workflows with independent golden values and absent-input quality, using only installed public APIs. The fresh-install gate runs its module with Python isolation, verifies public imports and fingerprints core bytes before/after execution. Repository examples retain explicitly documented sibling fixture ownership; a catalog alone cannot establish standalone installation. [Catalog](../EXAMPLES.md), [walkthrough](../../examples/external_consumer/src/equity_feature_demo/walkthrough.py), [separate final-head review](https://github.com/atulsrivas1/equity-features/pull/243#issuecomment-6019017263). Revisit when adding example modules, changing install topology or adding workflows; actual source-main/final delivery gates remain distinct from author installs.

## EF-L019 measured process peaks and isolated benchmark provenance

EQ041 actual frozen-source Windows observations use native process high-water memory and independent arithmetic before timing, not Python allocations alone. Whole-child peaks include materialized input/chunks/backend conversions/reference/result work; peak differences cannot establish retainedstate or calculator-only allocation. Requested thread budgets are distinguished from effective backend counts, raw repeated samples/hardware/fixture/harness/source identities retained, and variable CI smoke JSON stays outside deterministic corearchive hashes. [Methodology](../BENCHMARKS.md), [actual samples](../benchmarks/EQ-041_WINDOWS.json). Revisit for EQ042retainedstate analysis and every optimization; no universal threshold or production scale inferred. Final separate review/publication qualification remains pending at this checkpoint.

Subsequent [separate final-head review](https://github.com/atulsrivas1/equity-features/pull/245#issuecomment-6019494076) independently verified raw statistical summaries/native unit definitions/normalizedharness hash and ran installedquickbenchmark/622units. TWO authorfreshpair qualification and exactheadCI pass; source-main ef99dd2 is published. Preserve actualmain/FOURfreshpairs/finalreceipt archiveequality and independent variablebenchmarkJSON checks as separate gates. Timing files cannot be required byte-equal merely because corearchives are reproducible.


## EF-L020 retained dimensions and object graph scope

EQ042 actual clean b6e84c3 21case Windows diagnostics distinguish growing input from bounded retained record dimensions. Deduplicated sys.getsizeof builtin/owned graphs exclude globals/code/unknown native buffers and are not exclusive ownership/nativeRSS/allocation. Small decreases with rowcount reflect object sharing/layout and do not justify exact constant bytes. Optional fixed prior/seed context can itself be a CanonicalBatch; absence detector assertions apply to these explicitly no-prior/no-seed cases. Configured K/evidence/window dimensions, clones and legal merge coexistence remain explicit. [Measurements](../benchmarks/EQ-042_WINDOWS.md), [raw cases](../benchmarks/EQ-042_WINDOWS.json), [diagnostic](../../benchmarks/resource_behavior.py). Preserve actual typed invalid_schema version/corruption failures, caller-only cancellation and the public close_weighted_price identifier; do not invent a barVWAP producer. Revisit for changes to retained shape/state layout/resource controls.


Separate [final-head review](https://github.com/atulsrivas1/equity-features/pull/247#issuecomment-6020136442) independently passed626units/strict48/sixinstalledresourcecases and verified21rawcases/scopes. It found default Windows text decoding corrupting historical UTF8 punctuation in224255d; correctedf94407b restores original history and appends explicitUTF8 entries. Always specify UTF8 for durable tracked-document reads/writes, inspect netdiff and re-review corrected finalhead. Runtime/test/build remain measured-source identical; actualmain FOURpair/finalreceipt gates distinct from review.


## EF-L021 version labels require boundary-specific admission

EQ044 source inventory distinguishes generic nonempty algorithm/math labels from owned consuming validators, config schema1 from savedstate schema2 and resultmathv1 from internal state binding r1-exact-compensated-v1. Exact implementation mismatch rejects invalid_schema, not a universal incompatible_version code. Digests bind facts but cannot reconstruct historical omissions or authenticate supplied sources. Existing specs/registry/results/composition/custom/state/overflow/resource fixtures independently qualify the actual boundaries; no duplicated documentation-shaped tests needed. [Guide](../VERSIONING.md), [plan](../stories/EQ-044_PLAN.md). Revisit whenever a validator/schema/equation/implementation or declared migration changes. Documentation-only release preserves package/test/build/consumer bytes and verifies actualmain bundle equivalence plus new variable provenance, under PUBLIC_DEVELOPMENT publication gates.
