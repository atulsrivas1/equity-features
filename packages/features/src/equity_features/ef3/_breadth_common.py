"""Shared admission, three-valued logic and evidence helpers of the EF3 breadth and adaptive volume producers.

All roles are fixed nullable REFERENCE slots. A role batch holds one fact row per member (or per observation); a fact is
*resolved* when its row exists, is known (`known_at_ns` non-null and at most the knowledge cutoff), is an event before the
market cutoff and carries its value. Predicates are three valued (true, false, unknown); a known false decides without the
other inputs. No clock, I/O, storage, default or state across calls.
"""
from __future__ import annotations

from base64 import urlsafe_b64encode
from dataclasses import dataclass
from typing import Any

from equity_feature_contracts import (
    CanonicalBatch, ConfigSpec, EntityKey, ErrorCode, EvidenceRow, Reason, validate_batch,
)
from ._common import fail, label
from ._robust_common import _check_meta, _decode_part, columns_of

MAX_ROWS = 4096
NO_REASONS: frozenset[Reason] = frozenset()
# One member's three-valued result: (True | False | None, reasons of the unresolved inputs the predicate needed).
Tri = tuple[bool | None, frozenset[Reason]]
# Price-column modes of a fact kind (see `check_price`).
NONE_MODE, ANY_MODE, POSITIVE_MODE, NONNEG_MODE, VWAP_MODE, RATE_MODE = (
    "none", "any", "positive", "nonneg", "vwap", "rate")


def encode_part(text: str) -> str:
    """Component B(text) of a reference id: URL-safe base64 without padding."""
    return urlsafe_b64encode(text.encode("utf-8")).rstrip(b"=").decode("ascii")


def build_reference_id(prefix: str, shape: tuple[str, ...], values: tuple[str | int, ...]) -> str:
    """Reference id `prefix:part:...`; shape `t` is B(text), `dN` an N digit zero padded decimal."""
    parts = [prefix]
    for kind, value in zip(shape, values, strict=True):
        parts.append(encode_part(str(value)) if kind == "t" else str(value).zfill(int(kind[1:])))
    return ":".join(parts)


def parse_reference(reference_id: object, prefix: str, shape: tuple[str, ...]) -> tuple[str, ...]:
    """Closed reference grammar; returns the decoded components (decimal components stay digit strings)."""
    if type(reference_id) is not str or len(reference_id) > 256:
        fail(ErrorCode.INVALID_SCHEMA, "bounded reference identity required")
    parts = reference_id.split(":")
    if len(parts) != len(shape) + 1 or parts[0] != prefix:
        fail(ErrorCode.INVALID_SCHEMA, f"closed {prefix} reference grammar required")
    out: list[str] = []
    for part, kind in zip(parts[1:], shape):
        if kind == "t":
            out.append(_decode_part(part))
        elif len(part) != int(kind[1:]) or not part.isascii() or not part.isdigit():
            fail(ErrorCode.INVALID_SCHEMA, f"{prefix} reference needs a {kind[1:]} digit component")
        else:
            out.append(part)
    return tuple(out)


@dataclass(frozen=True)
class FactRow:
    """One delivered fact; `valued` is false for the state kinds that carry no value."""

    kind: str
    start: int
    end: int | None
    known_at: int | None
    price: int | None
    num: int | None
    den: int | None
    text: str | None
    valued: bool


@dataclass(frozen=True)
class Role:
    """An admitted role: its batch, coverage declaration and rows keyed by member (instrument)."""

    name: str
    batch: CanonicalBatch
    complete: bool
    rows: dict[str, FactRow]

    @property
    def input_id(self) -> str:
        return self.batch.metadata.source.input_id


def check_price(mode: str, price: int | None, num: int | None, den: int | None) -> None:
    """Price-column discipline of one fact kind (all refusals are structural)."""
    if mode == NONE_MODE:
        if price is not None or num is not None or den is not None:
            fail(ErrorCode.INVALID_SCHEMA, "this fact kind carries no price or factor")
    elif mode == VWAP_MODE:
        if num is None or den is None:
            fail(ErrorCode.INVALID_SCHEMA, "a VWAP fact carries both rational factors")
        if price is not None and price <= 0:
            fail(ErrorCode.INVALID_SCHEMA, "a VWAP notional coefficient is positive")
    elif mode == RATE_MODE:
        if (num is None) != (den is None):
            fail(ErrorCode.INVALID_SCHEMA, "the rate factors are both null or both present")
        if price is not None and price < 0:
            fail(ErrorCode.BOUNDS, "a negative rate coefficient is refused")
    else:
        if num is not None or den is not None:
            fail(ErrorCode.INVALID_SCHEMA, "this fact kind carries no rational factor")
        if mode == POSITIVE_MODE and price is not None and price <= 0:
            fail(ErrorCode.INVALID_SCHEMA, "a positive price coefficient is required")
        if mode == NONNEG_MODE and price is not None and price < 0:
            fail(ErrorCode.BOUNDS, "a negative quantity is refused")


