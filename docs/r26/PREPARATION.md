# R26 release preparation and admission decision

Owner selected planning and implementation of the next option release on October 21, 2026. R26 is **Option flow, activity and execution**, existing [E34#533](https://github.com/atulsrivas1/equity-features/issues/533), [milestone30](https://github.com/atulsrivas1/equity-features/milestone/30). R25 is published/Done. Source-only preparation is active under [GOV038#592](https://github.com/atulsrivas1/equity-features/issues/592). This preparation does not admit a dependency-blocked implementation story or modify another release's ownership.

## Existing scope and repositories

| Story | Scope | Home |
| --- | --- | --- |
| [EQ188#534](https://github.com/atulsrivas1/equity-features/issues/534) | Execution/tape contracts, clocks, signs, corrections, populations and conformance | option-features |
| [EQ189#535](https://github.com/atulsrivas1/equity-features/issues/535) | Exact contracts/premium rollups, signs and concentration | option-features |
| [EQ190#536](https://github.com/atulsrivas1/equity-features/issues/536) | Admitted equity-option participation and descriptive lead/lag | option-features, consuming compatible equity producers |
| [EQ215#574](https://github.com/atulsrivas1/equity-features/issues/574) | Prior-only activity baselines, median/MAD, clusters, DTE/OTM participation | option-features |
| [EQ191#537](https://github.com/atulsrivas1/equity-features/issues/537) | Ordered input/revisions and typed flow sink | option-feature-io |
| [EQ192#538](https://github.com/atulsrivas1/equity-features/issues/538) | Bounded ordered flow execution/replay/publication | option-feature-workers |
| [EQ193#539](https://github.com/atulsrivas1/equity-features/issues/539) | Both-platform artifacts, independent integration, resource evidence and browser demo | cross-repository acceptance |

No new repository is required. Add separately versioned optional domain packages only where dependency isolation warrants them; freeze exact distribution/import names and compatibility before implementation. Preserve all R25 APIs, released artifacts and source markers. Existing EQ188-193/EQ215 acceptance and full matrix coverage obligations remain unchanged. The seven delivery stories are currently Backlog/unassigned.

## Actual dependency audit

Live Project inspection on October21: EQ141/R17 and R25 are Done; EQ144, EQ145, EQ146, EQ153, EQ158 and EQ159 remain Backlog. The historical owner amendment removed the blanket R18/EQ146 gate only for R25. The separate approved R26 amendment below now defines R26 native admission; it does not accept missing equity producers.

EQ188 names EQ158/EQ159; EQ190 names EQ153/EQ158; EQ192 names EQ144/EQ145. Generic signed equity windows, correlation and quote dynamics remain equity-owned. Option contracts/asset conventions may be specified independently; claiming accepted equity reuse before actual compatible producers exist would be false. No equity math is duplicated or moved to evade an unimplemented producer.

The R25 trade record lacks execution price, signing/order/correction contracts. Its canonical snapshot sort, numeric-only result, BSM request, strict sink and independent-snapshot worker replay do not establish flow compatibility. R26 requires reviewed additive flow contracts, exact decimal accumulation and new typed storage/ordered execution admission, with old interfaces retained.

## Owner-approved bounded admission amendment — October 21, 2026

The owner selected extending independent admission to R26 option-native tracks while retaining equity integration gates. Permit EQ188 option-only contract authoring independently of its EQ158/EQ159 delivery prerequisites and, after separately reviewed frozen mathematics/interfaces/fixtures, option-native R26 implementation using accepted R25 foundations and its own compatibility/resource protocol. Replace only the blanket R18/EQ146 delivery prerequisite and EQ192 EQ144/EQ145 implementation-admission references with explicit R26-owned bounded execution and acceptance obligations. Do not claim an unimplemented R18 capability. Resource availability remains a separate actual gate.

Preserve EQ153/EQ158/EQ159 as real compatibility/integration gates for the outputs that consume their mathematics. Reviewed source interfaces may allow parallel consumer authoring; actual runtime integration and full EQ193/R26 release acceptance still wait for the required compatible producers. This proposal neither declares full R26 independent nor silently defers/drops EQ190 or changes later-release gates. Existing EF1/R18/equity ownership stays intact.

The alternative of retaining every existing gate was not selected. No active equity/R18 work is transferred to this chat.

The admission path is now approved. Numerical authoring still requires independently reviewed frozen exact contracts/fixtures and an explicit story/layer handoff. Actual runtime resource availability and artifact qualification remain separate gates; no previous R25 grant is silently reused.

## Delivery and acceptance

After gate resolution, finish exact source-to-output binding, original formulas/units/clocks/coverage/errors, independent tiny-tape fixtures, exact package/version and flow schema/sink/state contracts; obtain fresh independent review before freezing. Then admit dependency-satisfied stories through the actual lifecycle and launch three fresh release layer workers. Contract defects return to the coordinator.

Local build/test evidence plus fresh independent PR review governs merge; historical mandatory hosted-CI wording is superseded. Before release, qualify actual Windows/Linux original wheel/sdist cohorts, isolated dependency closures, complete direct/worker/stored value/status/quality/identity parity, ordered replay/correction/cancellation/conflicts and resources for declared modes, followed by an actual stored-output browser demo. Measure only performance claims actually made. API/SaaS is optional. Public release/package publication retains the owner boundary.

Read the [original mathematics and fixture proposal](MATHEMATICS_AND_FIXTURE_PLAN.md) and [additive boundaries/qualification proposal](BOUNDARY_AND_QUALIFICATION_PLAN.md). Both remain proposals pending exact contract/fixture review and applicable admission.
