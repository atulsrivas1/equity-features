## Measured source qualification — October15,2026

Reviewed source `86154ef76010d474fbc46a195d85bd03ec616b15` passed author Windows/fourfreshforms and [actual Windows/Linux workflow](https://github.com/atulsrivas1/equity-features/actions/runs/38811720198) with all42sourcechecks. Current source artifacts and all eightCImeasurement records/32workloads/640rawdurations were independently audited. Every form retains full independent snapshot and original input/result/receipt/source/package parity. The measurements below are the **wheel/pure subset** of that immutable source run; [all eight records/rawsamples/exact statistics](stories/EQ-105_MEASUREMENTS.json) include sdist/full forms and observed machine/CPU-count/Python/timer metadata. Ratio is rounded here; JSON retains exact reduced rationals. Fixed ordering/sharedprocess/uncontrolled machine load limit interpretation; no native speed extrapolation or general speedup promise.

| OS / CPython | Workload | Baseline median ns | Wrapper median ns | Extra median ns | Wrapper/baseline |
|---|---|---:|---:|---:|---:|
| Linux / 3.12.15 | k1 | 54763/2 | 98519 | 142275/2 | ~3.598 |
| Linux / 3.12.15 | k16 | 307305/2 | 486206 | 665107/2 | ~3.164 |
| Linux / 3.12.15 | k32 | 576393/2 | 1793125/2 | 608366 | ~3.111 |
| Linux / 3.12.15 | m512 | 1599416 | 1724555 | 125139 | ~1.078 |
| Windows / 3.12.10 | k1 | 38350 | 132950 | 94600 | ~3.467 |
| Windows / 3.12.10 | k16 | 225750 | 678250 | 452500 | ~3.004 |
| Windows / 3.12.10 | k32 | 421900 | 1247900 | 826000 | ~2.958 |
| Windows / 3.12.10 | m512 | 3100950 | 3327100 | 226150 | ~1.073 |

Final documentation/currenthead/main artifacts and release acceptance remain pending at this checkpoint. Later executions retain their own sampled durations; they do not replace this source snapshot. Captured nativeRECORD audits are not independent physicalnative rehash/reinstall. The older source-only preparation sections below are historical and cannot override this measured scope.

## Implemented source candidate; installed qualification pending

EQ105 is actual In progress after exact pre-code review. The source consumer and seven pure/one native development tests pass; its new sibling builder/workflow have not run. No actual installed timing result is claimed. Commands after installation: `python -I examples/r10_point_in_time.py` and `python -I tools/measure_r10.py --out NEW_MEASUREMENT.json` from the reviewed Git checkout or the builder’s exact Git materialization, using packages installed from selected wheels/sdists; these outer scripts are repository files rather than files installed by a project package archive; the latter writes only a new caller-selected outer qualification record. Pure package code performs no I/O. Build/install/example source materialization remains the reviewed builder responsibility.

## EQ105 pre-code packet; exact-head Ready review pending

EQ104 is now [accepted](https://github.com/atulsrivas1/equity-features/issues/204#issuecomment-6202751786) at main `1e8f89fe27a7409a3030b22558cb84ab3ae86fde`. EQ105 remains Backlog/unassigned; the preparation statements below preserve their original historical scope. No EQ105 runtime/measurement/build implementation or results exist.

# R10 consumer guide — preparation for EQ105

R10 separates a declared point-in-time observation from the decision to admit it. Diagnostics inspect explicitly supplied facts. Conformance compares complete diagnostic observations against an independent assertion. Provenance verifies selected content relationships, and its separate operational readback invokes the accepted fixed store. None of these authenticates source history, actual consumption, rights or profitability.

## Install and select the boundary

The minimal pure consumer needs contracts0.0.4a4, evidence0.1.0a2, diagnostics0.1.0a1 and conformance0.1.0a1. It requires no calculator, NumPy, DuckDB, I/O or worker imports. Keep acquisition and publication outside these packages. The optional full example adds unchanged accepted features/provenance/I/O/workers and explicit DuckDB1.5.6/NumPy2.2.6 costs. A successful pure example is not evidence that the full native composition was installed or executed.

Request each intended check explicitly with its subject identity, choose advisory or strict and allow or deny unknown, then inspect findings, unknown prerequisites and not_requested. A check not requested is not passed. Strict deny rejects failed and unknown findings; strict allow can admit an unknown while retaining its unknown status. Advisory returns not_applied rather than pretending admission occurred.

## Minimum supplied evidence

| Check | Required comparison operands | Important missing/false-positive limits |
|---|---|---|
| market_time | Matching declared session; selected ordinary/closing/completed convention; observation; completed interval start when relevant | Missing session, observation and required start are separate categories. A directly visible boundary failure remains failed when another category is missing. Ordinary event excludes C; supported closing auction and completed interval have their explicit accepted equality rules. |
| knowledge_time | The cited fact's known_at and requested K | Missing known_at is unknown. A cited raw row known after K fails this comparison; this does not prove the calculator consumed it. |
| declared_context | Requested and observed C/K/E and availability mode | Missing observation is unknown. Matching declared context is not proof of actual execution time; reconstruction cannot silently substitute known_at mode. |
| membership | Matching homogeneous reference identity/population; explicit complete flag; all row indices covering declared observed population; historical proof; effective intervals, active scope/text and known_at | Current-only, incomplete or projected-away facts cannot establish historical membership or absence. Explicit complete historical population with no active row gives absence failure. Visible late/ambiguous membership remains failure when other proof is missing. |
| revision | Both expected/observed snapshot and revision identities, start/query/known_at; explicit unbounded end when start exists | Missing identities count separately even with a shared reason. No implicit latest-revision substitution or inferred timestamp. |
| adjustment | Both complete action policies and both units | Missing policy/unit operands are separate categories. Exact scale/policy inequality detects declaration mismatch; it does not prove no economic conversion exists. |
| freshness | Explicit age basis, target, tolerance and observation | No wall-clock substitution. Missing observation unknown; future observation failed; age equal to tolerance passed. Different age bases are not interchangeable. |

The complete accepted rules and missing-category arithmetic are in [the diagnostic API](api/POINT_IN_TIME_DIAGNOSTICS.md) and [EQ101's independent table](stories/EQ-101_TRUTH_TABLE.json). Content fingerprints remain supplied citations until a separate supported content-verification operation checks the bytes. Even verified bytes do not establish truthful acquisition history.

## Coverage and interpreting a match

[EQ104's oracle](stories/EQ-104_CONFORMANCE_ORACLE.json) declares24diagnostic and6content cases, including exact temporal boundaries, reconstruction, historical/current-only/partial membership, revision/adjustment mismatch, stale/future freshness and visible failure with missing proof. A matched unknown is a successful assertion about missing evidence, not proof that the subject is safe. Summary all_matched means every asserted comparison matched; it is not an aggregate safety score or execution receipt. Locally constructed outcomes remain ordinary data.

Actual history composition compares original input/context/config/result snapshots. Mutating an unused future slot can change input content while preserving result content in the selected finite scenario. A selected-row change can change the result. This does not prove universal causal independence. Full content differences can reflect metadata, quality or evidence as well as numeric values. History declares a history_context binding without supplying a canonical context batch; R10 invents no history receipt materialization or expanded R9 replay registry. Fixed trade replay remains the accepted supported profile.

The full native composition separately verifies actual original trade result and receipt, acquisition/source maps and generation waiting/reopen/complete behavior. Operational completion can coexist with denied late-knowledge diagnostics or unavailable result quality. A supplied completion claim cannot make a store generation complete.

## Reproducible measurement and limits

EQ105's planned measurement compares accepted diagnostic evaluation with the conformance wrapper at1/16/32knowledge checks and4membership checks×128facts. The membership population is complete and historical but all facts are inactive at the query, so the independently expected finding is membership_absent. The workload exercises the wrapper's512fact bound without manufacturing active overlap or hiding missing proof.

Per installed form, one process runs3warmup and10measured baseline-then-wrapper pairs in fixed workload order. Fixture construction, parity assertions, serialization, build and installation are outside the timed callable intervals; wrapper validation, copying, evaluation and expectation comparison are inside its interval. All raw durations and exact rational min/median/max/difference/ratio are retained. A zero baseline gives no ratio; a negative observed difference is permitted and is not promoted to a speedup promise. Fixed ordering, shared process, timer resolution and uncontrolled machine load limit interpretation.

These are finite application-work measurements, not native calculation benchmarks, throughput promises, physical resource caps or hard interruption deadlines. BothOS records must be measured and audited before publishing quantitative results. No quantitative result exists in this preparation draft.

## Compatibility, migration and evidence

Existing calculations, C/K/E mathematics, schemas, versions, codecs and provider scope remain unchanged. Existing callers can continue without importing optional diagnostics/conformance/provenance. Adopting diagnostics requires explicit supplied evidence and policy; adopting conformance also requires a complete independent expected snapshot. Do not generate expectations by copying the output under test.

Final installed example commands, measured records, exact source/current artifacts, independent reviews and release acceptance will be linked only after execution. Captured native RECORD maps are not independent physical native rehash or reinstall. Experimental capability does not certify regulatory compliance or trading suitability. Public fixtures are synthetic; no private/provider entitlement or new reference acquisition is implied.
