"""Pure application of supplied exact factors and point-in-time references."""
from __future__ import annotations
from dataclasses import asdict, replace
from fractions import Fraction
import hashlib
import json
from typing import cast

from equity_feature_contracts import (
    AdjustmentSpec, CanonicalBatch, Cell, Column, ConfigSpec, ContractError, DataKind,
    EntityKey, ErrorCode, InputBinding, Reason, Status, checked_decimal128,
    checked_int64, validate_batch,
)
from equity_feature_contracts.policies import (
    ActionPolicy, AdjustmentApplication, ClassificationAdmission, PolicyAdmission,
    ReferenceFact,
)


def _context(config: ConfigSpec, entity: EntityKey) -> None:
    if type(config) is not ConfigSpec or type(entity) is not EntityKey:
        raise ContractError(ErrorCode.INVALID_CONFIG, "typed config and target entity required")
    if config.algorithm_version != "v1":
        raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "unsupported policy algorithm version")
    if entity.session_id != config.window.target_session_id:
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "entity/config target mismatch")
    if not config.session.open_ns <= config.availability.market_cutoff_ns <= config.session.close_ns:
        raise ContractError(ErrorCode.BOUNDS, "market cutoff outside supplied target session")


def _value(batch: CanonicalBatch, name: str, index: int) -> Cell:
    column = batch.column(name)
    return column.values[index] if column is not None else None


def _reference(reference: CanonicalBatch | None, config: ConfigSpec) -> InputBinding | None:
    if reference is None:
        return None
    if type(reference) is not CanonicalBatch or reference.kind != DataKind.REFERENCE:
        raise ContractError(ErrorCode.INVALID_SCHEMA, "supplied canonical reference required")
    if reference.metadata.namespace != config.session.namespace:
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "reference namespace mismatch")
    validate_batch(reference, required_fields=())
    return InputBinding("policy_reference", reference.kind, reference.metadata)


def _fact(reference: CanonicalBatch, index: int) -> ReferenceFact:
    return ReferenceFact(index, cast(str, _value(reference, "reference_id", index)),
                         cast(str, _value(reference, "fact_kind", index)),
                         cast(int, _value(reference, "effective_start_ns", index)),
                         cast(int | None, _value(reference, "effective_end_ns", index)),
                         cast(int | None, _value(reference, "known_at_ns", index)),
                         cast(int | None, _value(reference, "factor_num", index)),
                         cast(int | None, _value(reference, "factor_den", index)),
                         cast(str | None, _value(reference, "text", index)))


def _reasons(config: ConfigSpec, facts: tuple[ReferenceFact, ...]) -> list[Reason]:
    return [Reason(reason) for fact in facts
            if (reason := config.availability.knowledge_reason(fact.known_at_ns)) is not None]


def admit_action_policy(reference: CanonicalBatch | None, policy: ActionPolicy,
                        config: ConfigSpec, *, entity: EntityKey) -> PolicyAdmission:
    """Select factors within the anchor; retain their original availability."""
    _context(config, entity)
    if type(policy) is not ActionPolicy:
        raise ContractError(ErrorCode.INVALID_CONFIG, "typed supplied action policy required")
    if config.adjustment != policy.adjustment:
        raise ContractError(ErrorCode.UNSUPPORTED_ADJUSTMENT, "config/output policy mismatch")
    if policy.anchor_ns > config.availability.market_cutoff_ns:
        raise ContractError(ErrorCode.BOUNDS, "action anchor cannot exceed market cutoff")
    binding = _reference(reference, config)
    facts: tuple[ReferenceFact, ...] = ()
    reasons: list[Reason] = []
    status = Status.AVAILABLE
    if policy.adjustment.basis != "raw":
        if reference is None:
            status = Status.MISSING_INPUT
            reasons.append(Reason.MISSING_ACTION_EVIDENCE)
        else:
            if reference.metadata.source.snapshot_id != policy.adjustment.action_snapshot:
                raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "action snapshot differs from supplied revision")
            selected: list[ReferenceFact] = []
            for index in range(reference.row_count):
                if _value(reference, "instrument_id", index) != entity.instrument_id:
                    continue
                start = cast(int, _value(reference, "effective_start_ns", index))
                if start > policy.anchor_ns:
                    continue
                kind = cast(str, _value(reference, "fact_kind", index))
                if kind not in ("split_factor", "dividend_factor", "sector_membership", "universe_membership", "prior_close"):
                    raise ContractError(ErrorCode.UNSUPPORTED_ADJUSTMENT, "unsupported supplied action factor kind")
                if kind not in ("split_factor", "dividend_factor") or (kind == "dividend_factor" and policy.adjustment.basis == "split"):
                    continue
                fact = _fact(reference, index)
                if fact.effective_end_ns is not None:
                    raise ContractError(ErrorCode.UNSUPPORTED_ADJUSTMENT, "v1 factors require instantaneous effective boundary")
                selected.append(fact)
            facts = tuple(selected)
            reasons.extend(_reasons(config, facts))
            if any(x.factor_num is None or x.factor_den is None for x in facts):
                reasons.extend((Reason.MISSING_ACTION_EVIDENCE, Reason.NULL_FIELD))
            if reasons:
                status = Status.MISSING_INPUT
            if not reference.metadata.coverage.complete:
                reasons.append(Reason.MISSING_ACTION_EVIDENCE)
                if status == Status.AVAILABLE:
                    status = Status.INCOMPLETE_COVERAGE
    return PolicyAdmission(entity, policy, config.digest, config.availability, binding,
                           facts, status, tuple(dict.fromkeys(reasons)))


