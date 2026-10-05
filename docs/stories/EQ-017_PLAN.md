# EQ-017 — bar session metrics plan

Prepared 2026-10-05 before implementation; issue #21, epic #20, R1.
Confirmed estimate: 8 Fibonacci points. One active story. Author self-review and
CI apply; deferred PR120 remains untouched. No independent reviewer is claimed.

## Prerequisites and first action

Live main is 0f5165a42550f4886304a4165c9990d08b4afb86. BUG-001 #144 and
BUG-002 #145 are closed/Done after PR146 and PR148 acceptance; reuse those fixes.
EQ-017 is Ready. R0 acceptance records post1 wheel/sdist receipts, both OS checks
and four fresh installations. Verify the pinned baseline before implementing.
The execution uses an isolated worktree of the existing repository, preserving
the occupied repair checkout and every unrelated branch.

## Frozen interface and admission decisions

`equity_features.session.bars.compute_bars(batch: CanonicalBatch | None,
config: ConfigSpec, *, entity: EntityKey,
prior_close: CanonicalBatch | None = None) -> FeatureResult` computes the twelve
session.bar/session.price IDs in SESSION_FORMULAS.md. It handles one supplied
entity; mixed identities fail rather than aggregate accidentally. No source I/O.

Add an optional typed `InputScope(start_ns,end_ns,eligibility_policy,
include_opening_auction,include_closing_auction)` to BatchMetadata. This explicitly
binds coverage to the target and bar construction policy, survives Arrow and result
metadata, and leaves historical R0 constructors usable. Executable inputs require
this scope; a matching `eligibility_policy` string Parameter is mandatory in
ConfigSpec. Scope bounds must equal [open,C), auction choices must match the
session, and coverage.observed must equal this complete batch's row count.
No guessed full coverage from row count. An explicitly covered zero-row batch
represents no eligible observations. Partial delivery nulls published metrics.

Reuse semantic validation for order, overlap, OHLC, notional bounds and market/
knowledge admission. Missing payload fields affect only dependent features.
Unknown/future knowledge nulls dependent published values, preserving the original
input identity; reconstruction permits them with its distinct config identity.
No filtering unavailable bars into a falsely complete aggregate.

Price OHLC outputs are float64 currency/share after exact coefficient arithmetic;
volume is checked int64 shares; actual notional is checked decimal128 coefficient
with explicit currency/10^scale units. Proxy close-weighted price stays a separate
ID, never real notional/VWAP. Exact integer products/sums precede one Fraction to
float conversion (rtol/atol 1e-12). No throughput claim; this checked Python
implementation establishes correctness before backend optimization.

Prior close uses one supplied DAILY row for the immediately preceding governed
WindowSpec session, matching instrument/namespace/price unit/adjustment policy,
positive close, completed end<=open and known-at admission. Its scope certifies
its complete prior interval and compatible eligibility/auction construction.
Absent/unavailable enrichment nulls only gap and close-close return. Incompatible
identity/unit/basis/order is a typed error. No historical lookup or adjustment.

## Capability evolution

Capabilities permits typed flags, but Registry allows true flags only on the exact
accepted built-in implementation allowlist. Custom execution remains rejected.
Only these twelve IDs gain batch=True; update/restore/merge and R2/custom remain
false. Registry filtering and the development parity verifier check this invariant.
Schema1 scalar results remain suitable; structured output migration belongs to
EQ-018/020/021/022. Release both distributions together as 0.0.2a0, with exact
inward dependency and updated version/build checks.

## Independent tests and documentation

Use the hand-derived b1/b2 and P98 fixture: O100/H104/L99/C103, V500,
actual N51200 versus proxy102.6; returns3/100,5/103,4/5,1/49,5/98.
Test scaled prices, >int64 products, checked volume/notional overflow; flat range,
observed empty/zero, absent/null fields, absent prior, prior positivity/identity/
currency/basis/governed slot/known-at, incomplete scope, partial cutoff, C/K/E,
auction policy, overlapping/unsorted bars and independent readiness. Preserve all
123 formula references and R0 regressions. Add Arrow scope round-trip and capability
negative tests. Installed wheels and sdists must run the same tests and new example.

Update API/example, input and registry migration, package status/README, build
channel/changelog and continuity in the same PR. Freeze a concrete review head,
record author review, run strict typing/purity/import/license/compatibility/reference/
unit/repeat-build/install gates, require exact-head Windows/Linux CI, squash merge,
verify published blobs and main CI, download and inspect both actual OS bundles,
hash manifests and fresh-install both wheel/sdist pairs before Released/Done.

## Observable exit

All twelve IDs callable with independent quality and exact provenance, documented
precision/copy/admission limits, verified versioned experimental main artifacts,
issue acceptance/Project evidence recorded. EQ-018 is pulled only after this exit.
