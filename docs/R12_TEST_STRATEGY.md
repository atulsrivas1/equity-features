# R12 test strategy

This is a planned verification matrix for [EQ111–115](R12_RELEASE_PLAN.md), not executed evidence. Each story freezes literal cases/source identities and independent expected values before implementation. Preserve accepted math, schemas/digests, optional dependencies and source independence; use exact public types and meaningful negative controls rather than implementation-mirroring tests.

## EQ111 capability evidence

Use the accepted public SessionSpec/WindowSpec/ConfigSpec/AvailabilitySpec APIs on a supplied synthetic seven-day interval and seven contiguous finite day partitions. Check half-open start/end equality, an overnight interval, cutoff equality, disabled auction policy, an explicit gap, incomplete history, UTC durations and separately supplied23/25-hour civil-day examples. A timezone label is not a calendar lookup. Verify per-partition identity/config JSON/digest round trips and an independently frozen preexisting config byte/digest oracle. Test exact-type rejection of an unsupported companion without claiming that rejection proves every possible construction impossible. Separate demonstrated reuse, unsupported direct contract and questions requiring EQ112/113.

## EQ112 mathematical oracle

Hand-derive scaled integer and fractional basis/premium and freeze-deviation cases; show every unit/normalization/ratio/denominator and expected witness, including nonintegral means and zero/negative/ineligible references. Freeze observation-count versus duration weighting, interval endpoints and partial/empty coverage separately. Compare with a separate Fraction/decimal reference where appropriate, never the production formula as the expected result.

Temporal cases include future-nearest rejected despite tolerance, late known-at data, missing/unknown availability, per-leg age/mismatch limits, ties/revisions/ordering, mismatched currency/underlying/scale, conversion changes with their own knowledge times, closed/frozen versus outage/stale/unknown feed facts and conflicting intervals. Reopen cases must remain unavailable before first eligible reference AND selected continuous leg are known; distinguish a hindsight outcome from an as-of signal. Freeze all result/error/quality and overflow behavior before code.

## EQ113 contracts and compatibility

Round-trip exact old schema/config JSON/digests and old builtin/state fixtures unchanged. Exercise only admitted new companion/versioned contracts; reject accidental subclass/union/schema1 coercion. Tests cover feed/product identity, original effective/known-at facts, overlapping/conflicting intervals, endpoints, incomplete slots, future revisions and DST supplied boundaries. A no-new-session-type decision must have executed public reuse evidence and preserve the actual missing feed-state requirements. No filesystem/network/calendar lookup inside calculation contracts.

## EQ114 kernels

Independent expected complete outputs, original input/config/unit/availability/adjustment identity, null-quality-error distinctions, backward alignment and every selected leg's causal admission. Verify stable top-K ties and bounded evidence with explicit K/count/byte policies; guard int64/intermediate overflow and fractional representation. No interpolation/FX acquisition, future reopen leakage, builtin overrides or hidden dependencies. Test empty/missing/unsupported separately from valid zero. Unsupported update/merge/restore is explicit rather than a batch-parity promise. Performance claims, if made, require measured selected workloads, conversion costs and exact result parity; a speedup is not a release prerequisite.

## EQ115 installed composition and final delivery

Freeze the actually selected packages, exact supported runtimes/Windows/Linux pins and clean declaration/integration forms as applicable. Review the complete source/builder/workflow before execution. Fresh wheel/SDist installs must use public imports and verify owning RECORD/static payload/generated outputs/versions/origins, optional-import boundaries, complete license/dependency/source maps, repeat wheel/selected-SDist materialization and old-feature/full new-result parity. Report actual method/cohort counts with overlapping axes and shared-environment limits; captured maps are not an independent reinstall or full host/stdlib/ABI closure.

Installed synthetic examples cover continuous versus reference hours, weekend/gap/feed failures, supplied conversion/adjustment, late knowledge, unavailable reopen and admitted positive outputs. Reuse existing core/I/O/worker/service interfaces only where supported and qualified. Real-source examples need separately accepted adapters/rights; they are not required for this synthetic release. No provider connection is implied by an adapter capability record.

Require actual final-head and main CI, independent exact public source/attribution, current two-OS raw ZIP provider size/digest/expiry/every member and final criterion/lifecycle readback. Distinguish source tests from fresh installs and reference/fake fixtures from actual composition. If a qualification fixture changes, audit its current execution separately when it is outside the main bundle's input map, as the R11 retained-entry correction demonstrated. Observe owned forced exit before closing an independent input; retain genuine deadline errors and unknown cleanup instead of raising limits or relabeling failures.
