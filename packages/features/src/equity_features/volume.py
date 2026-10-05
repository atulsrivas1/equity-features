"""Pure governed volume baselines and supplied dependency ratios."""
from __future__ import annotations
from fractions import Fraction
from typing import cast
from equity_feature_contracts import (
    BatchMetadata, CanonicalBatch, Column, ConfigSpec, ContractError, Coverage, DataKind,
    ErrorCode, EvidenceRow, FeatureColumn, FeatureResult, InputBinding, QualityRow,
    Reason, ResultMetadata, SourceBinding, Status, ValueType, checked_decimal128,
)
from equity_feature_contracts.history import HistoryContext
from equity_feature_contracts.volume import TargetVolume, VolumeBaseline, _configuration
from . import __version__
from .history import _rows


def _context_binding(config: ConfigSpec, context: HistoryContext) -> InputBinding:
    return InputBinding("history_context", DataKind.REFERENCE,
                        BatchMetadata(config.session.namespace, SourceBinding("caller-history-context", context.grid_version,
                                      "history-context-v1", context.identity_digest),
                                      Coverage(len(context.sessions), len(context.sessions), True), None))


def _result(feature: str, value: float | None, status: Status, reasons: list[Reason], expected: int,
            observed: int, config: ConfigSpec, context: HistoryContext, inputs: list[InputBinding],
            evidence: list[EvidenceRow], limit: int) -> FeatureResult:
    return FeatureResult((FeatureColumn(feature, "v1", ValueType.FLOAT64,
                                         "shares" if feature == "baseline.daily_volume" else "fraction",
                                         (context.entity,), (value,)),),
                         (QualityRow(context.entity, feature, status, expected, observed, tuple(dict.fromkeys(reasons))),),
                         ResultMetadata(config.session.namespace, context.entity.session_id, config.availability,
                                        config.digest, tuple(inputs), "python-exact", __version__, limit), tuple(evidence))


def compute_daily_baseline(batch: CanonicalBatch | None, config: ConfigSpec, *, context: HistoryContext) -> VolumeBaseline:
    """Exact prior-only mean over required slots; never consume the target volume."""
    period, limit, basis = _configuration(config, context)
    rows = _rows(batch, config, context)
    selected = config.window.selected_sessions()
    slots = {s.session_id: (s, c) for s, c in zip(context.sessions, context.slot_coverage, strict=True)}
    volume = batch.column("volume") if batch is not None else None
    known = batch.column("known_at_ns") if batch is not None else None
    inputs = [_context_binding(config, context)]
    if batch is not None:
        inputs.append(InputBinding("daily_history", DataKind.DAILY, batch.metadata))
    action = context.action_admission
    if action is not None and action.reference is not None:
        inputs.append(action.reference)
    reasons: list[Reason] = []
    evidence: list[EvidenceRow] = []
    values: list[int] = []
    for sid in selected:
        session, certificate = slots[sid]
        row = rows.get(sid)
        knowledge = cast(int | None, known.values[row]) if known is not None and row is not None else None
        reason = None
        if row is None or not certificate.complete:
            reason = Reason.GOVERNED_GAP
        elif session.close_ns > config.availability.market_cutoff_ns:
            reason = Reason.FUTURE_MARKET
        elif (kr := config.availability.knowledge_reason(knowledge)) is not None:
            reason = Reason(kr)
        elif volume is None:
            reason = Reason.ABSENT_INPUT
        elif volume.values[row] is None:
            reason = Reason.NULL_FIELD
        if reason is None:
            values.append(cast(int, cast(Column, volume).values[cast(int, row)]))
        else:
            reasons.append(reason)
        if batch is not None and row is not None and len(evidence) < limit:
            evidence.append(EvidenceRow(context.entity, "baseline.daily_volume", batch.metadata.source.input_id,
                                        str(row), session.close_ns, knowledge, session.open_ns, session.close_ns,
                                        "consumed" if reason is None else "excluded", reason, "completed_interval"))
    status = Status.AVAILABLE
    if batch is None or volume is None:
        status = Status.MISSING_INPUT
        reasons.append(Reason.ABSENT_INPUT)
    elif not config.window.history_complete:
        status = Status.INSUFFICIENT_HISTORY
        reasons.append(Reason.INSUFFICIENT_HISTORY)
    elif any(r in (Reason.UNKNOWN_AVAILABILITY, Reason.FUTURE_KNOWLEDGE) for r in reasons):
        status = Status.MISSING_INPUT
    elif reasons:
        status = Status.INCOMPLETE_COVERAGE
    if action is not None and action.status != Status.AVAILABLE:
        status = action.status
        reasons.extend(action.reasons)
    numerator = checked_decimal128(sum(values)) if status == Status.AVAILABLE else None
    denominator = period if numerator is not None else None
    value = float(Fraction(numerator, period)) if numerator is not None else None
    result = _result("baseline.daily_volume", value, status, reasons, period, len(values), config, context, inputs, evidence, limit)
    return VolumeBaseline(result, config, context, numerator, denominator, basis)


