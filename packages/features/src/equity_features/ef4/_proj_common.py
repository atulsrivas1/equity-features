"""Shared admission, quality and result helpers of the EF4 statistical projection producers; pure, no I/O.

Roles are fixed nullable slots. Market roles (a close-only BAR on the daily governed grid, or the BAR delivery of one
reset epoch) are admitted slot by slot; REFERENCE roles carry the `ef4.*` facts (leg witnesses, sector membership and
tape window aggregates). A fact or row is KNOWN iff its original `known_at_ns` is non-null and at most the knowledge
cutoff, identically in `known_at` and reconstruction availability modes. No clock, I/O, storage, default window,
tolerance, age, adjacency or benchmark.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import re
from typing import Any

from equity_feature_contracts import (
    CanonicalBatch, ConfigSpec, DataKind, EntityKey, ErrorCode, EvidenceRow, FeatureColumn, FeatureResult,
    InputBinding, QualityRow, Reason, ResultMetadata, Status, ValueType, validate_batch,
)
from equity_features import __version__
from ..ef3._common import fail, integer, label
from ..ef3._robust_common import check_policy, check_reference_id, first_status, ordered
from ..ef3._stats import to_float

I64_MAX = 2**63 - 1
DEC128_LIMIT = 10**38
MAX_ROWS = 4096
MAX_NS = 2**62
_DECIMAL = re.compile("0|[1-9][0-9]*", re.ASCII)
_TOKEN = re.compile("[\x21-\x3a\x3c\x3e-\x7e]{1,128}", re.ASCII)

__all__ = ["Cell", "DEC128_LIMIT", "I64_MAX", "MAX_NS", "MAX_ROWS", "RefRow", "canonical_decimal", "check_features",
           "check_meta", "check_policy", "finish", "first_status", "fraction_float", "integer", "knowledge_reason",
           "label", "ordered", "reference_rows", "token", "validate_reference"]


def check_features(features: object, allowed: tuple[str, ...]) -> tuple[str, ...]:
    """Nonempty unique selected feature ids (sorted); an id outside the producer's outputs is `UNKNOWN_FEATURE`."""
    if (type(features) is not tuple or not features or any(type(f) is not str for f in features)
            or len(set(features)) != len(features)):
        fail(ErrorCode.INVALID_SCHEMA, "nonempty unique selected feature IDs required")
    if any(f not in allowed for f in features):
        fail(ErrorCode.UNKNOWN_FEATURE, "unknown selected feature")
    return tuple(sorted(features))


def token(value: object) -> str:
    """Printable ASCII text token without ';' or '=' (the fact text grammar separators)."""
    if type(value) is not str or _TOKEN.fullmatch(value) is None:
        fail(ErrorCode.INVALID_SCHEMA, "nonblank printable fact text token required")
    return value


def canonical_decimal(value: object, limit_exclusive: int) -> int:
    """Canonical non-negative decimal integer text strictly below the limit (wire: grammar, then range)."""
    if type(value) is not str or _DECIMAL.fullmatch(value) is None or len(value) > 64:
        fail(ErrorCode.INVALID_SCHEMA, "canonical non-negative decimal integer text required")
    number = int(value)
    if number >= limit_exclusive:
        fail(ErrorCode.OVERFLOW, "operand outside its declared integer range")
    return number


def fraction_float(value: Fraction) -> float:
    """One correctly rounded binary64 of an exact rational; an exact zero is the positive zero."""
    return to_float(value)


def knowledge_reason(known_at_ns: int | None, knowledge_cutoff_ns: int) -> Reason | None:
    """Original knowledge in every mode: null is unknown, later than K is future (equal to K is known)."""
    if known_at_ns is None:
        return Reason.UNKNOWN_AVAILABILITY
    if known_at_ns > knowledge_cutoff_ns:
        return Reason.FUTURE_KNOWLEDGE
    return None


@dataclass(frozen=True)
class RefRow:
    """One admitted REFERENCE fact row (wire level only; semantics are the producer's)."""

    kind: str
    instrument: str
    session: str
    reference_id: str
    start: int
    end: int | None
    known_at: int | None
    price: int | None
    text: str | None
    row: int


