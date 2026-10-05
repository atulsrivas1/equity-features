# EQ-033 supplied action and reference policies — pre-code plan

Issue: #38; E05/R2; provisional estimate 8 points confirmed as effort, not dates.
Pulled 2026-10-05 after GOV010, BUG003 and BUG004 are live Done with verified
source/artifact receipts. Accepted baseline main29ff0ca8311831d7906ff856bcd63f91fb991977,
experimental pair0.0.2a11. This pre-code plan is committed before implementation.

## Acceptance and boundary

Implement pure admission and exact application of supplied split/total-return
factors and point-in-time classification references. Preserve CanonicalBatch,
ConfigSpec, AdjustmentSpec, AvailabilitySpec and typed statuses/errors. No data
lookup, inferred action, calendar discovery, dividend invention or hidden return
calculation. Caller assertions do not authenticate source truth or legal rights.

## Concrete API decision before code

Contracts adds frozen ActionPolicy, PolicyAdmission, AdjustmentApplication and
ClassificationAdmission, schema1. ActionPolicy binds output AdjustmentSpec,
representation (`apply_factors` or `caller_transformed`), exact anchor boundary,
dividend convention and quantity basis (`raw_shares` or `split_shares`). Supported
application versions are raw-v1, split-factors-v1 and total-return-reinvest-v1;
unknown versions/conventions fail explicitly. Total return uses caller-supplied
positive price factors with a declared reinvestment convention, not invented cash
amounts. Split factors affect quantities reciprocally only for split_shares.

`admit_action_policy(reference: CanonicalBatch | None, policy: ActionPolicy,
config: ConfigSpec, *, entity: EntityKey) -> PolicyAdmission` returns typed
status/reasons, policy/config/source/revision binding and selected reference indices.
`apply_action_policy(batch: CanonicalBatch, reference: CanonicalBatch | None,
policy: ActionPolicy, config: ConfigSpec, *, entity: EntityKey)
-> AdjustmentApplication` returns admission and transformed CanonicalBatch or None,
plus original input binding; input objects remain unchanged. Output source identity
derives from original binding, supplied reference revision, policy and config.
Quantity basis is retained explicitly by the application/admission policy and
must accompany consumers; BatchMetadata.quantity_unit alone does not establish it.

`admit_classification(reference: CanonicalBatch | None, config: ConfigSpec,
*, entity: EntityKey, effective_ns: int, fact_kind: str)
-> ClassificationAdmission` admits only explicitly requested sector_membership
or universe_membership, with typed text/reference readiness independent of other
action/classification facts. Overlapping relevant facts are ambiguous errors;
the library never chooses a revision by sorting or latest-time inference.

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
implementation. Bump experimental pair to0.0.3a0; new policy contracts schema1, existing input/
config/result schema1 and session accumulator schema2 unchanged.
Run meaningful unit/reference/typing/import/boundary/registry/license/compatibility
gates, repeat four-archive build and fresh wheel/sdist execution. Author self-review
is labeled accurately. Exact final PR head checks precede gated merge. Verify
published blobs/main both-OS CI, actual bundles/manifests/hashes/content and four
fresh installed pairs before Released/Done, with linked receipt and issue evidence.
Use all eight actual lifecycle states; plan merge alone does not complete EQ033.

## Exact selection and representation decisions

Policy anchor_ns is an explicit int64 boundary no later than C. Effective actions
at the anchor are admitted; market rows strictly before effective_start receive
factors, rows at/after that boundary do not. An interval spanning a consumed action
boundary raises BOUNDS rather than adjusting mixed observations as one row.
Application supports DAILY/BAR/TRADE/QUOTE and REFERENCE price facts; no feature ID
or session accumulator capability changes. Structural input validation remains
mandatory, but future references outside the policy anchor are not knowledge
requirements for admitted arithmetic. Empty complete adjusted action evidence is
a valid no-action snapshot; absent/incomplete evidence is unavailable.

Consumed immutable reference facts retain original row index, reference ID,
effective bounds, factor/text and original known_at. Admission also binds original
reference InputBinding, output AdjustmentSpec, availability and config digest.
Caller-transformed batches must already match output basis/unit; apply_factors
accepts only raw input and prevents double conversion. An adjusted action snapshot
must match supplied reference snapshot_id. Relevant split_factor/dividend_factor
facts use positive exact rational coefficients; unrecognized relevant action
conventions fail UNSUPPORTED_ADJUSTMENT. Classification selection is independent
and half-open; overlapping applicable facts fail even if text agrees.

Transform actual_notional by the exact price-times-quantity multiplier, requiring
integral decimal128 coefficients. Reciprocal split shares preserve notional;
raw shares retain their quantities. Dividend factors never alter quantities.
Null cells remain null; absent fields remain absent; trade_count is unchanged.
Output input_id derives from original price binding, reference binding, policy and
config; original bindings remain separately accessible. Corrections require caller
replay, with no numerical state restore API added by this story.
