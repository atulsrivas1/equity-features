"""Pure EF4 producer `ef4.trade_top_k_notional` (ef4-notional1): the K largest eligible prints by exact notional.

Rank key `(-price * size, event_ns, order_key, event_id)`: the notional is an exact integer (below 10^38, so it always
fits decimal128) and an equal notional is broken by earlier time, `order_key` and the event identity (Unicode code
point), never by size or price. The result is the accepted `TopKTrades` cell holding `min(K, n)` original rows; the
size-ranked `session.trade.top_k` is a different output and is not touched. Partial results of disjoint populations merge
by concatenation, the rank key and a cut to K (DP-K6). Batch, conditional merge and full replay only.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, CanonicalBatch, ConfigSpec, DataKind, EntityKey, ErrorCode, EvidenceRow,
    FeatureColumn, FeatureResult, InputBinding, Parameter, PriceUnit, QualityRow, Reason, ResultMetadata, SessionSpec,
    Status, TopKTradeRow, TopKTrades, ValueType,
)
from equity_features import __version__
from equity_features.ef3._common import fail, integer
from equity_features.ef3._robust_common import (
    check_entity, check_features, check_policy, check_slots, first_status, make_config, ordered, parameter_map,
)
from ._tape_common import admit_trades, eligibility_policy, knowledge_flags

TOP_K_IDENTITY = "ef4.trade_top_k_notional"
TOP_K_ALGORITHM = "ef4-top-k-notional-v1"
# The label names the whole convention set (exact notional, rank key, tie key, eligibility, merge rule).
TOP_K_POLICY = "ef4-notional1"
TOP_K_FEATURE = "tape.top_k_notional"
TOP_K_FEATURES = (TOP_K_FEATURE,)
TOP_K_UNIT = "bounded original trade-row evidence"
_REQUIRED = frozenset({"policy_version", "top_k", "evidence_limit", "eligibility_policy"})
Key = tuple[int, int, int, str]


@dataclass(frozen=True)
class NotionalTopKSettings:
    policy_version: str
    top_k: int
    evidence_limit: int
    eligibility_policy: str


def _insert(kept: list[tuple[Key, TopKTradeRow]], key: Key, row: TopKTradeRow) -> None:
    """Insert into the key-sorted list at the leftmost position (keys are unique), by binary search."""
    low, high = 0, len(kept)
    while low < high:
        middle = (low + high) // 2
        if kept[middle][0] < key:
            low = middle + 1
        else:
            high = middle
    kept.insert(low, (key, row))


def notional_key(row: TopKTradeRow) -> Key:
    """`(-notional, event_ns, order_key, event_id)`; the notional is the exact product of the original row."""
    return (-(row.price * row.size), row.event_ns, row.order_key, row.event_id)


def notional_cell(k: int, rows: Sequence[TopKTradeRow]) -> TopKTrades:
    """The accepted `TopKTrades` cell with rows in notional rank order.

    The shared constructor checks the rows against the size-ranked key, which this ranking does not follow, and the
    contract forbids changing the cell. The rows are therefore validated by the shared constructor in the size order
    (type, bounds, duplicates, K) and the frozen cell is then assembled in the notional order without a second
    ordering check.
    """
    TopKTrades(k, tuple(sorted(rows, key=lambda row: row.rank_key)))
    cell = object.__new__(TopKTrades)
    object.__setattr__(cell, "k", k)
    object.__setattr__(cell, "rows", tuple(rows))
    return cell


def _check(policy: object, top_k: object, limit: object, eligibility: object) -> NotionalTopKSettings:
    k = integer(top_k, 1, 10000)
    evidence_limit = integer(limit, k, 10000)
    policy_label = eligibility_policy(eligibility)
    check_policy(policy, TOP_K_POLICY)
    assert type(policy) is str
    return NotionalTopKSettings(policy, k, evidence_limit, policy_label)


def build_notional_top_k_config(*, policy_version: str | None = None, top_k: int | None = None,
                                evidence_limit: int | None = None, eligibility_policy: str | None = None,
                                session: SessionSpec, availability: AvailabilitySpec, adjustment: AdjustmentSpec,
                                price_unit: PriceUnit) -> ConfigSpec:
    """Final ConfigSpec; every parameter is explicit with no default (auction choices as in `session.trade.top_k`)."""
    s = _check(policy_version, top_k, evidence_limit, eligibility_policy)
    params = (Parameter("policy_version", s.policy_version), Parameter("top_k", s.top_k),
              Parameter("evidence_limit", s.evidence_limit), Parameter("eligibility_policy", s.eligibility_policy))
    return make_config(TOP_K_IDENTITY, TOP_K_ALGORITHM, params, 1, session, availability, adjustment, price_unit)


def decode_notional_top_k_config(config: ConfigSpec) -> NotionalTopKSettings:
    """Validate the closed notional top-K envelope and return its settings."""
    v = parameter_map(config, TOP_K_IDENTITY, TOP_K_ALGORITHM, _REQUIRED, frozenset())
    s = _check(v["policy_version"], v["top_k"], v["evidence_limit"], v["eligibility_policy"])
    assert config.price_unit is not None
    expected = build_notional_top_k_config(
        policy_version=s.policy_version, top_k=s.top_k, evidence_limit=s.evidence_limit,
        eligibility_policy=s.eligibility_policy, session=config.session, availability=config.availability,
        adjustment=config.adjustment, price_unit=config.price_unit)
    if config != expected:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "configuration is not the final canonical notional top-K envelope")
    return s


def _evidence(entity: EntityKey, config: ConfigSpec, row: TopKTradeRow) -> EvidenceRow:
    boundary = "closing_auction" if row.event_ns == config.availability.market_cutoff_ns else "ordinary"
    return EvidenceRow(entity, TOP_K_FEATURE, row.input_id, row.event_id, row.event_ns, row.known_at_ns,
                       None, None, "consumed", None, boundary)


def _result(entity: EntityKey, config: ConfigSpec, settings: NotionalTopKSettings, status: Status,
            reasons: set[Reason], expected: int | None, observed: int, rows: Sequence[TopKTradeRow],
            bindings: tuple[InputBinding, ...]) -> FeatureResult:
    available = status == Status.AVAILABLE
    value = notional_cell(settings.top_k, rows) if available else None
    metadata = ResultMetadata(config.session.namespace, entity.session_id, config.availability, config.digest, bindings,
                              "python-exact", __version__, settings.evidence_limit)
    return FeatureResult(
        (FeatureColumn(TOP_K_FEATURE, TOP_K_ALGORITHM, ValueType.TOP_K_TRADES, TOP_K_UNIT, (entity,), (value,)),),
        (QualityRow(entity, TOP_K_FEATURE, status, expected, observed, ordered(reasons)),), metadata,
        tuple(_evidence(entity, config, row) for row in rows) if available else ())


def compute_trade_top_k_notional(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None],
                                 config: ConfigSpec, *, entity: EntityKey, features: tuple[str, ...]) -> FeatureResult:
    """`tape.top_k_notional`; `batches` is the fixed nullable slot `(trades,)`."""
    check_features(features, TOP_K_FEATURES)
    settings = decode_notional_top_k_config(config)
    entity = check_entity(entity, config)
    (trades,) = check_slots(batches, 1, (DataKind.TRADE,))
    if trades is None:
        return _result(entity, config, settings, Status.MISSING_INPUT, {Reason.ABSENT_INPUT}, 0, 0, (), ())
    columns = admit_trades(trades, config, entity, settings.eligibility_policy)
    n = trades.row_count
    flags = knowledge_flags(columns, n, config)
    reasons: set[Reason] = {flag for flag in flags if flag is not None}
    unready = sum(1 for flag in flags if flag is not None)
    delivered = "price" in columns and "size" in columns
    input_id = trades.metadata.source.input_id
    kept: list[tuple[Key, TopKTradeRow]] = []
    eligible = 0
    for i in range(n):
        if columns["eligible"][i] is not True:
            continue
        eligible += 1
        if not delivered:
            continue
        row = TopKTradeRow(input_id, columns["event_id"][i], columns["event_ns"][i], columns["order_key"][i],
                           columns["known_at_ns"][i] if "known_at_ns" in columns else None,
                           columns["price"][i], columns["size"][i])
        _insert(kept, notional_key(row), row)
        if len(kept) > settings.top_k:
            kept.pop()
    absent = eligible > 0 and not delivered
    if absent:
        reasons.add(Reason.ABSENT_INPUT)
    cov = trades.metadata.coverage
    if not cov.complete or cov.expected != n:
        reasons.add(Reason.GOVERNED_GAP)
    status = Status.AVAILABLE if not reasons else first_status(reasons)
    return _result(entity, config, settings, status, reasons, cov.expected, 0 if absent else n - unready,
                   tuple(row for _, row in kept),
                   (InputBinding("trades", DataKind.TRADE, trades.metadata),))


@dataclass(frozen=True)
class NotionalPartial:
    """One partial result of a disjoint population with the config and entity it was computed for."""

    config: ConfigSpec
    entity: EntityKey
    result: FeatureResult


def merge_trade_top_k_notional(partials: Sequence[NotionalPartial]) -> FeatureResult:
    """Merge compatible partials of disjoint populations (DP-K6); the caller certifies disjointness of unretained rows.

    Refusal order: empty list, policy version, price unit, adjustment, eligibility policy, K and evidence limit,
    entity / market cutoff / knowledge cutoff, then partial row order, then a retained duplicate event identity.
    """
    if type(partials) not in (tuple, list) or not partials:
        fail(ErrorCode.INVALID_CONFIG, "at least one partial is required")
    if any(type(p) is not NotionalPartial or type(p.config) is not ConfigSpec or type(p.entity) is not EntityKey
           or type(p.result) is not FeatureResult for p in partials):
        fail(ErrorCode.INVALID_SCHEMA, "typed partials (config, entity, result) are required")
    decoded = [decode_notional_top_k_config(p.config) for p in partials]
    first, settings = partials[0], decoded[0]
    for p in partials[1:]:
        if p.config.price_unit != first.config.price_unit:
            fail(ErrorCode.INVALID_UNIT, "partials differ in the price unit")
    for p in partials[1:]:
        if p.config.adjustment != first.config.adjustment:
            fail(ErrorCode.UNSUPPORTED_ADJUSTMENT, "partials differ in the adjustment basis")
    if any(d.eligibility_policy != settings.eligibility_policy for d in decoded[1:]):
        fail(ErrorCode.INVALID_CONFIG, "partials differ in the eligibility policy")
    if any((d.top_k, d.evidence_limit) != (settings.top_k, settings.evidence_limit) for d in decoded[1:]):
        fail(ErrorCode.INVALID_CONFIG, "partials differ in K or the evidence limit")
    for p in partials[1:]:
        cut, know = p.config.availability.market_cutoff_ns, p.config.availability.knowledge_cutoff_ns
        if (p.entity != first.entity or p.config.session.namespace != first.config.session.namespace
                or cut != first.config.availability.market_cutoff_ns
                or know != first.config.availability.knowledge_cutoff_ns):
            fail(ErrorCode.INCONSISTENT_IDENTITY, "partials differ in the entity, market cutoff or knowledge cutoff")
    parts: list[tuple[QualityRow, TopKTrades | None, ResultMetadata]] = []
    for p in partials:
        columns, quality = p.result.values, p.result.quality
        if (len(columns) != 1 or columns[0].feature_id != TOP_K_FEATURE or columns[0].entities != (p.entity,)
                or len(quality) != 1 or quality[0].feature_id != TOP_K_FEATURE or quality[0].entity != p.entity):
            fail(ErrorCode.INVALID_SCHEMA, "each partial is a single tape.top_k_notional result of its entity")
        if p.result.metadata.config_digest != p.config.digest:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "partial result was not computed with its configuration")
        cell = columns[0].values[0]
        if cell is not None and (type(cell) is not TopKTrades or cell.k != settings.top_k):
            fail(ErrorCode.INVALID_CONFIG, "partial cell differs in K")
        parts.append((quality[0], cell, p.result.metadata))
    bindings = tuple(InputBinding(f"p{i}.{b.role}", b.kind, b.metadata, b.schema_version)
                     for i, (_, _, meta) in enumerate(parts) for b in meta.inputs)
    entity = first.entity
    expected: int | None = 0
    observed = 0
    reasons: set[Reason] = set()
    for part_quality, _, _ in parts:
        expected = None if expected is None or part_quality.expected is None else expected + part_quality.expected
        observed += part_quality.observed
        if part_quality.status != Status.AVAILABLE:
            reasons.update(part_quality.reasons)
    if reasons:
        return _result(entity, first.config, settings, first_status(reasons), reasons, expected, observed, (),
                       bindings)
    rows: list[TopKTradeRow] = []
    for _, cell, _ in parts:
        assert cell is not None
        keys = [notional_key(row) for row in cell.rows]
        if keys != sorted(keys):
            fail(ErrorCode.INVALID_ORDER, "partial rows must be in notional rank order")
        rows.extend(cell.rows)
    if len({row.event_id for row in rows}) != len(rows):
        fail(ErrorCode.DUPLICATE, "the same event identity is retained by two partials")
    rows.sort(key=notional_key)
    return _result(entity, first.config, settings, Status.AVAILABLE, set(), expected, observed,
                   rows[:settings.top_k], bindings)

