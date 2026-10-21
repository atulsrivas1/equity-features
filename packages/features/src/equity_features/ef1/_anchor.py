"""Checked exact anchored totals over real canonical market and provenance batches."""
from __future__ import annotations

from collections.abc import Mapping
from fractions import Fraction
from typing import Any, cast

from equity_feature_contracts import (
    CanonicalBatch, ConfigSpec, DataKind, EntityKey, ErrorCode, FeatureColumn,
    FeatureResult, InputBinding, QualityRow, Reason, ResultMetadata, Status,
    PriceUnit, checked_decimal128, checked_int64, validate_batch,
)
from equity_features import __version__
from ._context import anchor_proof_id, decode_ef1_context, fail, label
from ._definitions import ef1_definitions

Readiness = tuple[Status, tuple[Reason, ...]]


def _reasons(*groups: tuple[Reason, ...]) -> tuple[Reason, ...]:
    return tuple(sorted({reason for group in groups for reason in group}, key=lambda reason: reason.value))


def _ready(reasons: tuple[Reason, ...]) -> Readiness:
    if not reasons:
        return Status.AVAILABLE, ()
    if any(reason != Reason.GOVERNED_GAP for reason in reasons):
        return Status.MISSING_INPUT, reasons
    return Status.INCOMPLETE_COVERAGE, reasons


def _columns(batch: CanonicalBatch) -> dict[str, tuple[Any, ...]]:
    return {column.name: column.values for column in batch.columns}


def _admit_common(batch: CanonicalBatch, config: ConfigSpec, entity: EntityKey) -> None:
    if type(batch) is not CanonicalBatch:
        fail(ErrorCode.INVALID_SCHEMA, "actual CanonicalBatch required")
    meta = batch.metadata
    if meta.namespace != config.session.namespace or meta.coverage.observed != batch.row_count:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "actual namespace/population binding mismatch")
    if meta.ordering != "declared" or meta.duplicate_policy != "reject":
        fail(ErrorCode.INVALID_ORDER, "ordered unique canonical inputs required")
    for text in (meta.namespace, meta.source.source_id, meta.source.snapshot_id,
                 meta.source.mapping_version, meta.source.input_id):
        label(text)
    for interval in meta.interval_coverage:
        label(interval.name)
    for column in batch.columns:
        for item in column.values:
            if type(item) is str:
                label(item)
    columns = _columns(batch)
    if any(value != entity.instrument_id for value in columns["instrument_id"]) or any(
            value != entity.session_id for value in columns["session_id"]):
        fail(ErrorCode.INCONSISTENT_IDENTITY, "one actual requested entity required")
    validate_batch(batch, required_fields=())


def _proof_ready(proof: CanonicalBatch | None, config: ConfigSpec,
                 context: Mapping[str, Any], entity: EntityKey) -> Readiness:
    if proof is None:
        return Status.MISSING_INPUT, (Reason.ABSENT_INPUT,)
    if proof.row_count > 4096:
        fail(ErrorCode.BOUNDS, "reference work bound exceeded")
    _admit_common(proof, config, entity)
    if proof.kind != DataKind.REFERENCE:
        fail(ErrorCode.INVALID_SCHEMA, "anchor proof must be REFERENCE")
    if proof.row_count > 1:
        fail(ErrorCode.DUPLICATE, "one exact anchor declaration required")
    columns = _columns(proof)
    if any(name in columns for name in ("price", "factor_num", "factor_den")):
        fail(ErrorCode.INVALID_SCHEMA, "anchor proof has unused numerical payload")
    definition = context["selection"]["definition"]
    if proof.metadata.source.snapshot_id != definition["revision"]:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "anchor proof revision mismatch")
    if proof.metadata.source.mapping_version != "ef1-reference-map1":
        fail(ErrorCode.INCOMPATIBLE_VERSION, "unsupported anchor proof mapping")
    if not proof.row_count:
        return Status.MISSING_INPUT, (Reason.ABSENT_INPUT,)
    if (columns["reference_id"][0] != anchor_proof_id(context)
            or columns["effective_start_ns"][0] != definition["start_ns"]):
        fail(ErrorCode.INCONSISTENT_IDENTITY, "anchor declaration hash/time mismatch")
    if columns["fact_kind"][0] != "ef1.anchor.provenance" or columns.get("text", (None,))[0] != "supplied_anchor":
        fail(ErrorCode.INVALID_SCHEMA, "closed anchor provenance vocabulary required")
    reasons: tuple[Reason, ...] = ()
    if not proof.metadata.coverage.complete:
        reasons += (Reason.GOVERNED_GAP,)
    known_at = columns.get("known_at_ns", (None,))[0]
    knowledge = config.availability.knowledge_reason(known_at)
    if knowledge is not None:
        reasons += (Reason(knowledge),)
    end = columns.get("effective_end_ns", (None,))[0]
    if end is not None and end <= config.availability.market_cutoff_ns:
        reasons += (Reason.INELIGIBLE,)
    return _ready(_reasons(reasons))


