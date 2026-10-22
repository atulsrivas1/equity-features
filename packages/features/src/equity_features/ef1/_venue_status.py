"""Pure multi-venue status reduction over an expected publisher population; no acquisition, arbitration or inference."""
from __future__ import annotations

import base64
import re
from typing import Any

from equity_feature_contracts import (
    CanonicalBatch, ConfigSpec, DataKind, EntityKey, ErrorCode, EvidenceRow,
    FeatureColumn, FeatureResult, InputBinding, QualityRow, Reason, ResultMetadata,
    Status, ValueType, checked_int64,
)
from equity_features import __version__
from ._anchor import _admit_common, _columns
from ._context import decode_ef1_context, fail, label
from ._definitions import ef1_definitions

ROLES = ("venue_population", "venue_seed", "venue_states", "venue_prefix", "venue_validity")
_DIMENSIONS = {"trading": ("t", ("active", "halted", "closed")),
               "quoting": ("q", ("enabled", "disabled")), "ssr": ("s", ("on", "off"))}
_CODES = {code: name for name, (code, _) in _DIMENSIONS.items()}
_POSITIVE = {"trading": "active", "quoting": "enabled", "ssr": "on"}
# Closed finding order of one fact; a population outcome precedes all of them in the aggregate reason.
_FINDINGS = ("absent_input", "incomplete_status_prefix", "unknown_availability", "future_knowledge",
             "outside_effective_interval", "stale_state")
_AGGREGATE_ORDER = ("absent_population", "incomplete_population", "empty_population") + _FINDINGS
_LEGACY = {"absent_input": Reason.ABSENT_INPUT, "incomplete_status_prefix": Reason.GOVERNED_GAP,
           "unknown_availability": Reason.UNKNOWN_AVAILABILITY, "future_knowledge": Reason.FUTURE_KNOWLEDGE,
           "outside_effective_interval": Reason.INELIGIBLE, "stale_state": Reason.INELIGIBLE}
_B64URL = re.compile("[A-Za-z0-9_-]+")
# Header discovery rows: output name, dtype, unit, formula (lexicographic by feature id).
VENUE_FIELDS = (
    ("aggregate_reason", ValueType.STRING, "reason",
     "unanimous|precedence_resolved|precedence_saturated, else first of the closed unavailability precedence"),
    ("aggregate_state", ValueType.STRING, "state",
     "highest-precedence known trading state; null unless all known or the top-ranked state dominates"),
    ("known_nontrading_count", ValueType.INT64, "publishers", "halted+closed publishers; null unless every expected publisher is known"),
    ("known_trading_count", ValueType.INT64, "publishers", "active publishers; null unless every expected publisher is known"),
    ("latest_event_ns", ValueType.INT64, "utc_ns",
     "max original event clock over known or stale facts; all eligible, or the maximum equals C-1"),
    ("quoting_any", ValueType.BOOL, "boolean", "OR of known quoting enabled; false only if every quoting fact is known disabled"),
    ("restriction_any", ValueType.BOOL, "boolean", "OR of known ssr on; false only if every ssr fact is known off"),
)


def _part(token: str) -> str:
    """Reversible unpadded base64url of safe UTF8; a noncanonical spelling is not accepted."""
    if _B64URL.fullmatch(token) is None or len(token) % 4 == 1:
        fail(ErrorCode.INVALID_SCHEMA, "closed venue reference grammar required")
    raw = base64.urlsafe_b64decode(token + "=" * (-len(token) % 4))
    if base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii") != token:
        fail(ErrorCode.INVALID_SCHEMA, "reversible venue reference grammar required")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        fail(ErrorCode.INVALID_SCHEMA, "UTF8 venue reference component required")
    return label(text)


def _seq(token: str) -> int:
    if len(token) != 19 or any(c not in "0123456789" for c in token) or int(token) > 2**63 - 1:
        fail(ErrorCode.INVALID_SCHEMA, "exact nonnegative int64 seq19 required")
    return int(token)


def _dimension(code: str) -> str:
    if code not in _CODES:
        fail(ErrorCode.INVALID_SCHEMA, "closed venue dimension code required")
    return _CODES[code]


