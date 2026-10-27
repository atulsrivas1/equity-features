"""Pure EF2 retracement level (ef2-retrace1): one caller-parameterized Fibonacci-style level from two supplied extrema.

The prior-window high and low arrive as exact integer coefficients in two REFERENCE roles owned by the
extrema producer; they are reused, never re-derived. No close price, I/O, clock, storage or default ratio.
"""
from __future__ import annotations

from base64 import urlsafe_b64decode, urlsafe_b64encode
from dataclasses import dataclass
from math import gcd
import re
from typing import Any, NoReturn, cast

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, CanonicalBatch, ConfigSpec, ContractError, DataKind, EntityKey,
    ErrorCode, EvidenceRow, FeatureColumn, FeatureResult, InputBinding, Parameter, PriceUnit,
    QualityRow, Reason, ResultMetadata, SessionSpec, Status, ValueType, WindowSpec, validate_batch,
)
from equity_features import __version__

RETRACEMENT_IDENTITY = "ef2.retracement_level"
RETRACEMENT_ALGORITHM = "ef2-retracement-level-v1"
# The label names the whole convention set (ratio domain 0..1, the two direction formulas,
# zero range as zero denominator, inverted range ineligible); another convention is another label.
RETRACEMENT_POLICY = "ef2-retrace1"
FEATURE_ID = "retracement.level"
ROLES = ("prior_high", "prior_low")
FACT_KINDS = ("ef2.extremum.high", "ef2.extremum.low")
DIRECTIONS = ("from_high", "from_low")
_KEYS = frozenset({"policy_version", "direction", "ratio_num", "ratio_den", "evidence_limit"})
_I64_MAX = 2**63 - 1
# The first applicable reason fixes the status; every applicable reason is still reported (lexical order).
_PRECEDENCE = (Reason.ABSENT_INPUT, Reason.UNKNOWN_AVAILABILITY, Reason.FUTURE_KNOWLEDGE, Reason.NULL_FIELD,
               Reason.INELIGIBLE, Reason.GOVERNED_GAP, Reason.INSUFFICIENT_HISTORY,
               Reason.NO_ELIGIBLE_OBSERVATIONS, Reason.ZERO_DENOMINATOR)
_STATUS = {Reason.GOVERNED_GAP: Status.INCOMPLETE_COVERAGE, Reason.INSUFFICIENT_HISTORY: Status.INSUFFICIENT_HISTORY,
           Reason.NO_ELIGIBLE_OBSERVATIONS: Status.NOT_APPLICABLE, Reason.ZERO_DENOMINATOR: Status.NOT_APPLICABLE}
_B64URL = re.compile("[A-Za-z0-9_-]+")


def fail(code: ErrorCode, message: str) -> NoReturn:
    raise ContractError(code, message)


def label(value: object) -> str:
    if type(value) is not str or not value.strip():
        fail(ErrorCode.INVALID_SCHEMA, "nonempty exact string required")
    if len(value) > 128 or any(ord(c) < 32 or ord(c) == 127 or 0xD800 <= ord(c) <= 0xDFFF for c in value):
        fail(ErrorCode.BOUNDS, "unsafe or over-limit identity")
    if len(value.encode("utf-8")) > 512:
        fail(ErrorCode.BOUNDS, "over-limit UTF8 identity")
    return value


@dataclass(frozen=True)
class RetracementSettings:
    policy_version: str
    direction: str
    ratio_num: int
    ratio_den: int
    evidence_limit: int


def _check_ratio(num: object, den: object) -> tuple[int, int]:
    """Free caller ratio as a reduced exact pair in 0..1; no default, no float, bool or extension ratio."""
    if type(num) is not int or type(den) is not int:
        fail(ErrorCode.INVALID_CONFIG, "exact integer ratio pair required")
    if not 1 <= den <= _I64_MAX:
        fail(ErrorCode.INVALID_CONFIG, "ratio denominator outside 1..2^63-1")
    if num < 0:
        fail(ErrorCode.INVALID_CONFIG, "negative ratio numerator")
    if num > den:
        fail(ErrorCode.INVALID_CONFIG, "extension ratios above 1 are out of v1")
    if gcd(num, den) != 1:
        fail(ErrorCode.INVALID_CONFIG, "reduced ratio required (zero only as 0/1, one only as 1/1)")
    return num, den


