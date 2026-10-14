# EQ091 forward-label implementation readiness proposal

Local preparation only, October14,2026. [EQ091 #103](https://github.com/atulsrivas1/equity-features/issues/103), E12#100, R8 milestone9; provisional eight complexity points. Blocked on accepted EQ089 exact label contracts and verified Atul Project access. No implementation, benchmark, runtime tests, Ready or acceptance.

## Concrete proposed deliverable

Implement optional pure equity-feature-labels under packages/labels, proposed 0.1.0a1/Python3.12, depending only on accepted core contracts. Public entry point evaluate_label(request:LabelRequest)->LabelResult and typed constructors/encode/digest helpers follow [EQ089 schemas](EQ-089_SCHEMA_PROPOSAL.md) and [formula draft](EQ-089_CONTRACT_DRAFT.md). It does not import strategies or mutate core signal/result namespaces. All prices, revisions, adjustment evidence, cutoffs and origin identities are supplied immutable facts.

Support only exact elapsed-UTC horizon simple price-return labels, with checked int64 endpoint, exact t0/t1 observations, finite positive Float64 prices, raw or caller-supplied split basis and documented no-dividend/no-interpolation definition. Explicitly preserve original signal anchor/request/result identities while binding any later adjusted label path and basis facts to their own admitted maturity and revision identity. Caller basis/origin bindings are trusted assertions, not proof of provider rights, authentic signals or correct corporate-action normalization.

## First actions after accepted contracts

1. Read actual EQ089 accepted schemas/fixtures/review and current clean default branch, verify source pins and Project dependency/assignment. Publish the exact packet, API/export/build/version choices and independent fixture pins to #103 before Ready/pull.
2. Materialize the independent label fixtures and precedence tables with actual proposed typed constructors, without calling the production evaluator to derive expected returns/states.
3. Implement structural/origin admission, pending/incomplete/mature state precedence and numeric calculation only for admitted endpoints/basis. Keep nonmature value/label-known-at null and do not emit endpoint prices or ratio in the label output.
4. Implement complete immutable path/config/origin/request/result identity and typed numerical/precision errors. Different revisions create new outputs, never silent historical replacement.

## Meaningful verification

Hand-derived positive/negative/zero returns, exact horizon and knowledge boundaries, missing one/both endpoints, unknown/future basis knowledge, basis not yet effective and crossed-condition precedence. Validate that future origin anchors/basis are rejected, while later label-only adjusted anchors cannot mutate the original signal facts. Support raw split discontinuity and separately supplied adjusted price comparability with distinct identities. Price-only dividend example remains -1/100, without invented cash addition.

Reject zero/negative/nonfinite prices, duplicate timestamps, bool/nonpositive/overflow horizons, unsupported total-return basis, inconsistent origin/path/source/basis identity and stale/mismatched schemas. Finite-input ratio overflow and underflow-to-zero have explicit errors; equal maximum finite prices return zero and supported nonzero subnormal ratios follow documented rounding. Independent rational finite-output fixtures use the declared tolerance; exact identities and states have no numerical tolerance.

Pending outputs expose no future numeric return; same admitted immutable request repeats exactly. Revisions change identities, complete path hashes include unused interior rows, and changing future labels never changes a fixed strategy request/result. As-of consumer joins require mature status, exact selected origin/revision, endpoint<=join C and label_known_at<=join K under causal join C/K/E. An unfiltered retrospective target join is not a causal backtest demonstration.

## Documentation and release

Public formula/API/errors/maturity/basis/revision/identity documentation, synthetic examples, fixture goldens, issue/PR acceptance, changelog, scoped lesson and handoff are part of this story. Source-independent boundaries and no fetching/scheduling/trading/publication are explicit. Separate authorized reviewer covers the exact final implementation and affected contracts/findings.

Test/release requires meaningful numerical/causal/type/boundary/docs checks, optional import independence, actual fresh Windows/Linux wheel/sdist qualification with source-tree fallback denied, and current source/archive/RECORD/sdist identities. Declared GitHub artifact delivery plus independent actual-main/current checks/public UTF8/Atul attribution readback precede Released then Done/closure. EQ092 aggregate cross-package example/version/distribution acceptance remains separate. No native/installed or label runtime execution was performed by this packet.
