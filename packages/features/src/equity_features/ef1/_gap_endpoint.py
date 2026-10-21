"""Pure source-neutral supplied-population gap endpoints; no acquisition or publication."""
from __future__ import annotations

from dataclasses import asdict
from fractions import Fraction
import hashlib
import json
import re
from typing import Any

from equity_feature_contracts import (
    CanonicalBatch, ConfigSpec, ContractError, DataKind, EntityKey, ErrorCode,
    FeatureColumn, FeatureResult, InputBinding, QualityRow, Reason, ResultMetadata,
    Status, checked_int64, validate_batch,
)
from equity_features import __version__
from ._anchor import _columns, _ready, _reasons
from ._clock import _calendar_ready
from ._context import decode_ef1_context, fail, label
from ._definitions import ef1_definitions
from ._path import _causal, _market, _witness

ROLES = ("calendar_provenance", "path", "prior_close", "population_proof")
_PROOF_COLUMNS = ("instrument_id", "session_id", "reference_id", "fact_kind",
                  "effective_start_ns", "effective_end_ns", "text", "known_at_ns")
_KEYS = {"version", "profile_id", "namespace", "instrument_id", "session_id", "start_ns", "end_ns",
         "market_cutoff_ns", "knowledge_cutoff_ns", "sampling", "eligibility_policy",
         "include_opening_auction", "include_closing_auction", "path_source", "proof_source",
         "row_count", "complete", "price_unit", "adjustment", "population_sha256"}


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            fail(ErrorCode.DUPLICATE, "duplicate population proof key")
        result[key] = value
    return result


def _tree(value: Any, depth: int = 0) -> None:
    if depth > 8:
        fail(ErrorCode.BOUNDS, "population proof nesting limit")
    if type(value) in (dict, list):
        if len(value) > 64:
            fail(ErrorCode.BOUNDS, "population proof collection limit")
        for item in value.values() if type(value) is dict else value:
            _tree(item, depth + 1)
    elif type(value) is str:
        label(value)
    elif value is not None and type(value) not in (int, bool):
        fail(ErrorCode.INVALID_SCHEMA, "population proof exact scalar required")


def _parse(text: Any) -> dict[str, Any]:
    if type(text) is not str or not text.isascii():
        fail(ErrorCode.INVALID_SCHEMA, "ASCII population proof required")
    if len(text) > 4096:
        fail(ErrorCode.BOUNDS, "population proof text limit")
    try:
        raw = json.loads(text, object_pairs_hook=_pairs,
                         parse_constant=lambda _: fail(ErrorCode.INVALID_SCHEMA, "nonfinite proof scalar"))
    except ContractError:
        raise
    except (ValueError, TypeError, RecursionError):
        fail(ErrorCode.INVALID_SCHEMA, "invalid population proof JSON")
    _tree(raw)
    if type(raw) is not dict or set(raw) != _KEYS or _json(raw) != text:
        fail(ErrorCode.INVALID_SCHEMA, "closed canonical population proof required")
    for name in ("version", "profile_id", "namespace", "instrument_id", "session_id", "sampling",
                 "eligibility_policy", "population_sha256"):
        if type(raw[name]) is not str:
            fail(ErrorCode.INVALID_SCHEMA, "exact proof string required")
    for name in ("start_ns", "end_ns", "market_cutoff_ns", "knowledge_cutoff_ns", "row_count"):
        if type(raw[name]) is not int:
            fail(ErrorCode.INVALID_SCHEMA, "exact proof integer required")
        checked_int64(raw[name])
    if raw["row_count"] < 0:
        fail(ErrorCode.INVALID_SCHEMA, "negative proof count")
    for name in ("complete", "include_opening_auction", "include_closing_auction"):
        if type(raw[name]) is not bool:
            fail(ErrorCode.INVALID_SCHEMA, "exact proof Boolean required")
    for name in ("path_source", "proof_source"):
        obj = raw[name]
        if type(obj) is not dict or set(obj) != {"source_id", "snapshot_id", "mapping_version", "input_id"} or any(type(v) is not str for v in obj.values()):
            fail(ErrorCode.INVALID_SCHEMA, "exact full proof binding required")
    unit = raw["price_unit"]
    if type(unit) is not dict or set(unit) != {"scale", "currency"} or type(unit["scale"]) is not int or type(unit["currency"]) is not str:
        fail(ErrorCode.INVALID_SCHEMA, "exact proof unit required")
    adj = raw["adjustment"]
    if type(adj) is not dict or set(adj) != {"basis", "policy_version", "action_snapshot", "anchor"} or any(type(v) is not str for v in adj.values()):
        fail(ErrorCode.INVALID_SCHEMA, "exact proof adjustment required")
    if re.fullmatch("[0-9a-f]{64}", raw["population_sha256"]) is None:
        fail(ErrorCode.INVALID_SCHEMA, "exact population digest required")
    if (raw["version"], raw["profile_id"]) != ("ef1-gap-population1", "gap-membership-asof1"):
        fail(ErrorCode.INCOMPATIBLE_VERSION, "unsupported population protocol")
    return raw