def _check_settings(policy: object, direction: object, num: object, den: object,
                    limit: object) -> RetracementSettings:
    if type(policy) is not str:
        fail(ErrorCode.INVALID_CONFIG, "exact retracement policy label required")
    if policy != RETRACEMENT_POLICY:
        fail(ErrorCode.INCOMPATIBLE_VERSION, "unsupported retracement policy label")
    if type(direction) is not str or direction not in DIRECTIONS:
        fail(ErrorCode.INVALID_CONFIG, "direction must be from_high or from_low")
    ratio_num, ratio_den = _check_ratio(num, den)
    if type(limit) is not int or not 0 <= limit <= 10000:
        fail(ErrorCode.INVALID_CONFIG, "evidence_limit must be an integer in 0..10000")
    return RetracementSettings(policy, direction, ratio_num, ratio_den, limit)


def build_retracement_config(*, policy_version: str, direction: str, ratio_num: int | None = None,
                             ratio_den: int | None = None, session: SessionSpec, availability: AvailabilitySpec,
                             adjustment: AdjustmentSpec, price_unit: PriceUnit,
                             evidence_limit: int = 0) -> ConfigSpec:
    """Final ConfigSpec for one direction and one ratio; a different ratio or direction is a different config."""
    if (type(session) is not SessionSpec or type(availability) is not AvailabilitySpec
            or type(adjustment) is not AdjustmentSpec):
        fail(ErrorCode.INVALID_CONFIG, "concrete session/timing/action required")
    if type(price_unit) is not PriceUnit:
        fail(ErrorCode.INVALID_UNIT, "retracement level requires an explicit PriceUnit")
    settings = _check_settings(policy_version, direction, ratio_num, ratio_den, evidence_limit)
    if not session.open_ns <= availability.market_cutoff_ns <= session.close_ns:
        fail(ErrorCode.BOUNDS, "market cutoff outside actual session")
    params = (Parameter("policy_version", settings.policy_version), Parameter("direction", settings.direction),
              Parameter("ratio_num", settings.ratio_num), Parameter("ratio_den", settings.ratio_den),
              Parameter("evidence_limit", settings.evidence_limit))
    return ConfigSpec(RETRACEMENT_IDENTITY, RETRACEMENT_ALGORITHM, params, session,
                      WindowSpec(1, session.session_id, (session.session_id,), "completed_eod"),
                      availability, adjustment, price_unit)


def decode_retracement_config(config: ConfigSpec) -> RetracementSettings:
    """Validate the closed retracement envelope and return its settings."""
    if type(config) is not ConfigSpec:
        fail(ErrorCode.INVALID_CONFIG, "concrete ConfigSpec required")
    if config.algorithm_version != RETRACEMENT_ALGORITHM:
        fail(ErrorCode.INCOMPATIBLE_VERSION, "retracement algorithm version differs")
    if config.identity != RETRACEMENT_IDENTITY:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "not a retracement-level configuration")
    values = {p.name: p.value for p in config.parameters}
    if set(values) != _KEYS:
        fail(ErrorCode.INVALID_CONFIG, "closed retracement parameters required (there is no default ratio)")
    settings = _check_settings(values["policy_version"], values["direction"], values["ratio_num"],
                               values["ratio_den"], values["evidence_limit"])
    if config.price_unit is None:
        fail(ErrorCode.INVALID_UNIT, "retracement level requires an explicit PriceUnit")
    expected = build_retracement_config(
        policy_version=settings.policy_version, direction=settings.direction, ratio_num=settings.ratio_num,
        ratio_den=settings.ratio_den, session=config.session, availability=config.availability,
        adjustment=config.adjustment, price_unit=config.price_unit, evidence_limit=settings.evidence_limit)
    if config != expected:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "configuration is not the final canonical retracement envelope")
    return settings


def _decode_part(part: str) -> str:
    """Reversible unpadded base64url of UTF8; a noncanonical spelling is not accepted."""
    if _B64URL.fullmatch(part) is None or len(part) % 4 == 1:
        fail(ErrorCode.INVALID_SCHEMA, "closed x1 reference grammar required")
    raw = urlsafe_b64decode(part + "=" * (-len(part) % 4))
    if urlsafe_b64encode(raw).rstrip(b"=").decode("ascii") != part:
        fail(ErrorCode.INVALID_SCHEMA, "reversible x1 reference grammar required")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        fail(ErrorCode.INVALID_SCHEMA, "UTF8 x1 reference component required")
    if not text.strip() or any(ord(c) < 32 or ord(c) == 127 or 0xD800 <= ord(c) <= 0xDFFF for c in text):
        fail(ErrorCode.INVALID_SCHEMA, "nonblank safe x1 reference component required")
    return text