def _opt(cols: dict[str, tuple[Any, ...]], name: str, i: int) -> Any:
    values = cols.get(name)
    return None if values is None else values[i]


def _reference(batch: CanonicalBatch, config: ConfigSpec, entity: EntityKey) -> dict[str, tuple[Any, ...]]:
    if batch.kind != DataKind.REFERENCE:
        fail(ErrorCode.INVALID_SCHEMA, "venue roles must be actual REFERENCE batches")
    _admit_common(batch, config, entity)
    if batch.metadata.source.mapping_version != "ef1-venue-map1":
        fail(ErrorCode.INCOMPATIBLE_VERSION, "unsupported venue reference mapping")
    cols = _columns(batch)
    if any(name in cols for name in ("price", "factor_num", "factor_den")):
        fail(ErrorCode.INVALID_SCHEMA, "venue references have no numerical payload")
    return cols


def _interval(cols: dict[str, tuple[Any, ...]], i: int, finite: bool) -> tuple[int, int | None]:
    start, end = cols["effective_start_ns"][i], _opt(cols, "effective_end_ns", i)
    if (end is None and finite) or (end is not None and end <= start):
        fail(ErrorCode.BOUNDS, "positive venue interval required")
    return start, end


def _known(known: int | None, knowledge: int) -> str | None:
    if known is None:
        return "unknown_availability"
    return "future_knowledge" if known > knowledge else None


class _Fact:
    """One (publisher, dimension) outcome: known (state and clock), stale (clock only) or unknown (finding)."""

    def __init__(self, kind: str, finding: str | None = None, state: str | None = None,
                 clock: int | None = None, row: int | None = None) -> None:
        self.kind, self.finding, self.state, self.clock, self.row = kind, finding, state, clock, row


