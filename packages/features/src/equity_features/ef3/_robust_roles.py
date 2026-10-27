"""Admission of the remaining EF3 robust roles: declared population, cohort values, bucket grid and bars."""
from __future__ import annotations

from dataclasses import dataclass

from equity_feature_contracts import CanonicalBatch, ConfigSpec, DataKind, EntityKey, ErrorCode, validate_batch
from ._common import fail, label
from ._robust_common import (
    EDGE_KIND, MAX_EDGES, POPULATION_KIND, Fact, SessionGrid, _check_meta, _coverage_map, admit_market,
    check_reference_id, columns_of,
)


@dataclass(frozen=True)
class Population:
    input_id: str
    members: tuple[str, ...]
    known_at: tuple[int | None, ...] = ()


def admit_population(batch: CanonicalBatch, config: ConfigSpec, entity: EntityKey) -> Population:
    """Declared members in declaration order (the order of the role); the target must be a member."""
    validate_batch(batch, required_fields=())
    _check_meta(batch, config)
    cols = columns_of(batch)
    members: list[str] = []
    known: list[int | None] = []
    reference: str | None = None
    session = config.session
    for row in range(batch.row_count):
        if cols["fact_kind"][row] != POPULATION_KIND:
            fail(ErrorCode.INVALID_SCHEMA, "unknown fact kind for the population role")
        check_reference_id(cols["reference_id"][row])
        for name in ("price", "factor_num", "factor_den"):
            if name in cols and cols[name][row] is not None:
                fail(ErrorCode.INVALID_SCHEMA, "EF3 facts carry no price or factor")
        if cols["session_id"][row] != session.session_id:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "population facts belong to the target session")
        end = cols["effective_end_ns"][row] if "effective_end_ns" in cols else None
        if (cols["effective_start_ns"][row], end) != (session.open_ns, session.close_ns):
            fail(ErrorCode.INCONSISTENT_IDENTITY, "population effective bounds differ from the target session")
        if "text" not in cols or cols["text"][row] != batch.metadata.source.snapshot_id:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "population revision differs from the snapshot")
        if reference is not None and cols["reference_id"][row] != reference:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "one population id required across the role")
        reference = cols["reference_id"][row]
        members.append(label(cols["instrument_id"][row], ErrorCode.INVALID_SCHEMA))
        known.append(cols["known_at_ns"][row] if "known_at_ns" in cols else None)
    if entity.instrument_id not in members:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "the target instrument is not a declared population member")
    return Population(batch.metadata.source.input_id, tuple(members), tuple(known))


def admit_cohort(batch: CanonicalBatch, config: ConfigSpec, population: Population, field: str) -> dict[str, Fact]:
    """One daily row per member for the target session; returns the per-member facts."""
    cols = admit_market(batch, DataKind.DAILY, config)
    input_id = batch.metadata.source.input_id
    session = config.session
    start, end = session.open_ns, session.close_ns
    rows: dict[str, int] = {}
    declared = set(population.members)
    for row in range(batch.row_count):
        member = cols["instrument_id"][row]
        if member not in declared:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "cohort value row for an undeclared member")
        if cols["session_id"][row] != session.session_id:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "cohort value row outside the target session")
        if (cols["start_ns"][row], cols["end_ns"][row]) != (start, end):
            fail(ErrorCode.INCONSISTENT_IDENTITY, "cohort value row differs from the target session bounds")
        rows[f"member:{member}"] = row
    declared_keys = {f"member:{m}" for m in population.members}
    coverage = _coverage_map(batch, lambda name: (start, end) if name in declared_keys else None, rows)
    facts: dict[str, Fact] = {}
    for member in population.members:
        key = f"member:{member}"
        row_index = rows.get(key)
        if row_index is None:
            facts[member] = Fact(input_id, None, coverage.get(key), False, None, None, start, end)
        else:
            facts[member] = Fact(input_id, row_index, coverage.get(key), field in cols,
                                 cols[field][row_index] if field in cols else None,
                                 cols["known_at_ns"][row_index] if "known_at_ns" in cols else None, start, end)
    return facts


@dataclass(frozen=True)
class Edges:
    offsets: tuple[int, ...]
    known_at: tuple[int | None, ...]