def _projection(path: CanonicalBatch) -> str:
    cols = _columns(path)
    rows: list[list[Any]] = []
    if path.kind == DataKind.TRADE:
        names = ["instrument_id", "session_id", "event_ns", "order_key", "event_id", "eligible", "condition_present", "condition"]
        for i in range(path.row_count):
            rows.append([cols[n][i] for n in names[:6]] + ["condition" in cols, cols.get("condition", (None,) * path.row_count)[i]])
    else:
        names = ["instrument_id", "session_id", "start_ns", "end_ns", "volume_present", "volume_class"]
        for i in range(path.row_count):
            volume = cols.get("volume", (None,) * path.row_count)[i]
            rows.append([cols[n][i] for n in names[:4]] + ["volume" in cols, "unknown" if volume is None else "positive" if volume > 0 else "zero"])
    return hashlib.sha256(_json({"version": "ef1-gap-membership-projection1", "kind": path.kind.value,
        "membership_columns": names, "rows": rows}).encode("ascii")).hexdigest()


def _population(proof: CanonicalBatch | None, path: CanonicalBatch | None, config: ConfigSpec,
                entity: EntityKey, sampling: str) -> tuple[Reason, ...]:
    if proof is None:
        return (Reason.ABSENT_INPUT,)
    meta = proof.metadata
    if meta.namespace != config.session.namespace or meta.coverage.observed != proof.row_count:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "proof namespace/population mismatch")
    if meta.ordering != "declared" or meta.duplicate_policy != "reject":
        fail(ErrorCode.INVALID_ORDER, "ordered unique proof required")
    for text in (meta.namespace, *asdict(meta.source).values()):
        label(text)
    for column in proof.columns:
        if column.name != "text":
            for item in column.values:
                if type(item) is str:
                    label(item)
    validate_batch(proof, required_fields=())
    if tuple(c.name for c in proof.columns) != _PROOF_COLUMNS or proof.row_count > 1:
        fail(ErrorCode.INVALID_SCHEMA, "exact one-row proof schema required")
    if meta.price_unit is not None:
        fail(ErrorCode.INVALID_UNIT, "population proof has no price unit")
    if meta.adjustment != config.adjustment:
        fail(ErrorCode.UNSUPPORTED_ADJUSTMENT, "population proof adjustment mismatch")
    if meta.scope is not None or meta.interval_coverage or meta.sampling != "none" or meta.quantity_unit != "shares":
        fail(ErrorCode.INVALID_SCHEMA, "population proof metadata shape mismatch")
    if not proof.row_count:
        return (Reason.ABSENT_INPUT,)
    cols = _columns(proof)
    raw = _parse(cols["text"][0])
    if cols["fact_kind"][0] != "ef1.gap.population.v1":
        fail(ErrorCode.INVALID_SCHEMA, "population fact family mismatch")
    assert config.price_unit is not None  # endpoint decoder requires explicit unit
    if raw["price_unit"] != asdict(config.price_unit):
        fail(ErrorCode.INVALID_UNIT, "population payload unit mismatch")
    if raw["adjustment"] != asdict(config.adjustment):
        fail(ErrorCode.UNSUPPORTED_ADJUSTMENT, "population payload adjustment mismatch")
    expected = {"namespace": config.session.namespace, "instrument_id": entity.instrument_id,
        "session_id": entity.session_id, "start_ns": config.session.open_ns,
        "end_ns": config.availability.market_cutoff_ns, "market_cutoff_ns": config.availability.market_cutoff_ns,
        "knowledge_cutoff_ns": config.availability.knowledge_cutoff_ns, "sampling": sampling,
        "eligibility_policy": "supplied_path", "include_opening_auction": config.session.include_opening_auction,
        "include_closing_auction": config.session.include_closing_auction, "proof_source": asdict(meta.source)}
    if any(raw[k] != v for k, v in expected.items()) or cols["instrument_id"][0] != entity.instrument_id or cols["session_id"][0] != entity.session_id or (
            cols["effective_start_ns"][0], cols["effective_end_ns"][0]) != (config.session.open_ns, config.availability.market_cutoff_ns):
        fail(ErrorCode.INCONSISTENT_IDENTITY, "population request/proof identity mismatch")
    if cols["reference_id"][0] != "pop1:" + hashlib.sha256(cols["text"][0].encode("ascii")).hexdigest():
        fail(ErrorCode.INCONSISTENT_IDENTITY, "population reference hash mismatch")
    if path is not None and (raw["path_source"] != asdict(path.metadata.source) or raw["row_count"] != path.row_count or
            raw["complete"] != path.metadata.coverage.complete or raw["population_sha256"] != _projection(path)):
        fail(ErrorCode.INCONSISTENT_IDENTITY, "population delivered membership mismatch")
    return _reasons(() if meta.coverage.complete else (Reason.GOVERNED_GAP,), _causal(cols["known_at_ns"][0], config))


