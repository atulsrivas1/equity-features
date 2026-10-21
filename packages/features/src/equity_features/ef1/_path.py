"""Pure causal sampled gap and completed opening-drive calculations."""
from __future__ import annotations

from fractions import Fraction
from typing import Any

from equity_feature_contracts import (
    CanonicalBatch, ConfigSpec, DataKind, EntityKey, ErrorCode, EvidenceRow,
    FeatureColumn, FeatureResult, InputBinding, QualityRow, Reason, ResultMetadata,
    Status, checked_int64,
)
from equity_features import __version__
from ._anchor import _admit_common, _columns, _ready, _reasons
from ._clock import _calendar_ready
from ._context import decode_ef1_context, fail, label
from ._definitions import ef1_definitions


def _causal(known: int | None, config: ConfigSpec) -> tuple[Reason, ...]:
    # Original knowledge remains required in reconstruction mode as well.
    if known is None:
        return (Reason.UNKNOWN_AVAILABILITY,)
    if known > config.availability.knowledge_cutoff_ns:
        return (Reason.FUTURE_KNOWLEDGE,)
    return ()


def _market(batch: CanonicalBatch, config: ConfigSpec, entity: EntityKey,
            start: int, end: int) -> dict[str, tuple[Any, ...]]:
    _admit_common(batch, config, entity)
    if batch.metadata.price_unit != config.price_unit:
        fail(ErrorCode.INVALID_UNIT, "sampled path unit mismatch")
    if batch.metadata.adjustment != config.adjustment:
        fail(ErrorCode.UNSUPPORTED_ADJUSTMENT, "sampled path adjustment mismatch")
    scope = batch.metadata.scope
    if scope is None or (scope.start_ns, scope.end_ns, scope.eligibility_policy,
            scope.include_opening_auction, scope.include_closing_auction) != (
            start, end, "supplied_path", config.session.include_opening_auction,
            config.session.include_closing_auction):
        fail(ErrorCode.INCONSISTENT_IDENTITY, "exact supplied path scope/auction policy required")
    return _columns(batch)


def _samples(batch: CanonicalBatch, columns: dict[str, tuple[Any, ...]], config: ConfigSpec,
             end: int) -> tuple[int | None, list[tuple[int, int]], tuple[Reason, ...]]:
    reasons: tuple[Reason, ...] = () if batch.metadata.coverage.complete else (Reason.GOVERNED_GAP,)
    opening: int | None = None
    samples: list[tuple[int, int]] = []
    trades = batch.kind == DataKind.TRADE
    conditions = columns.get("condition")
    volumes = columns.get("volume")
    known = columns.get("known_at_ns")
    for index in range(batch.row_count):
        if trades:
            event = columns["event_ns"][index]
            condition = conditions[index] if conditions is not None else None
            if not config.session.open_ns <= event < end or condition == "closing_auction":
                fail(ErrorCode.BOUNDS, "trade outside half-open sampled prefix")
            if condition == "opening_auction" and not (
                    event == config.session.open_ns and config.session.include_opening_auction):
                fail(ErrorCode.BOUNDS, "opening auction has no admitted boundary")
            candidate = columns["eligible"][index]
        else:
            if columns["start_ns"][index] < config.session.open_ns or columns["end_ns"][index] > end:
                fail(ErrorCode.BOUNDS, "bar straddles sampled prefix")
            volume = volumes[index] if volumes is not None else None
            if volume is None:
                reasons = _reasons(reasons, (Reason.NULL_FIELD if "volume" in columns else Reason.ABSENT_INPUT,))
                continue
            candidate = volume > 0
        if not candidate:
            continue
        reasons = _reasons(reasons, _causal(known[index] if known is not None else None, config))
        required = ("price", "size") if trades else (("open", "close") if not samples else ("close",))
        usable = True
        for field in required:
            if field not in columns or columns[field][index] is None:
                reasons = _reasons(reasons, (Reason.ABSENT_INPUT if field not in columns else Reason.NULL_FIELD,))
                usable = False
        if not usable:
            continue
        price = columns["price" if trades else "close"][index]
        if opening is None:
            opening = columns["price" if trades else "open"][index]
        samples.append((index, price))
    return opening, samples, reasons