def _market_admit(batch: CanonicalBatch, config: ConfigSpec,
                  context: Mapping[str, Any], entity: EntityKey) -> dict[str, tuple[Any, ...]]:
    _admit_common(batch, config, entity)
    if batch.metadata.price_unit != config.price_unit:
        fail(ErrorCode.INVALID_UNIT, "anchor market price unit mismatch")
    if batch.metadata.adjustment != config.adjustment:
        fail(ErrorCode.UNSUPPORTED_ADJUSTMENT, "anchor market adjustment mismatch")
    scope = batch.metadata.scope
    start = context["selection"]["definition"]["start_ns"]
    cutoff = config.availability.market_cutoff_ns
    if scope is None or (scope.start_ns, scope.end_ns) != (start, cutoff):
        fail(ErrorCode.INCONSISTENT_IDENTITY, "exact actual anchor input scope required")
    label(scope.eligibility_policy)
    if (scope.include_opening_auction, scope.include_closing_auction) != (
            config.session.include_opening_auction, config.session.include_closing_auction):
        fail(ErrorCode.INCONSISTENT_IDENTITY, "anchor auction construction mismatch")
    columns = _columns(batch)
    conditions = columns.get("condition")
    for i in range(batch.row_count):
        if batch.kind == DataKind.TRADE:
            event_ns = columns["event_ns"][i]
            condition = conditions[i] if conditions is not None else None
            closing = (condition == "closing_auction" and event_ns == cutoff == config.session.close_ns
                       and config.session.include_closing_auction)
            if event_ns < start or event_ns >= cutoff and not closing:
                fail(ErrorCode.BOUNDS, "trade outside requested anchor window")
            if condition == "closing_auction" and not closing:
                fail(ErrorCode.BOUNDS, "closing auction has no admitted boundary")
            if condition == "opening_auction" and not (
                    config.session.include_opening_auction and event_ns == config.session.open_ns):
                fail(ErrorCode.BOUNDS, "opening auction has no admitted boundary")
        else:
            if columns["start_ns"][i] < start or columns["end_ns"][i] > cutoff:
                fail(ErrorCode.BOUNDS, "bar straddles anchor/cutoff")
            quantity = columns["volume"][i] if "volume" in columns else None
            amount = columns["actual_notional"][i] if "actual_notional" in columns else None
            # Canonical OHLC is optional for this operand-only calculation. Its
            # low/high notional bound therefore cannot establish positivity.
            if quantity is not None and quantity > 0 and amount is not None and amount <= 0:
                fail(ErrorCode.INVALID_SCHEMA, "positive-volume bar needs positive actual notional")
    return columns


def _totals(batch: CanonicalBatch, columns: dict[str, tuple[Any, ...]],
            config: ConfigSpec) -> tuple[int, int, tuple[Reason, ...], tuple[Reason, ...]]:
    """Wide exact totals, with independent volume and notional dependency closure."""
    common: tuple[Reason, ...] = () if batch.metadata.coverage.complete else (Reason.GOVERNED_GAP,)
    volume_reasons: tuple[Reason, ...] = ()
    notional_reasons: tuple[Reason, ...] = ()
    volume, notional = 0, 0
    trades = batch.kind == DataKind.TRADE
    quantity_name = "size" if trades else "volume"
    price_name = "price" if trades else "actual_notional"
    known = columns.get("known_at_ns")
    for i in range(batch.row_count):
        knowledge = config.availability.knowledge_reason(known[i] if known is not None else None)
        # Even ineligible rows are part of the declared delivered population.
        if knowledge is not None:
            common = _reasons(common, (Reason(knowledge),))
        if trades and not columns["eligible"][i]:
            continue
        quantity = columns[quantity_name][i] if quantity_name in columns else None
        if quantity is None:
            reason = Reason.NULL_FIELD if quantity_name in columns else Reason.ABSENT_INPUT
            volume_reasons = _reasons(volume_reasons, (reason,))
            notional_reasons = _reasons(notional_reasons, (reason,))
            continue
        volume += quantity
        if not quantity:
            continue
        amount = columns[price_name][i] if price_name in columns else None
        if amount is None:
            reason = Reason.NULL_FIELD if price_name in columns else Reason.ABSENT_INPUT
            notional_reasons = _reasons(notional_reasons, (reason,))
        else:
            notional += amount * quantity if trades else amount
    return volume, notional, _reasons(common, volume_reasons), _reasons(common, notional_reasons)