def _add(inputs: list[InputBinding], binding: InputBinding) -> None:
    same = next((b for b in inputs if b.metadata.source.input_id == binding.metadata.source.input_id), None)
    if same is not None:
        if same.kind != binding.kind or same.metadata != binding.metadata:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "conflicting reused source identity")
        return
    if any(b.role == binding.role for b in inputs):
        raise ContractError(ErrorCode.DUPLICATE, "conflicting input role")
    inputs.append(binding)


def _identity_binding(role: str, digest: str, config: ConfigSpec) -> InputBinding:
    return InputBinding(role, DataKind.REFERENCE, BatchMetadata(config.session.namespace,
                        SourceBinding("caller-supplied-dependency", "schema1", "volume-reference-v1", digest),
                        Coverage(1, 1, True), None))


def compute_relative_volume(target: TargetVolume | None, baseline: VolumeBaseline | None,
                            config: ConfigSpec, *, context: HistoryContext) -> FeatureResult:
    """Consume a matching supplied baseline; never calculate a missing dependency."""
    _, limit, basis = _configuration(config, context)
    inputs = [_context_binding(config, context)]
    reasons: list[Reason] = []
    evidence: list[EvidenceRow] = []
    status = Status.AVAILABLE
    observed = 0
    if baseline is None:
        status = Status.MISSING_INPUT
        reasons.append(Reason.ABSENT_INPUT)
    else:
        if type(baseline) is not VolumeBaseline:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "owned volume reference required")
        if baseline.config != config or baseline.context != context or baseline.quantity_basis != basis or baseline.result.metadata.backend_id != "python-exact" or baseline.result.metadata.backend_version != __version__:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "volume dependency/config/context/version mismatch")
        for binding in baseline.result.metadata.inputs:
            _add(inputs, binding)
        _add(inputs, _identity_binding("baseline_reference", baseline.identity_digest, config))
        q = baseline.result.quality[0]
        if q.status != Status.AVAILABLE:
            status = q.status
            reasons.extend(q.reasons)
        else:
            observed += 1
        for e in baseline.result.evidence[:limit]:
            evidence.append(EvidenceRow(e.entity, "baseline.relative_volume", e.input_id, e.row_id, e.event_ns,
                                        e.known_at_ns, e.effective_start_ns, e.effective_end_ns, e.use,
                                        e.exclusion_reason, e.boundary))
    target_reason = None
    if target is None:
        target_reason = Reason.ABSENT_INPUT
    else:
        if type(target) is not TargetVolume:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "owned target volume required")
        if target.entity != context.entity or target.quantity_basis != basis or target.source.metadata.namespace != config.session.namespace or target.source.metadata.price_unit != config.price_unit or target.source.metadata.adjustment != config.adjustment:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "target volume entity/unit/basis mismatch")
        session, interval = config.session, target.interval
        if interval.start_ns != session.open_ns or interval.end_ns > session.close_ns or interval.include_opening_auction != session.include_opening_auction or interval.include_closing_auction != session.include_closing_auction:
            raise ContractError(ErrorCode.BOUNDS, "target interval/session construction mismatch")
        if target.endpoint_mode == "completed_eod":
            if interval.end_ns != session.close_ns:
                raise ContractError(ErrorCode.BOUNDS, "completed daily target must reach actual close")
        elif interval.end_ns != config.availability.market_cutoff_ns:
            raise ContractError(ErrorCode.BOUNDS, "observed prefix must end at explicit market cutoff")
        _add(inputs, target.source)
        _add(inputs, _identity_binding("target_certificate", target.identity_digest, config))
        if interval.end_ns > config.availability.market_cutoff_ns:
            target_reason = Reason.FUTURE_MARKET
        elif (kr := config.availability.knowledge_reason(target.known_at_ns)) is not None:
            target_reason = Reason(kr)
        elif not target.coverage.complete:
            target_reason = Reason.GOVERNED_GAP
        elif target.volume is None:
            target_reason = Reason.NULL_FIELD
        if target_reason is None:
            observed += 1
        # The same original daily frame may supply both prior rows and the target.
        if len(evidence) < limit:
            evidence.append(EvidenceRow(context.entity, "baseline.relative_volume", target.source.metadata.source.input_id,
                                        str(target.row_index), interval.end_ns, target.known_at_ns,
                                        interval.start_ns, interval.end_ns, "consumed" if target_reason is None else "excluded",
                                        target_reason, "completed_interval"))
    if target_reason is not None:
        reasons.append(target_reason)
        if status == Status.AVAILABLE:
            status = Status.INCOMPLETE_COVERAGE if target_reason in (Reason.GOVERNED_GAP, Reason.FUTURE_MARKET) else Status.MISSING_INPUT
    action = context.action_admission
    if action is not None:
        if action.reference is not None:
            _add(inputs, action.reference)
        if action.status != Status.AVAILABLE:
            status = action.status
            reasons.extend(action.reasons)
    value = None
    if status == Status.AVAILABLE:
        ref, fact = cast(VolumeBaseline, baseline), cast(TargetVolume, target)
        if ref.numerator == 0:
            status = Status.NOT_APPLICABLE
            reasons.append(Reason.ZERO_DENOMINATOR)
        else:
            value = float(Fraction(cast(int, fact.volume)*cast(int, ref.denominator), cast(int, ref.numerator)))
    return _result("baseline.relative_volume", value, status, reasons, 2, observed, config, context, inputs, evidence, limit)
