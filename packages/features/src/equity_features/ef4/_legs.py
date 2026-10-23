"""Leg witness facts (`ef4.leg.start`, `ef4.leg.end`) shared by the EF4 relative excess and rate producers.

A leg is an exact price witness of one instrument: the actual witness time, the session whose price it is, the profile
of a start witness (`prior_close`, `window_start`, `regular_open`), a slot (`A` or `B`), the original record revision
(evidence only) and the instrument's retained corporate-action snapshot id. Pure, no I/O.
"""
from __future__ import annotations

from dataclasses import dataclass

from equity_feature_contracts import ErrorCode, EvidenceRow, EntityKey
from ..ef3._common import fail
from ._proj_common import RefRow, token

LEG_START = "ef4.leg.start"
LEG_END = "ef4.leg.end"
PROFILES = frozenset({"prior_close", "window_start", "regular_open"})
SLOTS = frozenset({"A", "B"})
LEG_KINDS = frozenset({LEG_START, LEG_END})


@dataclass(frozen=True)
class Leg:
    instrument: str
    kind: str
    session: str
    t: int
    price: int
    profile: str | None
    slot: str
    rev: str
    act: str
    known_at: int | None
    reference_id: str
    row: int

    @property
    def is_start(self) -> bool:
        return self.kind == LEG_START

    def evidence(self, entity: EntityKey, feature: str, input_id: str, row_id: str) -> EvidenceRow:
        return EvidenceRow(entity, feature, input_id, row_id, self.t, self.known_at, self.t, None, "consumed", None,
                           "ordinary")


def _parse_text(kind: str, text: object) -> dict[str, str]:
    """Closed ordered `key=value;...` grammar: start `profile[;slot];rev;act`, end `[slot;]rev;act`."""
    if type(text) is not str:
        fail(ErrorCode.INVALID_SCHEMA, "a leg fact carries its profile, slot, revision and action text")
    fields: list[tuple[str, str]] = []
    for part in text.split(";"):
        key, separator, value = part.partition("=")
        if not separator:
            fail(ErrorCode.INVALID_SCHEMA, "closed key=value leg text grammar required")
        fields.append((key, token(value)))
    keys = tuple(key for key, _ in fields)
    lead = ("profile",) if kind == LEG_START else ()
    if keys not in (lead + ("rev", "act"), lead + ("slot", "rev", "act")):
        fail(ErrorCode.INVALID_SCHEMA, "closed ordered leg text grammar required")
    return dict(fields)


def parse_legs(rows: list[RefRow], input_profiles: frozenset[str], slots: frozenset[str]) -> list[Leg]:
    """Wire admission of the leg facts: no end time, positive price, closed text grammar with closed vocabularies."""
    legs: list[Leg] = []
    for row in rows:
        if row.end is not None:
            fail(ErrorCode.INVALID_SCHEMA, "a leg witness is a point in time (no effective end)")
        if row.price is None or row.price <= 0:
            fail(ErrorCode.INVALID_SCHEMA, "a leg carries a positive price coefficient")
        fields = _parse_text(row.kind, row.text)
        profile = fields.get("profile")
        if profile is not None and profile not in input_profiles:
            fail(ErrorCode.INVALID_SCHEMA, "unknown or unsupported start profile")
        slot = fields.get("slot", "A")
        if slot not in slots:
            fail(ErrorCode.INVALID_SCHEMA, "unknown or unsupported slot")
        legs.append(Leg(row.instrument, row.kind, row.session, row.start, row.price, profile, slot, fields["rev"],
                        fields["act"], row.known_at, row.reference_id, row.row))
    return legs


def check_legs(legs: list[Leg], declared: frozenset[str]) -> None:
    """Identity stage: only declared instruments, at most one start per (instrument, profile, slot) and end per slot."""
    seen: set[tuple[str, str, str | None, str]] = set()
    for leg in legs:
        if leg.instrument not in declared:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "leg fact of an undeclared instrument")
    for leg in legs:
        key = (leg.instrument, leg.kind, leg.profile, leg.slot)
        if key in seen:
            fail(ErrorCode.DUPLICATE, "two leg facts with one instrument, kind, profile and slot")
        seen.add(key)


def check_leg_bounds(legs: list[Leg]) -> None:
    """Data stage: a start witness must precede the end witness of the same instrument and slot."""
    ends = {(leg.instrument, leg.slot): leg for leg in legs if not leg.is_start}
    for leg in legs:
        end = ends.get((leg.instrument, leg.slot))
        if leg.is_start and end is not None and leg.t >= end.t:
            fail(ErrorCode.BOUNDS, "a leg start witness must precede its end witness")