def _window_set(reference_id: Any) -> str:
    """Return the window set id decoded from x1:B(window_set_id), bounded before any label check."""
    if (type(reference_id) is not str or len(reference_id) > 128
            or len(reference_id.encode("utf-8", errors="surrogatepass")) > 512):
        fail(ErrorCode.INVALID_SCHEMA, "bounded x1 reference identity required")
    parts = reference_id.split(":")
    if len(parts) != 2 or parts[0] != "x1":
        fail(ErrorCode.INVALID_SCHEMA, "closed x1 reference grammar required")
    return _decode_part(parts[1])


@dataclass(frozen=True)
class _Side:
    """One extremum role after structural admission; the price is read only for an admitted row."""
    role: str
    batch: CanonicalBatch | None
    reference_id: str | None = None
    price: int | None = None
    factor_num: int | None = None
    factor_den: int | None = None
    known_at_ns: int | None = None
    start_ns: int | None = None
    end_ns: int | None = None


def _admit(role: str, kind: str, batch: CanonicalBatch | None, config: ConfigSpec,
           entity: EntityKey) -> _Side:
    """Structural admission of one role; every contradiction refuses before any assessment."""
    if batch is None:
        return _Side(role, None)
    if batch.row_count > 1:
        fail(ErrorCode.DUPLICATE, "exactly one extremum row per role")
    meta = batch.metadata
    if meta.namespace != config.session.namespace or meta.coverage.observed != batch.row_count:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "extremum namespace/population mismatch")
    if meta.ordering != "declared" or meta.duplicate_policy != "reject":
        fail(ErrorCode.INVALID_ORDER, "ordered unique extremum row required")
    for text in (meta.namespace, meta.source.source_id, meta.source.snapshot_id,
                 meta.source.mapping_version, meta.source.input_id):
        label(text)
    if meta.price_unit != config.price_unit:
        fail(ErrorCode.INVALID_UNIT, "extremum unit must equal the config unit")
    if meta.adjustment != config.adjustment:
        fail(ErrorCode.UNSUPPORTED_ADJUSTMENT, "extremum basis must equal the config basis")
    validate_batch(batch, required_fields=())
    if batch.row_count == 0:
        return _Side(role, batch)
    cols = {column.name: column.values for column in batch.columns}
    for name in ("instrument_id", "session_id", "fact_kind"):
        label(cols[name][0])
    if cols["instrument_id"][0] != entity.instrument_id or cols["session_id"][0] != entity.session_id:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "one actual requested entity required")
    if cols["fact_kind"][0] != kind:
        fail(ErrorCode.INVALID_SCHEMA, "extremum fact family mismatch for the role")
    _window_set(cols["reference_id"][0])
    if cols.get("text", (None,))[0] != meta.source.snapshot_id:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "extremum revision differs from snapshot")
    price = cast("int | None", cols.get("price", (None,))[0])
    num = cast("int | None", cols.get("factor_num", (None,))[0])
    den = cast("int | None", cols.get("factor_den", (None,))[0])
    if (num is None) != (den is None):
        fail(ErrorCode.INVALID_SCHEMA, "factor_num and factor_den are all-or-none")
    known = cast("int | None", cols.get("known_at_ns", (None,))[0])
    causal = known is not None and known <= config.availability.knowledge_cutoff_ns
    # A row that is not causal or not completely covered is never inspected beyond its structure.
    if causal and meta.coverage.complete:
        if price is not None:
            if num is None:
                fail(ErrorCode.INVALID_SCHEMA, "a priced extremum carries its window factors")
            if num != den:
                fail(ErrorCode.INCONSISTENT_IDENTITY, "a priced extremum must present a complete window")
        elif num is not None and den is not None and num > den:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "observed slots cannot exceed the required window length")
    return _Side(role, batch, cast("str | None", cols["reference_id"][0]), price, num, den, known,
                 cast("int | None", cols["effective_start_ns"][0]),
                 cast("int | None", cols.get("effective_end_ns", (None,))[0]))


def _first_status(reasons: set[Reason]) -> Status:
    first = next((reason for reason in _PRECEDENCE if reason in reasons), None)
    return Status.AVAILABLE if first is None else _STATUS.get(first, Status.MISSING_INPUT)