def reference_rows(batch: object, kinds: frozenset[str]) -> list[RefRow]:
    """Wire admission of a REFERENCE batch: kind, row bound, fact kind, reference grammar, no rational factor."""
    if type(batch) is not CanonicalBatch:
        fail(ErrorCode.INVALID_SCHEMA, "an actual canonical batch is required for a fact role")
    if batch.row_count > MAX_ROWS:
        fail(ErrorCode.BOUNDS, "at most 4096 rows per role")
    validate_batch(batch, required_fields=())  # shared tier first; the slot-kind check follows it
    if batch.kind != DataKind.REFERENCE:
        fail(ErrorCode.INVALID_SCHEMA, "a REFERENCE batch is required for a fact role")
    cols = {c.name: c.values for c in batch.columns}
    rows: list[RefRow] = []
    for i in range(batch.row_count):
        kind = cols["fact_kind"][i]
        if kind not in kinds:
            fail(ErrorCode.INVALID_SCHEMA, "fact kind of another role or an unknown label")
        check_reference_id(cols["reference_id"][i])
        for name in ("factor_num", "factor_den"):
            if name in cols and cols[name][i] is not None:
                fail(ErrorCode.INVALID_SCHEMA, "EF4 facts carry no rational factor")
        rows.append(RefRow(
            kind, label(cols["instrument_id"][i], ErrorCode.INVALID_SCHEMA),
            label(cols["session_id"][i], ErrorCode.INVALID_SCHEMA), cols["reference_id"][i],
            cols["effective_start_ns"][i], cols["effective_end_ns"][i] if "effective_end_ns" in cols else None,
            cols["known_at_ns"][i] if "known_at_ns" in cols else None,
            cols["price"][i] if "price" in cols else None, cols["text"][i] if "text" in cols else None, i))
    return rows


def validate_reference(batch: CanonicalBatch) -> None:
    """Shared validator stage: duplicates, order and effective bounds of the REFERENCE rows."""
    validate_batch(batch, required_fields=())


def check_meta(batch: CanonicalBatch, config: ConfigSpec, *, unit: bool, adjustment: bool) -> None:
    """Metadata discipline of one admitted batch: source labels, declared order, unit, basis, namespace, coverage."""
    meta = batch.metadata
    for text in (meta.source.source_id, meta.source.snapshot_id, meta.source.mapping_version, meta.source.input_id):
        label(text, ErrorCode.INVALID_SCHEMA)
    if meta.ordering != "declared" or meta.duplicate_policy != "reject":
        fail(ErrorCode.INVALID_ORDER, "declared order and rejected duplicates required")
    if unit and meta.price_unit != config.price_unit:
        fail(ErrorCode.INVALID_UNIT, "input currency/scale differs from the config unit")
    if adjustment and meta.adjustment != config.adjustment:
        fail(ErrorCode.UNSUPPORTED_ADJUSTMENT, "input action basis differs from the config basis")
    if meta.namespace != config.session.namespace:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "input namespace differs from the target session")
    if meta.coverage.observed != batch.row_count:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "aggregate observed coverage differs from actual rows")
    if meta.scope is not None and meta.sampling != "none":
        fail(ErrorCode.INVALID_SCHEMA, "nonquote sampling required")


@dataclass
class Cell:
    """One selected output: its value, causes, counts and the consumed witnesses (built for available outputs)."""

    value: Any = None
    reasons: set[Reason] | None = None
    expected: int = 0
    observed: int = 0
    witnesses: list[EvidenceRow] | None = None


def finish(config: ConfigSpec, entity: EntityKey, algorithm: str, selected: tuple[str, ...],
           meta: dict[str, tuple[ValueType, str]], cells: dict[str, Cell], bindings: tuple[InputBinding, ...],
           limit: int) -> FeatureResult:
    """Assemble the result: a value exactly when no cause applies, causes in lexical order, result-wide evidence."""
    columns: list[FeatureColumn] = []
    quality: list[QualityRow] = []
    evidence: list[EvidenceRow] = []
    for feature in selected:
        cell = cells[feature]
        reasons = cell.reasons or set()
        value = None if reasons else cell.value
        status = Status.AVAILABLE if value is not None else first_status(reasons)
        dtype, unit = meta[feature]
        columns.append(FeatureColumn(feature, algorithm, dtype, unit, (entity,), (value,)))
        quality.append(QualityRow(entity, feature, status, cell.expected, cell.observed, ordered(reasons)))
        if value is not None:
            for row in cell.witnesses or ():
                if len(evidence) < limit:
                    evidence.append(row)
    metadata = ResultMetadata(config.session.namespace, entity.session_id, config.availability, config.digest,
                              bindings, "python-exact", __version__, limit)
    return FeatureResult(tuple(columns), tuple(quality), metadata, tuple(evidence))
