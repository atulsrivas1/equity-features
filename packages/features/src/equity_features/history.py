"""Governed finite historical windows; no acquisition or hidden adjustment."""
from __future__ import annotations
from fractions import Fraction
from typing import cast

from equity_feature_contracts import (
    BatchMetadata, CanonicalBatch, Column, ConfigSpec, ContractError, Coverage, DataKind,
    ErrorCode, EvidenceRow, FeatureColumn, FeatureResult, InputBinding, QualityRow,
    Reason, ResultCell, ResultMetadata, SourceBinding, Status, ValueType, checked_decimal128, validate_batch,
)
from equity_feature_contracts.history import HistoryContext, SMAReference
from . import __version__

_FIELDS = {"history.return": "close", "history.prior_high": "high", "history.prior_low": "low",
           "history.sma": "close", "history.ema": "close"}


def _configuration(config: ConfigSpec, context: HistoryContext, feature_ids: tuple[str, ...]) -> tuple[int, int]:
    if type(config) is not ConfigSpec or type(context) is not HistoryContext:
        raise ContractError(ErrorCode.INVALID_CONFIG, "typed history config/context required")
    if config.algorithm_version != "v1":
        raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "unsupported historical algorithm")
    if type(feature_ids) not in (tuple, list) or not feature_ids or any(type(x) is not str or x not in _FIELDS for x in feature_ids):
        raise ContractError(ErrorCode.UNSUPPORTED_CAPABILITY, "only implemented historical batch IDs accepted")
    if len(set(feature_ids)) != len(feature_ids):
        raise ContractError(ErrorCode.DUPLICATE, "duplicate requested historical ID")
    if "history.return" in feature_ids and len(feature_ids) > 1:
        raise ContractError(ErrorCode.INVALID_CONFIG, "return and prior extrema require distinct window configurations")
    averages = any(x in ("history.sma", "history.ema") for x in feature_ids)
    if averages and any(x not in ("history.sma", "history.ema") for x in feature_ids):
        raise ContractError(ErrorCode.INVALID_CONFIG, "moving averages and other windows require distinct configurations")
    parameters = {p.name: p.value for p in config.parameters}
    if set(parameters) - {"period", "evidence_limit"} or "period" not in parameters:
        raise ContractError(ErrorCode.INVALID_CONFIG, "explicit period and optional evidence_limit only")
    period = parameters["period"]
    evidence_limit = parameters.get("evidence_limit", 0)
    if type(period) is not int or not 1 <= period <= 2**63-2 or type(evidence_limit) is not int or not 0 <= evidence_limit <= 2**63-1:
        raise ContractError(ErrorCode.INVALID_CONFIG, "bounded positive integer period and nonnegative evidence limit required")
    ids = tuple(s.session_id for s in context.sessions)
    if config.window.governed_sessions != ids or context.entity.session_id != config.session.session_id or config.session != next(s for s in context.sessions if s.session_id == context.entity.session_id):
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "config must match exact governed target and grid")
    if config.price_unit is None or not config.session.open_ns <= config.availability.market_cutoff_ns <= config.session.close_ns:
        raise ContractError(ErrorCode.INVALID_CONFIG, "explicit price unit and target cutoff required")
    is_return = "history.return" in feature_ids
    if config.window.count != period + int(is_return) or config.window.anchor != ("completed_eod" if is_return or averages else "prior_only"):
        raise ContractError(ErrorCode.INVALID_CONFIG, "period/window count and inclusion policy disagree")
    if "history.ema" in feature_ids and (context.initialization_anchor is None or
            ids.index(context.initialization_anchor) > ids.index(context.entity.session_id)):
        raise ContractError(ErrorCode.INVALID_CONFIG, "EMA requires an explicit anchor at or before target")
    action = context.action_admission
    if action is None:
        if config.adjustment.basis != "raw" or config.adjustment.policy_version != "raw-v1":
            raise ContractError(ErrorCode.UNSUPPORTED_ADJUSTMENT, "adjusted history requires supplied policy admission")
    elif action.config_digest != config.digest or action.availability != config.availability or action.policy.adjustment != config.adjustment:
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "historical action/config/revision admission mismatch")
    return period, evidence_limit


