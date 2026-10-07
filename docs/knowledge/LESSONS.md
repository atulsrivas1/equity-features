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


## EF-L022 installation invariance begins before installation

EQ045 found that a post-install core fingerprint can establish callback execution invariance while missing a consumer installation overwrite. Independent namespace-contamination/path-escape/privatepath archive fixtures reject beforeinstallation; actualcore module+distribution metadata fingerprints are taken beforeconsumerinstall, afterward and afterpublicexecution, excluding bytecode caches. Standalone consumerwheel/sdist are independently repeat-built, inspected and retained with separate manifesthashes; freshcorepairs install actualmatchingconsumerforms, not a source rebuild substitute. [Plan](../stories/EQ-045_PLAN.md), [builder](../../tools/build_foundation.py), [fixtures](../../tests/unit/test_distribution_isolation.py), [install guide](../INSTALLING.md). Revisit for any new external distribution, packaging backend/content/layout or install topology; actualsource/FOURfreshpairs/finalreceipt remain distinct gates.


Subsequent [separate final-head review](https://github.com/atulsrivas1/equity-features/pull/250#issuecomment-6020694564) independently628units/strict48/archivecontent-license and184links pass; authorTWOactualcore+consumerforms confirm before/afterinstall/execution equality. Source-main c88a282 bothOSCI and actualconsumerreports verify actualinputartifact identities rather than a rebuilt example. Preserve FOURactualsourcepairs/currentfinal12archives+report checks as separate delivery gates; fingerprint digests bind installed metadata without exposing raw localdirectURL paths.


## EF-L023 backend initialization and conversion are separate purity scopes

EQ046 strict guard found Arrow20 sequence conversion reads PYARROW_IGNORE_TIMEZONE per call; merely importing pyarrow does not preload lazy compute/sysconfig. Versioned upstream source supports the observed lookup. Preload compute before execution, preserve all selected file/network/clock/process guards, separately run593 strict canonical fixtures and619 full fixtures with only audited backend key/exact26-case inventory. Snapshot43 owned module declarative data and prove detector with restored injected mutation; no allnativeglobal/callback sandbox claim. [Audit](../PURITY_AUDIT.md), [tests](../../tests/unit/test_purity_audit.py), [plan](../stories/EQ-046_PLAN.md). Revisit for new backend APIs/versions/import timing/owned global data or additional audited fixture cases.


## EF-L024 artifact and dependency provenance have distinct scopes

EQ047 inspected13 pinned upstream wheel/index hashes and complete shipped notices, including actualinstalledWindows matchingbytes and Linux-target native notice variants. NumPy/Arrow metadata license labels alone omit bundled notices; do not infer universal SPDX expressions or redistribute stripped binary license texts. Developmentpip25.1.1 differs from observedfreshbootstrap25.0.1; CPython minor selection/actiontags/indexversionpins are not immutablepatch/hashlocked/hermetic acquisition. Actualresolvedactions/source/OS/innerarchivehashes/serverbundledigests/expiry are distinct evidence fields. [Review](../RELEASE_INTEGRITY.md), [inventory](../DEPENDENCY_INVENTORY.json), [plan](../stories/EQ-047_PLAN.md). Revisit for any dependency/tool/nativewheel/platform/channel/permissions/rights change; no stable/registry/authentication or arbitrarycode license/security certificate.


EQ047 separate draftreview(7ff6539) caughtP2 prose conflating sourceLinux3.12.14 and finalLinux3.12.15; inventory and downloadedfinalmanifest alreadycorrect. Correct currentprose/handoff, preserve explicit source/final observations and re-review newhead. Archivebyte equality doesnotimply interpreter/tool provenance equality under a floatingminor selector. This correction strengthens the distinct-evidence rule; no package/test change.


## EF-L025 qualify admitted inputs and actual installed artifacts

EQ095 initial probe incorrectly treated zero OHLC as a reachable denominator outcome. Canonical positive-price admission rejects it first; valid zero-volume null prices do not replace the next price-bearing open. Use actual public admission and unknown availability to qualify missing_input; never weaken core validation to force a desired fixture. A wrong but contract-valid0.06 callback proves the independent5/100 golden can detect numerical error. Retain43 actual synthetic outcomes inside each installed consumer receipt, with actual archive/source/version and core installation/execution fingerprints; source-tree success cannot substitute. Historical backend/resource/license observations keep original versions. [Qualification](../EXTERNAL_QUALIFICATION.md), [plan](../stories/EQ-095_PLAN.md). Revisit for new input/callback modes, report schema or consumer artifacts.


## EF-L026 release acceptance joins live status with exact published evidence

EQ048 reads all50boundedR0–R3story Project records, acceptedprior milestones/repairs and actualqualified095source/final artifacts. A currentliveDone predecessor count does not substitute for exactfinalheadreview, publicblobs/tree, bothOSCI/downloaded archives and independently currentvariable reports. Conversely doc-only source-identical acceptance need not invent newnumericaltests/redundantlocalinstalls/secondreceipt. Preserve original measured/license/interpreter baselines and state laterconsumer metadata changes explicitly. Closeownstory afterReleasedreadback, then reconcileepic/milestone fromactualallDone. [Acceptance](../R3_ACCEPTANCE.md), [plan](../stories/EQ-048_PLAN.md). Revisit for changedcode/dependencies/requiredreview/publicchannel/scope; stop at ownerboundedrelease.

## EF-L027 metadata resolution is not row or source admission

R4 bootstrap independently inspected catalog metadata: explicit generation/layer
selection and retained sizes/schema/substitutions are available, while content
hashes require external receipt binding. Preserve original/optimized identities
and unknown admission rather than infer hashes, eligibility, clocks, calendar or
PIT from file presence/rewrite counts. EQ049 resolves metadata; EQ050/051 map/read
rows and EQ053 binds acquisition stability; EQ054/055 separately qualify synthetic
and actual numerical behavior. [Concrete plan](../stories/EQ-049_PLAN.md),
[qualification strategy](../R4_TEST_STRATEGY.md),
[handoff review](https://github.com/atulsrivas1/equity-features/pull/259#issuecomment-6023300273).
Revisit for changed catalog/schema/receipt/admission or source representations.

EQ049 release qualification distinguishes normalized Git source from actual working
checkout bytes: local new LF files and WindowsCI CRLF produce different optional
archive hashes, while each repeat-build is stable. Inspect member/RECORD differences
and qualify actual downloaded bytes; do not claim cross-checkout reproducibility.
Source-main producer interpreter also has its own provenance even where archive
hashes match priorPR evidence. [Receipt](../stories/EQ-049_DELIVERY.md).


## EF-L027 retained normalization needs explicit clock and policy evidence

EQ050 reuses accepted quantize_float_prices rather than duplicating numerical rounding. Interpretation/rounding/report identity cannot recover original scaled coefficients from retained DOUBLE. Exact UTCns parsing does not identify source clock, eligibility, calendar or known-at; require explicit evidence-bearing caller declarations, preserve unavailable/null and UTCdaily versus RTH distinctions. Source-occurrence identity preserves tied equal payloads without certifying exchange uniqueness. [Mapping API](../api/DUCKDB_MAPPING.md), [receipt](../stories/EQ-050_DELIVERY.md). Revisit for source representation/clock/eligibility/availability or normalization-policy changes.


## EF-L028 physical occurrence and measurements need explicit boundaries

EQ051 keeps original Parquet physical row identity through filtered/sorted reads;
optimized row positions cannot certify original occurrences. Map the whole bounded
population once so chunk delivery retains stable normalization/schema/coverage;
caller assertions bind exact selected populations rather than infer provider
completeness. Actual catalog.duckdb fixtures exposed database/schema ambiguity;
qualify identifiers without relaxing bound values. Measure whole public read plus
SQL/materialization/copy phases and actual installed native lifetime high-water
units; selected file sizes and DuckDB memory settings are not I/O or process-cap
measurements. [Plan](../stories/EQ-051_PLAN.md), [API](../api/DUCKDB_READER.md).
Revisit for storage rewrite/row identity, streaming, stability/coverage or measurement
method changes; final installed/review/publication evidence remains pending.


EQ051 clean installed environments exposed DuckDB Python-UDF NumPy dependence
masked by development imports. Pin/verify the optional runtime explicitly and
retain failed installation evidence; core invariance remains separate. Reviewer
null-time probe proved backend default null handling could silently certify empty
selection; route malformed event times through the parser and reject before
coverage assertions. [Actual receipt](../stories/EQ-051_DELIVERY.md) distinguishes
clean measurement source, doc-only head reuse, native producer Python provenance
and FOUR actual downloaded-form installs. No final receipt/publication claim yet.


## EF-L029 governed requests preserve structural gaps and source timing

EQ052 delegates finite membership to accepted WindowSpec and retains explicit
recursive anchor prefixes. Request sufficiency is not numerical readiness; a
missing prefix cannot be skipped or restarted, while a complete finite window can
recover. Actual daily row presence must agree with explicit per-slot certificates;
null fields are present unavailable observations, not absent or zero-filled rows.
Retained UTCdaily intervals cannot be relabeled RTH, and caller schedules do not
acquire calendar authority from file dates. Supplied reference availability gaps
observe the whole population; pure admission still selects relevant effective
facts and decides feature quality. [Plan](../stories/EQ-052_PLAN.md),
[API](../api/DUCKDB_GOVERNANCE.md). Interim independent75cases/strict5 pass; final
installed/review/publication evidence remains pending. Revisit for source calendars,
normalization, seed/window requirements, reference acquisition or PIT evidence.


EF-L029 delivery evidence: [EQ052 receipt](../stories/EQ-052_DELIVERY.md) binds actual synthetic Parquet finiteSMA40/prior35 versus anchoredmissing input, separately reviewed75installed cases and fouractual forms. Supplied sessions/certificates/reference facts are assertions; structural history sufficiency and whole-reference gaps never replace pure numerical or relevant-fact admission. Revisit when calendar/source/reference authority or history policy changes.


## EF-L030 acquisition hashes preserve observation boundaries

EQ053 binds actual current originals and normalization to evidence while rechecking catalog route/metadata and supplied pins. Same-sized content needs SHA256, not size-only checks. A newly observed hash is not a prior source pin or provider admission; optimized hash equality is not rewrite parity and pre/post equality is not atomic snapshot isolation or change/reversion exclusion. Bind original occurrences to actual observed content, preserve legacy/substitution/known-at/coverage declarations, and bound cumulative verification separately from SQL costs. [Plan](../stories/EQ-053_PLAN.md), [API](../api/DUCKDB_EVIDENCE.md). First development run failed Path JSON serialization; explicit catalog path encoding fixed it, prior75suite passed. Newfixture used wrong knowledge field name; corrected to accepted knowledge_cutoff_ns. Failed checks excluded. Revisit for physical source/replay/stability/availability policy changes; finalreview/installed/publication gates remain.


EF-L030 correction: [separateP2review](https://github.com/atulsrivas1/equity-features/pull/268#issuecomment-6025612285) independently reproduced transient file size causing nested hashcounter under-accounting. A priorstat is not an actual read charge. Share one actual cumulative counter across resolver/acquisition, and verify exact-bound adversarial restoration; outputwithholding alone does not prove resource-bound compliance. Current15regressions pass; priorheadbuild/greenchecks superseded.


EF-L030 [corrected actual delivery](../stories/EQ-053_DELIVERY.md) binds sharedcounter adversarialregression/90cases/fouractual forms; originalrace independently resolved by finalreview. Priorstats cannot account for actual nested reads; matchingobservations/bytebudget compliance/provideradmission are separate checks. Purecore unchanged; finalpublication gates remain.

## EF-L031 conformance observations and source coverage stay distinct

EQ054 supplies actual DuckDB envelopes/errors to the unchanged SDK and independently checks admitted public calculations. Source population coverage can legitimately exceed a delivered subset; uniformly declaring count4 across chunks delivering3 is not a defect. The rejection fixture changes one chunk's source coverage and verifies cross-chunk inconsistency. Initial malformed envelope failed its constructor, and the uniform-coverage expectation was rejected by actual SDK behavior; both runs are excluded. Check actual error stages rather than inventing adapter output. Canonical source unit checks exclude auxiliary history-grid metadata bindings, which have no price unit. Freeze explicit completed_eod membership for SMA/EMA goldens; default prior_only has different semantics. [Pre-code plan](../stories/EQ-054_PLAN.md), [guide](../api/DUCKDB_CONFORMANCE.md). Current92source tests29.634s/strict7/purity pass; installed/final-review/publication gates remain. Revisit when SDK coverage, history membership, source binding or fixture execution changes.

EF-L031 [actual source delivery](../stories/EQ-054_DELIVERY.md) binds thirtyactual SDK outcomes/sixteen independent numeric-unit-quality-binding checks/fouractual forms. Cross-chunk source coverage consistency is distinct from selected delivery counts. Source versus installed provenance is enforced; actual current harness/form/archive identities precede acceptance. Final publication gates remain.

## EF-L032 bounded delivery does not bound SQL callback work

EQ055 real-source development invoked at least10000 Python timestamp callbacks while requesting five bars. Owned output row bounds do not prove work proportional to selected rows. Interrupted old-query timing is not a benchmark or speedup denominator; timed-stack/native-crash observation does not establish a crash cause. Native source probes must preserve strict lexical/calendar/null/clock/fraction/int64 semantics, not silently use permissive TIMESTAMP_NS casting or lose extreme sentinel values. Pre-code refinement freezes native HUGEINT→guardedBIGINT arithmetic and consistent ASCII ISO admission before implementation. Two literal/stdlib/error methods and94sourcecases/strict7 pass; current installed/private/finalreview gates remain. [Plan](../stories/EQ-055_PLAN.md), [methodology](../api/DUCKDB_REAL_QUALIFICATION.md). Revisit when query/parsing/backend/source populations change; private rows/pins/receipts stay private.

EF-L032 installed evidence: clean a7 source f70d82c passed both fresh 94-test synthetic forms and two additional fresh real qualifications, each 68 numerical/status/unit/source checks, nine acquisitions and three blocked cases. Private immutable scope retains the original a6 preparation stamp; actual completed reports independently bind a7 artifacts/runtime/source/script. Preserve both identities rather than editing preparation to imply it already represented the final implementation. Whole-process native peaks and complete acquisition costs are observations with explicit scope; no old-query denominator means no speedup claim. Final review and actual delivered-main forms remain required.

EF-L032 [actual delivery](../stories/EQ-055_DELIVERY.md) binds four delivered a7 forms, each94synthetic tests and68private numerical/status/unit/source checks/nine acquisitions/three blocked cases. Native parsing fidelity and source/package/report provenance are separate gates; successful bounded real checks do not infer full-corpus cost/provider/PIT truth. Final publication/readback remains.

EF-L032 delivery correction: [issue62 evidence](https://github.com/atulsrivas1/equity-features/issues/62#issuecomment-6027020059) records a helper that assumed exactly10CI checks although15actual checks had passed before merge; its PowerShell command continued after failure. Count returned checks honestly, require all completed success and required roles, and make dependent merge commands fail fast. Git head guards and successful independent evidence do not excuse a launcher ignoring failure; retain the actual correction without inventing missing gates.

EF-L032 [R4 audit](../R4_ACCEPTANCE.md) retains both executed layers and explicit artifact/runtime/receipt/private-source bindings. Historical source measurements and preparation stamps are preserved; current acceptance comes from current delivered hashes/reports/readback, not silently relabeled history. Final docs-only reuse requires actual byte equality plus currentnative/private evidence. Revisit for changed backend/parser/source populations or capabilities.


## Architecture clarification, October 6

[R4 acceptance](../R4_ACCEPTANCE.md) established pure dependency boundaries while the optional adapter remained co-located. [GOV-014](https://github.com/atulsrivas1/equity-features/issues/275) adds repository separation as an ownership decision. Repository separation and dependency purity require distinct evidence: preserve inward imports and qualify installed compatibility during extraction. A renamed repository alone establishes neither. Revisit if new package dependencies threaten core independence.

## Handoff dispatch and readiness are separate gates

[GOV-015/PR290](https://github.com/atulsrivas1/equity-features/pull/290) review found a dependency cycle: preparation Done required assigned-session evidence, while the draft required preparation Done before assignment. Publish the reviewed handoff first; permit bootstrap-only assignment, verify it and close preparation; refresh actual Done before implementation. Keep these boundaries explicit in continuity, kickoff and acceptance. Revisit if a later handoff adds a prerequisite requiring the session that it also prevents creating.


## EF-L033 committed source provenance excludes working-tree additions

Separate EQ121 reviewer reproduced a P2 in both new companion builders: `git diff` alone ignores untracked discoverable Python files. Such a file could enter a dependency wheel even while its receipt named the accepted core commit. Corrected builds materialize exact Git archives for component and dependency package sources. An independent synthetic regression creates both untracked code and modified tracked bytes and verifies only committed bytes survive. [Canonical correction](https://github.com/atulsrivas1/equity-features/issues/278#issuecomment-6028430623), [I/O final review](https://github.com/atulsrivas1/equity-feature-io/pull/1#issuecomment-6028459186), [workers final review](https://github.com/atulsrivas1/equity-feature-workers/pull/1#issuecomment-6028459420). Initial green builds/CI are retained as superseded provenance evidence; corrected final-head CI/install/publication gates remain separate. Revisit for any source materialization, packaging input, dependency pin or artifact receipt change.


## EF-L034 extraction identity and qualification head are separate bindings

[EQ122 plan](../stories/EQ-122_PLAN.md) preserves canonical source/mapping identities while changing adapter receipt/package version0.1.0a7 to0.1.0a8. The receipt digest changes with its declared version field; compare complete receipt fields with explicit stamp/digest exclusions, never relabel an old receipt. Native same-file old/new actual installed comparisons bind both artifact hashes. Build reports capture the committed source head before materialization and reject a changed head/dirty source at completion; a build begun before source corrections is superseded even if its tests pass. [Separate reviewer record](https://github.com/atulsrivas1/equity-feature-io/pull/2#issuecomment-6028784915) resolves the relocated package link and reviews the corrected source guard. Current artifact/native/private/publication gates remain pending. Revisit when extraction/runtime stamps, receipt identity, build provenance or fixture bindings change.

EF-L034 standalone [actual main receipt](../stories/EQ-122_STANDALONE_RECEIPT.json) verifies bothnative currentreports/all24archives/all4serverZIP hashes/private4certificates reused by exact archive equality/publictree69/owner. Originalprivate execution was Windows3.12.10 for bothproducers; no Linuxprivate/fullcorpus inference. Core active removal begins only after that gate; purepackage bytes are preserved. Core review/CI/publication/canonical acceptance remains pending.

EF-L034 evidence wording correction: [completed separate core review](https://github.com/atulsrivas1/equity-features/pull/292#issuecomment-6029075161) resolves the historical example link and distinguishes43consumer qualification cases (including negative/error/discovery checks and numerical goldens) from43numerical goldens. Preserve case categories when summarizing evidence; do not inflate numerical coverage from the total test count. Actual12core/consumer archives equal accepted2cd51cd; current12reports/localfreshforms are separately bound in the [source receipt](../stories/EQ-122_CORE_SOURCE_RECEIPT.json). Finalcurrenthead/main acceptance remains under canonical279.

EF-L034 [EQ122 final acceptance](https://github.com/atulsrivas1/equity-features/issues/279#issuecomment-6029210719) verifies actual coremain45b3a6b and standalone7475e1e with final reviews/native/current reports/all channel hashes. Evidence parsers must explicitly decode UTF8 on Windows and count executions by platform/step: development plus installed wheel plus installed sdist yields three633-test runs per platform. A mistaken parser assertion is not a product failure, nor permission to bypass the check. Revisit for log formats or qualification step changes.

## EF-L035 complete native artifact membership precedes acceptance

[EQ123 acceptance](https://github.com/atulsrivas1/equity-features/issues/280#issuecomment-6029468862) verifies both native platforms explicitly. A running Actions job may expose only its completed Linux artifact; a nonempty download directory is not a complete supported-platform matrix. Require exactly both producer records and all current successful role checks before publication, then verify successful-main files/hashes/reports. Fetch the actual published Git object before comparing its fixture tree; a missing local object is a verifier precondition, not absent published source. Preserve failed/precondition checks without counting them as product qualification. Revisit when adding producer platforms, artifact discovery or Git source-provenance checks.

## EF-L036 startup admission and operational conformance require distinct evidence

[EQ124 acceptance](https://github.com/atulsrivas1/equity-features/issues/281#issuecomment-6029784487) qualifies separately installed synthetic factories/direct admission and exact declared capability views.21factory tests per freshform differs from23development cases including provenance. No acquisition/write by SDK admission does not sandbox trusted constructors, certify declared backend guarantees or establish a full runtime sink. Preserve this boundary when EQ125 adds operational conformance and EQ126/127 qualify actual process/storage behavior. Source/final/main heads, actualruntime patches and currentartifact hashes remain explicit bindings; unchangedbytes can support reuse but do not replace currentmain reports/readback. Revisit when admission side effects, codec/lifecycle or backend capability claims change.

## EF-L037 negative admission checks are separate from positive serialization/conformance

EQ125 separate reviewer [actual0a findings](https://github.com/atulsrivas1/equity-feature-io/pull/5#issuecomment-6029970029) independently reproduced dropped visibility/writer/retention requests and unknown wireversion admission despite44positive/negative existing tests and strict11files. Frozen envelope omits local operational guarantees intentionally; helpers must reject them as limits or enforce an explicit separate publication request. Raw wireversion/schema admission must precede current canonical construction, even when a future identity has a mathematically valid recomputed key. Conformance must test the backend's declared busy/exclusive-restart policy instead of rejecting an allowed design branch universally.

Corrections retain frozenwire/K/math semantics and add three regressions covering omitted requested guarantees/no reservation, exactversion matrix/validfuturekeys and mutually exclusive staging policies. Initial CI also lacked the purefeatures development dependency for a new numerical fixture while local/fresh environments already had it; declare all verification-only inputs in CI without adding them to product dependency metadata. [Rework record](https://github.com/atulsrivas1/equity-features/issues/282#issuecomment-6029967281). Old passing local0a artifacts are superseded; renewedreview/currentnative/freshforms/main readback remain required. Revisit for any config-to-envelope translation, decoder schema/version selection or backend recovery guarantee change.

EF-L037 [renewed review](https://github.com/atulsrivas1/equity-feature-io/pull/5#issuecomment-6030033580) reproduced two further P2s after47 green tests: restart returned an unusable handle but conformance never used it, and factual corrupt committed bytes were masked by a COMMITTED abort receipt. Exercise the replacement handle through full write/commit/verified readback, and preserve factual CORRUPTION through recovery branches. Independent fixtures must withhold committed receipts for physical or logical corruption. Corrected48 development cases and strict11 files pass locally; old32 artifacts/checks remain superseded, renewed exact-head review/current fresh/native/main gates pending. Revisit for recovery short circuits, replacement ownership or receipt-only success assertions.

EF-L037 [actual EQ125 acceptance](https://github.com/atulsrivas1/equity-features/issues/282#issuecomment-6030216151) verifies final reviewed heads/main publication and all40native delivered archives/current reports/sixserverZIP digests/allfiles/owner/retention. Final separate reviews6030152777/6030153334 preserve all five P2 dispositions; native48development/fourinstalled25publication21factory/strict typing hold. This is logical synthetic sink qualification, not process/storage durability. EQ126 now owns the real filesystem/process/resource evidence; unchanged source semantics permit no new private execution.

## EF-L038 physical schema and expansion bounds need real backend evidence

EQ126 initial Parquet run rejected valid cell schemas because PyArrow20 emits compliant list child element while the inferred Arrow schema used item. Explicit child names/metadata and closed reader handles are part of physical conformance; accepted logical codec bytes alone do not qualify stored projections. Repeated namespace/header strings can expand small canonical records greatly: admit actual repeated payload before Arrow allocation and limit every physical write, rather than checking size only after producing an oversized file. Corrected local15independent methods/strict5 files pass; actual native child-process/resource/fresh-form/main delivery remains pending under [EQ126](https://github.com/atulsrivas1/equity-features/issues/283). First fixture assertions also had wrong lowercase enum casing and invalid handle; retain failures as harness corrections, not fabricated backend failures or acceptance. Revisit for schema/backend/library upgrades, projection duplication, footer/buffer accounting or reader lifetime changes.

EF-L038 read-side correction: [separate I/O interim review6030431572](https://github.com/atulsrivas1/equity-feature-io/pull/6#issuecomment-6030431572) / [core6030432083](https://github.com/atulsrivas1/equity-features/pull/296#issuecomment-6030432083) reproduced2MiB ZSTD expansion from5727bytes and uncompressed dictionary amplification. Footer row/physical hash checks alone permit expanded allocation before parity rejects corruption. Admit qualified UNCOMPRESSED PLAIN/RLE format (reject dictionaries), bounded uncompressed footer bytes/group rows/leaf counts and conservative expected repeated payload/nullable fixed widths/offsets before Arrow read. Two altered/recomputed physical receipt regressions assert the read call never occurs.17development methods/strict5 passed before additional leaf-count admission; current source/full final-head acceptance still required. Eight real owned-child interruption/concurrency methods and two fresh Windows3.12.10/NTFS resource workloads64/2048cells locally pass, with exact int64/result/status parity. First different-content concurrency assertion wrongly excluded BUSY before reservation; correct fixture allows it and checks actual loser conflict after commitment. First resource script omitted required limits; excluded failed run/corrected measurement. These harness corrections do not prove backend faults or universal durability. Native fresh forms/current release gates remain pending.

EF-L038 source qualification [receipt](../stories/EQ-126_SOURCE_RECEIPT.json) binds8892ff6/core632cc24,54archives/eight serverZIP hashes/allfiles/finite retention/current source owner and full native installed physical/process/resource evidence. Native3.12.10/NTFS and3.12.14/ext4 process recovery is narrower than powerloss/network/adversarial namespace guarantees; no hard RSS/latency/private certificate. The first downloaded pull_request merge checkout78cff7a was rejected by the source-head guard; retain it as excluded provenance and use actual push/main checkout artifacts. Final package README uses current-evidence links instead of perpetually pending labels; changed packaging documentation requires new current actual artifacts. No mathematical/source/SDK/worker code changes.

EF-L038 [updated package source qualification](../stories/EQ-126_UPDATED_SOURCE_RECEIPT.json) preserves prior8892 receipt while binding94ccc/core7050 actual54archive/eightZIP/currentreports/owner/retention. New package README changes archive identities despite unchanged runtime; repeat/currentfresh/native verification is required rather than assuming doc-only packaging parity. Native patch release may vary across actual runs; retain producer runtime per report rather than extrapolating earlier3.12.14 to all subsequent Linux evidence. Renewed reviews6030586049/6030586582 verify previousfullreceipt and execute exactpublicdirectexample; currentfinalreceipt/head delta and main release gates remain distinct.

EF-L038 [actual EQ126 acceptance](https://github.com/atulsrivas1/equity-features/issues/283#issuecomment-6030782648) / [release receipt](../stories/EQ-126_RELEASE_RECEIPT.json) binds finalf59d92c/core6039fa1 to actual0002177/347d4fd,54mainarchivefiles/eightserverZIP hashes/all96files/currentreports/publictree-owner/finite expiry. Final separate reviews/artifact supplements independently cover current source; no unresolved P2. Real localprocess/manifest recovery/17physical8process/fourfreshforms/two resource workloads are narrower than network/adversarialnamespace/powerloss/hardRSS/provider/private guarantees. NextEQ127 uses database transaction/connection evidence independently; file-hash immutability cannot be inferred for a mutable multigeneration database.

## EF-L039 mutable database receipts and fresh committed snapshots

[EQ127 published plan](../stories/EQ-127_PLAN.md) separates immutable row-BLOB references from changing database pages, and cooperative process ownership from unsupported simultaneous native multi-process sharing. Separate automated pre-code review independently demonstrated an open control read transaction can miss a later commit until its snapshot ends. Use independent autocommit control statements and test both precommit STAGING/no results and postcommit verified complete receipt; merely using a second connection is insufficient.

[Current implementation evidence](../stories/EQ-127_DELIVERY.md) passes18localmethods/all18facts/21logicalcases/literalprecision/numerical50051200102.6/strict6;8real interruption/contention methods then ninth source DB+WAL rejection byte-invariance case passed. Fullrenewed9/native/freshinstalled/finalreview/main gates remain pending. Initial bytes-bundle codec rejection corrected with fixed-position inert hex, preserving accepted SDK bytes; constructor FactoryError translated to SinkError. Probe zero-spill display is '0 bytes'; wrong integer0 assertion excluded/corrected. 77.002s2048-cell write is observed, not a performance promise. Revisit for engine upgrades, explicit control transactions, receipt references, source-write preflight, lease/handle order and bounded reader changes.

EF-L039 [initial source review6031030267](https://github.com/atulsrivas1/equity-feature-io/pull/7#issuecomment-6031030267) independently reproduced two P2s despite18methods/9process/native bothforms passing: same-owner begin after actual COMMIT/lostresponse returned BUSY instead original verified receipt; persisted malformed envelope returned INVALID_CONTENT instead factual stored CORRUPTION. [Rework6031028441](https://github.com/atulsrivas1/equity-features/issues/284#issuecomment-6031028441) returns story to In progress. Inspect independent completion before own-active BUSY; normalize stored decode errors; exact regressions extend existing meaningful methods. Historical UTF8 helper decoding also corrupted unrelated continuity; restore exact pre-code historical text with explicit UTF8 and verify only additions remain, rather than accepting broad diff. Initial a799907 artifacts are preserved/superseded; renewed review/current fresh/native/main gates required.

EF-L039 [corrected source receipt](../stories/EQ-127_SOURCE_RECEIPT.json) binds f178d625/coreacc3f0e with actual68archivefiles/tenserverZIP hashes/all118files/currentreports/sourceowner/finiteexpiry. Renewedreviews6031112127/6031112734 independently resolve both P2s and historicalUTF8/EOF issues. Nativefourfreshnewforms18methods/9realprocess/sourceDB+WALbyteinvariance/commitlossoriginalreplay/malformedstoredCORRUPTION/publictyping/coreinvariance/twomeasuredworkloads pass. No private rerun; oldpackage/mathematics bytes remain equal. Readback-helper naive count substitution changed expected fixedepoch accidentally; failedverification excluded, exact1700000000 restored/fullactualverification renewed. Use targeted invariants and inspect literals rather than broad digit replacements. Finalmetadata/main publication acceptance still pending, and measured engine/RSS/DB/latency are narrower than universal resource/durability claims.

EF-L039 actual EQ127 acceptance [6031394363](https://github.com/atulsrivas1/equity-features/issues/284#issuecomment-6031394363) binds reviewed ae119aa/core75523ea to actualmain3a4b750/core584fa87,68archives/tenZIPs/118files/currentnativefresh reports/owner/finiteexpiry. Allmainarchives equal finalqualification by platform. Mutable DB page hashes never identify immutable generation row-BLOB receipts. Lost-response original replay/stored CORRUPTION regressions are required despite broad green suites; local process recovery remains narrower than powerloss/universal durability. Six supersededmetadata backend runs cancelled/preserved, not accepted.

## EF-L040 public extension defaults and cancellation boundaries

[EQ128 pre-code plan](../stories/EQ-128_PLAN.md) / [implementation delivery](../stories/EQ-128_DELIVERY.md): SDK.a2 SinkRequirements defaults allow zero cells; runnable nonempty calculation publication needs explicit planned bounds. Existing SDK publish creates a reservation before checking cancellation before writes/commit; pre-existing cancellation yieldsABORTED/no receipt, not proof no reservation/ABSENT. Initial independent tests exposed both incorrect consumer assumptions; they were corrected without changing accepted SDK behavior, then12meaningful methods/strict6files pass. Complete byte round trips need independent expected source IDs/coverage/timing/status/unit/evidence and literal values; close-weighted102.6 is a proxy distinct from actual-notional51200/500=102.4. Installed/native/main qualification still pending. Revisit if the frozen public protocol is explicitly versioned; do not silently change existing behavior for a tutorial.

EF-L040 actual source efec935/core90f1fc8 reviewed6031585443/6031586011, current native source receipt82archives/twelveZIPs/134files/Atulowner/finiteexpiry and actualfreshfourstandalone/fourcalculationconsumer forms pass. Protocoltyping/12meaningfulmethods/21actualcases/18facts/independentall12values+metadata/status/coverage/unit/evidence/twoinvalidcalls/purebyteinvariance support publicextension composition. Independently installing without featurelibrary/fixture/backends proves dependency direction beyond editable import success. Finalmetadata/main gates still pending; no remoteuploadedcode/processdurability/private guarantees.

EF-L040 separate finalmetadata reviews6031647166/6031647721 found P3: copied Linux3.12.14 qualification prose despite actual newextensionmanifest/report3.12.15. [Rework6031647590](https://github.com/atulsrivas1/equity-features/issues/285#issuecomment-6031647590) corrects allsix duplicatednew passages; receipt/native archives already correct, no code/artifact defect. Derive runtime prose from the story's actual producer reports rather than earlier backends; versions can differ within one native matrix. Superseded metadata CI may be cancelled with retained records to free capacity, never counted as currentcorrectedhead evidence. Renew exactmetadata review/currentCI/main gates before acceptance.

## EF-L041 composed compatibility requires source-specific facts and actual conflicts

[EQ129 concrete plan](../stories/EQ-129_PLAN.md) and [delivery](../stories/EQ-129_DELIVERY.md): separate automated reviewer preparation caught that accepted DuckDBsource.a8 enforces UTC-minute intervals and supplies no actual_notional. Keep custom source500/51200/102.6 separate from minute sourcevolume8/weighted11.625/notionalnull/MISSING_INPUT; no interval/source rewrite or fabricated notional to make parity. Own-temp preparation independently ran all three public sink readbacks and source catalog/original/optimized Parquet invariance; WAL absent before/after only, not WAL-present coverage. Source identity and available fields/timing can differ legitimately; complete readback bytes must agree within each declared source.

Historical negative compatibility cases need every requested transitive actual archive offline, explicit resolver conflict and a real forced-install pipcheck rejection; missing-candidate failures are not compatibility evidence. Oldworkers.a0 requiresSDK.a0, currentSDK.a2 requiresIOcontracts.a2; skeleton.a1 alignment is metadata/version/build provenance only. Use committed probes/fixed accepted dependency commits/captured head plus scoped/end guards, rather than mutable working probes or late-reported heads. The initial composed source-error fixture used nonexistent IO enum; corrected to public TRANSPORT with a safe message, then all six meaningful development methods/nine routes pass. This is preparation/development evidence; final review/currentnative/fresh archive/main acceptance pending.

GraphQL quota exhausted during actual EQ128 release; identical exact-head/check/sha guards allowed REST merge/publictree/owner readback. Official GitHub Projects REST2026-03-10 supports selected-item field update/readback, verified actual Readyrelease->Released6031894489->Done6031899095 without skipping lifecycle. Prefer selected-item status queries and avoid repeatedly listing500items. [API field update source](https://docs.github.com/en/rest/projects/items?apiVersion=2026-03-10) documents field IDs/option values; source assertions and postread remain mandatory independent of transport. Revisit if actual declared metadata, source field mapping, pin policy or API changes; no untested platform/version/right/durability/performance certificate.