def _witness(batch: CanonicalBatch, index: int, entity: EntityKey, feature: str) -> EvidenceRow:
    columns = _columns(batch)
    known = columns.get("known_at_ns", (None,) * batch.row_count)[index]
    if batch.kind == DataKind.TRADE:
        return EvidenceRow(entity, feature, batch.metadata.source.input_id, columns["event_id"][index],
                           columns["event_ns"][index], known)
    start, end = columns["start_ns"][index], columns["end_ns"][index]
    row_id = ("daily:" + columns["session_id"][index] if batch.kind == DataKind.DAILY else
              "bar:" + str(start) + ":" + str(end))
    return EvidenceRow(entity, feature, batch.metadata.source.input_id, row_id, end, known,
                       start, end, boundary="completed_interval")


def _compute(batches: tuple[CanonicalBatch, ...] | list[CanonicalBatch], config: ConfigSpec,
             entity: EntityKey, *, gap: bool) -> FeatureResult:
    context = decode_ef1_context(config)
    if context["producer"] != ("path_gap" if gap else "path_drive"):
        fail(ErrorCode.INVALID_CONFIG, "wrong sampled path producer")
    if type(entity) is not EntityKey or entity.session_id != config.session.session_id:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "exact target entity required")
    label(entity.instrument_id)
    label(entity.session_id)
    kind = DataKind.TRADE if context["selection"]["sampling"] == "eligible_trade" else DataKind.BAR
    roles: tuple[tuple[DataKind, str], ...] = ((DataKind.REFERENCE, "calendar_provenance"), (kind, "path"))
    if gap:
        roles += ((DataKind.DAILY, "prior_close"),)
    if type(batches) not in (tuple, list) or len(batches) > len(roles):
        fail(ErrorCode.INVALID_SCHEMA, "bounded concrete present batches required")
    selected: dict[str, CanonicalBatch] = {}
    previous = -1
    for batch in batches:
        if type(batch) is not CanonicalBatch:
            fail(ErrorCode.INVALID_SCHEMA, "actual present CanonicalBatch required")
        match = next((i for i, (expected, _) in enumerate(roles) if batch.kind == expected), -1)
        if match <= previous:
            fail(ErrorCode.INVALID_SCHEMA, "wrong/duplicate/reordered sampled path role")
        previous = match
        selected[roles[match][1]] = batch
    if len({batch.metadata.source.input_id for batch in batches}) != len(batches):
        fail(ErrorCode.DUPLICATE, "distinct actual input bindings required")
    proof, path, prior = (selected.get(role) for role in ("calendar_provenance", "path", "prior_close"))
    _, reasons = _calendar_ready(proof, config, context, entity)
    cutoff, start = config.availability.market_cutoff_ns, config.session.open_ns
    endpoint = cutoff if gap else min(cutoff, start + context["selection"]["duration_ns"])
    opening: int | None = None
    samples: list[tuple[int, int]] = []
    expected: int | None = None
    observed = 0
    if path is None:
        reasons = _reasons(reasons, (Reason.ABSENT_INPUT,))
    else:
        columns = _market(path, config, entity, start, endpoint)
        expected, observed = path.metadata.coverage.expected, path.row_count
        checked_int64(observed)
        if expected is not None:
            checked_int64(expected)
        opening, samples, path_reasons = _samples(path, columns, config, endpoint)
        reasons = _reasons(reasons, path_reasons)
    prior_price: int | None = None
    if gap:
        expected = None if expected is None else checked_int64(expected + 1)
        if prior is None:
            reasons = _reasons(reasons, (Reason.ABSENT_INPUT,))
        else:
            if prior.row_count != 1:
                fail(ErrorCode.INVALID_SCHEMA, "exactly one explicit prior DAILY row required")
            slot = context["calendar"]["sessions"][0]
            columns = _market(prior, config, EntityKey(entity.instrument_id, slot[0]), slot[2], slot[3])
            if (columns["start_ns"][0], columns["end_ns"][0]) != (slot[2], slot[3]):
                fail(ErrorCode.INCONSISTENT_IDENTITY, "prior DAILY bounds differ from explicit slot")
            observed = checked_int64(observed + 1)
            if not prior.metadata.coverage.complete:
                reasons = _reasons(reasons, (Reason.GOVERNED_GAP,))
            reasons = _reasons(reasons, _causal(columns.get("known_at_ns", (None,))[0], config))
            prior_price = columns.get("close", (None,))[0]
            if prior_price is None:
                reasons = _reasons(reasons, (Reason.NULL_FIELD if "close" in columns else Reason.ABSENT_INPUT,))
    elif cutoff < start + context["selection"]["duration_ns"]:
        reasons = _reasons(reasons, (Reason.GOVERNED_GAP,))
    status, reasons = _ready(reasons)
    values: dict[str, int | float | bool | None] = {}
    witnesses: dict[str, list[tuple[CanonicalBatch, int]]] = {}
    no_hit = False
    if status == Status.AVAILABLE:
        if not samples:
            status, reasons = Status.NOT_APPLICABLE, (Reason.NO_ELIGIBLE_OBSERVATIONS,)
        else:
            assert opening is not None and path is not None
            first, last = samples[0][0], samples[-1][0]
            if gap:
                assert prior_price is not None and prior is not None
                denominator = opening - prior_price
                if denominator == 0:
                    status, reasons = Status.NOT_APPLICABLE, (Reason.ZERO_DENOMINATOR,)
                else:
                    fills = [max(Fraction(0), min(Fraction(1), Fraction(opening - price, denominator)))
                             for _, price in samples]
                    best = max(range(len(samples)), key=lambda i: fills[i])
                    hit = next((index for index, price in samples if (price - prior_price) * denominator <= 0), None)
                    no_hit = hit is None
                    values = {"fill_fraction": float(fills[best]), "filled": hit is not None,
                              "first_fill_ns": None if hit is None else _columns(path)["event_ns" if kind == DataKind.TRADE else "end_ns"][hit],
                              "remaining_fraction": float(max(Fraction(0), Fraction(samples[-1][1] - prior_price, denominator)))}
                    witnesses = {"remaining_fraction": [(path, first), (prior, 0), (path, last)],
                                 "fill_fraction": [(path, first), (path, samples[best][0])]}
                    if hit is not None:
                        witnesses.update({"filled": [(path, hit)], "first_fill_ns": [(path, hit)]})
            else:
                maximum = max(samples, key=lambda item: item[1])
                minimum = min(samples, key=lambda item: item[1])
                values = {"return": float(Fraction(samples[-1][1], opening) - 1),
                          "excursion_up": float(max(Fraction(0), Fraction(maximum[1], opening) - 1)),
                          "excursion_down": float(max(Fraction(0), 1 - Fraction(minimum[1], opening)))}
                witnesses = {"return": [(path, first), (path, last)],
                             "excursion_up": [(path, maximum[0])], "excursion_down": [(path, minimum[0])]}
    bindings = tuple(InputBinding(role, batch.kind, batch.metadata) for role, batch in selected.items())
    metadata = ResultMetadata(config.session.namespace, entity.session_id, config.availability, config.digest,
                              bindings, "python-exact", __version__, evidence_limit=7 if gap else 4)
    output: list[FeatureColumn] = []
    quality: list[QualityRow] = []
    evidence: dict[tuple[str, str, str], EvidenceRow] = {}
    for definition in ef1_definitions(config):
        name = definition.feature_id.rsplit(".", 1)[1]
        field_status, field_reasons = status, reasons
        if status == Status.AVAILABLE and name == "first_fill_ns" and no_hit:
            field_status, field_reasons = Status.NOT_APPLICABLE, (Reason.NO_ELIGIBLE_OBSERVATIONS,)
        output.append(FeatureColumn(definition.feature_id, "v1", definition.dtype, definition.unit, (entity,), (values.get(name),)))
        quality.append(QualityRow(entity, definition.feature_id, field_status, expected, observed, field_reasons))
        for batch, index in witnesses.get(name, []):
            row = _witness(batch, index, entity, definition.feature_id)
            evidence[(row.feature_id, row.input_id, row.row_id)] = row
    return FeatureResult(tuple(output), tuple(quality), metadata, tuple(evidence[key] for key in sorted(evidence)))


def compute_path_gap(batches: tuple[CanonicalBatch, ...] | list[CanonicalBatch], config: ConfigSpec,
                     *, entity: EntityKey) -> FeatureResult:
    return _compute(batches, config, entity, gap=True)


def compute_path_drive(batches: tuple[CanonicalBatch, ...] | list[CanonicalBatch], config: ConfigSpec,
                       *, entity: EntityKey) -> FeatureResult:
    return _compute(batches, config, entity, gap=False)