def compute_venue_status(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None] | list[CanonicalBatch],
                         config: ConfigSpec, *, entity: EntityKey) -> FeatureResult:
    """Reduce per-publisher status streams over the expected population; the caller supplies the precedence."""
    context = decode_ef1_context(config)
    if context["producer"] != "multivenue_status":
        fail(ErrorCode.INVALID_CONFIG, "wrong multi-venue producer")
    if type(entity) is not EntityKey or entity.session_id != config.session.session_id:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "exact target entity required")
    label(entity.instrument_id)
    label(entity.session_id)
    if type(batches) not in (tuple, list) or len(batches) != 5:
        fail(ErrorCode.INVALID_SCHEMA, "exactly five fixed nullable venue slots required")
    if any(batch is not None and type(batch) is not CanonicalBatch for batch in batches):
        fail(ErrorCode.INVALID_SCHEMA, "each venue slot must be CanonicalBatch or None")
    roles = {role: batch for role, batch in zip(ROLES, batches) if batch is not None}
    if any(batch.kind != DataKind.REFERENCE for batch in roles.values()):
        fail(ErrorCode.INVALID_SCHEMA, "every present venue slot must be REFERENCE")
    if sum(batch.row_count for batch in roles.values()) > 4096:
        fail(ErrorCode.BOUNDS, "aggregate venue reference work bound exceeded")
    if len({batch.metadata.source.input_id for batch in roles.values()}) != len(roles):
        fail(ErrorCode.DUPLICATE, "distinct actual role input identities required")
    selection = context["selection"]
    epoch = selection["epoch"]
    dims = tuple(selection["clock_dimensions"])
    precedence = tuple(selection["state_policy"]["precedence"])
    max_age = selection["max_age_ns"]
    cutoff, knowledge = config.availability.market_cutoff_ns, config.availability.knowledge_cutoff_ns
    cols = {role: _reference(batch, config, entity) for role, batch in roles.items()}

    # Structural validation of every row of every present slot, before any semantics.
    members: dict[str, int] = {}
    population = roles.get("venue_population")
    if population is not None:
        pc = cols["venue_population"]
        for i in range(population.row_count):
            parts = pc["reference_id"][i].split(":")
            if len(parts) != 4 or parts[0] != "vp1":
                fail(ErrorCode.INVALID_SCHEMA, "closed venue population identity required")
            if (_part(parts[1]), _part(parts[2])) != (selection["population_id"], selection["population_revision"]):
                fail(ErrorCode.INCONSISTENT_IDENTITY, "population id/revision differs from the selection")
            publisher = _part(parts[3])
            if pc["fact_kind"][i] != "ef1.venue.population_member" or _opt(pc, "text", i) != "member":
                fail(ErrorCode.INVALID_SCHEMA, "closed venue population vocabulary required")
            _interval(pc, i, True)
            if publisher in members:
                fail(ErrorCode.DUPLICATE, "a publisher is declared once per population revision")
            members[publisher] = i
    streams = [roles[r] for r in ROLES[1:] if r in roles]
    if len({(b.metadata.source.source_id, b.metadata.source.snapshot_id) for b in streams}) > 1:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "venue stream roles must share one source and revision")
    states_batch = roles.get("venue_states")

    def stream_key(parts: list[str], dimension: str) -> tuple[str, str]:
        if _part(parts[2]) != epoch:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "venue epoch differs from the selection")
        publisher = _part(parts[3])
        if population is not None and publisher not in members:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "publisher is not a declared population member")
        return publisher, dimension

    # states[(publisher, dimension)] -> rows (seq, start, end, text, known_at, row index) in batch order.
    states: dict[tuple[str, str], list[tuple[int, int, int | None, str, int | None, int]]] = {}
    if states_batch is not None:
        sc = cols["venue_states"]
        for i in range(states_batch.row_count):
            parts = sc["reference_id"][i].split(":")
            if len(parts) != 6 or parts[0] != "v1":
                fail(ErrorCode.INVALID_SCHEMA, "closed venue state identity required")
            dimension = _dimension(parts[1])
            key = stream_key(parts, dimension)
            sequence = _seq(parts[4])
            _part(parts[5])
            if sc["fact_kind"][i] != "ef1.venue.state." + dimension or _opt(sc, "text", i) not in _DIMENSIONS[dimension][1]:
                fail(ErrorCode.INVALID_SCHEMA, "closed venue state fact/text required")
            start, end = _interval(sc, i, False)
            rows = states.setdefault(key, [])
            if rows:
                if sequence <= rows[-1][0]:
                    fail(ErrorCode.DUPLICATE if sequence == rows[-1][0] else ErrorCode.INVALID_ORDER,
                         "strict supplied venue sequence order required")
                if start < rows[-1][1]:
                    fail(ErrorCode.INVALID_ORDER, "nondecreasing venue effective time required")
            rows.append((sequence, start, end, sc["text"][i], _opt(sc, "known_at_ns", i), i))
    seeds: dict[tuple[str, str], list[tuple[int, int, int | None, int]]] = {}
    if "venue_seed" in roles:
        zc = cols["venue_seed"]
        for i in range(roles["venue_seed"].row_count):
            parts = zc["reference_id"][i].split(":")
            if len(parts) != 5 or parts[0] != "vs1":
                fail(ErrorCode.INVALID_SCHEMA, "closed venue seed identity required")
            dimension = _dimension(parts[1])
            key = stream_key(parts, dimension)
            sequence = _seq(parts[4])
            if zc["fact_kind"][i] != "ef1.venue.seed" or _opt(zc, "text", i) != parts[1]:
                fail(ErrorCode.INVALID_SCHEMA, "closed venue seed vocabulary required")
            start, end = _interval(zc, i, True)
            seeds.setdefault(key, []).append((sequence, start, end, i))
    proofs: dict[str, dict[tuple[str, str], list[tuple[int, int, int | None, int]]]] = {"venue_prefix": {}, "venue_validity": {}}
    for role, kind in (("venue_prefix", "ef1.venue.prefix_complete"), ("venue_validity", "ef1.venue.validity")):
        if role not in roles:
            continue
        qc = cols[role]
        for i in range(roles[role].row_count):
            parts = qc["reference_id"][i].split(":")
            if len(parts) != 6 or parts[0] != "vc1":
                fail(ErrorCode.INVALID_SCHEMA, "closed venue certificate identity required")
            dimension = _dimension(parts[1])
            key = stream_key(parts, dimension)
            target = _part(parts[4])
            _part(parts[5])
            if qc["fact_kind"][i] != kind or _opt(qc, "text", i) != parts[1]:
                fail(ErrorCode.INVALID_SCHEMA, "closed venue certificate vocabulary required")
            if states_batch is not None and target != states_batch.metadata.source.input_id:
                fail(ErrorCode.INCONSISTENT_IDENTITY, "certificate must bind the actual venue states input")
            start, end = _interval(qc, i, True)
            proofs[role].setdefault(key, []).append((start, end, qc["known_at_ns"][i] if "known_at_ns" in qc else None, i))
    # Ambiguity is counted before any knowledge arbitration or dependent evaluation.
    applicable_seed: dict[tuple[str, str], tuple[int, int, int | None, int]] = {}
    for key, rows in seeds.items():
        hits = [r for r in rows if r[1] <= cutoff < r[2]]
        if len(hits) > 1:
            fail(ErrorCode.DUPLICATE, "ambiguous applicable venue seeds")
        if hits:
            applicable_seed[key] = hits[0]
    applicable_validity: dict[tuple[str, str], tuple[int, int, int | None, int]] = {}
    for key, vrows in proofs["venue_validity"].items():
        hits = [r for r in vrows if r[0] <= cutoff < r[1]]
        if len(hits) > 1:
            fail(ErrorCode.DUPLICATE, "ambiguous applicable venue validity certificates")
        if hits:
            applicable_validity[key] = hits[0]
    applicable_prefix: dict[tuple[str, str], tuple[int, int, int | None, int]] = {}
    for key, prows in proofs["venue_prefix"].items():
        if key not in applicable_seed:
            continue
        origin = applicable_seed[key][1]
        hits = [r for r in prows if r[0] <= origin and cutoff <= r[1]]
        if len(hits) > 1:
            fail(ErrorCode.DUPLICATE, "ambiguous applicable venue prefix certificates")
        if hits:
            applicable_prefix[key] = hits[0]

    # Expected population: applicable members in batch order; the denominator is never reduced by missing facts.
    expected_members: list[str] = []
    outcome: str | None = None
    outcome_reasons: set[str] = set()
    if population is None:
        outcome = "absent_population"
    else:
        pc = cols["venue_population"]
        expected_members = [p for p, i in members.items()
                            if pc["effective_start_ns"][i] <= cutoff < pc["effective_end_ns"][i]]
        cov = population.metadata.coverage
        if not cov.complete or cov.expected != cov.observed or cov.observed != population.row_count:
            outcome = "incomplete_population"
        else:
            for p in expected_members:
                reason = _known(_opt(pc, "known_at_ns", members[p]), knowledge)
                if reason:
                    outcome_reasons.add(reason)
            if outcome_reasons:
                outcome = next(r for r in _FINDINGS if r in outcome_reasons)
            elif not expected_members:
                outcome = "empty_population"
    n = len(expected_members)

    def evaluate(publisher: str, dimension: str) -> _Fact:
        key = (publisher, dimension)
        findings: set[str] = set()
        seed = applicable_seed.get(key)
        rows = states.get(key, [])
        if seed is None:
            findings.add("absent_input")
        else:
            finding = _known(_opt(cols["venue_seed"], "known_at_ns", seed[3]), knowledge)
            if finding:
                findings.add(finding)
        start_index = None if seed is None else next((j for j, r in enumerate(rows) if r[0] == seed[0]), None)
        transitions: list[tuple[int, int, int | None, str, int | None, int]] = []
        if start_index is not None:
            for r in rows[start_index:]:
                if r[1] >= cutoff:
                    break
                transitions.append(r)
        if not transitions or transitions[0][0] != (seed[0] if seed else -1):
            findings.add("absent_input")
        for r in transitions:
            finding = _known(r[4], knowledge)
            if finding:
                findings.add(finding)
        if states_batch is not None and not states_batch.metadata.coverage.complete:
            findings.add("incomplete_status_prefix")
        for role in ("venue_prefix", "venue_validity"):
            batch = roles.get(role)
            if batch is None or key not in proofs[role]:
                findings.add("absent_input")
            elif not batch.metadata.coverage.complete:
                findings.add("incomplete_status_prefix")
        prefix = applicable_prefix.get(key)
        if seed is not None and transitions:
            if prefix is None and key in proofs["venue_prefix"]:
                findings.add("incomplete_status_prefix")
            elif prefix is not None:
                finding = _known(prefix[2], knowledge)
                if finding:
                    findings.add(finding)
        validity = applicable_validity.get(key)
        if validity is not None:
            finding = _known(validity[2], knowledge)
            if finding:
                findings.add(finding)
        if not findings:
            current = transitions[-1]
            if (key in proofs["venue_validity"] and validity is None) or (current[2] is not None and cutoff >= current[2]):
                findings.add("outside_effective_interval")
        if findings:
            return _Fact("unknown", next(f for f in _FINDINGS if f in findings))
        current = transitions[-1]
        age = checked_int64(cutoff - current[1])
        if max_age is not None and age > max_age:
            return _Fact("stale", "stale_state", None, current[1], current[5])
        return _Fact("known", None, current[3], current[1], current[5])

    facts: dict[tuple[str, str], _Fact] = {}
    if outcome is None:
        for publisher in expected_members:
            for dimension in _DIMENSIONS:
                facts[publisher, dimension] = evaluate(publisher, dimension)

    def column(dimension: str) -> list[tuple[str, _Fact]]:
        return [(p, facts[p, dimension]) for p in expected_members]

    values: dict[str, Any] = {name: None for name, *_ in VENUE_FIELDS}
    quality: dict[str, QualityRow] = {}
    witness: dict[str, tuple[str, str]] = {}  # output -> (publisher, dimension)
    expected_by: dict[str, tuple[int | None, int]] = {}
    unavailable: dict[str, set[str]] = {}

    def settle(name: str, required: list[tuple[str, str]], ok: Any, value: Any = None, single: bool = False) -> None:
        """Record one output: the value with its coverage, or null with the reasons of the facts it requires."""
        if value is not None:
            values[name] = value
            expected_by[name] = (1, 1) if single else (len(required), len(required))
        else:
            expected_by[name] = (len(required), sum(1 for key in required if ok(facts[key])))
            unavailable[name] = {facts[key].finding for key in required if not ok(facts[key])} - {None}  # type: ignore[misc]

    reason_value: str
    if outcome is None:
        trading = [(p, "trading") for p in expected_members]
        known_t = [(p, f) for p, f in column("trading") if f.kind == "known"]
        all_known = len(known_t) == n
        is_known = lambda f: f.kind == "known"  # noqa: E731
        settle("known_trading_count", trading, is_known,
               sum(f.state == "active" for _, f in known_t) if all_known else None)
        settle("known_nontrading_count", trading, is_known,
               sum(f.state != "active" for _, f in known_t) if all_known else None)
        best = min((precedence.index(f.state) for _, f in known_t), default=None)
        state = None
        single = False
        if best is not None and (all_known or best == 0):
            state, single = precedence[best], not all_known
        settle("aggregate_state", trading, is_known, state, single)
        if state is not None:
            witness["aggregate_state"] = next((p, "trading") for p, f in known_t if f.state == state)
            distinct = {f.state for _, f in known_t}
            reason_value = "precedence_saturated" if single else ("unanimous" if len(distinct) == 1 else "precedence_resolved")
        else:
            blocked = {facts[key].finding for key in trading if facts[key].kind != "known"}
            reason_value = next(r for r in _AGGREGATE_ORDER if r in blocked)
        for name, dimension in (("quoting_any", "quoting"), ("restriction_any", "ssr")):
            column_d = column(dimension)
            positive = [(p, f) for p, f in column_d if f.kind == "known" and f.state == _POSITIVE[dimension]]
            verdict = True if positive else (False if all(f.kind == "known" for _, f in column_d) else None)
            settle(name, [(p, dimension) for p in expected_members], is_known, verdict, bool(positive))
            if positive:
                witness[name] = (positive[0][0], dimension)
        clock = [(p, d) for p in expected_members for d in dims]
        eligible = lambda f: f.kind in ("known", "stale")  # noqa: E731
        clocks = [facts[key].clock for key in clock if eligible(facts[key])]
        latest = None
        saturated = False
        if clocks and (len(clocks) == len(clock) or max(clocks) == cutoff - 1):
            latest, saturated = max(clocks), len(clocks) != len(clock)
        settle("latest_event_ns", clock, eligible, latest, saturated)
        if latest is not None:
            witness["latest_event_ns"] = next(key for key in clock if facts[key].clock == latest)
    else:
        reason_value = outcome
        if outcome == "empty_population":
            status, reasons = Status.NOT_APPLICABLE, (Reason.EMPTY_UNIVERSE,)
            counts: tuple[int | None, int] = (0, 0)
        elif outcome == "incomplete_population":
            status, reasons, counts = Status.INCOMPLETE_COVERAGE, (Reason.GOVERNED_GAP,), (None, 0)
        elif outcome == "absent_population":
            status, reasons, counts = Status.MISSING_INPUT, (Reason.ABSENT_INPUT,), (None, 0)
        else:
            status, reasons, counts = Status.MISSING_INPUT, tuple(sorted((_LEGACY[r] for r in outcome_reasons),
                                                                         key=lambda r: r.value)), (None, 0)
        for name, *_ in VENUE_FIELDS:
            if name != "aggregate_reason":
                quality[name] = QualityRow(entity, "session.venue_status." + name, status, counts[0], counts[1], reasons)
    values["aggregate_reason"] = reason_value
    if outcome is None:
        for name, *_ in VENUE_FIELDS:
            if name == "aggregate_reason":
                continue
            exp, obs = expected_by[name]
            if values[name] is not None:
                quality[name] = QualityRow(entity, "session.venue_status." + name, Status.AVAILABLE, exp, obs)
            else:
                legacy = {_LEGACY[f] for f in unavailable[name]}
                reasons = tuple(sorted(legacy, key=lambda r: r.value))
                status = Status.INCOMPLETE_COVERAGE if legacy == {Reason.GOVERNED_GAP} else Status.MISSING_INPUT
                quality[name] = QualityRow(entity, "session.venue_status." + name, status, exp, obs, reasons)
    quality["aggregate_reason"] = QualityRow(entity, "session.venue_status.aggregate_reason", Status.AVAILABLE, 1, 1)

    bindings = tuple(sorted((InputBinding(role, batch.kind, batch.metadata) for role, batch in roles.items()),
                            key=lambda binding: binding.role))
    metadata = ResultMetadata(config.session.namespace, entity.session_id, config.availability, config.digest,
        bindings, "python-exact", __version__, evidence_limit=4)
    out_columns: list[FeatureColumn] = []
    out_quality: list[QualityRow] = []
    for definition in ef1_definitions(config):
        name = definition.feature_id.rsplit(".", 1)[1]
        out_columns.append(FeatureColumn(definition.feature_id, "v1", definition.dtype, definition.unit, (entity,), (values[name],)))
        out_quality.append(quality[name])
    evidence: list[EvidenceRow] = []
    for name in ("aggregate_state", "quoting_any", "restriction_any", "latest_event_ns"):
        if name not in witness:
            continue
        publisher, dimension = witness[name]
        row = facts[publisher, dimension].row
        assert row is not None and states_batch is not None
        sc = cols["venue_states"]
        evidence.append(EvidenceRow(entity, "session.venue_status." + name, states_batch.metadata.source.input_id,
            sc["reference_id"][row], sc["effective_start_ns"][row], _opt(sc, "known_at_ns", row),
            sc["effective_start_ns"][row], _opt(sc, "effective_end_ns", row)))
    return FeatureResult(tuple(out_columns), tuple(out_quality), metadata, tuple(evidence))