def compute_retracement_level(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None],
                              config: ConfigSpec, *, entity: EntityKey) -> FeatureResult:
    """Return the one `retracement.level` cell for the config's direction and ratio, exact then rounded once."""
    settings = decode_retracement_config(config)
    if type(entity) is not EntityKey or entity.session_id != config.session.session_id:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "exact target entity required")
    label(entity.instrument_id)
    label(entity.session_id)
    if type(batches) not in (tuple, list) or len(batches) != 2:
        fail(ErrorCode.INVALID_SCHEMA, "two fixed nullable slots prior_high, prior_low required")
    if any(batch is not None and (type(batch) is not CanonicalBatch or batch.kind != DataKind.REFERENCE)
           for batch in batches):
        fail(ErrorCode.INVALID_SCHEMA, "wrong extremum slot kind")
    present = [batch for batch in batches if batch is not None]
    if len({batch.metadata.source.input_id for batch in present}) != len(present):
        fail(ErrorCode.DUPLICATE, "distinct actual extremum input IDs required")
    sides = [_admit(role, kind, batch, config, entity) for role, kind, batch in zip(ROLES, FACT_KINDS, batches)]
    rows = [side for side in sides if side.reference_id is not None]
    if len({side.reference_id for side in rows}) > 1:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "both roles must carry one window set id")
    if len({side.factor_den for side in rows if side.factor_den is not None}) > 1:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "both roles must carry one required window length")

    reasons: set[Reason] = set()
    observed = 0
    coefficients: dict[str, int] = {}
    for side in sides:
        batch = side.batch
        if batch is None:
            reasons.add(Reason.ABSENT_INPUT)
        elif batch.row_count == 0:
            complete = batch.metadata.coverage.complete and batch.metadata.coverage.expected == 0
            reasons.add(Reason.ABSENT_INPUT if complete else Reason.GOVERNED_GAP)
        else:
            known = side.known_at_ns
            # Original knowledge is enforced identically in known_at and reconstruction availability modes.
            if known is None:
                reasons.add(Reason.UNKNOWN_AVAILABILITY)
            elif known > config.availability.knowledge_cutoff_ns:
                reasons.add(Reason.FUTURE_KNOWLEDGE)
            if not batch.metadata.coverage.complete:
                reasons.add(Reason.GOVERNED_GAP)
            if known is not None and known <= config.availability.knowledge_cutoff_ns and batch.metadata.coverage.complete:
                if side.price is None:
                    short = side.factor_num is not None and side.factor_den is not None and side.factor_num < side.factor_den
                    reasons.add(Reason.INSUFFICIENT_HISTORY if short else Reason.NULL_FIELD)
                elif side.price <= 0:
                    reasons.add(Reason.INELIGIBLE)
                else:
                    observed += 1
                    coefficients[side.role] = side.price
    value: float | None = None
    if not reasons:
        high, low = coefficients["prior_high"], coefficients["prior_low"]
        if high == low:
            reasons.add(Reason.ZERO_DENOMINATOR)
        elif high < low:
            reasons.add(Reason.INELIGIBLE)
        else:
            assert config.price_unit is not None
            spread = high - low
            denominator = settings.ratio_den * 10**config.price_unit.scale
            # Exact rational (H - rR or L + rR) over 10^scale, converted with one round-half-even rounding.
            if settings.direction == "from_high":
                value = (high*settings.ratio_den - settings.ratio_num*spread) / denominator
            else:
                value = (low*settings.ratio_den + settings.ratio_num*spread) / denominator
    status = _first_status(reasons)
    evidence: list[EvidenceRow] = []
    if value is not None:
        for side in sides:
            assert side.batch is not None and side.reference_id is not None and side.start_ns is not None
            if len(evidence) < settings.evidence_limit:
                evidence.append(EvidenceRow(entity, FEATURE_ID, side.batch.metadata.source.input_id,
                    side.reference_id, side.start_ns, side.known_at_ns, side.start_ns, side.end_ns))
    bindings = tuple(sorted((InputBinding(side.role, side.batch.kind, side.batch.metadata)
                             for side in sides if side.batch is not None), key=lambda binding: binding.role))
    metadata = ResultMetadata(config.session.namespace, entity.session_id, config.availability, config.digest,
                              bindings, "python-exact", __version__, evidence_limit=settings.evidence_limit)
    ordered = tuple(sorted(reasons, key=lambda reason: reason.value))
    return FeatureResult(
        (FeatureColumn(FEATURE_ID, RETRACEMENT_ALGORITHM, ValueType.FLOAT64, "currency/share", (entity,), (value,)),),
        (QualityRow(entity, FEATURE_ID, status, 2, observed, ordered),), metadata, tuple(evidence))