def _rows(batch: CanonicalBatch | None, config: ConfigSpec, context: HistoryContext) -> dict[str, int]:
    if batch is None:
        return {}
    if type(batch) is not CanonicalBatch or batch.kind != DataKind.DAILY:
        raise ContractError(ErrorCode.INVALID_SCHEMA, "owned canonical daily history required")
    if batch.metadata.namespace != config.session.namespace:
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "historical namespace mismatch")
    if batch.metadata.price_unit != config.price_unit:
        raise ContractError(ErrorCode.INVALID_UNIT, "historical scale/currency mismatch")
    if batch.metadata.adjustment != config.adjustment:
        raise ContractError(ErrorCode.UNSUPPORTED_ADJUSTMENT, "historical price basis mismatch")
    if batch.metadata.coverage.observed != batch.row_count:
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "historical delivered row count mismatch")
    validate_batch(batch, required_fields=())
    fields = {c.name: c.values for c in batch.columns}
    grid = {s.session_id: (i, s) for i, s in enumerate(context.sessions)}
    result: dict[str, int] = {}
    previous = -1
    for index in range(batch.row_count):
        session_id = cast(str, fields["session_id"][index])
        if fields["instrument_id"][index] != context.entity.instrument_id or session_id not in grid:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "row outside declared historical instrument/grid")
        position, session = grid[session_id]
        if position <= previous:
            raise ContractError(ErrorCode.INVALID_ORDER, "historical rows must follow governed grid order")
        if (fields["start_ns"][index], fields["end_ns"][index]) != (session.open_ns, session.close_ns):
            raise ContractError(ErrorCode.BOUNDS, "daily row must match exact governed session bounds")
        scope = batch.metadata.scope
        if scope is not None and (session.open_ns < scope.start_ns or session.close_ns > scope.end_ns):
            raise ContractError(ErrorCode.BOUNDS, "historical row outside declared source input scope")
        result[session_id] = index
        previous = position
    for session, certificate in zip(context.sessions, context.slot_coverage, strict=True):
        if certificate.observed != int(session.session_id in result):
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "slot certificate contradicts actual daily row presence")
    return result


