## EQ112 changing-ratios coverage correction

Actual public review at60345f0 found that the original changing-ratios criterion lacked admitted same-pair nonoverlapping conversion changes. The first97 literal records remain unchanged; two appended full-input/full-result examples now make99. Freeze101/98/102 against100 with1:1 before102 and2:1 from102 gives deviations1,-51,-49, max51 and observation mean101/3; topK c2,c3 binds conversion-2, and conversion proofs include both facts. At reopenR200, continuous199 still uses the old1:1 factor despite a2:1 factor effective atR; gap-5/premium-1/25 remains, only the old mapping is consumed, and the full input digest binds both facts. These are independent literal/data-tool expectations, not executed kernels. Earlier prepared/public approval missed this absence and is preserved with its exact97-record scope. EQ112 returned Code review to In progress before correction; renewed final working/public/current CI/main gates remain.

## EQ112 mathematical specification in progress

[Story214](https://github.com/atulsrivas1/equity-features/issues/214), [proposed mathematics](stories/EQ112_MATHEMATICS.md), [independent fixtures](stories/EQ112_FIXTURES.json). EQ111 accepted at main6e0bd77c70fe20ab9f35368432a84b38a2e946ac, [acceptance](https://github.com/atulsrivas1/equity-features/issues/213#issuecomment-6221005594). EQ112 public precode72262192e9fd677bc0ca4265a4342afaf9320c0f/[PR417](https://github.com/atulsrivas1/equity-features/pull/417) was independently reviewed before actual Ready/In progress and assignment5points/Atul. Its97literal operation records,6Rational boundaries and arithmetic/codec controls are mathematical design evidence, not executed product kernels. Exact profile is supplied raw positive last trades/same currency/declared conversion, complete causal scopes/known-at/feed proofs and reduced rational witnesses. New optional namespace remains unimplemented; old core39IDs/ConfigSpec1/math/versions unchanged. [API specification](api/CONTINUOUS_RESEARCH.md) and [formula guide](features/CROSS_VENUE_FORMULAS.md) accompany this story. Final working/public/current CI/main verification and original criteria remain; EQ113-115 Backlog, E16/milestone13 open. Earlier dated checkpoints retain their scopes.

## EQ111 executed finite-session reuse - October16,2026

[Capability assessment](stories/EQ-111_CAPABILITY.md) demonstrates supplied week/day/overnight/23-25hour bounds, gaps, existing trade outputs and unchanged legacy configuration with16 source methods passed by author and independent reviewer. Named intervals do not automatically enforce feed state; count windows do not become duration windows. Reuse SessionSpec; no new session type/schema/core math/version. EQ112/113 still own missing feed/temporal/cross-venue semantics; EQ114/115 remain later dependent work. [Validation](stories/EQ-111_VALIDATION.json) records same-environment separate processes and pending delivery gates. Earlier checkpoints retain their dates/scopes.

## Owner selection of R12 — October16,2026

The owner requests a fresh R11 review, R12 handoff and work on original EQ111–115 in this chat. [GOV024#414](https://github.com/atulsrivas1/equity-features/issues/414) prepares the [release](R12_RELEASE_PLAN.md), [tests](R12_TEST_STRATEGY.md), [handoff](R12_AUTONOMOUS_HANDOFF.md) and [first plan](stories/EQ-111_PLAN.md). R11 is [accepted](https://github.com/atulsrivas1/equity-features/issues/195#issuecomment-6214256540); the [fresh independent R11 review](reviews/R11_POST_DELIVERY_REVIEW.md) found no new actionable issue:118 exact-source pure methods passed, without SQLite/native/build/install/qualification rerun. Original R12 five stories/31points/dependencies remain, plus3governance points. No runtime story is Ready from this preparation. The owner explicitly authorized separate local review throughout R12/PR415/EQ111–115/necessary companion changes/final delivery. Completed exact independent review and all actual gates remain required; permission is not review completion. No new session, automation, provider/private/paid/trading/hosted/admin/registry or R13 selection. Earlier dated status below is preserved history.

# Continuous-market extensions — revised pre-code direction

Owner-authorized future planning: E16 / R12 / EQ-111–115. Earlier suggested EQ-098–100 and E14 are superseded and must not be reassigned. All stories are Backlog. No calculations or adapter implementations are started by this plan; R2 continues unchanged.

## Capability and contract decision first

Existing SessionSpec supports arbitrary supplied finite intervals and disabled auctions. Demonstrate day/week partitions on continuous venues before adding types. An always-open venue still uses finite caller-selected computation partitions; no unbounded epoch session/state claim. Duration windows, supplied feed-state facts and cross-venue relationships are distinct potential gaps.

ConfigSpec currently requires exact SessionSpec/WindowSpec instances. New companions or unions need explicit versioned admission/serialization/migration; preserve accepted existing config digests and equations. No promise to insert new types into schema1 unchanged. Missing governed slots remain missing, not compressed. Decide fixed UTC durations versus local civil days/DST using supplied boundaries; callers own calendar discovery and schedule facts.

## Mathematical decisions before kernels

Define venue/instrument/underlying identity, token-to-share ratio, price type (mid/last/official close), currency, scale, adjustment basis and conversion known-at evidence. Same ticker or currency does not prove economic equivalence. Conversion/rebase and revision snapshots bind configuration and evidence.

Basis is normalized continuous price minus the specified reference; premium divides by an explicitly eligible nonzero reference with declared exact witness/floating policy. Causal alignment must use only admitted data at the target cutoff: a nearest future point inside tolerance is still inadmissible. Specify backward matching, ties, ordering, per-leg age and maximum mismatch independently; no hidden interpolation.

Freeze deviation compares eligible continuous observations against an explicitly admitted frozen reference. Specify max/mean absolute deviation; means may be fractional, so choose rational witness or declared scaling/rounding rather than claiming all exact results fit int64. Freeze interval boundaries, count versus duration weighting, coverage/empty population, overflow and top-K tie order require hand-derived fixtures.

Reopen-gap is a distinct outcome only available after both selected legs are observed and known. Define pre-reopen selection, first eligible reference after reopening, delivery delay and target cutoff. Before availability return explicit missing/insufficient status; never expose a future label as a causal signal.

Feed facts identify feed/product and original known-at/effective intervals. Separate planned closure/freeze, unexpected outage, stale delivery and unknown state; conflicting intervals fail. Schedules are provider/product-specific, with holidays/DST provided externally, not universal Friday/Sunday constants. Thin-liquidity assertions require actual supplied liquidity evidence; ordinary delivery coverage cannot establish liquidity quality.

## Planned stories

### [EQ-111](https://github.com/atulsrivas1/equity-features/issues/213) — Assess continuous-market contract gaps and freeze scope

5 provisional points. Dependencies: EQ-012/013/014, EQ-033, EQ-039/044/048.

Design/end state: Demonstrate which supplied finite SessionSpec intervals already support 24/7 data; separate duration-window, feed-state and cross-venue requirements. Record reuse/no-change versus genuine missing capability. No new session type without evidence.

Tests: Existing-session synthetic 24/7 week/day partitions, boundary/overnight/gap cases, typed ConfigSpec compatibility probes.

Questions: Session identity granularity, finite partitioning and what is genuinely unsupported.

Documentation: contracts/formulas/API/registry and synthetic installed examples with versioned acceptance/continuity.

### [EQ-112](https://github.com/atulsrivas1/equity-features/issues/214) — Specify cross-venue mathematics and causal availability

5 provisional points. Dependencies: EQ-111, EQ-006, EQ-033.

Design/end state: Freeze basis/premium, freeze deviation and reopen-gap formulas, weighting, units, underlying/token-share conversion, adjustments, exact versus floating representations and overflow. Alignment uses only admitted observations at cutoff; reopen metrics are unavailable until both legs are known.

Tests: Hand-derived scaled/rational cases; future nearest-neighbor rejection, missing legs, mismatched currency/underlying, changing ratios, observation/time weighting and partial coverage.

Questions: Reference mid/last/official close, conversion availability, denominator rules, gap endpoints and time weighting.

Documentation: contracts/formulas/API/registry and synthetic installed examples with versioned acceptance/continuity.

### [EQ-113](https://github.com/atulsrivas1/equity-features/issues/215) — Implement conditional continuous windows and supplied feed-state contracts

8 provisional points. Dependencies: EQ-111/112, EQ-048; approved contract evolution only.

Design/end state: Prefer SessionSpec reuse. Add only demonstrated missing duration-slot/feed-state contracts with explicit schema compatibility and config digest rules. Preserve old digests. Distinguish scheduled freeze, unscheduled outage, stale delivery and unknown state; calendars/holidays/DST supplied externally. A justified no-change decision satisfies unnecessary session-type scope.

Tests: Old schema round-trip/digest compatibility, fixed UTC versus civil-day slots, missing governed slots, overlap/unknown/later knowledge and interruption boundaries.

Questions: Companion schema versus versioned union, DST semantics, feed/product identity and schema migration.

Documentation: contracts/formulas/API/registry and synthetic installed examples with versioned acceptance/continuity.

### [EQ-114](https://github.com/atulsrivas1/equity-features/issues/216) — Implement admitted cross-venue research feature kernels

8 provisional points. Dependencies: EQ-112/113, EQ-017, EQ-020, EQ-036.

Design/end state: Pure batch kernels use supplied normalized legs, mapping/conversion and feed facts; explicit per-leg readiness and output quality. Exact difference/rational witnesses or declared float tolerance; bounded top-K deviation evidence. No interpolation, FX lookup, forward reopening data or existing-feature overrides.

Tests: Independent reference values, causal alignment, first-known reopen, nonintegral means, overflow, stale/frozen distinction, stable ties and bounded evidence.

Questions: New namespaced feature IDs and the exact structured witness/output representation, frozen before code.

Documentation: contracts/formulas/API/registry and synthetic installed examples with versioned acceptance/continuity.

### [EQ-115](https://github.com/atulsrivas1/equity-features/issues/217) — Qualify continuous-market research extensions and guides

5 provisional points. Dependencies: EQ-111–114, EQ-045/048; real sources require relevant R4/R6 adapter acceptance.

Design/end state: Installed synthetic examples cover 24/7 versus supplied reference hours and feed failures. Verify old-feature parity, schema migration, timing/evidence and bounded resources; report no-change decisions and unsupported modes. No launch-status, liquidity, token equivalence, provider rights or price-discovery claims.

Tests: Clean wheel/sdist installations, compatibility/regression suite, independent synthetic weekend/gap replay and coverage evidence.

Questions: Actual feature delivery scope after capability analysis, adapter prerequisites and distribution placement.

Documentation: contracts/formulas/API/registry and synthetic installed examples with versioned acceptance/continuity.

## Limits

Pure supplied calculation work only; pool reconstruction, provider API/RPC, trading, settlement/bridging and private deployment remain outside scope. Current market announcements are motivation only, not contract facts. No asserted competitor exclusivity, regulatory certification, profitable basis trading or operational venue launch. Sources/versions for any future market-context paragraph must be verified at publication.
