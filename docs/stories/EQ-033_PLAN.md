# EQ-033 supplied action and reference policies — pre-code plan

Issue: #38; E05/R2; provisional estimate 8 points confirmed as effort, not dates.
Prepared 2026-10-05 while governance/repair delivery gates are pending. This is
a local draft, not an implementation or Ready claim. Pull only after GOV010 and
both BUG003/004 are live Done with verified source/artifact receipts.

## Acceptance and boundary

Implement pure admission and exact application of supplied split/total-return
factors and point-in-time classification references. Preserve CanonicalBatch,
ConfigSpec, AdjustmentSpec, AvailabilitySpec and typed statuses/errors. No data
lookup, inferred action, calendar discovery, dividend invention or hidden return
calculation. Caller assertions do not authenticate source truth or legal rights.

## Concrete API decision before code

Contracts adds frozen ActionPolicy and PolicyAdmission, version 1. ActionPolicy
binds output AdjustmentSpec, declared representation (`apply_factors` or
`caller_transformed`), anchor session/start, dividend convention and quantity basis.
`admit_action_policy(reference: CanonicalBatch | None, policy: ActionPolicy,
availability: AvailabilitySpec, *, instrument_id: str, session_id: str)` returns
typed admission with status/reasons, source/revision identity and retained exact
selected reference row indices. `apply_action_policy(batch: CanonicalBatch,
reference: CanonicalBatch | None, policy: ActionPolicy,
availability: AvailabilitySpec) -> AdjustmentApplication` returns typed admission
plus transformed CanonicalBatch or None; input objects remain unchanged.
`admit_classification(reference: CanonicalBatch | None,
availability: AvailabilitySpec, *, instrument_id: str, session_id: str,
effective_ns: int, fact_kind: str) -> ClassificationAdmission` returns typed
text/reference readiness independently of unrelated action or classification facts.

Use supplied reference factor_num/factor_den (positive int64) as exact rational
price multipliers. Compound using arbitrary-width transient integers/Fraction;
require exact integral output coefficients and quantities within int64, otherwise
reject explicitly (no quantization). Split quantity multiplier is reciprocal when
declared adjusted shares. Price fields OHLC/bid/ask/prior supplied price receive
the same applicable multiplier; dividend factors never affect quantities.
Actions only affect slots strictly before supplied effective_start_ns, with
effective_start_ns <= anchor boundary. No action after the anchor is consumed.
For `total_return`, require an explicit supplied-factor/reinvestment convention;
caller-transformed input is only admitted, never adjusted again. Raw remains raw.

Bind policy/version/action snapshot/anchor and source input identities. Adjusted
inputs with incompatible prior basis or evidence fail typed validation. Unknown
knowledge or known_at>K produces missing_input; reconstruction retains original
knowledge and distinct mode/reason. Effective intervals are half-open; duplicate
or contradictory relevant identities fail. Reference rows beyond the anchor or
outside classification interval are excluded before availability affects readiness.
Corrections/new action snapshots produce new identities and invalidate dependent
state; replay is caller-owned. No streaming or merge capabilities introduced here.

## Independent verification

Production API tests use independent rational expectations: 2:1 price100->50,
shares10->20, exact notional1000; multiple splits; maximum-int64 rejection;
nonintegral factors rejected. Synthetic prior100/ex99/cash1 supplies price factor
99/100 at scale2 and establishes total-return0 versus raw/split -1/100 without
adding a dividend twice. Test missing/unsupported policies/evidence, C/K/E equality,
future/unknown knowledge, effective/anchor boundaries, reconstruction preservation,
revision identity changes, caller-transformed no-op, independent classification
readiness, malformed/duplicate/order/unit/basis errors and input immutability.
Retain all123 formula references and repaired session regressions.

## Documentation and observable Done

Publish this plan before source code; API policy guide, contracts/version decision,
synthetic installed example, changelog, package descriptions and continuity accompany
implementation. Bump experimental pair to R2 alpha0 after accepted repair baseline.
Run meaningful unit/reference/typing/import/boundary/registry/license/compatibility
gates, repeat four-archive build and fresh wheel/sdist execution. Author self-review
is labeled accurately. Exact final PR head checks precede gated merge. Verify
published blobs/main both-OS CI, actual bundles/manifests/hashes/content and four
fresh installed pairs before Released/Done, with linked receipt and issue evidence.
Use all eight actual lifecycle states; plan merge alone does not complete EQ033.