def compute_history(batch: CanonicalBatch | None, config: ConfigSpec, *, context: HistoryContext,
                    feature_ids: tuple[str, ...]) -> FeatureResult:
    """Finite windows or explicitly anchored EMA over supplied governed slots."""
    period, evidence_limit = _configuration(config, context, feature_ids)
    rows = _rows(batch, config, context)
    context_meta = BatchMetadata(config.session.namespace,
                                SourceBinding("caller-history-context", context.grid_version,
                                              "history-context-v1", context.identity_digest),
                                Coverage(len(context.sessions), len(context.sessions), True), None)
    inputs = [InputBinding("history_context", DataKind.REFERENCE, context_meta)]
    if batch is not None:
        inputs.append(InputBinding("daily_history", batch.kind, batch.metadata))
    action = context.action_admission
    if action is not None and action.reference is not None:
        inputs.append(action.reference)
    metadata = ResultMetadata(config.session.namespace, context.entity.session_id, config.availability,
                              config.digest, tuple(inputs), "python-exact", __version__, evidence_limit)
    selected = config.window.selected_sessions()
    certificates = {s.session_id: coverage for s, coverage in zip(context.sessions, context.slot_coverage, strict=True)}
    sessions = {s.session_id: s for s in context.sessions}
    columns: list[FeatureColumn] = []
    qualities: list[QualityRow] = []
    evidence: list[EvidenceRow] = []
    for feature_id in feature_ids:
        dependencies = selected
        expected = config.window.count
        history_complete = config.window.history_complete
        if feature_id == "history.ema":
            ids = tuple(s.session_id for s in context.sessions)
            anchor = cast(str, context.initialization_anchor)
            dependencies = ids[ids.index(anchor):ids.index(context.entity.session_id)+1]
            expected = len(dependencies)
            history_complete = expected >= period
        values: list[int] = []
        reasons: list[Reason] = []
        observed = 0
        status = Status.AVAILABLE
        field = batch.column(_FIELDS[feature_id]) if batch is not None else None
        known = batch.column("known_at_ns") if batch is not None else None
        for session_id in dependencies:
            row = rows.get(session_id)
            reason = None
            knowledge = cast(int | None, known.values[row]) if known is not None and row is not None else None
            if row is None or not certificates[session_id].complete:
                reason = Reason.GOVERNED_GAP
            elif sessions[session_id].close_ns > config.availability.market_cutoff_ns:
                reason = Reason.FUTURE_MARKET
            elif (knowledge_reason := config.availability.knowledge_reason(knowledge)) is not None:
                reason = Reason(knowledge_reason)
            elif field is None:
                reason = Reason.ABSENT_INPUT
            elif field.values[row] is None:
                reason = Reason.NULL_FIELD
            if reason is None:
                values.append(cast(int, field.values[row]))  # type: ignore[union-attr,index]
                observed += 1
            else:
                reasons.append(reason)
            if batch is not None and row is not None and len(evidence) < evidence_limit:
                evidence.append(EvidenceRow(context.entity, feature_id, batch.metadata.source.input_id,
                                            str(row), sessions[session_id].close_ns, knowledge,
                                            sessions[session_id].open_ns, sessions[session_id].close_ns,
                                            "consumed" if reason is None else "excluded", reason, "completed_interval"))
        if batch is None or field is None:
            status = Status.MISSING_INPUT
            reasons.append(Reason.ABSENT_INPUT)
        elif not history_complete:
            status = Status.INSUFFICIENT_HISTORY
            reasons.append(Reason.INSUFFICIENT_HISTORY)
        elif any(x in (Reason.UNKNOWN_AVAILABILITY, Reason.FUTURE_KNOWLEDGE) for x in reasons):
            status = Status.MISSING_INPUT
        elif reasons:
            status = Status.INCOMPLETE_COVERAGE
        if action is not None and action.status != Status.AVAILABLE:
            status = action.status
            reasons.extend(action.reasons)
        value: ResultCell = None
        if status == Status.AVAILABLE:
            if feature_id == "history.return":
                value = float(Fraction(values[-1], values[0]) - 1)
            elif feature_id in ("history.sma", "history.ema"):
                scale = 10**config.price_unit.scale  # type: ignore[union-attr]
                total = checked_decimal128(sum(values[:period]))
                mean = float(Fraction(total, period*scale))
                if feature_id == "history.ema":
                    alpha = 2.0/(period+1)
                    for coefficient in values[period:]:
                        mean = alpha*(coefficient/scale)+(1.0-alpha)*mean
                value = mean
            else:
                coefficient = max(values) if feature_id == "history.prior_high" else min(values)
                value = float(Fraction(coefficient, 10**config.price_unit.scale))  # type: ignore[union-attr]
        quality = QualityRow(context.entity, feature_id, status, expected, observed,
                             tuple(dict.fromkeys(reasons)))
        qualities.append(quality)
        unit = "fraction" if feature_id == "history.return" else f"{config.price_unit.currency}/share"  # type: ignore[union-attr]
        columns.append(FeatureColumn(feature_id, "v1", ValueType.FLOAT64, unit, (context.entity,), (value,)))
    return FeatureResult(tuple(columns), tuple(qualities), metadata, tuple(evidence))


def compute_sma_reference(batch: CanonicalBatch | None, config: ConfigSpec, *,
                          context: HistoryContext) -> SMAReference:
    """Qualify SMA and retain its exact sum/count for supplied dependency comparison."""
    result = compute_history(batch, config, context=context, feature_ids=("history.sma",))
    numerator = denominator = None
    if result.quality[0].status == Status.AVAILABLE:
        supplied = cast(CanonicalBatch, batch)
        rows = _rows(supplied, config, context)
        close = cast(Column, supplied.column("close"))
        numerator = checked_decimal128(sum(cast(int, close.values[rows[s]]) for s in config.window.selected_sessions()))
        denominator = config.window.count
    return SMAReference(result, numerator, denominator, config.price_unit)  # type: ignore[arg-type]
