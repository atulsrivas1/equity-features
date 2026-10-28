"""Shared EF4 admission, knowledge, coverage, quality and result assembly of the quote dynamics and VWAP path producers.

Both producers read the declared half-open interval `[S, E)` from one `ef4.interval.bounds` fact. Statistics run on
exact integers and `Fraction`s; the price coefficient is divided by `10^scale` only when a value is published, and each
published float64 is one correctly rounded rational. No clock, I/O, storage, default or state across calls.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, cast

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, CanonicalBatch, ConfigSpec, DataKind, EntityKey, ErrorCode, EvidenceRow,
    FeatureColumn, FeatureResult, InputBinding, Parameter, PriceUnit, QualityRow, Reason, ResultMetadata,
    SessionSpec, Status, ValueType, WindowSpec, validate_batch,
)
from equity_features import __version__
from ..ef3._common import fail, label
from ..ef3._robust_common import check_reference_id, columns_of, first_status, ordered

BOUNDS_KIND = "ef4.interval.bounds"
EDGE_KIND = "ef4.window.edge"
PROOF_KIND = "ef4.series.proof"
SEC = 10**9
SAMPLINGS = ("trade_snapshot", "continuous")
SOURCES = ("trade", "bar", "prepared_window")


def divide(num: int, den: int) -> float:
    """One correctly rounded binary64 of an exact integer ratio (exact zero is the positive zero)."""
    try:
        return num / den
    except OverflowError:
        fail(ErrorCode.OVERFLOW, "statistic outside binary64")


def knowledge_reason(known_at: int | None, knowledge_cutoff: int) -> Reason | None:
    """Original knowledge in every availability mode: null is unknown, after K is future, K itself is known."""
    if known_at is None:
        return Reason.UNKNOWN_AVAILABILITY
    if known_at > knowledge_cutoff:
        return Reason.FUTURE_KNOWLEDGE
    return None


def make_config(identity: str, algorithm: str, params: tuple[Parameter, ...], session: SessionSpec,
                availability: AvailabilitySpec, adjustment: AdjustmentSpec, price_unit: PriceUnit) -> ConfigSpec:
    """Final ConfigSpec: the target session, an explicit unit and one shared adjustment basis."""
    if (type(session) is not SessionSpec or type(availability) is not AvailabilitySpec
            or type(adjustment) is not AdjustmentSpec):
        fail(ErrorCode.INVALID_CONFIG, "concrete session/timing/action required")
    if type(price_unit) is not PriceUnit:
        fail(ErrorCode.INVALID_UNIT, "an explicit PriceUnit is required")
    for value in (adjustment.policy_version, adjustment.action_snapshot, adjustment.anchor, price_unit.currency):
        label(value)
    if availability.reconstruction_reason is not None:
        label(availability.reconstruction_reason)
    return ConfigSpec(identity, algorithm, params, session,
                      WindowSpec(1, session.session_id, (session.session_id,), "prior_only"),
                      availability, adjustment, price_unit)


def parameter_values(config: ConfigSpec, identity: str, algorithm: str, policy: str, features: tuple[str, ...] | None,
                     allowed_features: tuple[str, ...]) -> tuple[dict[str, Any], tuple[str, ...]]:
    """Tier one of the refusal precedence: version, then selected feature, then (by the caller) the parameters."""
    if type(config) is not ConfigSpec:
        fail(ErrorCode.INVALID_CONFIG, "concrete ConfigSpec required")
    if config.algorithm_version != algorithm:
        fail(ErrorCode.INCOMPATIBLE_VERSION, "algorithm version differs")
    if config.identity != identity:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "not this producer's configuration")
    values: dict[str, Any] = {p.name: p.value for p in config.parameters}
    version = values.get("policy_version")
    if type(version) is str and version != policy:
        fail(ErrorCode.INCOMPATIBLE_VERSION, "unsupported policy label")
    selected: tuple[str, ...] = ()
    if features is not None:
        if (type(features) is not tuple or not 1 <= len(features) <= len(allowed_features)
                or any(type(f) is not str for f in features) or len(set(features)) != len(features)):
            fail(ErrorCode.INVALID_SCHEMA, "nonempty unique selected feature IDs required")
        if any(f not in allowed_features for f in features):
            fail(ErrorCode.UNKNOWN_FEATURE, "unknown selected feature")
        selected = tuple(sorted(features))
    if config.price_unit is None:
        fail(ErrorCode.INVALID_UNIT, "an explicit PriceUnit is required")
    return values, selected


def check_closed(values: dict[str, Any], required: frozenset[str], optional: frozenset[str]) -> None:
    if not required <= set(values) or not set(values) <= required | optional:
        fail(ErrorCode.INVALID_CONFIG, "closed producer parameters required (there are no defaults)")


def check_limit(value: object) -> int:
    if type(value) is not int or not 0 <= value <= 10000:
        fail(ErrorCode.INVALID_CONFIG, "exact integer evidence_limit in 0..10000 required")
    return value


# ----------------------------------------------------------------------------------------------- batch admission
def check_roles(batches: object, count: int) -> list[CanonicalBatch | None]:
    """The fixed nullable role slots (types and distinct actual input ids); slot kinds follow the shared validator."""
    candidate = cast("tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None]", batches)
    if type(candidate) not in (tuple, list) or len(candidate) != count:
        fail(ErrorCode.INVALID_SCHEMA, "the fixed nullable role slots are required")
    slots: list[CanonicalBatch | None] = list(candidate)
    for batch in slots:
        if batch is not None and type(batch) is not CanonicalBatch:
            fail(ErrorCode.INVALID_SCHEMA, "wrong slot kind")
    present = [b for b in slots if b is not None]
    if len({b.metadata.source.input_id for b in present}) != len(present):
        fail(ErrorCode.DUPLICATE, "distinct actual role input IDs required")
    return slots


def check_kinds(slots: list[CanonicalBatch | None], kinds: tuple[DataKind, ...]) -> None:
    """Tier four: a batch of another kind in a role (after the shared validator, which accepts every kind)."""
    for batch, kind in zip(slots, kinds):
        if batch is not None and batch.kind != kind:
            fail(ErrorCode.INVALID_SCHEMA, "wrong slot kind")


def shared_validation(batches: list[CanonicalBatch | None], order: tuple[int, ...], config: ConfigSpec) -> None:
    """Tier three: the shared validator per delivered batch in the stated role order (references, then market)."""
    for index in order:
        batch = batches[index]
        if batch is not None:
            validate_batch(batch, availability=config.availability, required_fields=())


def check_meta(batch: CanonicalBatch, config: ConfigSpec, *, market: bool) -> None:
    """Unit, basis, namespace and declaration discipline of one admitted batch."""
    meta = batch.metadata
    if (market or meta.price_unit is not None) and meta.price_unit != config.price_unit:
        fail(ErrorCode.INVALID_UNIT, "input currency/scale differs from the config unit")
    if meta.adjustment != config.adjustment:
        fail(ErrorCode.UNSUPPORTED_ADJUSTMENT, "input action basis differs from the config basis")
    if meta.namespace != config.session.namespace:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "input namespace differs from the target session")
    if meta.ordering != "declared" or meta.duplicate_policy != "reject":
        fail(ErrorCode.INVALID_ORDER, "declared order and rejected duplicates required")
    if meta.coverage.observed != batch.row_count:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "aggregate observed coverage differs from actual rows")


@dataclass(frozen=True)
class Fact:
    ref: str
    start: int
    end: int | None
    known_at: int | None
    text: str | None


def admit_facts(batch: CanonicalBatch, config: ConfigSpec, entity: EntityKey, kind: str, *,
                end_null: bool) -> list[Fact]:
    """Closed reference facts of one role: kind, grammar, identity and the null price columns."""
    check_meta(batch, config, market=False)
    cols = columns_of(batch)
    facts: list[Fact] = []
    for i in range(batch.row_count):
        if cols["fact_kind"][i] != kind:
            fail(ErrorCode.INVALID_SCHEMA, "fact kind of another role")
        check_reference_id(cols["reference_id"][i])
        for name in ("price", "factor_num", "factor_den"):
            if name in cols and cols[name][i] is not None:
                fail(ErrorCode.INVALID_SCHEMA, "EF4 facts carry no price or factor")
        if cols["instrument_id"][i] != entity.instrument_id or cols["session_id"][i] != config.session.session_id:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "fact identity differs from the target entity and session")
        end = cols["effective_end_ns"][i] if "effective_end_ns" in cols else None
        if (end is None) != end_null:
            fail(ErrorCode.INVALID_SCHEMA, "effective end presence differs from the fact schema")
        facts.append(Fact(cols["reference_id"][i], cols["effective_start_ns"][i], end,
                          cols["known_at_ns"][i] if "known_at_ns" in cols else None,
                          cols["text"][i] if "text" in cols else None))
    return facts


@dataclass(frozen=True)
class Interval:
    start: int
    end: int
    known_at: int | None


def admit_bounds(batch: CanonicalBatch | None, config: ConfigSpec, entity: EntityKey) -> Interval:
    """Exactly one `ef4.interval.bounds` fact whose text is the batch snapshot id."""
    if batch is None:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "exactly one interval bounds fact is required")
    facts = admit_facts(batch, config, entity, BOUNDS_KIND, end_null=False)
    if len(facts) != 1:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "exactly one interval bounds fact is required")
    fact = facts[0]
    if fact.text != batch.metadata.source.snapshot_id:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "interval bounds text differs from the batch snapshot")
    assert fact.end is not None
    return Interval(fact.start, fact.end, fact.known_at)


def declared_coverage(batch: CanonicalBatch, start: int, end: int) -> str:
    """`complete`, `incomplete`, or `undeclared` (no declaration; only a batch with zero rows, which the caller reads as
    absent_input). An undeclared batch that delivers rows is refused INVALID_SCHEMA (E2, no fail-open)."""
    meta = batch.metadata
    entries = meta.interval_coverage
    if entries:
        if len(entries) != 1 or (entries[0].start_ns, entries[0].end_ns) != (start, end):
            fail(ErrorCode.INCONSISTENT_IDENTITY, "coverage entry differs from the declared interval")
        if entries[0].coverage.observed != batch.row_count:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "interval observed coverage differs from actual rows")
        return "complete" if entries[0].coverage.complete else "incomplete"
    if meta.coverage.complete:
        return "complete"
    if meta.coverage.expected is not None:
        return "incomplete"
    if batch.row_count:
        fail(ErrorCode.INVALID_SCHEMA, "coverage not declared")  # fail closed: rows without a declaration are never complete
    return "undeclared"


# ------------------------------------------------------------------------------------------------ result assembly
@dataclass(frozen=True)
class Witness:
    input_id: str
    row_id: str
    event_ns: int
    known_at: int | None
    start: int | None = None
    end: int | None = None
    boundary: str = "ordinary"


@dataclass
class Out:
    value: Fraction | int | None
    reasons: frozenset[Reason]
    expected: int
    observed: int
    witnesses: list[Witness] = field(default_factory=list)


def unavailable(reasons: set[Reason] | frozenset[Reason], expected: int, observed: int) -> Out:
    return Out(None, frozenset(reasons), expected, observed)


def assemble(config: ConfigSpec, entity: EntityKey, selected: tuple[str, ...], outs: dict[str, Out],
             meta: dict[str, tuple[ValueType, str]], algorithm: str, limit: int,
             bindings: tuple[InputBinding, ...]) -> FeatureResult:
    columns: list[FeatureColumn] = []
    quality: list[QualityRow] = []
    evidence: list[EvidenceRow] = []
    for feature in selected:
        out = outs[feature]
        dtype, unit = meta[feature]
        published: float | int | None = None
        if out.value is not None:
            if dtype == ValueType.INT64:
                published = int(out.value)
            else:
                value = Fraction(out.value)
                published = divide(value.numerator, value.denominator)
        columns.append(FeatureColumn(feature, algorithm, dtype, unit, (entity,), (published,)))
        status = Status.AVAILABLE if out.value is not None else first_status(out.reasons)
        quality.append(QualityRow(entity, feature, status, out.expected, out.observed,
                                  () if out.value is not None else ordered(out.reasons)))
        if out.value is not None:
            for w in out.witnesses[:limit]:
                evidence.append(EvidenceRow(entity, feature, w.input_id, w.row_id, w.event_ns, w.known_at, w.start,
                                            w.end, "consumed", None, w.boundary))
    evidence = evidence[:limit]
    metadata = ResultMetadata(config.session.namespace, entity.session_id, config.availability, config.digest,
                              bindings, "python-exact", __version__, limit)
    return FeatureResult(tuple(columns), tuple(quality), metadata, tuple(evidence))


def bindings_of(roles: tuple[tuple[str, CanonicalBatch | None], ...]) -> tuple[InputBinding, ...]:
    return tuple(InputBinding(role, b.kind, b.metadata) for role, b in roles if b is not None)