def admit_classification(reference: CanonicalBatch | None, config: ConfigSpec, *,
                         entity: EntityKey, effective_ns: int,
                         fact_kind: str) -> ClassificationAdmission:
    """Select exactly one supplied half-open membership interval."""
    _context(config, entity)
    checked_int64(effective_ns)
    if effective_ns > config.availability.market_cutoff_ns:
        raise ContractError(ErrorCode.BOUNDS, "classification cannot exceed market cutoff")
    if fact_kind not in ("sector_membership", "universe_membership"):
        raise ContractError(ErrorCode.INVALID_CONFIG, "supported explicit classification kind required")
    binding = _reference(reference, config)
    facts: tuple[ReferenceFact, ...] = ()
    reasons: list[Reason] = []
    status = Status.AVAILABLE
    if reference is None:
        reasons.append(Reason.ABSENT_INPUT)
    else:
        selected = []
        for index in range(reference.row_count):
            if _value(reference, "instrument_id", index) != entity.instrument_id or _value(reference, "fact_kind", index) != fact_kind:
                continue
            start = cast(int, _value(reference, "effective_start_ns", index))
            end = cast(int | None, _value(reference, "effective_end_ns", index))
            if start <= effective_ns and (end is None or effective_ns < end):
                selected.append(_fact(reference, index))
        if len(selected) > 1:
            raise ContractError(ErrorCode.DUPLICATE, "overlapping applicable classification revisions")
        facts = tuple(selected)
        if not facts:
            reasons.append(Reason.ABSENT_INPUT)
        else:
            reasons.extend(_reasons(config, facts))
            if facts[0].text is None or not facts[0].text.strip():
                reasons.append(Reason.NULL_FIELD)
        if not reference.metadata.coverage.complete:
            reasons.append(Reason.GOVERNED_GAP)
            status = Status.INCOMPLETE_COVERAGE
    if any(x != Reason.GOVERNED_GAP for x in reasons):
        status = Status.MISSING_INPUT
    return ClassificationAdmission(entity, fact_kind, effective_ns, config.digest,
                                   config.availability, binding, facts, status,
                                   tuple(dict.fromkeys(reasons)))


def _integer(value: int, factor: Fraction, *, wide: bool = False) -> int:
    product = value * factor
    if product.denominator != 1:
        raise ContractError(ErrorCode.UNSUPPORTED_ADJUSTMENT, "nonintegral adjusted coefficient; supply explicit exact representation")
    return checked_decimal128(product.numerator) if wide else checked_int64(product.numerator)