def _operand(batch: CanonicalBatch | None, index: int, field: str, config: ConfigSpec) -> tuple[int | None, tuple[Reason, ...]]:
    if batch is None:
        return None, (Reason.ABSENT_INPUT,)
    cols = _columns(batch)
    value = cols.get(field, (None,) * batch.row_count)[index]
    reasons = _causal(cols.get("known_at_ns", (None,) * batch.row_count)[index], config)
    if value is None:
        reasons = _reasons(reasons, (Reason.NULL_FIELD if field in cols else Reason.ABSENT_INPUT,))
    return value, reasons


def compute_gap_endpoint(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None] | list[CanonicalBatch],
                         config: ConfigSpec, *, entity: EntityKey) -> FeatureResult:
    context = decode_ef1_context(config)
    if context["producer"] != "path_gap_endpoint":
        fail(ErrorCode.INVALID_CONFIG, "wrong endpoint producer")
    if type(entity) is not EntityKey or entity.session_id != config.session.session_id:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "exact target entity required")
    label(entity.instrument_id)
    label(entity.session_id)
    sampling = context["selection"]["sampling"]
    kind = DataKind.TRADE if sampling == "eligible_trade" else DataKind.BAR
    if type(batches) not in (tuple, list) or len(batches) != 4:
        fail(ErrorCode.INVALID_SCHEMA, "four fixed nullable endpoint slots required")
    for batch, expected_kind in zip(batches, (DataKind.REFERENCE, kind, DataKind.DAILY, DataKind.REFERENCE)):
        if batch is not None and (type(batch) is not CanonicalBatch or batch.kind != expected_kind):
            fail(ErrorCode.INVALID_SCHEMA, "wrong endpoint slot kind")
    present = [b for b in batches if b is not None]
    if len({b.metadata.source.input_id for b in present}) != len(present):
        fail(ErrorCode.DUPLICATE, "distinct actual endpoint input IDs required")
    calendar, path, prior, proof = batches
    # REFERENCE kinds do not distinguish these roles. Check their closed family
    # before the legacy calendar validator sees the population JSON text.
    for reference, family in ((calendar, "ef1.calendar.provenance"), (proof, "ef1.gap.population.v1")):
        if reference is not None and any(value != family for value in _columns(reference).get("fact_kind", ())):
            fail(ErrorCode.INVALID_SCHEMA, "wrong endpoint reference role family")
    _, reasons = _calendar_ready(calendar, config, context, entity)
    cols: dict[str, tuple[Any, ...]] = {}
    if path is None:
        reasons = _reasons(reasons, (Reason.ABSENT_INPUT,))
    else:
        cols = _market(path, config, entity, config.session.open_ns, config.availability.market_cutoff_ns)
        if path.metadata.interval_coverage:
            fail(ErrorCode.INVALID_SCHEMA, "endpoint path interval coverage must be empty")
        for i in range(path.row_count):
            if kind == DataKind.TRADE:
                event = cols["event_ns"][i]
                condition = cols.get("condition", (None,) * path.row_count)[i]
                if not config.session.open_ns <= event < config.availability.market_cutoff_ns or condition == "closing_auction" or condition == "opening_auction" and not (event == config.session.open_ns and config.session.include_opening_auction):
                    fail(ErrorCode.BOUNDS, "endpoint trade outside exact prefix")
            elif cols["start_ns"][i] < config.session.open_ns or cols["end_ns"][i] > config.availability.market_cutoff_ns:
                fail(ErrorCode.BOUNDS, "endpoint bar outside exact prefix")
        if not path.metadata.coverage.complete:
            reasons = _reasons(reasons, (Reason.GOVERNED_GAP,))
    if prior is not None:
        if prior.row_count != 1:
            fail(ErrorCode.INVALID_SCHEMA, "exact explicit prior row required")
        slot = context["calendar"]["sessions"][0]
        pc = _market(prior, config, EntityKey(entity.instrument_id, slot[0]), slot[2], slot[3])
        if (pc["start_ns"][0], pc["end_ns"][0]) != (slot[2], slot[3]):
            fail(ErrorCode.INCONSISTENT_IDENTITY, "explicit prior interval mismatch")
    reasons = _reasons(reasons, _population(proof, path, config, entity, sampling))
    values: list[float | None] = [None, None]
    statuses = [_ready(reasons), _ready(reasons)]
    witnesses: list[list[tuple[CanonicalBatch, int]]] = [[], []]
    if not reasons:
        assert path is not None
        membership = [cols["eligible"][i] if kind == DataKind.TRADE else
            None if cols.get("volume", (None,) * path.row_count)[i] is None else cols["volume"][i] > 0 for i in range(path.row_count)]
        selected = [i for i, member in enumerate(membership) if member is True]
        unknown = [i for i, member in enumerate(membership) if member is None]
        missing_member = (Reason.NULL_FIELD if "volume" in cols else Reason.ABSENT_INPUT,)
        if not selected and not unknown:
            statuses = [(Status.NOT_APPLICABLE, (Reason.NO_ELIGIBLE_OBSERVATIONS,))] * 2
        elif not selected or unknown and unknown[0] < selected[0]:
            statuses = [_ready(missing_member)] * 2
        else:
            first, last = selected[0], selected[-1]
            opening, oreasons = _operand(path, first, "price" if kind == DataKind.TRADE else "open", config)
            previous, preasons = _operand(prior, 0, "close", config)
            if prior is not None and not prior.metadata.coverage.complete:
                preasons = _reasons(preasons, (Reason.GOVERNED_GAP,))
            shared = _reasons(oreasons, preasons)
            statuses = [_ready(shared)] * 2
            if not shared:
                assert opening is not None and previous is not None and prior is not None
                gap = opening - previous
                values[1] = float(Fraction(gap, previous))
                witnesses[1] = [(path, first), (prior, 0)]
                if gap == 0:
                    statuses[0] = (Status.NOT_APPLICABLE, (Reason.ZERO_DENOMINATOR,))
                else:
                    final, freasons = _operand(path, last, "price" if kind == DataKind.TRADE else "close", config)
                    if unknown and unknown[-1] > last:
                        freasons = missing_member
                    statuses[0] = _ready(freasons)
                    if not freasons:
                        assert final is not None
                        values[0] = float(max(Fraction(0), min(Fraction(1), Fraction(opening - final, gap))))
                        witnesses[0] = [(path, first), (prior, 0), (path, last)]
    expected_count = None if path is None or path.metadata.coverage.expected is None else checked_int64(path.metadata.coverage.expected + 1)
    observed = checked_int64((0 if path is None else path.row_count) + (0 if prior is None else 1))
    bindings = tuple(InputBinding(role, b.kind, b.metadata) for role, b in zip(ROLES, batches) if b is not None)
    metadata = ResultMetadata(config.session.namespace, entity.session_id, config.availability, config.digest,
        bindings, "python-exact", __version__, evidence_limit=5)
    output: list[FeatureColumn] = []
    quality: list[QualityRow] = []
    evidence = {}
    for i, definition in enumerate(ef1_definitions(config)):
        output.append(FeatureColumn(definition.feature_id, "v1", definition.dtype, definition.unit, (entity,), (values[i],)))
        quality.append(QualityRow(entity, definition.feature_id, statuses[i][0], expected_count, observed, statuses[i][1]))
        for b, index in witnesses[i]:
            row = _witness(b, index, entity, definition.feature_id)
            evidence[(row.feature_id, row.input_id, row.row_id)] = row
    return FeatureResult(tuple(output), tuple(quality), metadata, tuple(evidence[key] for key in sorted(evidence)))
