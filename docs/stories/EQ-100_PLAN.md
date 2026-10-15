# EQ100 — final R9 composition and release qualification

Issue [200](https://github.com/atulsrivas1/equity-features/issues/200), epic [193](https://github.com/atulsrivas1/equity-features/issues/193), milestone10. Provisional5points represent complexity, not days. This pre-code packet specifies qualification, not an accepted release. Read live Project for status. Ready requires196–199 and EQ048 Closed/Done, complete separate pre-code review and owner-authorized bounded R9 execution. One active implementation at a time.

## Outcome and boundaries

An installed consumer composes accepted receipts/content fingerprints, data-only bundles/explicit fixed replay and bounded explanations with actual synthetic compute_trades. It reproduces declared results exactly, preserves unavailable quality and refuses tampering/unsupported versions before calculation. No package source/version or mathematical formula change is planned. No new provider, reconstruction service, ledger, R10 diagnostic, arbitrary registry, public hosting, registry/stable release or R7 automation change.

Accepted packages remain contracts0.0.4a4/features0.0.4a4/evidence0.1.0a2/explanations0.1.0a1 plus companion bundles0.1.0a1 at immutable IOmain18d86761aa3eebb7414e51e8fa2aba089717b5eb. Worker main6538f21b441c8527b465899b98cfd0476e7af08a unchanged. Canonical predecessor EQ099main1bc2eb89f0d6102f8c71e767349cbf631e584a5d. Existing source/package pins and finite parser/replay bounds remain mandatory.

## Exact supported demonstration

`examples/r9_reproduction.py` will use only installed public package APIs. Fixed caller-owned synthetic trades: prices100,102,101; sizes2,3,5; events110,130,160; known-at110,130,210; session100–200; C200/K210/E210; scale0USD; complete3-of3 coverage. Independent arithmetic: count3,volume10,notional200+306+505=1011,vwap101.1,mean10/3. Config has one explicit nonempty eligibility policy, exact accepted fixed-registry five output columns, no retained evidence rows and EvidenceDisclosure not_supplied0.

Sequence: actual compute_trades→make_content_receipt→explain_result/encode→write_bundle→read_bundle→explicit replay_bundle→explain decoded result. Compare full canonical result, original graph unchanged, receipt content verified, replay matched/one calculation, environment verification false; source_authenticated/execution_verified false. Receipt environment is caller-declared, not an installed/original environment attestation.

Reference-only bundle: replay unavailable/zero calls and explanation input_content_unverified. Caller explicitly supplies the matching batch: matched/one call and content_verified. Changed size with unchanged metadata: integrity_mismatch before calculator. No fetching, automatic reconstruction, imports/install instructions from a bundle or automatic replay on read. Cancel-before-start: cancelled_before_start/zero calls. Complete embedded bundle without installed features: incompatible/zero calls. Missing references remain unavailable even if no calculator is installed.

Causal boundary: thirdknown-at210 is admitted atK210;211 produces allfive nulls, missing_input/future_knowledge, expected3/observed3. Replay may match that unavailable result with one call; explanation includes result_unavailable while supplied content remains verified. This proves faithful reproduction of reported facts, not safe data, historical availability truth or a leakage detector. Missing actual batch separately produces five nulls/missing_input/absent_input/expectednull/observed0; exact zero-input replay can match that result in combined installations. Missing input, unavailable quality, reference absence and compatibility failure stay distinct.

## Independent pre-code expectations and refusals

[Hand expectations](EQ-100_EXPECTATIONS.json) freeze numeric seeds, state/count table, source semantics references and cost populations before implementation. SHA256 at preparation4c709ebb224342dcfd110a23e0c8a841218cd42e18b1d84f5445acb6cc609c35. Source references are exact committed Git bytes, not new runtime tests.

A test-only standard-library ZIP packer uses accepted stored ZIP geometry: sortedASCII names, no compression, timestamp1980-01-01, create_system3/create_version20/extract_version20, mode0o100600, empty extras/comments. Verify it reproduces the original accepted valid bundle before applying canonical manifest registry=os.system or versions.features=9; both must refuse unsupported_version before any explicit replay. Exact result payload byte flip preserves original headers/CRC and must refuse integrity_mismatch. No private package codec used to generate expected values or by the public example. Counter/patch instrumentation is test-only and never becomes supported caller code.

Tests cover the composition/state table, exact numeric/full-result parity, input declaration versus content consistency, raw integrity, version/registry, caller reference mismatch, cancellation, optional dependency isolation and quality boundary. Accepted independent EQ096/097/098/099 fixtures remain exact pinned evidence; repeated installed test cohorts are not additional unique tests. Unexpected errors propagate to qualification failure. No failed run is relabeled pass.

## Fresh source-closed qualification

New `tools/build_r9.py` and `R9 release qualification` workflow target Windows-latest and Ubuntu24.04/CPython3.12. Readonly immutable IO checkout; verify exact IO head before consuming files. Materialize committed Git bytes from each repo into new owned directories, include complete package trees/tests/fixtures/examples/build/helper/workflow/requirements in source maps. No untracked source or bundle-selected path/import/URL. Full source closure before and after qualification.

Reuse accepted `tools/build_explanations.py` helpers for archive/license/RECORD/installed maps by exact pinned trusted source; never call its old main. Explicitly extend the closed qualification package table with bundles. Report canonical/IO origins independently. Produce ten wheel/sdist archives twice, compare complete bytes/maps; inspect every entry, license, METADATA/exact dependencies, RECORD and sdist source. Use fresh `dist/r9`, preserve older qualifications.

Per OS: four fresh light/combined wheel/sdist forms. Light installs contracts/evidence/explanations/bundles without features; root imports stay calculator-free, fixed replay incompatible or unavailable according to state. Combined adds actual features. Map original packages before optional installation, prove unchanged payloads after installation and operations; full installed payload equality to built source/archive maps. Run relevant accepted independent evidence/bundle/explanation tests with exact optional skips and composition tests. Combined runs the actual public example. Strict typed public consumer and dependency checks required. All child environments remove inherited MYPYPATH/PYTHONPATH/PYTHONHOME/PYTHONUSERBASE; installed-I/site-packages identities, no source checkout fallback. No accepted R7/R8 workload reruns or EQ097 benchmark reruns for status.

## Measured overhead protocol

New qualification-only script outside pure packages; no performance threshold or speedup claim. Populations N10 and1000: event1..N,price100,size1,eligibletrue,known-at=event,session0..N+1,C=K=E=N+1,completeN-ofN. Independent expected outputs N,N,100N,100.0,1.0. Each population has three repeats of five operations (30raw samples/OS), executed once in combined wheel form:

1. actual calculate;
2. make_content_receipt plus encode_receipt;
3. explain_result plus encode_explanation;
4. write_bundle;
5. read_bundle plus explicit replay plus explanation/encode.

Preconstruct inputs and baseline graphs outside measurement as appropriate per operation. `gc.collect` before each sample, `tracemalloc.start` then `perf_counter_ns`, operation, stopclock/read traced peak/stop tracing; result/parity/count/size validation after timing. Record all raw durations/traced peaks/byte counts and runtime/platform/package/source identities. Output allocations included; inputs/preowned baseline excluded, timings include tracing overhead and Python interpreter allocation behavior. Replay's own returnedelapsed is distinct from whole phase time. Traced Python peak is not RSS/native/total physical memory, no physical quotas or interrupt deadline. Accepted five-second replay gate checks after return; qualification never claims synchronous call interruption. Any unmatched/refused/unexpected state fails the vector rather than relaxing comparison.

## Retention, compatibility, threat model and rights

Library APIs persist no files/cache or TTL: caller owns returned bytes/objects, access controls, permitted retention and cleanup. Experimental CI artifacts use30days; no permanent download, stable registry or signed provenance promise. Retain permitted inputs/configuration/results/archives before expiry if future reproduction is required; digests cannot reconstruct missing content. Qualification uses only new owned work directories and ordinary finally cleanup, not bounded physical cleanup proof. Borrowed repositories and accepted archive evidence remain untouched.

Existing exact package/schema/registry versions and numeric full-result comparison apply; no tolerance relaxation, transparent dependency update or environment repair. Reject unsupported versions. Archive bounded parsing is no sandbox for arbitrary code; only fixed installed replay runs. Content match/CRC/hash consistency do not authenticate origin, source rights, original execution, declared environment, historical availability, economic truth, profitability or regulatory compliance. Public examples contain only caller-created synthetic data; publication declarations remain assertions. No provider certification or actual provider acquisition is implied.

## Delivery and final acceptance

Publish this packet and independent expected fixtures before Ready; separate local reviewer verifies formulas/state/call counts/control/source closure/rights/retention/gates. Recheck actual dependencies, Ready/assignAtul/Inprogress before code. Complete source/security/docs review, actual author/current bothOS tenarchive/fourform qualification, raw overhead measurements and current finalhead CI/artifacts before Test and ReadyRelease.

Guard exact finalhead/parent/tree/closed review-file map/current checks/artifact identities before main publication. Independently verify actual defaultbranch/tree/public UTF8/Atul author+GitHub committer/noCoauthors and unchanged oldpackages/IOworker, current unexpired bothOS archives/maps/logs/fourforms and measurement vectors. Distinguish reviewer artifact audit from an independent reinstall. Then Released→acceptance/criteria→Done with real readbacks. Preserve original failures/rework; no receipt-only recursive commit loop.

R9 final aggregation is separately real: all196–200 Closed/ProjectDone, five story acceptance links, epic193 fullscope reviewed/tested→ReadyRelease→Released→Done/close, and exactmilestone10 membership/zeroopen/closed before fullR9 notification. Verify existing aggregate lifecycle and criteria before transitions; do not fabricate a retrospective CodeReview/Test. Final tracked R9_ACCEPTANCE, API/example/install/build/compatibility/security/rights/changelog/lessons/knowledge/handoff and issue/PR evidence accompany the same story. Only owned primary CURRENT_STATE paragraph may change; unrelated work and pausedR7automation preserved. No nextrelease work inferred.


Measurement order is population10 then1000, repeat0/1/2, five phases in listed order, no warmup/randomization. Retain each phase output until traced peak is sampled. Preowned: calculate(config,batch,entity); receipt adds baseline result; explain adds baseline receipt; write adds publication; read phase only baseline raw bundle and fixed feature focus. Return graphs retained at trace end: result; receipt+encodedbytes; explanation+encodedbytes; bundlebytes; decodedbundle+replayreport+explanation+encodedbytes respectively. Internal production validation/encoding/hash work stays measured; external correctness/size checks happen afterward. Record typed batch/result/receipt/explanation/bundle lengths, tracedbytes and durationns. Full expected ReplayReport fields and elapsed policy are literal in the fixture; direct production is a separate one call from each explicit replay_count1. Final membership target is epic193 plus196–200: after199acceptance2open4closed, after200acceptance1open5closed, afterepicclosure0open6closed, then milestone closure. Original initial pre-code expectations SHA4239655a retained outsideGit as superseded proposal history, not implementation evidence.