def admit_edges(batch: CanonicalBatch, config: ConfigSpec, entity: EntityKey, grid_version: str) -> Edges:
    """Bucket edge offsets from the actual open: first edge 0, strictly increasing, 2..4097 edges; the original
    `known_at` of each edge travels with it so the producer can gate it."""
    validate_batch(batch, required_fields=())
    _check_meta(batch, config)
    cols = columns_of(batch)
    offsets: list[int] = []
    known: list[int | None] = []
    for row in range(batch.row_count):
        if cols["fact_kind"][row] != EDGE_KIND:
            fail(ErrorCode.INVALID_SCHEMA, "unknown fact kind for the grid role")
        check_reference_id(cols["reference_id"][row])
        if cols["instrument_id"][row] != entity.instrument_id or cols["session_id"][row] != entity.session_id:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "grid facts belong to the target entity")
        if "text" not in cols or cols["text"][row] != grid_version:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "grid version differs from the configuration")
        if ("effective_end_ns" in cols and cols["effective_end_ns"][row] is not None) or any(
                name in cols and cols[name][row] is not None for name in ("price", "factor_num", "factor_den")):
            fail(ErrorCode.INVALID_SCHEMA, "a bucket edge carries an offset only")
        offsets.append(cols["effective_start_ns"][row])
        known.append(cols["known_at_ns"][row] if "known_at_ns" in cols else None)
    if not 2 <= len(offsets) <= MAX_EDGES:
        fail(ErrorCode.INVALID_CONFIG, "a grid of 1..4096 buckets (2..4097 edges) is required")
    if offsets[0] != 0 or any(b <= a for a, b in zip(offsets, offsets[1:])):
        fail(ErrorCode.BOUNDS, "grid edges start at 0 and increase strictly")
    return Edges(tuple(offsets), tuple(known))


def admit_bars(batch: CanonicalBatch, config: ConfigSpec, entity: EntityKey, grid: SessionGrid,
               offsets: tuple[int, ...]) -> dict[tuple[str, int], Fact]:
    """Bucket volumes per (session, bucket); a bar must be exactly one grid bucket inside its actual session."""
    cols = admit_market(batch, DataKind.BAR, config)
    input_id = batch.metadata.source.input_id
    index = {offset: c for c, offset in enumerate(offsets[:-1])}
    rows: dict[tuple[str, int], int] = {}
    for row in range(batch.row_count):
        if cols["instrument_id"][row] != entity.instrument_id:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "bar instrument differs from the target entity")
        session_id = cols["session_id"][row]
        if session_id not in grid.bounds:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "bar for a session without a bounds fact")
        open_ns, close_ns = grid.bounds[session_id]
        start, end = cols["start_ns"][row], cols["end_ns"][row]
        c = index.get(start - open_ns)
        if c is None or end != open_ns + offsets[c + 1]:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "bar offsets match no grid bucket")
        if end > close_ns:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "bar for a bucket beyond the actual session close")
        rows[(session_id, c)] = row
    def bucket_bounds(name: str) -> tuple[int, int] | None:
        if not name.startswith("bucket:"):
            return None
        session_id, _, c_text = name[7:].rpartition(":")
        if session_id not in grid.bounds or not c_text.isascii() or not c_text.isdigit() or int(c_text) >= len(offsets) - 1:
            return None
        c = int(c_text)
        o = grid.bounds[session_id][0]
        return o + offsets[c], o + offsets[c + 1]

    coverage = _coverage_map(batch, bucket_bounds, {f"bucket:{s}:{c}": r for (s, c), r in rows.items()})
    facts: dict[tuple[str, int], Fact] = {}
    for (session_id, c), row_index in rows.items():
        o = grid.bounds[session_id][0]
        facts[(session_id, c)] = Fact(
            input_id, row_index, coverage.get(f"bucket:{session_id}:{c}"), "volume" in cols,
            cols["volume"][row_index] if "volume" in cols else None,
            cols["known_at_ns"][row_index] if "known_at_ns" in cols else None, o + offsets[c], o + offsets[c + 1])
    for name, entry in coverage.items():
        session_id, _, c_text = name[7:].rpartition(":")
        key = (session_id, int(c_text))
        if key not in facts:
            o = grid.bounds[session_id][0]
            facts[key] = Fact(input_id, None, entry, False, None, None, o + offsets[key[1]], o + offsets[key[1] + 1])
    return facts
