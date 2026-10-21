"""Pure original-population observable-v2 admission and ordered reductions."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict
import hashlib
import json
import re
from typing import Any, cast

from equity_feature_contracts import (
    CanonicalBatch, ConfigSpec, DataKind, EntityKey, ErrorCode, EvidenceRow, FeatureColumn,
    FeatureResult, InputBinding, QualityRow, Reason, ResultMetadata, Status, checked_int64, validate_batch,
)
from equity_features import __version__
from ._anchor import _columns, _reasons
from ._context import calendar_proof_id, decode_ef1_context, fail
from ._definitions import ef1_definitions
from ._observable_context import TOKEN

Columns = dict[str, tuple[Any, ...]]
Row = tuple[str, int]
OPEN_ROLES = ("calendar_provenance", "market_prefix", "source_capability", "trades")
HISTORY_ROLES = ("calendar_provenance", "history_events", "history_prefix", "history_seed", "source_capability")


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _hash(value: Any) -> str:
    return hashlib.sha256(_json(value).encode("ascii")).hexdigest()


def _decimal(text: str, *, signed: bool = False) -> int:
    if re.fullmatch(r"(?:0|-[1-9][0-9]*|[1-9][0-9]*)" if signed else r"(?:0|[1-9][0-9]*)", text) is None:
        fail(ErrorCode.INVALID_SCHEMA, "canonical original integer text required")
    # Bounded before int conversion (Python's arbitrary integer parser is not an input bound).
    if len(text) > 20:
        fail(ErrorCode.OVERFLOW, "original integer exceeds int64")
    return checked_int64(int(text))


def _knowledge(columns: Columns, index: int, config: ConfigSpec) -> tuple[Reason, ...]:
    known = columns.get("known_at_ns", (None,) * (index + 1))[index]
    return (Reason.UNKNOWN_AVAILABILITY,) if known is None else (
        (Reason.FUTURE_KNOWLEDGE,) if known > config.availability.knowledge_cutoff_ns else ())


def _status(reasons: tuple[Reason, ...]) -> Status:
    if not reasons:
        return Status.AVAILABLE
    if any(r not in (Reason.GOVERNED_GAP, Reason.NO_ELIGIBLE_OBSERVATIONS) for r in reasons):
        return Status.MISSING_INPUT
    return Status.INCOMPLETE_COVERAGE if Reason.GOVERNED_GAP in reasons else Status.NOT_APPLICABLE


def _admit(batch: CanonicalBatch, config: ConfigSpec, entity: EntityKey) -> Columns:
    m = batch.metadata
    if m.namespace != config.session.namespace or m.coverage.observed != batch.row_count:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "actual observable namespace/population mismatch")
    if m.ordering != "declared" or m.duplicate_policy != "reject":
        fail(ErrorCode.INVALID_ORDER, "original declared unique population required")
    if m.sampling != "none" or m.quantity_unit != "shares":
        fail(ErrorCode.INVALID_UNIT, "original observable units/sampling required")
    for text in (m.namespace, m.source.source_id, m.source.snapshot_id, m.source.mapping_version, m.source.input_id):
        if len(text) > 256 or not text.isascii() or any(ord(x) < 32 or ord(x) == 127 for x in text):
            fail(ErrorCode.BOUNDS, "bounded original ASCII observable identity required")
    c = _columns(batch)
    for column in batch.columns:
        for value in column.values:
            if type(value) is str and (len(value) > 256 or not value.isascii() or any(ord(x) < 32 or ord(x) == 127 for x in value)):
                fail(ErrorCode.BOUNDS, "bounded original ASCII observable cell required")
    if any(x != entity.instrument_id for x in c["instrument_id"]) or any(x != entity.session_id for x in c["session_id"]):
        fail(ErrorCode.INCONSISTENT_IDENTITY, "actual observable entity mismatch")
    validate_batch(batch, required_fields=())
    if batch.kind == DataKind.REFERENCE:
        if any(any(v is not None for v in c.get(name, ())) for name in ("price", "factor_num", "factor_den")):
            fail(ErrorCode.INVALID_SCHEMA, "unused observable proof payload must be null")
    elif m.price_unit != config.price_unit or m.adjustment != config.adjustment:
        fail(ErrorCode.INVALID_UNIT, "observable market representation mismatch")
    return c


def _descriptor(context: Mapping[str, Any], config: ConfigSpec, entity: EntityKey,
                target: CanonicalBatch | None, history: bool) -> dict[str, Any]:
    s = context["selection"]
    incoming = asdict(target.metadata.source) if target is not None else {
        "source_id": s["source_id"], "snapshot_id": s["source_snapshot"],
        "mapping_version": s["mapping_version"], "input_id": "history_events" if history else "trades"}
    # Frozen contexts are recursively immutable; JSON uses detached plain trees.
    plain = json.loads(cast(str, config.parameters[0].value))
    return {"calendar_hash": _hash(plain["calendar"]), "entity": asdict(entity), "incoming_source": incoming,
        "population": s["population"], "producer_family": "status_history" if history else "opening_trade",
        "publisher": s["publisher"], "epoch": s["epoch"], "start_ns": config.session.open_ns,
        "end_ns": min(config.availability.market_cutoff_ns, config.session.close_ns),
        "knowledge_cutoff_ns": config.availability.knowledge_cutoff_ns, "selection_hash": _hash(plain["selection"])}


def _events(batch: CanonicalBatch, c: Columns, context: Mapping[str, Any], start: int, end: int) -> list[tuple[str, str]]:
    actions = dict(context["selection"]["action_map"])
    parsed: list[tuple[str, str]] = []
    ids: set[str] = set()
    orders: set[int] = set()
    for i in range(batch.row_count):
        identity = c["reference_id"][i].split("~")
        if len(identity) != 5 or identity[0] != "oe2" or any(TOKEN.fullmatch(x) is None for x in (identity[1], identity[2], identity[4])):
            fail(ErrorCode.INVALID_SCHEMA, "closed original physical-event identity required")
        if identity[1:3] != [context["selection"]["publisher"], context["selection"]["epoch"]]:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "original publisher/epoch mismatch")
        if re.fullmatch(r"[0-9]{19}", identity[3]) is None:
            fail(ErrorCode.INVALID_SCHEMA, "original fixed-width order required")
        order = checked_int64(int(identity[3]))
        if identity[4] in ids or order in orders:
            fail(ErrorCode.DUPLICATE, "repeated original identity/order")
        ids.add(identity[4]); orders.add(order)
        if c["fact_kind"][i] != "ef1.observable.status_event" or c.get("effective_end_ns", (None,) * batch.row_count)[i] is not None:
            fail(ErrorCode.INVALID_SCHEMA, "closed physical event kind/end required")
        if not start <= c["effective_start_ns"][i] < end:
            fail(ErrorCode.BOUNDS, "event outside exact original history prefix")
        text = c.get("text", (None,) * batch.row_count)[i]
        tokens = text.split("~") if type(text) is str else []
        if len(tokens) != 8 or tokens[0] != "ov2" or any(re.fullmatch(r"[0-9]{5}", x) is None or int(x) > 65535 for x in tokens[1:4]):
            fail(ErrorCode.INVALID_SCHEMA, "closed original physical-event payload required")
        if any(x != "--" and re.fullmatch(r"[0-7][0-9a-f]", x) is None for x in tokens[4:7]):
            fail(ErrorCode.INVALID_SCHEMA, "original ASCII flags required")
        if tokens[7] != "u":
            _decimal(tokens[7], signed=True)
        parsed.append((actions.get(int(tokens[1]), "unknown"), tokens[6]))
    return parsed


def compute_observable(batches: Any, config: ConfigSpec, *, entity: EntityKey) -> FeatureResult:
    context = decode_ef1_context(config)
    history = context["producer"] == "status_history"
    slots = HISTORY_ROLES if history else OPEN_ROLES
    if type(entity) is not EntityKey or entity.session_id != config.session.session_id:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "exact observable entity required")
    if type(batches) not in (tuple, list) or len(batches) != len(slots):
        fail(ErrorCode.INVALID_SCHEMA, "exact nullable observable tuple required")
    if any(b is not None and (type(b) is not CanonicalBatch or b.kind != (DataKind.TRADE if r == "trades" else DataKind.REFERENCE))
           for r, b in zip(slots, batches)):
        fail(ErrorCode.INVALID_SCHEMA, "exact observable slot type required")
    roles = {r: b for r, b in zip(slots, batches) if b is not None}
    if sum(b.row_count for b in roles.values() if b.kind == DataKind.REFERENCE) > 4096 or any(b.row_count > 4096 for b in roles.values()):
        fail(ErrorCode.BOUNDS, "observable population bound exceeded")
    columns = {r: _admit(b, config, entity) for r, b in roles.items()}
    selection = context["selection"]
    for role, batch in roles.items():
        source = batch.metadata.source
        if role == "calendar_provenance":
            if source.snapshot_id != context["calendar"]["revision"]:
                fail(ErrorCode.INCONSISTENT_IDENTITY, "actual calendar revision mismatch")
            if source.mapping_version != "ef1-reference-map1":
                fail(ErrorCode.INCOMPATIBLE_VERSION, "calendar mapping mismatch")
        elif (source.source_id, source.snapshot_id, source.mapping_version) != (
                selection["source_id"], selection["source_snapshot"], selection["mapping_version"]):
            fail(ErrorCode.INCONSISTENT_IDENTITY, "actual original source/revision/mapping mismatch")
    start, cutoff = config.session.open_ns, config.availability.market_cutoff_ns
    end = min(cutoff, config.session.close_ns)
    target_role, prefix_role = ("history_events", "history_prefix") if history else ("trades", "market_prefix")
    target = roles.get(target_role)
    descriptor = _descriptor(context, config, entity, target, history)
    digest = _hash(descriptor)
    proof_reasons: dict[str, tuple[Reason, ...]] = {}
    texts: dict[str, str] = {}
    for role in slots:
        if role in (target_role,):
            continue
        batch = roles.get(role)
        if batch is None or batch.row_count == 0:
            proof_reasons[role] = (Reason.ABSENT_INPUT,)
            continue
        if batch.row_count != 1:
            fail(ErrorCode.INVALID_SCHEMA, "one original proof row required")
        c = columns[role]
        identity, kind, text = c["reference_id"][0], c["fact_kind"][0], c.get("text", (None,))[0]
        lo, hi = c["effective_start_ns"][0], c.get("effective_end_ns", (None,))[0]
        if role == "calendar_provenance":
            if identity != calendar_proof_id(context):
                fail(ErrorCode.INCONSISTENT_IDENTITY, "calendar hash mismatch")
            if kind != "ef1.calendar.provenance" or text != "supplied_schedule":
                fail(ErrorCode.INVALID_SCHEMA, "closed calendar proof required")
            cal = context["calendar"]
            if hi is None or lo > min([r[2] for r in cal["sessions"]] + [r[1] for r in cal["segments"]]) or hi < max([r[3] for r in cal["sessions"]] + [r[2] for r in cal["segments"]]):
                fail(ErrorCode.BOUNDS, "calendar proof must cover supplied schedule")
        else:
            prefix = "oc2" if role == "source_capability" else ("os2" if role == "history_seed" else "op2")
            parts = identity.split("~")
            expected_digest = _hash({"domain": "seed", "history_descriptor": descriptor}) if role == "history_seed" else digest
            if len(parts) != 3 or parts[0] != prefix or re.fullmatch(r"[0-9a-f]{64}", parts[1]) is None or TOKEN.fullmatch(parts[2]) is None:
                fail(ErrorCode.INVALID_SCHEMA, "closed original proof identity required")
            if parts[1] != expected_digest:
                fail(ErrorCode.INCONSISTENT_IDENTITY, "proof does not bind exact selected original target")
            expected_kind = "ef1.observable." + ("capability" if role == "source_capability" else role)
            if kind != expected_kind:
                fail(ErrorCode.INVALID_SCHEMA, "wrong observable proof family")
            if role == prefix_role:
                if (lo, hi) != (start, end):
                    fail(ErrorCode.INCONSISTENT_IDENTITY, "exact prefix interval required")
                p = text.split("~") if type(text) is str else []
                if len(p) != 3 or p[0] != "pv2" or p[2] not in ("complete", "partial") or (p[1] == "u" and p[2] != "partial"):
                    fail(ErrorCode.INVALID_SCHEMA, "closed population certificate required")
                if p[1] != "u":
                    _decimal(p[1])
            elif role == "source_capability":
                if text not in ("opening_ready", "history_ready", "missing_identity", "missing_order", "missing_payload", "unavailable"):
                    fail(ErrorCode.INVALID_SCHEMA, "closed source capability required")
                if text.endswith("_ready") and text != ("history_ready" if history else "opening_ready"):
                    fail(ErrorCode.INVALID_SCHEMA, "wrong capability family")
                if hi is None or lo > start or hi < config.session.close_ns:
                    fail(ErrorCode.BOUNDS, "capability must cover governed session")
            else:
                if text not in ("clear", "interrupted", "unknown") or hi is None or not lo <= start < hi:
                    fail(ErrorCode.INVALID_SCHEMA, "closed original boundary relation seed required")
        texts[role] = text
        proof_reasons[role] = _reasons(_knowledge(c, 0, config), () if batch.metadata.coverage.complete else (Reason.GOVERNED_GAP,))
    if cutoff <= start and any(r in roles for r in (target_role, prefix_role, "history_seed")):
        fail(ErrorCode.BOUNDS, "zero prefix requires absent population/prefix/seed roles")
    parsed: list[tuple[str, str]] = []
    row_reasons: list[tuple[Reason, ...]] = []
    if target is not None:
        c = columns[target_role]
        scope = target.metadata.scope
        if cutoff > start and (scope is None or (scope.start_ns, scope.end_ns, scope.eligibility_policy,
                scope.include_opening_auction, scope.include_closing_auction) != (start, end,
                "observable_status_v2" if history else "observable_regular_v2", selection["include_opening_auction"], False)):
            fail(ErrorCode.INCONSISTENT_IDENTITY, "exact original observable population scope required")
        if history:
            parsed = _events(target, c, context, start, end)
        else:
            for i in range(target.row_count):
                stamp = c["event_ns"][i]
                condition = c.get("condition", (None,) * target.row_count)[i]
                if condition not in (None, "regular", "opening_auction", "closing_auction"):
                    fail(ErrorCode.INVALID_SCHEMA, "closed trade condition required")
                if not start <= stamp < end or condition == "closing_auction" or (
                        condition == "opening_auction" and (not selection["include_opening_auction"] or stamp != start)):
                    fail(ErrorCode.BOUNDS, "trade outside selected opening population")
        for i in range(target.row_count):
            reasons = _knowledge(c, i, config)
            if not history and any(name not in c for name in ("price", "size")):
                reasons = _reasons(reasons, (Reason.ABSENT_INPUT,))
            row_reasons.append(reasons)
    cal_reasons = proof_reasons["calendar_provenance"]
    base = _reasons(cal_reasons, proof_reasons["source_capability"], proof_reasons[prefix_role])
    unavailable_capability = texts.get("source_capability") in ("missing_identity", "missing_order", "missing_payload", "unavailable") and not proof_reasons["source_capability"]
    n: int | None = None
    if prefix_role in texts:
        token = texts[prefix_role].split("~")[1]
        n = None if token == "u" else _decimal(token)
    delivered = 0 if target is None else target.row_count
    delivery_expected = None if target is None else target.metadata.coverage.expected
    if unavailable_capability:
        base = _reasons(cal_reasons, (Reason.INELIGIBLE,))
    else:
        if target is None:
            base = _reasons(base, (Reason.ABSENT_INPUT,))
        for row_reason in row_reasons:
            base = _reasons(base, row_reason)
        if prefix_role in texts and (texts[prefix_role].endswith("~partial") or n != delivered or
                target is None or not target.metadata.coverage.complete or delivery_expected != n):
            base = _reasons(base, (Reason.GOVERNED_GAP,))
    expected = None if n is None else checked_int64(3 + max(n, delivered, delivery_expected or 0))
    observed = sum(not proof_reasons[r] or proof_reasons[r] == (Reason.GOVERNED_GAP,) for r in ("calendar_provenance", "source_capability", prefix_role)) + sum(not r for r in row_reasons)
    if unavailable_capability:
        expected, observed = None, int(not cal_reasons)
    if cal_reasons:
        expected, observed = (None if "calendar_provenance" not in roles else 1), 0
        base = cal_reasons
    zero = cutoff <= start and not cal_reasons
    if zero:
        expected, observed, base = 0, 0, ()
    proofs = [(r, 0) for r in ("calendar_provenance", "source_capability", prefix_role) if r in roles and roles[r].row_count]
    if unavailable_capability:
        proofs = [(r, i) for r, i in proofs if r == "calendar_provenance"]
    values: dict[str, int | bool | None] = {}
    reasons_by: dict[str, tuple[Reason, ...]] = {}
    evidence_by: dict[str, list[Row]] = {}
    count_by: dict[str, tuple[int | None, int]] = {}
    if not history:
        eligible = [] if target is None else [i for i in range(delivered) if columns[target_role]["eligible"][i] and not row_reasons[i]]
        first = eligible[0] if eligible else None
        witness = [] if first is None else [(target_role, first)]
        for name in ("observed", "first_trade_time_ns", "delay_ns", "delay_seconds"):
            reasons_by[name] = base
            evidence_by[name] = proofs + witness
        if zero:
            for name in reasons_by:
                reasons_by[name] = (Reason.NO_ELIGIBLE_OBSERVATIONS,)
                evidence_by[name] = []
        elif not base:
            values["observed"] = first is not None
            if first is None:
                for name in ("first_trade_time_ns", "delay_ns", "delay_seconds"):
                    reasons_by[name] = (Reason.NO_ELIGIBLE_OBSERVATIONS,)
            else:
                stamp = columns[target_role]["event_ns"][first]
                delay = checked_int64(stamp - start)
                values.update(first_trade_time_ns=stamp, delay_ns=delay, delay_seconds=delay // 1_000_000_000)
    else:
        names = ("event_count", "halt_observed", "resume_observed", "ssr_on_observed")
        known = [i for i, r in enumerate(row_reasons) if not r]
        halt = next((i for i in known if parsed[i][0] == "halt"), None)
        ssr_on = context["selection"]["flag_map"][2][1]
        ssr_off = context["selection"]["flag_map"][2][2]
        ssr = next((i for i in known if parsed[i][1] == ssr_on), None)
        relation = texts.get("history_seed", "unknown") if not proof_reasons["history_seed"] else "unknown"
        origin: Row | None = ("history_seed", 0) if relation == "interrupted" else None
        relation_from_seed = relation != "unknown"
        # Irrelevant records preserve the boundary relation; physical index is
        # not a dependency. Every action that changes relation clears its origin.
        initial_relation = True
        seed_needed = False
        seed_events: list[Row] = []
        unresolved = False
        resume_witness: list[Row] | None = None
        for i in known:
            action = parsed[i][0]
            if action == "halt":
                relation, origin, relation_from_seed = "interrupted", (target_role, i), False
                initial_relation = False
            elif action == "resume":
                if resume_witness is None:
                    resume_witness = [(target_role, i)]
                relation, origin, relation_from_seed = "clear", None, False
                initial_relation = False
            elif action == "initial":
                relation, origin, relation_from_seed = "clear", None, False
                initial_relation = False
            elif action == "active":
                if relation == "interrupted" and resume_witness is None:
                    resume_witness = ([] if origin is None else [origin]) + [(target_role, i)]
                if relation == "unknown":
                    unresolved = True
                    seed_needed = seed_needed or initial_relation
                elif relation_from_seed:
                    seed_needed = True
                    seed_events.append((target_role, i))
                relation, origin, relation_from_seed = "clear", None, False
                initial_relation = False
            elif action == "unknown":
                relation, origin, relation_from_seed = "unknown", None, False
                initial_relation = False
        if resume_witness is not None:
            seed_needed = any(r == "history_seed" for r, _ in resume_witness)
        last = [] if not known else [(target_role, known[-1])]
        first_last = [] if not known else [(target_role, known[0])] + ([] if len(known) == 1 else last)
        for name in names:
            reasons_by[name] = base
            evidence_by[name] = proofs + (first_last if name == "event_count" else last)
        if halt is not None:
            evidence_by["halt_observed"] = proofs + [(target_role, halt)]
        if ssr is not None:
            evidence_by["ssr_on_observed"] = proofs + [(target_role, ssr)]
        elif any(parsed[i][1] not in (ssr_on, ssr_off) for i in known):
            reasons_by["ssr_on_observed"] = _reasons(base, (Reason.NULL_FIELD,))
            count_by["ssr_on_observed"] = (expected, observed - sum(parsed[i][1] not in (ssr_on, ssr_off) for i in known))
        if resume_witness is not None:
            evidence_by["resume_observed"] = proofs + resume_witness
        elif unresolved:
            reasons_by["resume_observed"] = _reasons(base, (Reason.MISSING_ACTION_EVIDENCE,))
            evidence_by["resume_observed"] = proofs.copy()
        elif base:
            evidence_by["resume_observed"] = proofs.copy()
        if seed_needed:
            count_by["resume_observed"] = (None if expected is None else checked_int64(expected + 1), observed + int(not proof_reasons["history_seed"]))
            seed_knowledge = tuple(r for r in proof_reasons["history_seed"] if r != Reason.ABSENT_INPUT)
            reasons_by["resume_observed"] = _reasons(reasons_by["resume_observed"], seed_knowledge)
            if "history_seed" in roles and roles["history_seed"].row_count:
                evidence_by["resume_observed"].append(("history_seed", 0))
                evidence_by["resume_observed"].extend(seed_events)
        values.update(event_count=n, halt_observed=halt is not None, resume_observed=resume_witness is not None, ssr_on_observed=ssr is not None)
        if zero:
            for name in names:
                reasons_by[name], evidence_by[name] = (), []
            values.update(event_count=0, halt_observed=False, resume_observed=False, ssr_on_observed=False)
    all_reasons = _reasons(*(reasons_by.values()))
    state = "unavailable" if unavailable_capability else ("unknown" if _status(all_reasons) == Status.MISSING_INPUT else (
        "partial" if Reason.GOVERNED_GAP in all_reasons else "passed"))
    diagnostic = "none"
    for reason in (Reason.ABSENT_INPUT, Reason.UNKNOWN_AVAILABILITY, Reason.FUTURE_KNOWLEDGE,
                   Reason.NULL_FIELD, Reason.MISSING_ACTION_EVIDENCE, Reason.INELIGIBLE, Reason.GOVERNED_GAP,
                   Reason.NO_ELIGIBLE_OBSERVATIONS):
        if reason in all_reasons:
            diagnostic = {Reason.INELIGIBLE: "missing_capability", Reason.GOVERNED_GAP: "partial_prefix",
                          Reason.NO_ELIGIBLE_OBSERVATIONS: "no_eligible"}.get(reason, reason.value)
            break
    if zero:
        state, diagnostic = ("passed", "empty_interval") if history else ("not_applicable", "before_open" if cutoff < start else "at_open")
    result_columns: list[FeatureColumn] = []
    quality: list[QualityRow] = []
    evidence: list[EvidenceRow] = []
    for definition in ef1_definitions(config):
        name = definition.feature_id.rsplit(".", 1)[1]
        assessment = name in ("admission_reason", "admission_state")
        reasons = () if assessment else reasons_by[name]
        status = _status(reasons)
        value = (diagnostic if name == "admission_reason" else state) if assessment else (values.get(name) if status == Status.AVAILABLE else None)
        result_columns.append(FeatureColumn(definition.feature_id, "observable-v2", definition.dtype, definition.unit, (entity,), (value,)))
        exp, obs = (1, 1) if assessment else count_by.get(name, (expected, observed))
        quality.append(QualityRow(entity, definition.feature_id, status, exp, obs, reasons))
        for role, i in ([] if assessment else evidence_by[name]):
            c = columns[role]
            if _knowledge(c, i, config):
                continue
            market = roles[role].kind == DataKind.TRADE
            stamp = c["event_ns" if market else "effective_start_ns"][i]
            if stamp > cutoff:
                continue
            evidence.append(EvidenceRow(entity, definition.feature_id, roles[role].metadata.source.input_id,
                c["event_id" if market else "reference_id"][i], stamp, c.get("known_at_ns", (None,) * roles[role].row_count)[i],
                None if market else stamp, None if market else c.get("effective_end_ns", (None,) * roles[role].row_count)[i]))
    evidence = list({(e.feature_id, e.input_id, e.row_id): e for e in evidence}.values())
    evidence.sort(key=lambda e: (e.entity.instrument_id, e.entity.session_id, e.feature_id, e.input_id, e.row_id))
    metadata = ResultMetadata(config.session.namespace, entity.session_id, config.availability, config.digest,
        tuple(InputBinding(r, roles[r].kind, roles[r].metadata) for r in slots if r in roles), "ef1", __version__,
        math_policy_version="v1", evidence_limit=32)
    return FeatureResult(tuple(result_columns), tuple(quality), metadata, tuple(evidence))
