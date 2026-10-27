"""Pure comparison of the calculated regular close with a supplied same-session close; no acquisition or publication."""
from __future__ import annotations

from base64 import urlsafe_b64decode, urlsafe_b64encode
from dataclasses import asdict
from fractions import Fraction
import re
from typing import Any

from equity_feature_contracts import (
    CanonicalBatch, ConfigSpec, DataKind, EntityKey, ErrorCode, EvidenceRow,
    FeatureColumn, FeatureResult, InputBinding, QualityRow, Reason, ResultMetadata,
    Status, checked_decimal128, validate_batch,
)
from equity_features import __version__
from ._anchor import _columns
from ._context import decode_ef1_context, fail, label
from ._definitions import ef1_definitions
from ._path import _causal, _witness
from ._regular_bar_prices import _select_regular_bars

ROLES = ("calendar_provenance", "bars", "population_proof", "authoritative_close")
FACT_KIND = "ef1.close.authoritative"
# One reported reason per output: the first applicable entry wins, and the status follows it.
_PRIORITY = (Reason.ABSENT_INPUT, Reason.UNKNOWN_AVAILABILITY, Reason.FUTURE_KNOWLEDGE, Reason.NULL_FIELD,
             Reason.INELIGIBLE, Reason.GOVERNED_GAP, Reason.NO_ELIGIBLE_OBSERVATIONS, Reason.ZERO_DENOMINATOR)
_B64URL = re.compile("[A-Za-z0-9_-]+")


def _decode_part(part: str) -> str:
    """Reversible unpadded base64url of UTF8; a noncanonical spelling is not accepted."""
    if _B64URL.fullmatch(part) is None or len(part) % 4 == 1:
        fail(ErrorCode.INVALID_SCHEMA, "closed k1 reference grammar required")
    raw = urlsafe_b64decode(part + "=" * (-len(part) % 4))
    if urlsafe_b64encode(raw).rstrip(b"=").decode("ascii") != part:
        fail(ErrorCode.INVALID_SCHEMA, "reversible k1 reference grammar required")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        fail(ErrorCode.INVALID_SCHEMA, "UTF8 k1 reference component required")
    if not text.strip() or any(ord(c) < 32 or ord(c) == 127 or 0xD800 <= ord(c) <= 0xDFFF for c in text):
        fail(ErrorCode.INVALID_SCHEMA, "nonblank safe k1 reference component required")
    return text


def _scope_of(reference_id: Any) -> str:
    """Return the scope decoded from k1:B(scope):B(source_close_id), bounded before any label check."""
    if (type(reference_id) is not str or len(reference_id) > 128
            or len(reference_id.encode("utf-8", errors="surrogatepass")) > 512):
        fail(ErrorCode.INVALID_SCHEMA, "bounded k1 reference identity required")
    parts = reference_id.split(":")
    if len(parts) != 3 or parts[0] != "k1":
        fail(ErrorCode.INVALID_SCHEMA, "closed k1 reference grammar required")
    scope = _decode_part(parts[1])
    _decode_part(parts[2])
    return scope


def _admit(batch: CanonicalBatch, config: ConfigSpec, entity: EntityKey,
           scope_id: str) -> dict[str, tuple[Any, ...]]:
    """Structural admission of the supplied close; every contradiction refuses before assessment."""
    # Cardinality is counted before knowledge arbitration: a late or unknown duplicate still refuses.
    if batch.row_count > 1:
        fail(ErrorCode.DUPLICATE, "at most one authoritative close row")
    meta = batch.metadata
    if meta.namespace != config.session.namespace or meta.coverage.observed != batch.row_count:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "authoritative close namespace/population mismatch")
    if meta.ordering != "declared" or meta.duplicate_policy != "reject":
        fail(ErrorCode.INVALID_ORDER, "ordered unique authoritative close required")
    for text in (meta.namespace, *asdict(meta.source).values()):
        label(text)
    if meta.source.mapping_version != "ef1-reference-map1":
        fail(ErrorCode.INCOMPATIBLE_VERSION, "unsupported authoritative close mapping")
    if meta.price_unit != config.price_unit:
        fail(ErrorCode.INVALID_UNIT, "authoritative close unit must equal the config unit")
    if meta.adjustment != config.adjustment:
        fail(ErrorCode.UNSUPPORTED_ADJUSTMENT, "authoritative close basis must equal the config basis")
    cols = _columns(batch)
    if any(value is not None for name in ("factor_num", "factor_den") for value in cols.get(name, ())):
        fail(ErrorCode.INVALID_SCHEMA, "a close row carries no adjustment factor")
    for i in range(batch.row_count):
        scope = _scope_of(cols["reference_id"][i])
        for name in ("instrument_id", "session_id", "fact_kind"):
            label(cols[name][i])
        if cols["instrument_id"][i] != entity.instrument_id or cols["session_id"][i] != entity.session_id:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "one actual requested entity required")
        if cols["fact_kind"][i] != FACT_KIND:
            fail(ErrorCode.INVALID_SCHEMA, "authoritative close fact family mismatch")
        if scope != scope_id:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "authoritative close scope differs from the selected scope")
        if cols["effective_start_ns"][i] != config.session.close_ns:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "authoritative close must be effective at the actual session close")
        end = cols.get("effective_end_ns", (None,) * batch.row_count)[i]
        if end is not None and end <= cols["effective_start_ns"][i]:
            fail(ErrorCode.BOUNDS, "invalid authoritative close effective bounds")
        # The revision binding is the row's own text; it must be the batch snapshot.
        if cols.get("text", (None,) * batch.row_count)[i] != meta.source.snapshot_id:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "authoritative close revision differs from snapshot")
    validate_batch(batch, required_fields=())
    return cols


