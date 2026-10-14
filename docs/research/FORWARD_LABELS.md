## EQ091 current candidate qualification passed — October 14

Exact eaab022b9058754af0360969894adac8ec5d381d passed all14 candidate checks, including both Windows/Linux research jobs. PUSH run38646944319 artifacts Linux11932642959 SHA761f9883f6416595bc9af52546ac97c12fb71b8701c8ea06af087e646680a5c7 and Windows11931959367 SHA01554cb3044e60c280dd9676b00519197fec8cb8dd98c69c0e578ad662ef85d7 each contain eight archives plus completed schema2 qualification. Per OS, four fresh component/form environments passed independent fixtures and installed positive/negative typing, while two explicitly combined consumer/form environments passed actual core production, scanner/future-label invariance and as-of joins with complete core parity. Source head/materialization closure and twice-built archive parity passed. Four label methods cover30 standalone label requirements; the combined consumer covers the remaining three and predicate-order identity. This is candidate evidence, not completed release: separate final docs/artifact review, final-head current CI and actual main evidence remain. [Ledger](../stories/EQ-091_VALIDATION.json).

# Forward price-return labels

EQ091 #103 candidate implementation, experimental `equity-feature-labels==0.1.0a1`.
Source review, execution and current artifact acceptance are pending. Exact fields,
errors and canonical encoding follow the [normative contract](STRATEGY_LABEL_CONTRACTS.md).

`evaluate_label(request: LabelRequest) -> LabelResult` receives frozen supplied
facts. Construct an independent `Entity`, `BasisWitness`, `LabelOrigin`,
`PriceObservation`, `LabelConfig(horizon_ns)` and `LabelRequest`. Core
`AvailabilitySpec` supplies causal C/K/E cutoffs. Lists snapshot to owned tuples;
observations normalize by unique event_ns. Exact built-in types are required,
including finite positive Float64 prices and int64 nanoseconds. There is no type
coercion, date lookup or automatic migration. Raw witnesses require raw-v1/none/none;
supplied split witnesses require explicit non-none identifiers. Total-return basis
is unsupported. All path rows must share complete basis and source revision and
bind to the immutable original origin digest, including unused/future rows.

For checked `t1=origin.anchor_event_ns+horizon_ns`, `horizon_ns>0`, state precedence is:

1. Structural/origin errors reject before state evaluation. Original anchor and
   basis must have been available by signal K and effective by the anchor event.
2. `t1>C` is pending with horizon_not_elapsed.
3. Missing exact endpoints are incomplete, with missing_anchor_endpoint then
   missing_horizon_endpoint. No interpolation occurs.
4. Unknown consumed endpoint/common-basis knowledge gives unknown_availability;
   knowledge after K gives future_knowledge. Both reasons retain this order.
5. Basis effective after t1 gives pending/basis_not_effective.
6. Otherwise compute `q=P(t1)/P(t0)` then `R=q-1`. Mature known_at is the maximum
   consumed endpoint/basis known_at. R has unit fraction. Nonfinite q/R raises
   numerical_bounds; q rounded to zero raises precision_bounds. Finite nonzero
   subnormal ratios retain normal Float64 rounding. Independent finite fixtures
   use absolute/relative 1e-12; states and identities use exact assertions.

Pending/incomplete outputs have null value and label_known_at_ns and expose no
endpoint price or ratio. Dividends are not added: 100 to 99 is -1/100. A raw split
100 to 50 is -1/2; separately supplied comparable adjusted 50 to 50 is zero. The
adjusted path never replaces the original signal anchor or signal identity.

`encode`, `digest`, `origin_digest` and `path_content_digest` produce canonical
in-memory bytes/SHA256. Own domains are label-origin:1, label-config:1,
label-request:1, label-result:1 and label-price-path:1. Complete original path,
revisions, basis, timing and fields participate; an unused interior row still
changes identity. Origin/config/request/result expose derived identity_digest.
There is no decoder or arbitrary-record serializer. Digest equality does not
authenticate facts or promise secrecy. `LabelError.code` is immutable with fixed
messages and the closed vocabulary in the normative contract.

The [combined synthetic consumer](../../examples/research_labels.py) explicitly
installs features and both research packages. An actual core producer feeds a
fixed scanner prefix. Changing future label prices, adjustment revisions and
evaluation leaves the signal bytes unchanged; label objects reject as signal
features. Application as-of joins require a mature matching-origin explicitly
selected request/revision, endpoint<=join C, known_at<=join K and original signal
cutoffs<=causal join cutoffs. Retrospective targets are not tradable signals.

The standalone suite covers 30 of the 33 published label requirements without
strategies/features installed; the combined consumer covers causal-signal-invariance,
join-reject-future-known and join-admit-boundary. Seven directly applicable identity
requirements run standalone; predicate-order runs with strategies in the combined
consumer and existing strategy suite. These are requirement mappings, not executed
test counts. Four label test methods are authored; no runtime pass is claimed yet.

See [installation](../INSTALLING.md), [public API](../api/PUBLIC_API.md) and
[validation ledger](../stories/EQ-091_VALIDATION.json). Both Windows/Linux wheel and
sdist forms, current main checks and separate final review precede acceptance.
EQ092 retains the broader final backtest/aggregate release qualification.