def compute_ef1(batches: tuple[CanonicalBatch, ...] | list[CanonicalBatch], config: ConfigSpec,
                *, entity: EntityKey) -> FeatureResult:
    """Compute exactly the three anchored outputs with original complete input bindings."""
    context = decode_ef1_context(config)
    if type(entity) is not EntityKey or entity.session_id != config.session.session_id:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "exact target entity required")
    label(entity.instrument_id)
    label(entity.session_id)
    if type(batches) not in (tuple, list) or len(batches) > 2:
        fail(ErrorCode.INVALID_SCHEMA, "bounded concrete present canonical batches required")
    expected_kind = DataKind.TRADE if context["selection"]["mode"] == "trades" else DataKind.BAR
    market: CanonicalBatch | None = None
    proof: CanonicalBatch | None = None
    for batch in batches:
        if type(batch) is not CanonicalBatch:
            fail(ErrorCode.INVALID_SCHEMA, "actual present CanonicalBatch required")
        if batch.kind == expected_kind and market is None and proof is None:
            market = batch
        elif batch.kind == DataKind.REFERENCE and proof is None:
            proof = batch
        else:
            fail(ErrorCode.INVALID_SCHEMA, "wrong/duplicate/reordered anchor role")
    if len({batch.metadata.source.input_id for batch in batches}) != len(batches):
        fail(ErrorCode.DUPLICATE, "distinct actual input bindings required")
    proof_status, proof_reasons = _proof_ready(proof, config, context, entity)
    del proof_status  # Reasons retain independent proof readiness without rewriting source inputs.
    bindings = tuple(InputBinding("anchor_provenance" if batch.kind == DataKind.REFERENCE else
                                 "trades" if expected_kind == DataKind.TRADE else "bars",
                                 batch.kind, batch.metadata) for batch in batches)
    metadata = ResultMetadata(config.session.namespace, entity.session_id, config.availability,
                              config.digest, bindings, "python-exact", __version__)
    expected: int | None = None
    observed = 0
    volume_reasons: tuple[Reason, ...]
    notional_reasons: tuple[Reason, ...]
    if market is None:
        volume, notional = 0, 0
        volume_reasons = notional_reasons = (Reason.ABSENT_INPUT,)
    else:
        columns = _market_admit(market, config, context, entity)
        expected, observed = market.metadata.coverage.expected, market.row_count
        volume, notional, volume_reasons, notional_reasons = _totals(market, columns, config)
    volume_reasons = _reasons(volume_reasons, proof_reasons)
    notional_reasons = _reasons(notional_reasons, proof_reasons)
    result_values: list[FeatureColumn] = []
    qualities: list[QualityRow] = []
    for definition in ef1_definitions(config):
        name = definition.feature_id.rsplit(".", 1)[1]
        reasons = volume_reasons if name == "volume" else _reasons(volume_reasons, notional_reasons)
        status, reasons = _ready(reasons)
        value: int | float | None = None
        if status == Status.AVAILABLE:
            checked_int64(volume)
            if name == "volume":
                value = volume
            elif name == "notional":
                value = checked_decimal128(notional)
            elif not volume:
                status, reasons = Status.NOT_APPLICABLE, (Reason.ZERO_DENOMINATOR,)
            else:
                checked_decimal128(notional)
                value = float(Fraction(notional, volume * 10 ** cast(PriceUnit, config.price_unit).scale))
        result_values.append(FeatureColumn(definition.feature_id, "v1", definition.dtype,
                                          definition.unit, (entity,), (value,)))
        qualities.append(QualityRow(entity, definition.feature_id, status, expected, observed, reasons))
    return FeatureResult(tuple(result_values), tuple(qualities), metadata)
