"""Pure EF3 adaptive volume diagnostics (ef3-adaptive1): a time-weighted smoothed rate baseline and event-time peaks.

The supplied raw rate (shares per second) of each observation before the market cutoff C builds the baseline
`B_1 = r_1`, `B_k = (tau B_(k-1) + d_k r_k) / (tau + d_k)` (d_k the elapsed ns, a rational weight, no exponential).
Observation k >= W+1 is scorable; its relative rate is `r_k / B_(k-1)` and its relative acceleration
`(r_k - r_(k-1)) 10^9 / (d_k B_(k-1))` per second, each defined for a positive baseline (and a positive elapsed time).
Every comparison, tie and peak is decided on exact rationals (the earliest observation wins an exact tie); each
published float64 is one correctly rounded rational. Output is a pure function of the in-scope prefix; no state.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import gcd

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, CanonicalBatch, ConfigSpec, DataKind, EntityKey, ErrorCode, EvidenceRow,
    FeatureColumn, FeatureResult, InputBinding, Parameter, PriceUnit, QualityRow, Reason, ResultMetadata,
    SessionSpec, Status, ValueType,
)
from equity_features import __version__
from ._breadth_common import NO_REASONS, RATE_MODE, fact_rows
from ._common import fail, integer, label
from ._robust_common import (
    check_entity, check_features, check_policy, check_slots, first_status, make_config, ordered, parameter_map,
)

ADAPTIVE_IDENTITY = "ef3.adaptive_volume"
ADAPTIVE_ALGORITHM = "ef3-adaptive-volume-v1"
# The label names the whole convention set (rational time-weighted baseline seeded by the first observation,
# warm-up W, scorable k >= W+1, zero baseline undefined not an error, earliest exact tie, per-epoch reset).
ADAPTIVE_POLICY = "ef3-adaptive1"
RATE_KIND = "ef3.adaptive.rate"
ACCELERATION_COUNT = "adaptive.volume.acceleration_scored_count"
BASELINE_AVAILABLE = "adaptive.volume.baseline_available"
BASELINE_RATE = "adaptive.volume.baseline_rate"
LATEST_EVENT = "adaptive.volume.latest_event_ns"
OBSERVATION_COUNT = "adaptive.volume.observation_count"
PEAK_ACCELERATION = "adaptive.volume.peak_relative_acceleration"
PEAK_ACCELERATION_NS = "adaptive.volume.peak_relative_acceleration_event_ns"
PEAK_RATE = "adaptive.volume.peak_relative_rate"
PEAK_RATE_NS = "adaptive.volume.peak_relative_rate_event_ns"
SCORED_COUNT = "adaptive.volume.scored_count"
ADAPTIVE_FEATURES = (ACCELERATION_COUNT, BASELINE_AVAILABLE, BASELINE_RATE, LATEST_EVENT, OBSERVATION_COUNT,
                     PEAK_ACCELERATION, PEAK_ACCELERATION_NS, PEAK_RATE, PEAK_RATE_NS, SCORED_COUNT)
FEATURE_META: dict[str, tuple[ValueType, str]] = {
    ACCELERATION_COUNT: (ValueType.INT64, "observations"), BASELINE_AVAILABLE: (ValueType.BOOL, "boolean"),
    BASELINE_RATE: (ValueType.FLOAT64, "shares/s"), LATEST_EVENT: (ValueType.INT64, "utc_ns"),
    OBSERVATION_COUNT: (ValueType.INT64, "observations"), PEAK_ACCELERATION: (ValueType.FLOAT64, "1/s"),
    PEAK_ACCELERATION_NS: (ValueType.INT64, "utc_ns"), PEAK_RATE: (ValueType.FLOAT64, "ratio"),
    PEAK_RATE_NS: (ValueType.INT64, "utc_ns"), SCORED_COUNT: (ValueType.INT64, "observations"),
}
# Outputs that depend on the rates (a null rate in scope is null_field for these); the others use event times only.
RATE_OUTPUTS = frozenset(ADAPTIVE_FEATURES) - {OBSERVATION_COUNT, LATEST_EVENT}
_REQUIRED = frozenset({"policy_version", "epoch", "tau_ns", "warmup_count", "evidence_limit"})


@dataclass(frozen=True)
class AdaptiveVolumeSettings:
    policy_version: str
    epoch: str
    tau_ns: int
    warmup_count: int
    evidence_limit: int


def _check(policy: object, epoch: object, tau: object, warmup: object, limit: object) -> AdaptiveVolumeSettings:
    check_policy(policy, ADAPTIVE_POLICY)
    assert type(policy) is str
    return AdaptiveVolumeSettings(policy, label(epoch), integer(tau, 1, 2**62), integer(warmup, 1, 4096),
                                  integer(limit, 0, 10000))


def build_adaptive_volume_config(*, policy_version: str | None = None, epoch: str | None = None,
                                 tau_ns: int | None = None, warmup_count: int | None = None, session: SessionSpec,
                                 availability: AvailabilitySpec, adjustment: AdjustmentSpec, price_unit: PriceUnit,
                                 evidence_limit: int = 0) -> ConfigSpec:
    """Final ConfigSpec; every parameter is explicit with no default."""
    s = _check(policy_version, epoch, tau_ns, warmup_count, evidence_limit)
    params = (Parameter("policy_version", s.policy_version), Parameter("epoch", s.epoch),
              Parameter("tau_ns", s.tau_ns), Parameter("warmup_count", s.warmup_count),
              Parameter("evidence_limit", s.evidence_limit))
    return make_config(ADAPTIVE_IDENTITY, ADAPTIVE_ALGORITHM, params, 1, session, availability, adjustment,
                       price_unit)


def decode_adaptive_volume_config(config: ConfigSpec) -> AdaptiveVolumeSettings:
    """Validate the closed adaptive-volume envelope and return its settings."""
    v = parameter_map(config, ADAPTIVE_IDENTITY, ADAPTIVE_ALGORITHM, _REQUIRED, frozenset())
    s = _check(v["policy_version"], v["epoch"], v["tau_ns"], v["warmup_count"], v["evidence_limit"])
    assert config.price_unit is not None
    expected = build_adaptive_volume_config(
        policy_version=s.policy_version, epoch=s.epoch, tau_ns=s.tau_ns, warmup_count=s.warmup_count,
        session=config.session, availability=config.availability, adjustment=config.adjustment,
        price_unit=config.price_unit, evidence_limit=s.evidence_limit)
    if config != expected:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "configuration is not the final canonical adaptive-volume envelope")
    return s


@dataclass(frozen=True)
class _Obs:
    """One observation; the raw rate is the exact rational a / b (a >= 0, b >= 1) or None."""

    seq: int
    start: int
    known_at: int | None
    a: int | None
    b: int


@dataclass(frozen=True)
class _Peak:
    """An exact peak num / den (den > 0), its correctly rounded float (the exact tie breaker is the integers)."""

    num: int
    den: int
    value: float
    obs: _Obs


def _divide(num: int, den: int) -> float:
    """One correctly rounded binary64 of an exact integer ratio (exact zero is the positive zero)."""
    try:
        return num / den
    except OverflowError:
        fail(ErrorCode.OVERFLOW, "statistic outside binary64")


def _better(num: int, den: int, value: float, best: _Peak | None) -> bool:
    """Strictly greater than the current peak, decided exactly: rounding is monotone, so the integers only matter
    when the two floats are equal."""
    if best is None:
        return True
    if value != best.value:
        return value > best.value
    return num * best.den > best.num * den


@dataclass
class _Out:
    value: bool | int | float | None
    reasons: frozenset[Reason]
    expected: int | None
    observed: int
    witness: _Obs | None = None


def _admit(batch: CanonicalBatch, config: ConfigSpec, settings: AdaptiveVolumeSettings,
           entity: EntityKey) -> list[_Obs]:
    rows = fact_rows(batch, config, {RATE_KIND: RATE_MODE}, "ao1", ("t", "d19", "t"))
    snapshot = batch.metadata.source.snapshot_id
    result: list[_Obs] = []
    for instrument, row, parts in rows:
        if instrument != entity.instrument_id:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "observation instrument differs from the target entity")
        if parts[0] != settings.epoch:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "observation epoch differs from the configuration")
        if row.text != snapshot:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "observation snapshot differs from the batch snapshot")
        seq = int(parts[1])
        if result and seq <= result[-1].seq:
            fail(ErrorCode.DUPLICATE if seq == result[-1].seq else ErrorCode.INVALID_ORDER,
                 "sequence must strictly increase within the epoch")
        a = None if row.price is None else row.price * (row.num or 1)
        result.append(_Obs(seq, row.start, row.known_at, a, row.den or 1))
    return result


def compute_adaptive_volume(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None],
                            config: ConfigSpec, *, entity: EntityKey, features: tuple[str, ...]) -> FeatureResult:
    """Selected ef3-adaptive1 outputs; `batches` is the one nullable `observations` slot."""
    settings = decode_adaptive_volume_config(config)
    entity = check_entity(entity, config)
    selected = check_features(features, ADAPTIVE_FEATURES)
    (batch,) = check_slots(batches, 1, (DataKind.REFERENCE,))
    cutoff, knowledge = config.availability.market_cutoff_ns, config.availability.knowledge_cutoff_ns
    rows: list[_Obs] = [] if batch is None else _admit(batch, config, settings, entity)
    scope = [o for o in rows if o.start < cutoff]
    n, warm, tau = len(scope), settings.warmup_count, settings.tau_ns

    findings: set[Reason] = set()
    if batch is None:
        findings.add(Reason.ABSENT_INPUT)
    elif not batch.metadata.coverage.complete:
        findings.add(Reason.GOVERNED_GAP)
    knowledge_reasons: set[Reason] = set()
    unknown = 0
    usable = 0
    for o in scope:
        failed = o.known_at is None or o.known_at > knowledge
        if failed:
            unknown += 1
            knowledge_reasons.add(Reason.UNKNOWN_AVAILABILITY if o.known_at is None else Reason.FUTURE_KNOWLEDGE)
        elif o.a is not None:
            usable += 1
    null_rate = any(o.a is None for o in scope)

    # The exact stream recurrence B = P / Q (integers, no float), run only when every in-scope row is usable.
    scored = accelerated = 0
    peak_rate: _Peak | None = None
    peak_accel: _Peak | None = None
    base_p = base_q = 0
    if not findings and not knowledge_reasons and not null_rate:
        previous: _Obs | None = None
        for k, o in enumerate(scope):
            assert o.a is not None
            if previous is None:
                base_p, base_q = o.a, o.b
            else:
                assert previous.a is not None
                d = o.start - previous.start
                if k >= warm and base_p > 0:
                    num, den = o.a * base_q, o.b * base_p
                    value = _divide(num, den)
                    scored += 1
                    if _better(num, den, value, peak_rate):
                        peak_rate = _Peak(num, den, value, o)
                    if d > 0:
                        num = (o.a * previous.b - previous.a * o.b) * 10**9 * base_q
                        den = o.b * previous.b * d * base_p
                        value = _divide(num, den)
                        accelerated += 1
                        if _better(num, den, value, peak_accel):
                            peak_accel = _Peak(num, den, value, o)
                if d > 0:
                    base_p, base_q = tau * base_p * o.b + d * o.a * base_q, base_q * o.b * (tau + d)
                    if k % 32 == 0:
                        g = gcd(base_p, base_q)
                        base_p, base_q = base_p // g, base_q // g
            previous = o

    def peak(found: _Peak | None, as_time: bool) -> _Out:
        if n < warm + 1:
            return _Out(None, frozenset({Reason.INSUFFICIENT_HISTORY}), warm + 1, n)
        if found is None:
            return _Out(None, frozenset({Reason.ZERO_DENOMINATOR}), n, n)
        return _Out(found.obs.start if as_time else found.value, NO_REASONS, n, n, found.obs)

    def evaluate(feature: str) -> _Out:
        if findings:
            return _Out(None, frozenset(findings), None, 0)
        reasons = set(knowledge_reasons)
        if feature in RATE_OUTPUTS and null_rate:
            reasons.add(Reason.NULL_FIELD)
        if reasons:
            return _Out(None, frozenset(reasons), n, usable if feature in RATE_OUTPUTS else n - unknown)
        if feature == OBSERVATION_COUNT:
            return _Out(n, NO_REASONS, n, n)
        if feature == LATEST_EVENT:
            if n == 0:
                return _Out(None, frozenset({Reason.NO_ELIGIBLE_OBSERVATIONS}), 0, 0)
            return _Out(scope[-1].start, NO_REASONS, n, n, scope[-1])
        if feature == BASELINE_AVAILABLE:
            return _Out(n >= warm, NO_REASONS, n, n)
        if feature == BASELINE_RATE:
            if n < warm:
                return _Out(None, frozenset({Reason.INSUFFICIENT_HISTORY}), warm, n)
            return _Out(_divide(base_p, base_q), NO_REASONS, n, n, scope[-1])
        if feature == SCORED_COUNT:
            return _Out(scored, NO_REASONS, n, n)
        if feature == ACCELERATION_COUNT:
            return _Out(accelerated, NO_REASONS, n, n)
        if feature in (PEAK_RATE, PEAK_RATE_NS):
            return peak(peak_rate, feature == PEAK_RATE_NS)
        return peak(peak_accel, feature == PEAK_ACCELERATION_NS)

    columns: list[FeatureColumn] = []
    quality: list[QualityRow] = []
    evidence: list[EvidenceRow] = []
    for feature in selected:
        out = evaluate(feature)
        status = Status.AVAILABLE if out.value is not None else first_status(out.reasons)
        dtype, unit = FEATURE_META[feature]
        columns.append(FeatureColumn(feature, ADAPTIVE_ALGORITHM, dtype, unit, (entity,), (out.value,)))
        quality.append(QualityRow(entity, feature, status, out.expected, out.observed,
                                  () if out.value is not None else ordered(out.reasons)))
        witness = out.witness
        if witness is not None and out.value is not None and len(evidence) < settings.evidence_limit:
            assert batch is not None
            evidence.append(EvidenceRow(entity, feature, batch.metadata.source.input_id, f"seq:{witness.seq}",
                                        witness.start, witness.known_at, witness.start, None, "consumed", None,
                                        "ordinary"))
    bindings = () if batch is None else (InputBinding("observations", batch.kind, batch.metadata),)
    metadata = ResultMetadata(config.session.namespace, entity.session_id, config.availability, config.digest,
                              bindings, "python-exact", __version__, settings.evidence_limit)
    return FeatureResult(tuple(columns), tuple(quality), metadata, tuple(evidence))
