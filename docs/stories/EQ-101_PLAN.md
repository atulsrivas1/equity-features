# EQ101 preparation — diagnostic findings and admissibility

[Issue201](https://github.com/atulsrivas1/equity-features/issues/201), [epic194](https://github.com/atulsrivas1/equity-features/issues/194), R10. Provisional5points estimate complexity, not days. This preparation accompanies GOV022; it is not the complete reviewed pre-code freeze or implemented API. Runtime remains Backlog until the handoff/review route and the remaining concrete schema/oracle decisions below are resolved.

## Dependencies and smallest accepted outcome

EQ096 #196, EQ033 #38 and EQ037 #42 were freshly read Closed/ProjectDone; R9 final acceptance is linked in the R10 handoff. Read accepted timing/action/reference contracts and source before choosing records. EQ101 owns a versioned diagnostic specification and independent expected boundary fixtures with validation, package ownership and consumer examples of the declared schema. EQ102 owns actual membership/revision evaluation. Do not deliver a placeholder runtime evaluator or claim an unimplemented diagnostic check is running.

Recommended optional pure allocation is `equity-feature-diagnostics` / `equity_feature_diagnostics` under canonical `packages/diagnostics`, initial experimental0.1.0a1; exact inward dependencies on contracts0.0.4a4/evidence0.1.0a2, no feature/adapter/worker import on the root. These are proposals to freeze in the final EQ101 packet. No change to core math, schemas or existing digest meanings.

## Proposed contract decisions

Each requested check has immutable policy/check/version/subject identities, explicit supplied evidence references, a passed/failed/unknown result, reason and coverage. Nonrequested checks are separately identifiable and cannot count as passed. Syntax/identity/version contradictions are typed validation errors. Advisory immutable reporting is the default; strict admission, if selected, separately declines according to named failure/unknown policies without rewriting the finding's evidence state. No aggregate safety score.

Separate checks: ordinary/exceptional market-bound admission; consumed known-at availability; requested-versus-declared C/K/E policy; reconstruction versus causal declaration; historical membership/classification coverage; revision identity/availability; adjustment compatibility; explicit freshness age. The full freeze must define which are schema declarations in EQ101 and which evaluators are implemented in EQ102, without expanding existing acceptance.

Source identity, execution environment and timestamps are supplied facts. Real execution time never substitutes for simulated decision E. K is a bound; a later declared K is a policy mismatch, not proof that each consumed fact was late. Current-only membership and absent acquisition proof cannot be repaired by hashes or a self-consistent receipt. Zero assessed population remains not evaluated, not zero leakage.

## Independent seeds to freeze before runtime

| Seed | Supplied facts | Expected policy distinction |
| --- | --- | --- |
| ordinary-before | Session0..200, C100, event99 | Market-bound pass |
| ordinary-at | Same, event100 | Market-bound fail; ordinary upper bound is exclusive |
| closing-exception | Session0..200, C200, closing-auction event200 | Pass only under existing explicit closing-auction inclusion |
| known-equality | K100, consumed known_at100 | Knowledge pass |
| known-later | K100, consumed known_at101 | Observed later-knowledge failure |
| known-missing | K100, consumed known_at null | Unknown knowledge; no invented time |
| bound-mismatch | Requested K100, declared K110, E120, all supplied known_at90 | Policy mismatch; do not assert each row was future knowledge |
| membership-end | Effective[20,100), query100 | Outside effective interval, distinct from absent proof |
| current-only | Current snapshot supplied for historical query without history | Historical evidence unknown, not certified empty or safe |
| revision-later | Effective20, exact selected revision known_at101, K100 | Knowledge failure despite old effective time |
| freshness-edge | Target100, observation90, tolerance10 under selected age basis | Age10 admitted; observation89 exceeds tolerance |
| no-assessment | No assessable required facts | Unknown/not evaluated; denominator0 and ratio null |

These seeds are independent design expectations, not executed test results. Final fixtures must name exact supported types, contexts, policy modes, counts/reasons and byte/hash representations if encoded, including closing-event discriminator and completeness evidence. Validate the fixture constructors independently against existing contracts; preserve failed fixture attempts honestly. Add reconstruction, unknown/contradictory policy, duplicate/mismatched references and int64 extremes before Ready.

## Remaining Ready decisions and delivery

Freeze concrete records/check IDs, schema/canonicalization and compatibility; status/reason/severity/admission table; subject/evidence coverage and trust assumptions; literal counts/byte/depth/node limits with preflight order; exact fixture/oracle source and minimal public consumer; documentation and applicable validation. No arbitrary code/path/URL resolver, fetching, clock, scheduling or publication in pure code.

Publish that completed packet and independent review before actual Ready/assignment/In progress. EQ101 specification delivery uses relevant schema/math/reference/documentation checks; a later installable implementation requires its own current Windows/Linux forms and exact source/artifact maps. Final-head separate review and actual main/readback/acceptance precede Done. Update public API/decision/example/compatibility/rights/lesson/handoff and issue/PR in the same story. Review request or green docs alone is not accepted runtime. Continue EQ102 only after EQ101 acceptance and its own concrete reviewed readiness packet.
