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