def _first(reasons: set[Reason]) -> tuple[Reason, ...]:
    return next(((reason,) for reason in _PRIORITY if reason in reasons), ())


def _status(reasons: tuple[Reason, ...]) -> Status:
    if not reasons:
        return Status.AVAILABLE
    if reasons[0] == Reason.GOVERNED_GAP:
        return Status.INCOMPLETE_COVERAGE
    if reasons[0] in (Reason.ZERO_DENOMINATOR, Reason.NO_ELIGIBLE_OBSERVATIONS):
        return Status.NOT_APPLICABLE
    return Status.MISSING_INPUT


def compute_reference_close(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None] | list[CanonicalBatch],
                            config: ConfigSpec, *, entity: EntityKey) -> FeatureResult:
    """Compare the exact calculated close with the supplied close; the supplied close is the denominator."""
    context = decode_ef1_context(config)
    if context["producer"] != "reference_close":
        fail(ErrorCode.INVALID_CONFIG, "wrong close-reconciliation producer")
    if type(entity) is not EntityKey or entity.session_id != config.session.session_id:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "exact target entity required")
    label(entity.instrument_id)
    label(entity.session_id)
    if type(batches) not in (tuple, list) or len(batches) != 4:
        fail(ErrorCode.INVALID_SCHEMA, "four fixed nullable close-reconciliation slots required")
    for batch, kind in zip(batches, (DataKind.REFERENCE, DataKind.BAR, DataKind.REFERENCE, DataKind.REFERENCE)):
        if batch is not None and (type(batch) is not CanonicalBatch or batch.kind != kind):
            fail(ErrorCode.INVALID_SCHEMA, "wrong close-reconciliation slot kind")
    present = [b for b in batches if b is not None]
    if len({b.metadata.source.input_id for b in present}) != len(present):
        fail(ErrorCode.DUPLICATE, "distinct actual close-reconciliation input IDs required")
    calendar, bars, proof, close = batches
    assert config.price_unit is not None
    selection_context = context["selection"]
    # A prefix before the actual regular close is provisional and never comparable (it joins as a governed gap).
    early = config.availability.market_cutoff_ns < config.session.close_ns
    provisional = (Reason.GOVERNED_GAP,) if early else ()
    calculated = _select_regular_bars(calendar, bars, proof, config, context, entity, provisional)
    cols = {} if close is None else _admit(close, config, entity, selection_context["scope_id"])
    num, den = selection_context["tolerance_bps_num"], selection_context["tolerance_bps_den"]

    calc_status, calc_reasons = calculated.statuses[0]
    calc_ready = calc_status == Status.AVAILABLE
    row = close is not None and close.row_count == 1
    price: int | None = cols["price"][0] if row and "price" in cols else None
    known: int | None = cols.get("known_at_ns", (None,))[0] if row else None
    causal = row and not _causal(known, config)
    complete = close is not None and close.metadata.coverage.complete
    # Reference side. A non-causal or incompletely covered row is not admitted, so its price is never inspected.
    reference: set[Reason] = set()
    if not row:
        reference.add(Reason.ABSENT_INPUT)
    else:
        reference.update(_causal(known, config))
    # Amendment 1: a close effective after the market cutoff lies beyond the market bound and is not projected.
    if close is not None and not complete:
        reference.add(Reason.GOVERNED_GAP)
    invalid = False
    if row and causal and complete and not early:
        if price is None:
            reference.add(Reason.NULL_FIELD)
        elif price <= 0:
            invalid = True
            reference.add(Reason.INELIGIBLE)
    state_reasons = set(reference)  # the provisional gap below is the calculated side's condition, not the reference's
    if close is not None and early:
        reference.add(Reason.GOVERNED_GAP)
    supplied_reasons = _first(reference)
    # A zero supplied close is a zero denominator for the arithmetic outputs, not merely an ineligible price.
    reference_arithmetic = set(reference)
    if invalid and price == 0:
        reference_arithmetic = (reference_arithmetic - {Reason.INELIGIBLE}) | {Reason.ZERO_DENOMINATOR}
    arithmetic = set(calc_reasons) | reference_arithmetic
    arithmetic_reasons = _first(arithmetic)
    admitted = not reference

    bps: float | None = None
    within: bool | None = None
    if not arithmetic:
        assert price is not None and calc_ready
        calculated_close = calculated.coefficients[0]
        assert calculated_close is not None
        difference = abs(calculated_close - price)
        # One correctly rounded binary64 conversion of the exact rational; the verdict stays exact integer arithmetic.
        bps = float(Fraction(10000 * difference, price))
        within = 10000 * difference * den <= num * price
    if Reason.FUTURE_KNOWLEDGE in reference:
        state = "reference_future"
    elif invalid:
        state = "reference_invalid"
    elif state_reasons:
        state = "reference_unavailable"
    elif not calc_ready:
        state = "calculated_unavailable"
    else:
        state = "within_tolerance" if within else "outside_tolerance"

    bindings = tuple(sorted((InputBinding(role, batch.kind, batch.metadata)
        for role, batch in zip(ROLES, batches) if batch is not None), key=lambda binding: binding.role))
    metadata = ResultMetadata(config.session.namespace, entity.session_id, config.availability, config.digest,
        bindings, "python-exact", __version__, evidence_limit=7)
    expected_close = None if close is None else close.metadata.coverage.expected
    observed_close = 0 if close is None else close.row_count
    ready_operands = int(calc_ready) + int(admitted)
    bars_row = calculated.rows[0]
    value_for = {
        "reference.close.absolute_difference_bps": bps,
        "reference.close.comparison_state": state,
        "reference.close.supplied_price": None if supplied_reasons or price is None else checked_decimal128(price),
        "reference.close.within_tolerance": within,
    }
    reasons_for = {
        "reference.close.absolute_difference_bps": arithmetic_reasons,
        "reference.close.comparison_state": (),
        "reference.close.supplied_price": supplied_reasons,
        "reference.close.within_tolerance": arithmetic_reasons,
    }
    counts_for = {
        "reference.close.absolute_difference_bps": (2, ready_operands),
        "reference.close.comparison_state": (1, 1),
        "reference.close.supplied_price": (expected_close, observed_close),
        "reference.close.within_tolerance": (2, ready_operands),
    }
    output_columns: list[FeatureColumn] = []
    quality: list[QualityRow] = []
    evidence: list[EvidenceRow] = []
    for definition in ef1_definitions(config):
        name = definition.feature_id
        reasons = reasons_for[name]
        output_columns.append(FeatureColumn(name, "v1", definition.dtype, definition.unit, (entity,), (value_for[name],)))
        expected, observed = counts_for[name]
        quality.append(QualityRow(entity, name, _status(reasons), expected, observed, reasons))
        # Numerical outputs cite witnesses only when their value is available; the state cites every causal operand.
        if name == "reference.close.comparison_state":
            cite_bars, cite_close = calc_ready, causal and not early
        else:
            cite_bars = cite_close = value_for[name] is not None
            if name == "reference.close.supplied_price":
                cite_bars = False
        if cite_bars:
            assert bars is not None and bars_row is not None
            evidence.append(_witness(bars, bars_row, entity, name))
        if cite_close:
            assert close is not None
            evidence.append(EvidenceRow(entity, name, close.metadata.source.input_id, cols["reference_id"][0],
                cols["effective_start_ns"][0], known, cols["effective_start_ns"][0],
                cols.get("effective_end_ns", (None,))[0]))
    return FeatureResult(tuple(output_columns), tuple(quality), metadata, tuple(evidence))