def open_batch(batch: CanonicalBatch, config: ConfigSpec) -> dict[str, tuple[Any, ...]]:
    """Row bound, shared validator, metadata and the one shared PriceUnit (every role batch carries it)."""
    if batch.row_count > MAX_ROWS:
        fail(ErrorCode.BOUNDS, "at most 4096 rows per role")
    validate_batch(batch, required_fields=())
    _check_meta(batch, config)
    if batch.metadata.price_unit != config.price_unit:
        fail(ErrorCode.INVALID_UNIT, "every role batch carries the config PriceUnit")
    return columns_of(batch)


def fact_rows(batch: CanonicalBatch, config: ConfigSpec, kinds: dict[str, str], prefix: str,
              shape: tuple[str, ...]) -> list[tuple[str, FactRow, tuple[str, ...]]]:
    """Admitted rows `(instrument, row, reference components)` in batch order: kind, grammar, session, price mode."""
    cols = open_batch(batch, config)
    result: list[tuple[str, FactRow, tuple[str, ...]]] = []
    for i in range(batch.row_count):
        kind = cols["fact_kind"][i]
        if kind not in kinds:
            fail(ErrorCode.INVALID_SCHEMA, "fact kind of another role")
        parts = parse_reference(cols["reference_id"][i], prefix, shape)
        instrument = label(cols["instrument_id"][i], ErrorCode.INVALID_SCHEMA)
        if cols["session_id"][i] != config.session.session_id:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "fact belongs to the target session")
        price = cols["price"][i] if "price" in cols else None
        num = cols["factor_num"][i] if "factor_num" in cols else None
        den = cols["factor_den"][i] if "factor_den" in cols else None
        check_price(kinds[kind], price, num, den)
        row = FactRow(kind, cols["effective_start_ns"][i],
                      cols["effective_end_ns"][i] if "effective_end_ns" in cols else None,
                      cols["known_at_ns"][i] if "known_at_ns" in cols else None, price, num, den,
                      cols["text"][i] if "text" in cols else None, kinds[kind] != NONE_MODE)
        result.append((instrument, row, parts))
    return result


def resolve(role: Role | None, member: str, cutoff: int, knowledge: int) -> tuple[FactRow | None, frozenset[Reason]]:
    """The fact of one member and the causes (empty when resolved) that make it unusable at this cutoff pair."""
    if role is None:
        return None, frozenset({Reason.ABSENT_INPUT})
    row = role.rows.get(member)
    reasons: set[Reason] = set()
    if row is None:
        reasons.add(Reason.ABSENT_INPUT)
        if not role.complete:
            reasons.add(Reason.GOVERNED_GAP)
        return None, frozenset(reasons)
    if row.known_at is None:
        reasons.add(Reason.UNKNOWN_AVAILABILITY)
    elif row.known_at > knowledge:
        reasons.add(Reason.FUTURE_KNOWLEDGE)
    if not role.complete:
        reasons.add(Reason.GOVERNED_GAP)
    if row.start >= cutoff:
        reasons.add(Reason.FUTURE_MARKET)
    if row.valued and row.price is None:
        reasons.add(Reason.NULL_FIELD)
    return row, frozenset(reasons)


def tri_and(*items: Tri) -> Tri:
    """Kleene conjunction: a known false decides; unknown keeps the reasons of its unresolved operands."""
    if any(value is False for value, _ in items):
        return False, NO_REASONS
    if all(value is True for value, _ in items):
        return True, NO_REASONS
    reasons: frozenset[Reason] = NO_REASONS
    for value, why in items:
        if value is None:
            reasons |= why
    return None, reasons


def member_evidence(entity: EntityKey, feature: str, role: Role, member: str) -> EvidenceRow:
    """Deciding fact row of one member (ordinary boundary, as the other EF3 reference witnesses)."""
    row = role.rows[member]
    return EvidenceRow(entity, feature, role.input_id, f"member:{member}", row.start, row.known_at, row.start,
                       row.end, "consumed", None, "ordinary")
