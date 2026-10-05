# Supplied action and classification policies

EQ033, experimental pair0.0.3a0; schema1 policy contracts. These are pure utilities
over owned canonical inputs. They do not acquire corporate actions, authenticate
source history, infer dividends or implement a historical feature ID. The existing
39-ID catalog and23 session batch/update/restore/22 conditional merge capabilities
are unchanged. [Pre-code decisions](../stories/EQ-033_PLAN.md),
[frozen timing policy](../features/TIMING_ADJUSTMENT_POLICY.md).

## API and identities

Import `ActionPolicy`, `ReferenceFact`, `PolicyAdmission`, `AdjustmentApplication`
and `ClassificationAdmission` from `equity_feature_contracts`. Import these calls
from `equity_features.policies`:

```python
admit_action_policy(reference, policy, config, *, entity) -> PolicyAdmission
apply_action_policy(batch, reference, policy, config, *, entity) -> AdjustmentApplication
admit_classification(reference, config, *, entity, effective_ns, fact_kind) -> ClassificationAdmission
```

Inputs remain `CanonicalBatch` and `ConfigSpec`; `entity` is the target `EntityKey`.
Its session must match the config target; market inputs must belong to its instrument
and governed session IDs. Namespace, exact price scale/currency, output adjustment
and algorithm version must agree. Reference facts may carry their own session labels.
Observed coverage must equal actual supplied row count; selected evidence indices
must stay within that bound. Structural validation rejects duplicates/order/bounds/
invalid factors without sorting.
Original bindings, row indices, reference IDs, effective bounds and known-at values
remain in immutable evidence. List construction detaches; lazy iterables fail.

The policy has output `AdjustmentSpec`, exact `anchor_ns`, representation, quantity
basis, dividend convention and schema version. Supported versions/conventions:

| Basis | Version | Dividend convention |
| --- | --- | --- |
| raw | raw-v1 | none |
| split | split-factors-v1 | none |
| total_return | total-return-reinvest-v1 | supplied_reinvestment_factors |

`apply_factors` accepts raw input only. `caller_transformed` accepts an already
matching output basis; its batch is returned unchanged after admission, so no
dividend or split is applied twice. `raw_shares` preserves quantities;
`split_shares` applies only reciprocal split factors. Dividend factors never alter
volume, trade size or quote sizes. Pass the application/admission policy to later
consumers; `BatchMetadata.quantity_unit="shares"` alone cannot distinguish these bases.

Adjusted policies require supplied reference snapshot_id equal to action_snapshot
and complete coverage. Complete empty snapshots explicitly mean no supplied actions.
Absent/incomplete snapshots are unavailable, never assumed empty. Raw needs no
action evidence and consumes no factors; an optional reference binding retains
context without claiming split-neutral or shareholder returns.

## Exact arithmetic

Recognized action fact kinds are `split_factor` and `dividend_factor`, with positive
int64 factor_num/factor_den. Versions above use instantaneous effective boundaries,
so effective_end_ns must be absent. Split basis excludes dividend facts. Known
classification/prior_close facts are separate dependencies; unknown relevant kinds
within the anchor fail UNSUPPORTED_ADJUSTMENT. Other instruments and facts after
the anchor are not action dependencies; their knowledge does not block readiness.

For row time t, multiply all applicable supplied price factors with t<effective_start
and effective_start<=anchor. Anchor cannot exceed market cutoff C. Interval rows
ending exactly at the effective boundary are pre-action; rows starting exactly
there are post-action. An interval straddling an action fails BOUNDS, because its
mixed observations cannot be transformed as one aggregate.

OHLC, trade price, bid/ask and reference prior_close price receive the same exact
price multiplier. For split_shares, volume/size/bid_size/ask_size receive its split
reciprocal. Actual notional receives price_multiplier*quantity_multiplier;
trade_count is unchanged. Transient arbitrary-width rational arithmetic avoids
intermediate wrapping. Every resulting coefficient must be integral and fit int64,
or decimal128 for actual_notional; nonintegral results fail UNSUPPORTED_ADJUSTMENT
and range overflow fails OVERFLOW. There is no rounding or retained recursive state.
Null cells remain null; absent fields remain absent.

A2:1 split maps price100 to50 and10shares to20 with notional1000 unchanged.
For prior100/ex99/cash1, the caller supplies the declared total-return price factor
99/100 at sufficient exact scale: transformed closes99 and99 yield return0.
Raw/split closes100 and99 yield -1/100. This utility does not calculate that return
or add cash again. The supplied convention asserts how factors were prepared;
their economic correctness and source rights remain caller qualification.

## Readiness and point-in-time classification

`PolicyAdmission` records action readiness, facts, reasons, config digest and original
reference binding. `AdjustmentApplication` separately records market readiness,
original market binding and nullable output batch. Available action evidence cannot
certify later-known market data. Missing action operands yield missing_input;
incomplete coverage yields incomplete_coverage. The utility preserves field nulls
but does not certify downstream field-specific feature readiness.

Consumed rows in known_at mode require original known_at<=K; equality is admitted,
null gives unknown_availability and later knowledge future_knowledge. Reconstruction
permits later/unknown knowledge while retaining original values and its distinct
mode/reason/C/K/E identity. Market input must still meet C. Application does not
select or filter future market rows; forming intervals and ordinary events at C
fail BOUNDS. Reference price application supports only supplied prior_close facts.

Classification selects exactly one `sector_membership` or `universe_membership`
for the instrument with start<=effective_ns<end, or an open-ended interval; requested
time cannot exceed C. Facts outside that interval are excluded before knowledge
readiness. Overlap is ambiguous even if text matches or one revision is later-known;
callers must supply the intended revision, not expect a latest-row choice. Missing
or null text, absent fact and unavailable knowledge remain distinct typed reasons.
Sector/universe readiness does not consume or depend on split/dividend fields.

Policy/classification `identity_digest` binds supplied revisions, selected facts,
policy and config/availability. Transformed input_id additionally binds the original
market binding. Corrected sources/policies/configurations therefore invalidate
dependent state; callers replay from a compatible anchor. Future facts do not alter
selected arithmetic/readiness, but a new snapshot/coverage identity remains a new
binding. Digests detect identity differences, not authenticated source truth.

Run [the synthetic example](../../examples/action_policies.py). See the
[delivery record](../stories/EQ-033_DELIVERY.md) for actual qualification; source
implementation and editable tests alone are not a completed release.