def apply_action_policy(batch: CanonicalBatch, reference: CanonicalBatch | None,
                        policy: ActionPolicy, config: ConfigSpec, *,
                        entity: EntityKey) -> AdjustmentApplication:
    """Apply exact factors without sorting, rounding, acquisition or mutation."""
    admission = admit_action_policy(reference, policy, config, entity=entity)
    if type(batch) is not CanonicalBatch:
        raise ContractError(ErrorCode.INVALID_SCHEMA, "owned canonical input required")
    if batch.metadata.namespace != config.session.namespace:
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "market input namespace mismatch")
    if batch.metadata.price_unit != config.price_unit:
        raise ContractError(ErrorCode.INVALID_UNIT, "policy requires explicit matching price scale/currency")
    expected = policy.adjustment if policy.representation == "caller_transformed" or policy.adjustment.basis == "raw" else AdjustmentSpec()
    if batch.metadata.adjustment != expected:
        raise ContractError(ErrorCode.UNSUPPORTED_ADJUSTMENT, "input basis incompatible with declared representation")
    for index in range(batch.row_count):
        if _value(batch, "instrument_id", index) != entity.instrument_id:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "application only accepts declared instrument")
        if batch.kind != DataKind.REFERENCE and _value(batch, "session_id", index) not in config.window.governed_sessions:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "market input outside governed session identities")
        if _value(batch, "session_id", index) == entity.session_id:
            if batch.kind in (DataKind.BAR, DataKind.DAILY) and (cast(int, _value(batch, "start_ns", index)) < config.session.open_ns or cast(int, _value(batch, "end_ns", index)) > config.session.close_ns):
                raise ContractError(ErrorCode.BOUNDS, "target interval outside supplied session")
            if batch.kind in (DataKind.TRADE, DataKind.QUOTE) and cast(int, _value(batch, "event_ns", index)) < config.session.open_ns:
                raise ContractError(ErrorCode.BOUNDS, "target event before supplied session open")
        if batch.kind == DataKind.REFERENCE:
            if _value(batch, "fact_kind", index) != "prior_close":
                raise ContractError(ErrorCode.INVALID_SCHEMA, "reference price application only supports prior_close facts")
            if cast(int, _value(batch, "effective_start_ns", index)) > config.availability.market_cutoff_ns:
                raise ContractError(ErrorCode.BOUNDS, "future supplied reference price")
            price = _value(batch, "price", index)
            if price is not None and cast(int, price) <= 0:
                raise ContractError(ErrorCode.INVALID_SCHEMA, "positive supplied reference price required")
    report = validate_batch(batch, availability=config.availability, required_fields=())
    original = InputBinding("policy_input", batch.kind, batch.metadata)
    reasons = list(admission.reasons)
    reasons.extend(x.reason for x in report.knowledge_exclusions)
    status = admission.status
    if report.knowledge_exclusions:
        status = Status.MISSING_INPUT
    if not batch.metadata.coverage.complete:
        reasons.append(Reason.GOVERNED_GAP)
        if status == Status.AVAILABLE:
            status = Status.INCOMPLETE_COVERAGE
    if status != Status.AVAILABLE:
        return AdjustmentApplication(admission, original, None, status, tuple(dict.fromkeys(reasons)))
    if policy.representation == "caller_transformed" or policy.adjustment.basis == "raw":
        return AdjustmentApplication(admission, original, batch, Status.AVAILABLE)
    fields = {column.name: list(column.values) for column in batch.columns}
    for index in range(batch.row_count):
        if batch.kind in (DataKind.BAR, DataKind.DAILY):
            stamp = cast(int, _value(batch, "start_ns", index))
            end = cast(int, _value(batch, "end_ns", index))
        else:
            stamp = cast(int, _value(batch, "effective_start_ns" if batch.kind == DataKind.REFERENCE else "event_ns", index))
            end = stamp
        price_factor = Fraction(1)
        quantity_factor = Fraction(1)
        for fact in admission.facts:
            if stamp < fact.effective_start_ns < end:
                raise ContractError(ErrorCode.BOUNDS, "interval crosses supplied action boundary")
            if stamp < fact.effective_start_ns:
                factor = Fraction(cast(int, fact.factor_num), cast(int, fact.factor_den))
                price_factor *= factor
                if fact.fact_kind == "split_factor" and policy.quantity_basis == "split_shares":
                    quantity_factor /= factor
        for name in ("price", "open", "high", "low", "close", "bid", "ask"):
            if name in fields and fields[name][index] is not None:
                fields[name][index] = _integer(cast(int, fields[name][index]), price_factor)
        for name in ("volume", "size", "bid_size", "ask_size"):
            if name in fields and fields[name][index] is not None:
                fields[name][index] = _integer(cast(int, fields[name][index]), quantity_factor)
        if "actual_notional" in fields and fields["actual_notional"][index] is not None:
            fields["actual_notional"][index] = _integer(cast(int, fields["actual_notional"][index]), price_factor * quantity_factor, wide=True)
    identity = json.dumps({"input": asdict(original), "policy": admission.identity_digest},
                          sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    source = replace(batch.metadata.source, input_id="policy:" + hashlib.sha256(identity.encode("utf-8")).hexdigest())
    metadata = replace(batch.metadata, source=source, adjustment=policy.adjustment)
    output = CanonicalBatch(batch.kind, tuple(Column(column.name, tuple(fields[column.name]))
                                             for column in batch.columns), metadata)
    validate_batch(output, required_fields=())
    return AdjustmentApplication(admission, original, output, Status.AVAILABLE)
